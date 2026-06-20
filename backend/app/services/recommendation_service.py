"""
recommendation_service.py
=========================
Integrates with src.recommendation_engine.
"""

from backend.app.schemas.recommendation import RecommendationRequest, RecommendationResponse
from src.recommendation_engine import RecommendationService as CoreRecommendationService

def generate_recommendations(request: RecommendationRequest, top_n: int = 3) -> RecommendationResponse:
    """
    Orchestrates the rule-based recommendation generation.
    """
    core_service = CoreRecommendationService()
    
    # Map the Pydantic schema to the dict expected by the core service
    profile_dict = request.model_dump()
    
    ranked_recs = core_service.generate_recommendations(profile_dict, top_n=top_n)
    
    return RecommendationResponse(
        user_id=request.user_id,
        recommendations=[rec.to_dict() for rec in ranked_recs]
    )
