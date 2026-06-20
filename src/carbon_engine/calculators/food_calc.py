"""
food_calc.py
============
Food carbon calculator.
"""

from typing import Dict, Any, Union, List
import pandas as pd

from ..schemas import FoodInput, CategoryEmission, FactorTrace
from ..factor_lookup import EmissionFactorLookup

class FoodCarbonCalculator:
    """Calculates food emissions based on items and quantities."""
    
    def __init__(self):
        self.lookup = EmissionFactorLookup()

    def calculate(self, input_data: Union[FoodInput, List[FoodInput], dict, pd.Series]) -> CategoryEmission:
        """
        Calculate food emissions.
        Can take a single FoodInput, a list of FoodInputs, or a raw dictionary/series (user's dietary habits).
        Returns CategoryEmission object.
        """
        emissions_kg_co2e = 0.0
        traces = []
        flags = {"missing_factors": False, "no_food_items": False}
        details = {"items_processed": 0, "items_not_found": []}
        
        inputs: List[FoodInput] = []

        if isinstance(input_data, pd.Series):
            input_data = input_data.to_dict()

        if isinstance(input_data, dict):
            # This would be an aggregate dictionary, e.g. from a user profile
            # For simplicity, if we have a top_emission_driver == 'food' or similar, we might
            # not have specific item quantities. The engine needs specific quantities.
            # If the dict contains item names as keys, we try to parse them:
            found_any = False
            for k, v in input_data.items():
                if isinstance(v, (int, float)) and v > 0:
                    # check if k is a known food item
                    factor = self.lookup.get_food_factor(k)
                    if factor is not None:
                        inputs.append(FoodInput(food_item=k, quantity_kg=v))
                        found_any = True
            
            if not found_any:
                flags["no_food_items"] = True
                return CategoryEmission(
                    category="food",
                    emissions_kg_co2e=0.0,
                    completeness_flags=flags,
                    details={"message": "No recognizable food items with quantities found in dict."}
                )

        elif isinstance(input_data, list):
            inputs = [i for i in input_data if isinstance(i, FoodInput)]
        elif isinstance(input_data, FoodInput):
            inputs = [input_data]

        if not inputs:
            flags["no_food_items"] = True
            return CategoryEmission(category="food", emissions_kg_co2e=0.0, completeness_flags=flags)

        for inp in inputs:
            factor = self.lookup.get_food_factor(inp.food_item)
            if factor is None:
                details["items_not_found"].append(inp.food_item)
                flags["missing_factors"] = True
                continue
            
            item_emissions = inp.quantity_kg * factor
            emissions_kg_co2e += item_emissions
            details["items_processed"] += 1
            
            traces.append(FactorTrace(
                category="food",
                factor_value=factor,
                factor_unit="kg CO2e per kg",
                source_dataset="food_ghg_factors.csv",
                description=f"Emission factor for {inp.food_item}"
            ))

        return CategoryEmission(
            category="food",
            emissions_kg_co2e=emissions_kg_co2e,
            traces=traces,
            completeness_flags=flags,
            details=details
        )
