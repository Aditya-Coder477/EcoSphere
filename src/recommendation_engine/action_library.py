"""
action_library.py
=================
Registry of predefined carbon reduction actions.
"""

from typing import List
from .schemas import ActionDefinition, RecommendationContext

_ACTION_LIBRARY: List[ActionDefinition] = []

def get_action_library() -> List[ActionDefinition]:
    """Returns the full list of available carbon-reduction actions."""
    global _ACTION_LIBRARY
    if not _ACTION_LIBRARY:
        _ACTION_LIBRARY = [
        # --- Transport Actions ---
        ActionDefinition(
            action_id="TR-01",
            title="Switch to Public Transit",
            category="transport",
            description="Replace solo car commutes with bus, subway, or train.",
            base_carbon_saved_pct=40.0,
            base_effort=5.0,
            base_cost=3.0,
            # Exclude if they already mainly use public transit or don't commute
            eligibility_rule=lambda ctx: ctx.commute_mode not in ["Bus", "Metro/Subway", "Electric Train"] and ctx.category_emissions.get("transport", 0) > 0,
            explanation_template="Switching to public transit can drastically cut your transport footprint, which is currently {cat_pct}% of your total emissions."
        ),
        ActionDefinition(
            action_id="TR-02",
            title="Start Carpooling",
            category="transport",
            description="Share rides with colleagues or neighbors to split emissions.",
            base_carbon_saved_pct=25.0,
            base_effort=6.0,
            base_cost=2.0,
            # Eligible if they drive solo
            eligibility_rule=lambda ctx: ctx.commute_mode in ["Car - solo", "Car", "Motorcycle"],
            explanation_template="Carpooling reduces the number of vehicles on the road, directly cutting your transport emissions."
        ),
        ActionDefinition(
            action_id="TR-03",
            title="Walk or Cycle Short Trips",
            category="transport",
            description="Replace short driving trips with active transport.",
            base_carbon_saved_pct=15.0,
            base_effort=4.0,
            base_cost=1.0,
            # Exclude for rural users who might not have short trip options
            eligibility_rule=lambda ctx: ctx.city_type in ["Urban", "Metro", "Suburban"] and ctx.category_emissions.get("transport", 0) > 0,
            explanation_template="Since you live in a {city_type} area, walking or cycling is a zero-carbon, zero-cost way to reduce your footprint."
        ),

        # --- Food Actions ---
        ActionDefinition(
            action_id="FD-01",
            title="Reduce Beef Consumption",
            category="food",
            description="Swap beef for lower-carbon proteins like poultry or plant-based alternatives a few days a week.",
            base_carbon_saved_pct=30.0,
            base_effort=3.0,
            base_cost=2.0,
            # Exclude if already vegetarian
            eligibility_rule=lambda ctx: not ctx.is_vegetarian and ctx.category_emissions.get("food", 0) > 0,
            explanation_template="Beef is highly carbon-intensive. Reducing it can significantly lower your food footprint."
        ),
        ActionDefinition(
            action_id="FD-02",
            title="Adopt a Plant-Based Diet",
            category="food",
            description="Shift completely to a vegetarian or vegan diet.",
            base_carbon_saved_pct=50.0,
            base_effort=7.0,
            base_cost=3.0,
            # Exclude if already vegetarian
            eligibility_rule=lambda ctx: not ctx.is_vegetarian and ctx.category_emissions.get("food", 0) > 0,
            explanation_template="A plant-based diet is one of the most effective ways to lower personal emissions. Food makes up {cat_pct}% of your footprint."
        ),

        # --- Electricity Actions ---
        ActionDefinition(
            action_id="EL-01",
            title="Upgrade to LED Lighting",
            category="electricity",
            description="Replace incandescent or CFL bulbs with highly efficient LED lighting.",
            base_carbon_saved_pct=10.0,
            base_effort=2.0,
            base_cost=4.0,
            eligibility_rule=lambda ctx: ctx.category_emissions.get("electricity", 0) > 0,
            explanation_template="LEDs use up to 80% less energy. Because your electricity footprint is notable, this quick fix saves both carbon and money."
        ),
        ActionDefinition(
            action_id="EL-02",
            title="Adjust Thermostat and AC Settings",
            category="electricity",
            description="Lower heating in winter and raise AC temp in summer by just 1-2 degrees.",
            base_carbon_saved_pct=15.0,
            base_effort=2.0,
            base_cost=1.0,
            eligibility_rule=lambda ctx: ctx.category_emissions.get("electricity", 0) > 0,
            explanation_template="Heating and cooling are huge energy drains. Small thermostat adjustments can save 15% of your electricity emissions."
        ),

        # --- Waste Actions ---
        ActionDefinition(
            action_id="WS-01",
            title="Start Composting Organic Waste",
            category="waste",
            description="Compost food scraps to prevent methane emissions in landfills.",
            base_carbon_saved_pct=20.0,
            base_effort=6.0,
            base_cost=2.0,
            eligibility_rule=lambda ctx: ctx.category_emissions.get("waste", 0) > 0,
            explanation_template="Organic waste in landfills generates methane. Composting at home directly cuts your waste footprint."
        ),
        ActionDefinition(
            action_id="WS-02",
            title="Increase Household Recycling",
            category="waste",
            description="Ensure all paper, plastic, glass, and metal are properly sorted and recycled.",
            base_carbon_saved_pct=15.0,
            base_effort=3.0,
            base_cost=1.0,
            eligibility_rule=lambda ctx: ctx.category_emissions.get("waste", 0) > 0,
            explanation_template="Recycling diverts materials from high-emission incineration and landfilling processes."
        )
    ]
    return _ACTION_LIBRARY
