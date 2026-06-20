"""
tests/test_edge_cases.py
========================
Edge cases and integration tests for the Carbon Footprint Awareness Platform.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from unittest.mock import patch, MagicMock

# Carbon Engine Imports
from src.carbon_engine import (
    TransportInput, FoodInput, ElectricityInput, WasteInput,
    UnitConverter, EmissionFactorLookup, CarbonFootprintAggregator
)
from src.carbon_engine.calculators import (
    TransportCarbonCalculator, FoodCarbonCalculator, 
    ElectricityCarbonCalculator, WasteCarbonCalculator
)

# Recommendation Engine Imports
from src.recommendation_engine import RecommendationService
from src.recommendation_engine.schemas import RecommendationContext, ActionDefinition
from src.recommendation_engine.scoring import ImpactScoreCalculator
from src.recommendation_engine.rules import RelevanceEvaluator

# Pipeline/Cleaning/Integration Imports
from src.cleaning.loader import DatasetLoader
from src.cleaning.cleaner import CleaningPipeline
from src.cleaning.validators import validate_required_columns
from src.feature_engineering.transport_features import build_transport_features
from src.feature_engineering.electricity_features import build_electricity_features
from src.feature_engineering.food_features import build_food_features
from src.feature_engineering.waste_features import build_waste_features
from src.feature_engineering.context_features import build_country_context_features, build_behavior_features
from src.integration.merger import IntegrationPipeline
from src.llm import ExplanationService, ExplanationRequest


# ===========================================================================
# 1. Carbon Engine Edge Cases
# ===========================================================================

def test_transport_zero_distance():
    """Edge Case: Test transport calculator with zero distance."""
    calc = TransportCarbonCalculator()
    inp = TransportInput(mode="Car", distance_km=0.0)
    res = calc.calculate(inp)
    
    assert res.emissions_kg_co2e == 0.0
    assert res.completeness_flags["zero_distance"] is True


def test_transport_negative_distance():
    """Edge Case: Test transport calculator with negative distance."""
    calc = TransportCarbonCalculator()
    inp = TransportInput(mode="Car", distance_km=-50.0)
    res = calc.calculate(inp)
    
    assert res.emissions_kg_co2e == 0.0
    assert res.completeness_flags["zero_distance"] is True


def test_electricity_zero_consumption():
    """Edge Case: Test electricity calculator with zero consumption."""
    calc = ElectricityCarbonCalculator()
    inp = ElectricityInput(country="United States", kwh_per_month=0.0)
    res = calc.calculate(inp)
    
    assert res.emissions_kg_co2e == 0.0
    assert res.completeness_flags["used_regional_fallback_kwh"] is False


def test_electricity_missing_country_fallback():
    """Edge Case: Test electricity calculator with a missing/unknown country."""
    calc = ElectricityCarbonCalculator()
    # "Atlantis" is not in the database, should fallback to global/regional average grid intensity
    inp = ElectricityInput(country="Atlantis", kwh_per_month=100.0)
    res = calc.calculate(inp)
    
    # Verify that it produces a valid positive carbon footprint rather than crashing
    assert res.emissions_kg_co2e > 0.0
    assert res.completeness_flags["missing_grid_intensity"] is True


def test_food_zero_quantity():
    """Edge Case: Test food calculator with zero quantity."""
    calc = FoodCarbonCalculator()
    inp = [FoodInput(food_item="Beef (beef herd)", quantity_kg=0.0)]
    res = calc.calculate(inp)
    
    assert res.emissions_kg_co2e == 0.0


def test_food_unknown_item():
    """Edge Case: Test food calculator with an unknown food item."""
    calc = FoodCarbonCalculator()
    inp = [
        FoodInput(food_item="Beef (beef herd)", quantity_kg=1.0),
        FoodInput(food_item="Vibranium Soup", quantity_kg=2.0)
    ]
    res = calc.calculate(inp)
    
    # Should only calculate emissions for known items and flag missing factors
    assert res.emissions_kg_co2e > 0.0
    assert res.completeness_flags["missing_factors"] is True
    assert "Vibranium Soup" in res.details["items_not_found"]


def test_waste_missing_country_fallback():
    """Edge Case: Test waste calculator with missing country data."""
    calc = WasteCarbonCalculator()
    inp = WasteInput(country="Atlantis")
    res = calc.calculate(inp)
    
    # Should fallback to global defaults safely without throwing an exception
    assert res.emissions_kg_co2e > 0.0
    assert res.completeness_flags["missing_factors"] is True
    assert res.completeness_flags["used_country_average_waste"] is True


# ===========================================================================
# 2. Recommendation Engine Edge Cases
# ===========================================================================

def test_recommendation_low_budget_user():
    """Edge Case: Test recommendation scoring modifications for low-budget users."""
    service = RecommendationService()
    profile = {
        "user_id": "low_budget_user",
        "category_emissions": {"electricity": 1000.0, "transport": 500.0},
        "budget_profile": "low"
    }
    
    recs = service.generate_recommendations(profile, top_n=20)
    
    # Ensure expensive recommendations (like installing solar panels "EL-01") 
    # are penalised / ranked lower than cheap options (like LED lights "EL-02" or adjusting thermostat "EL-03")
    solar_rec = next((r for r in recs if r.action_id == "EL-01"), None)
    led_rec = next((r for r in recs if r.action_id == "EL-02"), None)
    
    if solar_rec and led_rec:
        assert led_rec.impact_score > solar_rec.impact_score


def test_recommendation_vegetarian_user():
    """Edge Case: Verify that vegetarian users do not receive meat-reduction recommendations."""
    service = RecommendationService()
    profile = {
        "user_id": "veg_user",
        "category_emissions": {"food": 1200.0},
        "is_vegetarian": True
    }
    
    recs = service.generate_recommendations(profile, top_n=10)
    action_ids = [r.action_id for r in recs]
    
    # Food actions related to reducing meat/beef should be excluded
    assert "FD-01" not in action_ids  # Reduce beef
    assert "FD-02" not in action_ids  # Adopt plant-based diet


def test_recommendation_student_commuter():
    """Edge Case: Student user with high commute distance boost."""
    service = RecommendationService()
    profile = {
        "user_id": "student_commuter",
        "category_emissions": {"transport": 5000.0},
        "commute_mode": "Car",
        "weekly_commute_distance_km": 150,
        "occupation": "student",
        "budget_profile": "low"
    }
    
    recs = service.generate_recommendations(profile, top_n=10)
    action_ids = [r.action_id for r in recs]
    
    # Should recommend carpooling or public transport (e.g. "TR-01", "TR-02")
    # and they should be ranked high due to relevance boost
    public_transport_rec = next((r for r in recs if r.action_id in ["TR-01", "TR-02"]), None)
    assert public_transport_rec is not None
    assert public_transport_rec.relevance > 1.0


# ===========================================================================
# 3. Full Integration Flow Test
# ===========================================================================

@patch("src.llm.explanation_service.GeminiClient")
def test_full_pipeline_to_assistant_flow(mock_gemini_client, tmp_path):
    """
    Integration Test: Full data flow:
    dataset -> cleaning -> engineered features -> carbon calculation -> recommendations -> explanation
    """
    # 1. Setup Mock Datasets and Paths
    raw_data = {
        "user_id": ["user_int_01"],
        "commute_mode": ["Car"],
        "weekly_commute_distance_km": [50.0],
        "monthly_flight_distance_km": [200.0],
        "estimated_monthly_transport_emissions_kg_co2e": [100.0],
        "country": ["United States"],
        "kwh_per_month": [300.0],
        "is_vegetarian": [False],
        "budget_profile": ["medium"],
        "occupation": ["professional"]
    }
    df_raw = pd.DataFrame(raw_data)
    
    # 2. Cleaning & Schema Validation
    cleaner = CleaningPipeline()
    # Simulate generic cleaning
    df_cleaned = cleaner._generic_clean(df_raw, "user_activity")
    validation_res = validate_required_columns(df_cleaned, ["user_id", "commute_mode"])
    assert validation_res.passed is True
    
    # 3. Feature Engineering
    # Transport features
    factors_df = pd.DataFrame({
        "mode": ["Car", "Bus", "Short-haul Flight"],
        "co2e_kg_per_unit": [0.20, 0.08, 0.25]
    })
    
    # Create transport_activity df structured for feature builder
    transport_activity_df = pd.DataFrame({
        "user_id": ["user_int_01"],
        "commute_mode": ["Car"],
        "weekly_commute_distance_km": [50.0],
        "monthly_flight_distance_km": [200.0],
        "estimated_monthly_transport_emissions_kg_co2e": [100.0]
    })
    
    df_transport_feats = build_transport_features(transport_activity_df, factors_df)
    assert "annual_transport_emission_kg_co2e" in df_transport_feats.columns
    
    # 4. Carbon Footprint Calculation
    transport_calc = TransportCarbonCalculator()
    user_record = df_transport_feats.iloc[0].to_dict()
    # Add other categories manually for carbon aggregation
    user_record["kwh_per_month"] = 300.0
    user_record["country"] = "United States"
    
    transport_emission = transport_calc.calculate(user_record)
    
    electricity_calc = ElectricityCarbonCalculator()
    electricity_emission = electricity_calc.calculate(ElectricityInput(
        country=user_record["country"], 
        kwh_per_month=user_record["kwh_per_month"]
    ))
    
    # Aggregate
    agg = CarbonFootprintAggregator()
    report = agg.aggregate(
        user_id="user_int_01",
        emissions={
            "transport": transport_emission,
            "electricity": electricity_emission
        }
    )
    
    assert report.total_emissions_kg_co2e > 0.0
    
    # 5. Recommendation Generation & Ranking
    rec_service = RecommendationService()
    profile = {
        "user_id": "user_int_01",
        "category_emissions": report.category_emissions,
        "total_emissions_kg_co2e": report.total_emissions_kg_co2e,
        "dominant_emission_source": report.dominant_source,
        "commute_mode": "Car",
        "is_vegetarian": False,
        "budget_profile": "medium"
    }
    
    recs = rec_service.generate_recommendations(profile, top_n=3)
    assert len(recs) > 0
    assert recs[0].impact_score > 0.0
    
    # 6. LLM Explanation Generation (Mocked Client)
    # Configure mock client
    mock_client_instance = mock_gemini_client.return_value
    mock_client_instance.generate_content.return_value = '{"answer": "Your footprint is 2500 kg, dominated by transport. You should try carpooling.", "grounded_facts": ["Transport is dominant"], "suggested_follow_up_questions": []}'
    mock_client_instance.model_name = "gemini-2.5-flash"
    
    # Create explanation service with mocked client
    service = ExplanationService()
    
    req = ExplanationRequest(
        user_id="user_int_01",
        context_type="footprint",
        context_data=report.to_dict(),
        query="Explain my carbon footprint"
    )
    
    res = service.generate_explanation(req)
    
    assert "dominated by transport" in res.explanation_text
    assert res.model_used is not None
