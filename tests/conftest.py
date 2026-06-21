"""
tests/conftest.py
=================
Shared pytest fixtures for the EcoSphere codebase.
"""

import pytest
import pandas as pd
from pathlib import Path
from src.recommendation_engine.schemas import RecommendationContext

@pytest.fixture
def sample_ctx() -> RecommendationContext:
    return RecommendationContext(
        user_id="test_user",
        category_emissions={"transport": 1200.0, "food": 800.0, "electricity": 1500.0, "waste": 200.0},
        total_emissions_kg_co2e=3700.0,
        dominant_emission_source="electricity",
        occupation="engineer",
        city_type="Urban",
        budget_profile="medium",
        commute_mode="Car",
        is_vegetarian=False,
        synthetic_green_adoption_probability=0.75,
        commute_flexibility_score=60.0,
        diet_flexibility_score=50.0,
        energy_saving_flexibility_score=70.0
    )

@pytest.fixture
def sample_transport_input():
    return {
        "mode": "Car",
        "distance_km": 15000.0
    }

@pytest.fixture
def sample_electricity_input():
    return {
        "country": "United States",
        "kwh_per_month": 500.0
    }

@pytest.fixture
def tmp_csv_paths(tmp_path: Path):
    """Fixture returning temporary directory paths for CSV saving/loading."""
    return {
        "dir": tmp_path,
        "filename": "test_output.csv"
    }
