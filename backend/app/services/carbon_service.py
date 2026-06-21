"""
carbon_service.py
=================
Integrates with src.carbon_engine.
"""

import sys
from pathlib import Path

# Need to ensure src is importable if running locally outside docker
# The root of the project should ideally be in PYTHONPATH

from backend.app.schemas.carbon import CarbonCalculationRequest, CarbonCalculationResponse
from src.carbon_engine import (
    TransportInput, FoodInput, ElectricityInput, WasteInput,
    TransportCarbonCalculator, FoodCarbonCalculator, 
    ElectricityCarbonCalculator, WasteCarbonCalculator,
    CarbonFootprintAggregator
)

# ---------------------------------------------------------------------------
# Module-level singletons for calculators to avoid instantiation overhead
# ---------------------------------------------------------------------------
_TRANSPORT_CALCULATOR = TransportCarbonCalculator()
_FOOD_CALCULATOR = FoodCarbonCalculator()
_ELECTRICITY_CALCULATOR = ElectricityCarbonCalculator()
_WASTE_CALCULATOR = WasteCarbonCalculator()
_AGGREGATOR = CarbonFootprintAggregator()


def calculate_footprint(request: CarbonCalculationRequest) -> CarbonCalculationResponse:
    """
    Orchestrates the carbon footprint calculation using the core engine.
    """
    emissions = {}
    
    # 1. Transport
    if request.transport:
        # For simplicity in this demo, if multiple modes, we could calculate all
        # We'll just take the first or sum them. Let's sum them if multiple.
        # But actually, the calculator takes one dict or TransportInput.
        # So we iterate.
        total_transport = 0.0
        for t_act in request.transport:
            res = _TRANSPORT_CALCULATOR.calculate(TransportInput(mode=t_act.mode, distance_km=t_act.distance_km))
            total_transport += res.emissions_kg_co2e
        # Mocking a CategoryEmission object to pass to aggregator
        from src.carbon_engine.schemas import CategoryEmission
        emissions["transport"] = CategoryEmission("transport", total_transport)
        
    # 2. Food
    if request.food:
        food_inputs = [FoodInput(f.food_item, f.quantity_kg) for f in request.food]
        res = _FOOD_CALCULATOR.calculate(food_inputs)
        emissions["food"] = res
        
    # 3. Electricity
    if request.electricity:
        res = _ELECTRICITY_CALCULATOR.calculate(ElectricityInput(
            country=request.electricity.country,
            kwh_per_month=request.electricity.kwh_per_month
        ))
        emissions["electricity"] = res
        
    # 4. Waste
    if request.waste:
        res = _WASTE_CALCULATOR.calculate(WasteInput(
            country=request.waste.country,
            waste_generated_kg_per_day=request.waste.waste_generated_kg_per_day
        ))
        emissions["waste"] = res
        
    # 5. Aggregate
    report = _AGGREGATOR.aggregate(user_id=request.user_id, emissions=emissions)
    
    return CarbonCalculationResponse(
        user_id=report.user_id,
        total_emissions_kg_co2e=report.total_emissions_kg_co2e,
        category_emissions={k: v.emissions_kg_co2e for k, v in report.category_emissions.items()},
        category_shares_pct=report.category_shares_pct,
        dominant_source=report.dominant_source,
        human_readable_summary=report.human_readable_summary
    )
