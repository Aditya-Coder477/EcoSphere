"""
electricity_calc.py
===================
Electricity carbon calculator.
"""

from typing import Dict, Any, Union
import pandas as pd

from ..schemas import ElectricityInput, CategoryEmission, FactorTrace
from ..factor_lookup import EmissionFactorLookup
from src.feature_engineering.electricity_features import _REGIONAL_KWH_DEFAULTS

class ElectricityCarbonCalculator:
    """Calculates electricity emissions based on country grid intensity and consumption."""
    
    def __init__(self):
        self.lookup = EmissionFactorLookup()

    def calculate(self, input_data: Union[ElectricityInput, dict, pd.Series]) -> CategoryEmission:
        """
        Calculate electricity emissions.
        Returns CategoryEmission object.
        """
        if isinstance(input_data, pd.Series):
            input_data = input_data.to_dict()
            
        if isinstance(input_data, dict):
            inp = ElectricityInput(
                country=str(input_data.get('country', '')),
                kwh_per_month=float(input_data['kwh_per_month']) if pd.notna(input_data.get('kwh_per_month')) else None,
                year=int(input_data['year']) if pd.notna(input_data.get('year')) else None
            )
        else:
            inp = input_data

        flags = {"missing_country": False, "missing_grid_intensity": False, "used_regional_fallback_kwh": False}
        traces = []
        
        if not inp.country:
            flags["missing_country"] = True
            return CategoryEmission(
                category="electricity",
                emissions_kg_co2e=0.0,
                completeness_flags=flags
            )

        intensity = self.lookup.get_electricity_grid_intensity(inp.country, inp.year)
        if intensity is None:
            # Fallback to World average if country not found
            intensity = self.lookup.get_electricity_grid_intensity("World", inp.year)
            if intensity is None:
                flags["missing_grid_intensity"] = True
                return CategoryEmission(
                    category="electricity",
                    emissions_kg_co2e=0.0,
                    completeness_flags=flags,
                    details={"country": inp.country}
                )
            
            traces.append(FactorTrace(
                category="electricity",
                factor_value=intensity,
                factor_unit="kg CO2 per kWh",
                source_dataset="electricity_mix.csv",
                description=f"World average grid intensity used as fallback for {inp.country}"
            ))
        else:
            traces.append(FactorTrace(
                category="electricity",
                factor_value=intensity,
                factor_unit="kg CO2 per kWh",
                source_dataset="electricity_mix.csv",
                description=f"Grid intensity for {inp.country}"
            ))

        # Determine kWh to use
        kwh_annual = 0.0
        if inp.kwh_per_month is not None and inp.kwh_per_month > 0:
            kwh_annual = inp.kwh_per_month * 12
        else:
            # Try to map to regional default
            # A simple mapping could be done, or we just fallback to World default from electricity_features
            # For simplicity without a full country->region map here, we use World fallback
            kwh_annual = _REGIONAL_KWH_DEFAULTS.get("World", 3300.0)
            flags["used_regional_fallback_kwh"] = True
            
            traces.append(FactorTrace(
                category="electricity",
                factor_value=kwh_annual,
                factor_unit="kWh per year",
                source_dataset="regional_defaults",
                description="World average annual per-capita electricity usage fallback"
            ))

        emissions_kg_co2e = kwh_annual * intensity

        return CategoryEmission(
            category="electricity",
            emissions_kg_co2e=emissions_kg_co2e,
            traces=traces,
            completeness_flags=flags,
            details={"country": inp.country, "kwh_annual_used": kwh_annual}
        )
