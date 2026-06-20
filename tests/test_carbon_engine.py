"""
test_carbon_engine.py
=====================
Tests for the deterministic Carbon Engine calculations.
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

from src.carbon_engine import (
    TransportInput, FoodInput, ElectricityInput, WasteInput,
    UnitConverter, EmissionFactorLookup, CarbonFootprintAggregator
)
from src.carbon_engine.calculators import (
    TransportCarbonCalculator, FoodCarbonCalculator, 
    ElectricityCarbonCalculator, WasteCarbonCalculator
)

# --- Unit Converter Tests ---

def test_unit_converters():
    assert UnitConverter.miles_to_km(10) == 16.0934
    assert UnitConverter.pounds_to_kg(10) == 4.53592
    
    # Test GWP
    co2e = UnitConverter.calculate_co2e(co2=1.0, ch4=1.0, n2o=1.0, ch4_is_biogenic=False)
    # CO2 (1.0) + CH4_FOSSIL (29.8) + N2O (273.0) = 303.8
    assert round(co2e, 1) == 303.8


# --- Transport Calculator Tests ---

@patch.object(EmissionFactorLookup, 'get_transport_factor')
def test_transport_calculator(mock_get_factor):
    mock_get_factor.return_value = (0.2, "kg CO2e / km")
    calc = TransportCarbonCalculator()
    
    res = calc.calculate(TransportInput(mode="Car", distance_km=100))
    
    assert res.category == "transport"
    assert res.emissions_kg_co2e == 20.0
    assert len(res.traces) == 1
    assert not res.completeness_flags["missing_factor"]


@patch.object(EmissionFactorLookup, 'get_transport_factor')
def test_transport_calculator_dict_input(mock_get_factor):
    mock_get_factor.side_effect = lambda m: (0.1, "kg/km") if m == "Bus" else (0.25, "kg/km")
    calc = TransportCarbonCalculator()
    
    res = calc.calculate({"commute_mode": "Bus", "weekly_commute_distance_km": 10, "monthly_flight_distance_km": 100})
    
    # Bus: 10 * 52 * 0.1 = 52.0 kg
    # Flight: 100 * 12 * 0.25 = 300.0 kg
    # Total = 352.0 kg
    assert res.emissions_kg_co2e == 352.0


# --- Food Calculator Tests ---

@patch.object(EmissionFactorLookup, 'get_food_factor')
def test_food_calculator(mock_get_factor):
    mock_get_factor.side_effect = lambda item: 99.48 if item == "Beef (beef herd)" else None
    calc = FoodCarbonCalculator()
    
    res = calc.calculate([
        FoodInput(food_item="Beef (beef herd)", quantity_kg=2.0),
        FoodInput(food_item="Unknown Item", quantity_kg=5.0)
    ])
    
    assert res.category == "food"
    assert res.emissions_kg_co2e == 198.96  # 2.0 * 99.48
    assert res.details["items_processed"] == 1
    assert "Unknown Item" in res.details["items_not_found"]
    assert res.completeness_flags["missing_factors"] is True


# --- Electricity Calculator Tests ---

@patch.object(EmissionFactorLookup, 'get_electricity_grid_intensity')
def test_electricity_calculator(mock_get_intensity):
    mock_get_intensity.return_value = 0.5  # kg CO2 / kWh
    calc = ElectricityCarbonCalculator()
    
    res = calc.calculate(ElectricityInput(country="TestLand", kwh_per_month=100))
    
    assert res.category == "electricity"
    assert res.emissions_kg_co2e == 600.0  # 100 * 12 * 0.5
    assert not res.completeness_flags["used_regional_fallback_kwh"]


# --- Waste Calculator Tests ---

@patch.object(EmissionFactorLookup, 'get_waste_factors')
def test_waste_calculator(mock_get_factors):
    mock_get_factors.return_value = {
        "waste_generated_kg_per_capita_per_day": 1.0,
        "landfill_rate_pct": 50.0,
        "emission_factor": 0.5
    }
    calc = WasteCarbonCalculator()
    
    res = calc.calculate(WasteInput(country="TestLand"))
    
    assert res.category == "waste"
    # Fallback to country average: 1.0 kg/day * 365 = 365.0 kg
    # 365.0 * 0.5 = 182.5 kg CO2e
    assert res.emissions_kg_co2e == 182.5
    assert res.completeness_flags["used_country_average_waste"] is True


# --- Aggregation Tests ---

def test_carbon_aggregator():
    from src.carbon_engine.schemas import CategoryEmission
    
    emissions = {
        "transport": CategoryEmission(category="transport", emissions_kg_co2e=100.0),
        "food": CategoryEmission(category="food", emissions_kg_co2e=300.0),
        "electricity": CategoryEmission(category="electricity", emissions_kg_co2e=0.0)
    }
    
    agg = CarbonFootprintAggregator()
    report = agg.aggregate("user_123", emissions)
    
    assert report.total_emissions_kg_co2e == 400.0
    assert report.dominant_source == "food"
    assert report.category_shares_pct["food"] == 75.0
    assert report.category_shares_pct["transport"] == 25.0
    
    json_dict = report.to_dict()
    assert json_dict["user_id"] == "user_123"
    assert json_dict["dominant_source"] == "food"
    assert "food" in json_dict["human_readable_summary"].lower()
    
