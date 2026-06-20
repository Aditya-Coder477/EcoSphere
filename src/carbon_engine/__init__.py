"""
Carbon Calculation Engine
=========================
A deterministic, modular engine that calculates carbon footprints from user 
activities and merged datasets using real emission-factor logic.
"""

from .schemas import (
    TransportInput,
    FoodInput,
    ElectricityInput,
    WasteInput,
    CategoryEmission,
    FootprintReport,
    FactorTrace
)

from .exceptions import (
    CarbonEngineError,
    MissingColumnError,
    UnknownModeError,
    UnknownFoodItemError,
    MissingCountryDataError,
    InvalidInputError
)

from .conversion_utils import UnitConverter

from .factor_lookup import EmissionFactorLookup

from .calculators import (
    TransportCarbonCalculator,
    FoodCarbonCalculator,
    ElectricityCarbonCalculator,
    WasteCarbonCalculator
)

from .carbon_aggregator import CarbonFootprintAggregator
from .carbon_report import CarbonReportBuilder

__all__ = [
    "TransportInput",
    "FoodInput",
    "ElectricityInput",
    "WasteInput",
    "CategoryEmission",
    "FootprintReport",
    "FactorTrace",
    "CarbonEngineError",
    "MissingColumnError",
    "UnknownModeError",
    "UnknownFoodItemError",
    "MissingCountryDataError",
    "InvalidInputError",
    "UnitConverter",
    "EmissionFactorLookup",
    "TransportCarbonCalculator",
    "FoodCarbonCalculator",
    "ElectricityCarbonCalculator",
    "WasteCarbonCalculator",
    "CarbonFootprintAggregator",
    "CarbonReportBuilder",
]
