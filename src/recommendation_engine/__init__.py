"""
Recommendation Engine
=====================
A deterministic, explainable recommendation engine that suggests carbon-reduction actions 
based on a user's footprint profile, behavior, and budget.
"""

from .schemas import (
    ActionDefinition,
    RecommendationContext,
    RankedRecommendation
)
from .exceptions import (
    RecommendationEngineError,
    MissingContextError,
    InvalidActionError
)
from .action_library import get_action_library
from .rules import AdoptionEvaluator, RelevanceEvaluator
from .scoring import ImpactScoreCalculator
from .ranker import RuleBasedRanker
from .recommendation_service import RecommendationService

__all__ = [
    "ActionDefinition",
    "RecommendationContext",
    "RankedRecommendation",
    "RecommendationEngineError",
    "MissingContextError",
    "InvalidActionError",
    "get_action_library",
    "AdoptionEvaluator",
    "RelevanceEvaluator",
    "ImpactScoreCalculator",
    "RuleBasedRanker",
    "RecommendationService",
]
