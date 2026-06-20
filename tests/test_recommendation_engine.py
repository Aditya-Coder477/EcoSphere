"""
test_recommendation_engine.py
=============================
Tests for the deterministic Recommendation Engine.
"""

import pytest

from src.recommendation_engine.schemas import RecommendationContext, ActionDefinition
from src.recommendation_engine.rules import AdoptionEvaluator, RelevanceEvaluator
from src.recommendation_engine.scoring import ImpactScoreCalculator
from src.recommendation_engine.recommendation_service import RecommendationService


def test_impact_score_formula_safety():
    """Ensure zero-division safety and basic math correctness."""
    ctx = RecommendationContext(
        user_id="U1",
        category_emissions={"transport": 1000.0},
        total_emissions_kg_co2e=1000.0,
        dominant_emission_source="transport"
    )
    
    # An action that saves 50% of transport (500kg)
    action = ActionDefinition(
        action_id="TEST-1",
        title="Test Action",
        category="transport",
        description="",
        base_carbon_saved_pct=50.0,
        base_effort=0.0,  # Zero effort
        base_cost=0.0,    # Zero cost
        eligibility_rule=lambda c: True,
        explanation_template=""
    )
    
    carbon_saved = ImpactScoreCalculator.calculate_carbon_saved_kg(action, ctx)
    assert carbon_saved == 500.0
    
    cost = ImpactScoreCalculator.calculate_adjusted_cost(action, ctx)
    effort = ImpactScoreCalculator.calculate_adjusted_effort(action, ctx)
    
    assert cost == 0.1  # min floor
    assert effort == 0.1 # min floor
    
    score = ImpactScoreCalculator.calculate_impact_score(
        carbon_saved_kg=carbon_saved,
        adoption_prob=1.0,
        relevance=1.0,
        effort=effort,
        cost=cost
    )
    
    # (500 * 1 * 1) / (0.1 + 0.1) = 500 / 0.2 = 2500
    assert score == 2500.0


def test_vegetarian_exclusion():
    """Ensure vegetarian users don't get the 'Reduce Beef' recommendation."""
    service = RecommendationService()
    
    profile = {
        "user_id": "U2",
        "category_emissions": {"food": 1000.0},
        "is_vegetarian": True
    }
    
    recs = service.generate_recommendations(profile, top_n=10)
    
    action_ids = [r.action_id for r in recs]
    assert "FD-01" not in action_ids  # Reduce beef should be excluded
    assert "FD-02" not in action_ids  # Adopt plant-based should be excluded


def test_student_budget_relevance():
    """Ensure students and low-budget profiles modify relevance and cost."""
    ctx = RecommendationContext(
        user_id="U3",
        category_emissions={},
        total_emissions_kg_co2e=0.0,
        dominant_emission_source="",
        occupation="student",
        budget_profile="low"
    )
    
    # Low cost action
    action_low = ActionDefinition(
        action_id="LOW", title="", category="", description="",
        base_carbon_saved_pct=10.0, base_effort=1.0, base_cost=2.0,
        eligibility_rule=lambda c: True, explanation_template=""
    )
    
    # High cost action
    action_high = ActionDefinition(
        action_id="HIGH", title="", category="", description="",
        base_carbon_saved_pct=10.0, base_effort=1.0, base_cost=8.0,
        eligibility_rule=lambda c: True, explanation_template=""
    )
    
    rel_low = RelevanceEvaluator.calculate(action_low, ctx)
    rel_high = RelevanceEvaluator.calculate(action_high, ctx)
    
    assert rel_low > 1.0  # Student + low cost = boost
    assert rel_high < 1.0 # Student + high cost = penalty
    
    cost_high = ImpactScoreCalculator.calculate_adjusted_cost(action_high, ctx)
    assert cost_high == 12.0 # 8.0 * 1.5 because budget is low


def test_full_ranking_order():
    """Ensure recommendations are sorted strictly descending by impact score."""
    service = RecommendationService()
    
    profile = {
        "user_id": "U4",
        "category_emissions": {
            "transport": 5000.0,  # Dominant
            "electricity": 1000.0
        },
        "city_type": "Urban",
        "commute_mode": "Car",
        "synthetic_green_adoption_probability": 0.8
    }
    
    recs = service.generate_recommendations(profile, top_n=5)
    
    # Check sorting
    for i in range(len(recs) - 1):
        assert recs[i].impact_score >= recs[i+1].impact_score
        assert recs[i].ranking_position == i + 1
        
    # Check explanation formatting
    assert "{cat_pct}" not in recs[0].explanation  # Should be formatted
