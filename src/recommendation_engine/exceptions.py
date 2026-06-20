"""
exceptions.py
=============
Domain exceptions for the recommendation engine.
"""

class RecommendationEngineError(Exception):
    """Base exception for recommendation engine."""
    pass

class MissingContextError(RecommendationEngineError):
    """Raised when required profile data is missing from the context."""
    pass

class InvalidActionError(RecommendationEngineError):
    """Raised when an action is incorrectly defined or invalid."""
    pass
