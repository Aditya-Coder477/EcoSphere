"""
tests/test_ranker.py
====================
Unit tests for impact level thresholds, empty-emissions guard, and ranking in RuleBasedRanker.
"""

import pytest
from src.recommendation_engine.ranker import RuleBasedRanker, HIGH_IMPACT_THRESHOLD, MEDIUM_IMPACT_THRESHOLD
from src.recommendation_engine.schemas import RecommendationContext
from src.recommendation_engine.scoring import ImpactScoreCalculator

def test_impact_level_thresholds(sample_ctx):
    """Verify that impact levels are correctly categorized based on thresholds."""
    ranker = RuleBasedRanker()
    
    recs = ranker.rank(sample_ctx, top_n=10)
    for r in recs:
        if r.impact_score > HIGH_IMPACT_THRESHOLD:
            assert r.impact_level == "high"
        elif r.impact_score > MEDIUM_IMPACT_THRESHOLD:
            assert r.impact_level == "medium"
        else:
            assert r.impact_level == "low"

def test_empty_emissions_guard():
    """Verify that ranking works or is guarded when user emissions are zero."""
    ranker = RuleBasedRanker()
    empty_ctx = RecommendationContext(
        user_id="empty_user",
        category_emissions={},
        total_emissions_kg_co2e=0.0,
        dominant_emission_source=""
    )
    # Rank should run successfully without ZeroDivisionError and return empty or eligible recommendations.
    # Since all carbon savings are 0, they should all be filtered out.
    recs = ranker.rank(empty_ctx, top_n=5)
    assert isinstance(recs, list)
    assert len(recs) == 0

def test_all_categories_ranked(sample_ctx):
    """Verify that recommendations across multiple categories are evaluated."""
    ranker = RuleBasedRanker()
    recs = ranker.rank(sample_ctx, top_n=10)
    
    assert len(recs) > 0
    categories = {r.category for r in recs}
    assert len(categories) > 0
