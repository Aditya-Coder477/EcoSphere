"""
transport_calc.py
=================
Transport carbon calculator.
"""

from typing import Dict, Any, Union
import pandas as pd

from ..schemas import TransportInput, CategoryEmission, FactorTrace
from ..factor_lookup import EmissionFactorLookup
from ..conversion_utils import UnitConverter

class TransportCarbonCalculator:
    """Calculates transport emissions based on mode and distance."""
    
    def __init__(self):
        self.lookup = EmissionFactorLookup()

    def calculate(self, input_data: Union[TransportInput, dict, pd.Series]) -> CategoryEmission:
        """
        Calculate transport emissions.
        Returns CategoryEmission object.
        """
        if isinstance(input_data, pd.Series):
            input_data = input_data.to_dict()
            
        if isinstance(input_data, dict):
            # Try to map from flat dictionary/series, common in batch processing
            mode = input_data.get('commute_mode', input_data.get('mode', ''))
            
            # Figure out distance
            distance_km = 0.0
            if 'weekly_commute_distance_km' in input_data and pd.notna(input_data['weekly_commute_distance_km']):
                # Convert weekly to annual
                distance_km += float(input_data['weekly_commute_distance_km']) * 52
            elif 'distance_km' in input_data and pd.notna(input_data['distance_km']):
                distance_km += float(input_data['distance_km'])

            # Add flight distance if present
            if 'monthly_flight_distance_km' in input_data and pd.notna(input_data['monthly_flight_distance_km']):
                flight_dist = float(input_data['monthly_flight_distance_km']) * 12
                # We handle flight separately to sum them up, but for simple schema we just use mode
            else:
                flight_dist = 0.0

            inp = TransportInput(
                mode=str(mode) if mode else "",
                distance_km=distance_km
            )
        else:
            inp = input_data

        emissions_kg_co2e = 0.0
        traces = []
        flags = {"missing_mode": False, "missing_factor": False, "zero_distance": False}

        if not inp.mode:
            flags["missing_mode"] = True
            return CategoryEmission(
                category="transport",
                emissions_kg_co2e=0.0,
                completeness_flags=flags
            )

        if inp.distance_km <= 0:
            flags["zero_distance"] = True

        # Look up factor
        result = self.lookup.get_transport_factor(inp.mode)
        if result is None:
            flags["missing_factor"] = True
            return CategoryEmission(
                category="transport",
                emissions_kg_co2e=0.0,
                completeness_flags=flags,
                details={"mode_attempted": inp.mode}
            )

        factor_val, unit = result
        
        # We assume factor unit is per passenger-km or vehicle-km and distance is in km
        # If it's miles, we would use UnitConverter, but we enforce km in schema
        emissions_kg_co2e = inp.distance_km * factor_val

        traces.append(FactorTrace(
            category="transport",
            factor_value=factor_val,
            factor_unit=unit,
            source_dataset="transport_factors.csv",
            description=f"Emission factor for {inp.mode}"
        ))

        # Add flights if we processed a raw dict that contained flights
        if isinstance(input_data, dict) and 'monthly_flight_distance_km' in input_data and pd.notna(input_data['monthly_flight_distance_km']):
            flight_dist = float(input_data['monthly_flight_distance_km']) * 12
            flight_res = self.lookup.get_transport_factor("Short-haul Flight") # generic fallback for flight
            if flight_res:
                f_val, f_unit = flight_res
                flight_emissions = flight_dist * f_val
                emissions_kg_co2e += flight_emissions
                traces.append(FactorTrace(
                    category="transport",
                    factor_value=f_val,
                    factor_unit=f_unit,
                    source_dataset="transport_factors.csv",
                    description=f"Emission factor for flights (assumed short-haul average)"
                ))

        return CategoryEmission(
            category="transport",
            emissions_kg_co2e=emissions_kg_co2e,
            traces=traces,
            completeness_flags=flags,
            details={"primary_mode": inp.mode, "distance_km": inp.distance_km}
        )
