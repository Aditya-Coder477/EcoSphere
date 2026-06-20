"""
waste_calc.py
=============
Waste carbon calculator.
"""

from typing import Dict, Any, Union
import pandas as pd

from ..schemas import WasteInput, CategoryEmission, FactorTrace
from ..factor_lookup import EmissionFactorLookup
from src.feature_engineering.waste_features import _LANDFILL_FACTOR_KG_CO2E_PER_KG

class WasteCarbonCalculator:
    """Calculates waste emissions based on country disposal rates."""
    
    def __init__(self):
        self.lookup = EmissionFactorLookup()

    def calculate(self, input_data: Union[WasteInput, dict, pd.Series]) -> CategoryEmission:
        """
        Calculate waste emissions.
        Returns CategoryEmission object.
        """
        if isinstance(input_data, pd.Series):
            input_data = input_data.to_dict()
            
        if isinstance(input_data, dict):
            inp = WasteInput(
                country=str(input_data.get('country', '')),
                waste_generated_kg_per_day=float(input_data['waste_generated_kg_per_day']) if pd.notna(input_data.get('waste_generated_kg_per_day')) else None,
                year=int(input_data['year']) if pd.notna(input_data.get('year')) else None
            )
        else:
            inp = input_data

        flags = {"missing_country": False, "missing_factors": False, "used_country_average_waste": False}
        traces = []
        
        if not inp.country:
            flags["missing_country"] = True
            return CategoryEmission(
                category="waste",
                emissions_kg_co2e=0.0,
                completeness_flags=flags
            )

        waste_data = self.lookup.get_waste_factors(inp.country, inp.year)
        if waste_data is None:
            # Fallback to a global average if missing
            waste_data = self.lookup.get_waste_factors("World", inp.year)
            if waste_data is None:
                # If "World" is not in dataset, use generic fallback
                waste_data = {
                    "waste_generated_kg_per_capita_per_day": 1.0, # generic kg
                    "landfill_rate_pct": 50.0, 
                    "emission_factor": _LANDFILL_FACTOR_KG_CO2E_PER_KG
                }
            
            flags["missing_factors"] = True
            traces.append(FactorTrace(
                category="waste",
                factor_value=waste_data['emission_factor'],
                factor_unit="kg CO2e per kg waste",
                source_dataset="waste.csv (fallback)",
                description=f"Fallback waste emission factor for {inp.country}"
            ))
        else:
            traces.append(FactorTrace(
                category="waste",
                factor_value=waste_data['emission_factor'],
                factor_unit="kg CO2e per kg waste",
                source_dataset="waste.csv",
                description=f"Waste emission factor for {inp.country}"
            ))

        kg_per_day = inp.waste_generated_kg_per_day
        if kg_per_day is None or kg_per_day <= 0:
            kg_per_day = waste_data["waste_generated_kg_per_capita_per_day"]
            flags["used_country_average_waste"] = True

        # Calculation logic: total waste * emission factor
        # If landfill rate is provided, we might adjust, but the dataset gives an overall emission factor
        # which usually accounts for the country's specific disposal mix (landfill vs recycling).
        annual_waste_kg = kg_per_day * 365
        emissions_kg_co2e = annual_waste_kg * waste_data["emission_factor"]

        return CategoryEmission(
            category="waste",
            emissions_kg_co2e=emissions_kg_co2e,
            traces=traces,
            completeness_flags=flags,
            details={
                "country": inp.country, 
                "annual_waste_kg": annual_waste_kg,
                "landfill_rate_pct": waste_data["landfill_rate_pct"]
            }
        )
