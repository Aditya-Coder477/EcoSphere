from pydantic import BaseModel
from typing import Dict, List, Any

class RecommendationRequest(BaseModel):
    user_id: str
    category_emissions: Dict[str, float]
    total_emissions_kg_co2e: float
    dominant_emission_source: str
    occupation: str = ""
    city_type: str = ""
    budget_profile: str = "medium"
    commute_mode: str = ""
    is_vegetarian: bool = False
    synthetic_green_adoption_probability: float = 0.5

class RankedRecommendationModel(BaseModel):
    action_id: str
    title: str
    category: str
    description: str
    impact_score: float
    carbon_saved_kg: float
    adoption_probability: float
    relevance: float
    effort: float
    cost: float
    ranking_position: int
    impact_level: str
    explanation: str

class RecommendationResponse(BaseModel):
    user_id: str
    recommendations: List[RankedRecommendationModel]
