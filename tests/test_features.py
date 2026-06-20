import pandas as pd
import pytest
import numpy as np

from src.feature_engineering.transport_features import build_transport_features
from src.feature_engineering.waste_features import build_waste_features
from src.feature_engineering.context_features import build_behavior_features

def test_build_transport_features():
    transport_df = pd.DataFrame({
        "estimated_monthly_transport_emissions_kg_co2e": [100.0, 200.0],
        "weekly_commute_distance_km": [50.0, 0.0],
        "commute_mode": ["Bus", "Car"],
        "monthly_flight_distance_km": [0.0, 500.0]
    })
    factors_df = pd.DataFrame({
        "commute_mode": ["Bus", "Car"],
        "commute_mode_emission_factor": [0.1, 0.2]
    })
    
    res = build_transport_features(transport_df, factors_df)
    
    assert "annual_transport_emission_kg_co2e" in res.columns
    assert res.loc[0, "annual_transport_emission_kg_co2e"] == 1200.0
    
    assert "is_low_carbon_commuter" in res.columns
    assert res.loc[0, "is_low_carbon_commuter"] == True
    assert res.loc[1, "is_low_carbon_commuter"] == False
    
    assert "annual_flight_emission_kg_co2e" in res.columns
    assert res.loc[0, "annual_flight_emission_kg_co2e"] == 0.0

def test_build_waste_features():
    waste_df = pd.DataFrame({
        "waste_kg_per_cap_per_day": [1.0, 2.0],
        "waste_emission_factor_kg_co2e_per_kg": [0.5, 0.5],
        "landfill_rate_pct": [50.0, 80.0],
        "recycling_rate_pct": [30.0, 10.0],
        "composting_rate_pct": [20.0, 10.0]
    })
    
    res = build_waste_features(waste_df)
    
    assert "waste_emission_kg_co2e_per_capita_per_year" in res.columns
    # 1.0 * 365.0 * 0.5 = 182.5
    assert res.loc[0, "waste_emission_kg_co2e_per_capita_per_year"] == 182.5
    
    assert "waste_diversion_rate_pct" in res.columns
    assert res.loc[0, "waste_diversion_rate_pct"] == 50.0
    
    assert "waste_management_tier" in res.columns
    assert res.loc[0, "waste_management_tier"] == "Moderate"

def test_build_behavior_features():
    df = pd.DataFrame({
        "price_sensitivity": [50.0, 100.0],
        "commute_flexibility": [50.0, 80.0],
        "diet_flexibility": [50.0, 60.0],
        "digital_engagement": [80.0, 20.0],
        "social_influence": [80.0, 40.0],
        "adoption_probability": [0.8, 0.2],
        "awareness_score": [90.0, 30.0]
    })
    
    res = build_behavior_features(df)
    
    assert "effort_score" in res.columns
    assert res.loc[0, "effort_score"] == 50.0
    
    assert "green_readiness_index" in res.columns
    assert res.loc[0, "green_readiness_index"] == pytest.approx(0.72)  # (90/100) * 0.8
    
    assert "behavior_adoption_tier" in res.columns
    assert res.loc[0, "behavior_adoption_tier"] == "Very Likely"
    assert res.loc[1, "behavior_adoption_tier"] == "Unlikely"
