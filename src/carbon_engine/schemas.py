"""
schemas.py
==========
Pydantic-free dataclasses for inputs, outputs, and global constants.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


# IPCC AR6 Global Warming Potential (GWP) constants for 100-year timeframe
GWP_CO2 = 1.0
GWP_CH4_FOSSIL = 29.8     # Includes climate-carbon feedbacks
GWP_CH4_BIOGENIC = 27.2   # Includes climate-carbon feedbacks
GWP_N2O = 273.0

# --- Input Schemas ---

@dataclass
class TransportInput:
    mode: str
    distance_km: float
    vehicle_type: Optional[str] = None
    fuel_type: Optional[str] = None

@dataclass
class FoodInput:
    food_item: str
    quantity_kg: float

@dataclass
class ElectricityInput:
    country: str
    kwh_per_month: Optional[float] = None  # If None, will fallback to country average
    year: Optional[int] = None

@dataclass
class WasteInput:
    country: str
    waste_generated_kg_per_day: Optional[float] = None # If None, will fallback to country average
    year: Optional[int] = None


# --- Output Schemas ---

@dataclass
class FactorTrace:
    """Traceability for a single emission calculation."""
    category: str
    factor_value: float
    factor_unit: str
    source_dataset: str
    description: str

@dataclass
class CategoryEmission:
    """Emission result for a specific category."""
    category: str
    emissions_kg_co2e: float
    details: Dict[str, Any] = field(default_factory=dict)
    traces: List[FactorTrace] = field(default_factory=list)
    completeness_flags: Dict[str, bool] = field(default_factory=dict)

@dataclass
class FootprintReport:
    """Unified carbon footprint report."""
    user_id: str
    total_emissions_kg_co2e: float
    category_emissions: Dict[str, CategoryEmission]
    dominant_source: str
    category_shares_pct: Dict[str, float]
    human_readable_summary: str
    recommendation_hooks: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to a JSON-serializable dictionary."""
        return {
            "user_id": self.user_id,
            "total_emissions_kg_co2e": round(self.total_emissions_kg_co2e, 2),
            "dominant_source": self.dominant_source,
            "category_shares_pct": {k: round(v, 2) for k, v in self.category_shares_pct.items()},
            "human_readable_summary": self.human_readable_summary,
            "recommendation_hooks": self.recommendation_hooks,
            "category_details": {
                cat: {
                    "emissions_kg_co2e": round(cem.emissions_kg_co2e, 2),
                    "details": cem.details,
                    "traces": [
                        {
                            "factor_value": t.factor_value,
                            "factor_unit": t.factor_unit,
                            "source_dataset": t.source_dataset,
                            "description": t.description
                        } for t in cem.traces
                    ],
                    "completeness_flags": cem.completeness_flags
                } for cat, cem in self.category_emissions.items()
            }
        }
