import pandas as pd
import pytest

from src.integration.merger import safe_left_merge, IntegrationPipeline
from src.integration.lineage import LineageTracker

def test_safe_left_merge():
    left = pd.DataFrame({
        "country": ["A", "B"],
        "year": [2020, 2020],
        "val_left": [10, 20]
    })
    right = pd.DataFrame({
        "country": ["A", "B"],
        "year": [2020, 2020],
        "val_y": [100, 200],
        "val_left": [99, 99]  # This should be dropped/renamed to avoid conflicts
    })
    
    merged = safe_left_merge(left, right, on=["country", "year"])
    
    assert "val_left" in merged.columns
    assert "val_y" in merged.columns
    
    # Check that original left values were preserved
    assert list(merged["val_left"]) == [10, 20]

def test_safe_left_merge_row_explosion_raises():
    left = pd.DataFrame({
        "id": [1, 2]
    })
    # Right has duplicated keys leading to a row explosion
    right = pd.DataFrame({
        "id": [1, 1, 2],
        "val": ["X", "Y", "Z"]
    })
    
    with pytest.raises(ValueError, match="row explosion detected"):
        safe_left_merge(left, right, on="id")

def test_lineage_tracker():
    tracker = LineageTracker()
    # It should prepopulate with known features
    assert len(tracker.all_records()) > 0
    
    # Test registering a new one
    rec = tracker.register(
        feature_name="test_feature",
        source_datasets=["test_source"],
        formula="A + B",
        module="test_module",
        unit="kg",
        description="A test feature",
        category="test"
    )
    
    retrieved = tracker.get("test_feature")
    assert retrieved is not None
    assert retrieved.formula == "A + B"
    
    df = tracker.to_dataframe()
    assert len(df) > 0
    assert "test_feature" in df["feature_name"].values

def test_integration_pipeline_basic(tmp_path):
    pipeline = IntegrationPipeline(merged_dir=tmp_path)
    
    # Mock engineered dict
    electricity = pd.DataFrame({
        "country": ["A"], "year": [2020], "electricity_emission_kg_co2e_per_capita": [100]
    })
    waste = pd.DataFrame({
        "country": ["A"], "year": [2020], "waste_emission_kg_co2e_per_capita_per_year": [50]
    })
    context = pd.DataFrame({
        "country": ["A"], "year": [2020], "gdp_per_capita_usd": [1000]
    })
    food = pd.DataFrame({
        "country": ["A"], "year": [2020], "food_emission_kg_co2e_per_capita_per_year": [200]
    })
    transport = pd.DataFrame({
        "user_id": [1], "annual_transport_emission_kg_co2e": [500]
    })
    
    engineered = {
        "electricity": electricity,
        "waste": waste,
        "country_context": context,
        "food": food,
        "transport": transport
    }
    
    # This should run through Stage 1 & 2 without failing.
    # Note: behavior is missing but pipeline handles it gracefully
    cy = pipeline._build_country_year_base(engineered)
    assert len(cy) == 1
    
    master = pipeline.run(engineered)
    
    assert "annual_transport_emission_kg_co2e" in master.columns
    # since user base didn't have country, it couldn't merge with country_year
    # but the pipeline should add a NaN country column
    assert "country" in master.columns
