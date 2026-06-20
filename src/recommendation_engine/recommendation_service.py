"""
recommendation_service.py
=========================
High level service bridging footprint reports and the ranker.
"""

from typing import Dict, Any, List

from .schemas import RecommendationContext, RankedRecommendation
from .ranker import RuleBasedRanker

class RecommendationService:
    """Service endpoint for generating recommendations."""

    def __init__(self):
        self.ranker = RuleBasedRanker()

    def _build_context(self, user_profile: Dict[str, Any]) -> RecommendationContext:
        """
        Parses a unified profile dictionary (from DB, CSV, or Carbon Engine) 
        into a RecommendationContext.
        """
        # Default safety extractions
        cat_emissions = user_profile.get("category_emissions", {})
        
        # Calculate total if missing
        total = user_profile.get("total_emissions_kg_co2e")
        if total is None:
            total = sum(cat_emissions.values())
            
        # Infer dominant source if missing
        dominant = user_profile.get("dominant_emission_source")
        if not dominant and cat_emissions:
            dominant = max(cat_emissions.items(), key=lambda x: x[1])[0]
            
        return RecommendationContext(
            user_id=str(user_profile.get("user_id", "unknown")),
            category_emissions=cat_emissions,
            total_emissions_kg_co2e=total,
            dominant_emission_source=dominant or "none",
            occupation=str(user_profile.get("occupation", "")),
            city_type=str(user_profile.get("city_type", "")),
            budget_profile=str(user_profile.get("budget_profile", "medium")).lower(),
            commute_mode=str(user_profile.get("commute_mode", "")),
            is_vegetarian=bool(user_profile.get("is_vegetarian", False)),
            price_sensitivity_score=float(user_profile.get("price_sensitivity_score", 50.0)),
            commute_flexibility_score=float(user_profile.get("commute_flexibility_score", 50.0)),
            diet_flexibility_score=float(user_profile.get("diet_flexibility_score", 50.0)),
            energy_saving_flexibility_score=float(user_profile.get("energy_saving_flexibility_score", 50.0)),
            synthetic_green_adoption_probability=float(user_profile.get("synthetic_green_adoption_probability", 0.5))
        )

    def generate_recommendations(self, user_profile: Dict[str, Any], top_n: int = 3) -> List[RankedRecommendation]:
        """
        Main entry point to get recommendations for a user.
        """
        ctx = self._build_context(user_profile)
        return self.ranker.rank(ctx, top_n=top_n)
