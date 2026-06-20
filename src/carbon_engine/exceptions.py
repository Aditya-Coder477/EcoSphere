"""
exceptions.py
=============
Domain-specific exceptions for the Carbon Engine.
"""

class CarbonEngineError(Exception):
    """Base exception for all Carbon Engine errors."""
    pass

class MissingColumnError(CarbonEngineError):
    """Raised when a required column is missing from a dataset."""
    pass

class UnknownModeError(CarbonEngineError):
    """Raised when an unknown transport mode is encountered."""
    pass

class UnknownFoodItemError(CarbonEngineError):
    """Raised when an unknown food item is encountered."""
    pass

class MissingCountryDataError(CarbonEngineError):
    """Raised when no country or regional fallback data is available."""
    pass

class InvalidInputError(CarbonEngineError):
    """Raised when input data format or values are invalid."""
    pass
