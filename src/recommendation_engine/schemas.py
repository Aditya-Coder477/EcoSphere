"""
schemas.py
==========
Pydantic-free dataclasses for recommendation engine objects.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable


@dataclass
class RecommendationContext:
    """The user's context, including footprint emissions and behavioral traits."""
    user_id: str
    
    # Footprint
    category_emissions: Dict[str, float]  # e.g., {"transport": 1200.0, "food": 800.0}
    total_emissions_kg_co2e: float
    dominant_emission_source: str
    
    # Demographics and Traits
    occupation: str = ""
    city_type: str = ""
    budget_profile: str = "medium"  # "low", "medium", "high"
    commute_mode: str = ""
    is_vegetarian: bool = False
    
    # Behavioral scores (0-100)
    price_sensitivity_score: float = 50.0
    commute_flexibility_score: float = 50.0
    diet_flexibility_score: float = 50.0
    energy_saving_flexibility_score: float = 50.0
    synthetic_green_adoption_probability: float = 0.5


@dataclass
class ActionDefinition:
    """A single predefined action in the recommendation library."""
    action_id: str
    title: str
    category: str
    description: str
    
    # Properties for scoring
    base_carbon_saved_pct: float  # Percentage of the category's emissions this can save
    base_effort: float            # 1 to 10 scale (1 = easiest)
    base_cost: float              # 1 to 10 scale (1 = cheapest)
    
    # Logic hooks
    # Takes RecommendationContext, returns bool (True if eligible, False to exclude)
    eligibility_rule: Callable[[RecommendationContext], bool]
    
    # Explanation generation
    explanation_template: str


@dataclass
class RankedRecommendation:
    """An action that has been scored and ranked for a specific user."""
    action_id: str
    title: str
    category: str
    description: str
    
    # Scores
    impact_score: float
    carbon_saved_kg: float
    adoption_probability: float
    relevance: float
    effort: float
    cost: float
    
    ranking_position: int
    impact_level: str  # "high", "medium", "low"
    explanation: str

    def to_dict(self) -> dict:
        return {
            "action_id": self.action_id,
            "title": self.title,
            "category": self.category,
            "description": self.description,
            "impact_score": round(self.impact_score, 4),
            "carbon_saved_kg": round(self.carbon_saved_kg, 2),
            "adoption_probability": round(self.adoption_probability, 4),
            "relevance": round(self.relevance, 4),
            "effort": round(self.effort, 2),
            "cost": round(self.cost, 2),
            "ranking_position": self.ranking_position,
            "impact_level": self.impact_level,
            "explanation": self.explanation
        }
