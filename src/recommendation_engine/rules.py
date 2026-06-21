"""
rules.py
========
Heuristics and rule evaluators for adoption probability and relevance.
"""

from .schemas import ActionDefinition, RecommendationContext

# ---------------------------------------------------------------------------
# Named multipliers and thresholds for evaluation logic
# ---------------------------------------------------------------------------
FLEXIBILITY_SCALING_BASE: float = 50.0

DOMINANT_SOURCE_BOOST: float = 1.5
STUDENT_LOW_COST_BOOST: float = 1.2
STUDENT_HIGH_COST_PENALTY: float = 0.7
LOW_BUDGET_HIGH_COST_PENALTY: float = 0.5
HIGH_BUDGET_HIGH_COST_BOOST: float = 1.2

STUDENT_LOW_COST_THRESHOLD: float = 3.0
STUDENT_HIGH_COST_THRESHOLD: float = 7.0
BUDGET_HIGH_COST_THRESHOLD: float = 5.0


class AdoptionEvaluator:
    """Evaluates the probability that a user will adopt a specific action."""
    
    @staticmethod
    def calculate(action: ActionDefinition, ctx: RecommendationContext) -> float:
        """
        Calculates Adoption Probability (0.0 to 1.0).
        Uses the user's synthetic green adoption probability as a base,
        adjusted by specific flexibility scores.
        """
        # Base probability from the user's profile
        prob = ctx.synthetic_green_adoption_probability

        # Adjust based on specific action category and flexibility scores
        # Flex scores are 0-100, so we scale them around 50 (neutral = 1.0 multiplier)
        if action.category == "transport":
            flex_multiplier = ctx.commute_flexibility_score / FLEXIBILITY_SCALING_BASE
            prob *= flex_multiplier
        elif action.category == "food":
            flex_multiplier = ctx.diet_flexibility_score / FLEXIBILITY_SCALING_BASE
            prob *= flex_multiplier
        elif action.category == "electricity":
            flex_multiplier = ctx.energy_saving_flexibility_score / FLEXIBILITY_SCALING_BASE
            prob *= flex_multiplier
        
        # Hard limits
        return max(0.01, min(1.0, prob))


class RelevanceEvaluator:
    """Evaluates how relevant an action is to the user's specific context."""
    
    @staticmethod
    def calculate(action: ActionDefinition, ctx: RecommendationContext) -> float:
        """
        Calculates a Relevance multiplier (default around 1.0).
        """
        relevance = 1.0
        
        # 1. Dominant Source Boost
        if action.category == ctx.dominant_emission_source:
            relevance *= DOMINANT_SOURCE_BOOST
            
        # 2. Occupation/Context Adjustments
        if ctx.occupation.lower() == "student":
            # Students often find low-cost, low-effort actions more relevant
            if action.base_cost <= STUDENT_LOW_COST_THRESHOLD:
                relevance *= STUDENT_LOW_COST_BOOST
            if action.base_cost > STUDENT_HIGH_COST_THRESHOLD:
                relevance *= STUDENT_HIGH_COST_PENALTY
                
        # 3. Budget adjustments
        if ctx.budget_profile == "low" and action.base_cost > BUDGET_HIGH_COST_THRESHOLD:
            relevance *= LOW_BUDGET_HIGH_COST_PENALTY
        elif ctx.budget_profile == "high" and action.base_cost > BUDGET_HIGH_COST_THRESHOLD:
            relevance *= HIGH_BUDGET_HIGH_COST_BOOST
            
        return max(0.1, relevance)
