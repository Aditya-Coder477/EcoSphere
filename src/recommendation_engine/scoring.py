"""
scoring.py
==========
Core impact score calculator.
"""

from .schemas import ActionDefinition, RecommendationContext

class ImpactScoreCalculator:
    """Calculates the final impact score for a recommendation."""
    
    @staticmethod
    def calculate_carbon_saved_kg(action: ActionDefinition, ctx: RecommendationContext) -> float:
        """Calculates absolute kg CO2e saved based on category footprint and base_pct."""
        category_footprint = ctx.category_emissions.get(action.category, 0.0)
        return category_footprint * (action.base_carbon_saved_pct / 100.0)

    @staticmethod
    def calculate_adjusted_cost(action: ActionDefinition, ctx: RecommendationContext) -> float:
        """Adjusts the perceived cost based on user profile."""
        cost = action.base_cost
        if ctx.budget_profile == "low":
            cost *= 1.5 # Feels more expensive
        elif ctx.budget_profile == "high":
            cost *= 0.5 # Feels less expensive
        return max(0.1, cost)
        
    @staticmethod
    def calculate_adjusted_effort(action: ActionDefinition, ctx: RecommendationContext) -> float:
        """Adjusts the perceived effort based on user profile."""
        effort = action.base_effort
        # Just an example: maybe high digital engagement lowers effort for tracking/app actions
        # But for general physical effort, we use the base effort.
        return max(0.1, effort)

    @staticmethod
    def calculate_impact_score(carbon_saved_kg: float, adoption_prob: float, relevance: float, effort: float, cost: float) -> float:
        """
        Executes the core formula:
        Impact Score = (Carbon Saved × Adoption Probability × Relevance) / (Effort + Cost)
        """
        numerator = carbon_saved_kg * adoption_prob * relevance
        denominator = effort + cost
        
        # Denominator safety
        safe_denominator = max(0.1, denominator)
        
        return numerator / safe_denominator
