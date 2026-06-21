"""
recommendation.py
=================
Pydantic request/response schemas for the recommendation API.
Budget profile is enum-validated; emission values are bounded.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Dict, List

_VALID_BUDGET_PROFILES: frozenset[str] = frozenset({"low", "medium", "high"})


class RecommendationRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=128)
    category_emissions: Dict[str, float] = Field(
        ..., description="Emissions per category in kg CO2e"
    )
    total_emissions_kg_co2e: float = Field(..., ge=0)
    dominant_emission_source: str = Field(..., min_length=1, max_length=100)
    occupation: str = Field("", max_length=100)
    city_type: str = Field("", max_length=100)
    budget_profile: str = Field("medium", description="One of: low, medium, high")
    commute_mode: str = Field("", max_length=100)
    is_vegetarian: bool = False
    synthetic_green_adoption_probability: float = Field(0.5, ge=0.0, le=1.0)

    @field_validator("budget_profile")
    @classmethod
    def _validate_budget(cls, v: str) -> str:
        v = v.strip().lower()
        if v not in _VALID_BUDGET_PROFILES:
            raise ValueError(f"budget_profile must be one of {sorted(_VALID_BUDGET_PROFILES)}, got '{v}'")
        return v

    @field_validator("category_emissions")
    @classmethod
    def _validate_emissions(cls, v: Dict[str, float]) -> Dict[str, float]:
        for key, val in v.items():
            if val < 0:
                raise ValueError(f"Emission value for '{key}' must be ≥ 0, got {val}")
        return v


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

