import pandas as pd
import pytest
import numpy as np

from src.cleaning.validators import (
    validate_required_columns,
    validate_numeric_range,
    validate_no_duplicate_keys,
    ValidationResult
)
from src.cleaning.cleaner import (
    drop_high_null_columns,
    remove_duplicate_rows,
    coerce_year_column,
    flag_outliers
)

def test_validate_required_columns():
    df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    res = validate_required_columns(df, ["A", "B"])
    assert res.passed is True
    
    res = validate_required_columns(df, ["A", "C"])
    assert res.passed is False
    assert len(res.issues) == 1

def test_validate_numeric_range():
    df = pd.DataFrame({"val": [1, 5, 10]})
    res = validate_numeric_range(df, "val", 0, 10)
    assert res.passed is True
    
    res = validate_numeric_range(df, "val", 0, 5)
    assert res.passed is False

def test_validate_no_duplicate_keys():
    df = pd.DataFrame({"key1": [1, 2, 1], "key2": ["A", "B", "A"]})
    res = validate_no_duplicate_keys(df, ["key1", "key2"])
    assert res.passed is False

    df2 = pd.DataFrame({"key1": [1, 2, 3], "key2": ["A", "B", "A"]})
    res2 = validate_no_duplicate_keys(df2, ["key1", "key2"])
    assert res2.passed is True

def test_drop_high_null_columns():
    df = pd.DataFrame({
        "good": [1, 2, 3, 4],
        "bad": [1, np.nan, np.nan, np.nan] # 75% null
    })
    res = drop_high_null_columns(df, max_fraction=0.5)
    assert "good" in res.columns
    assert "bad" not in res.columns

def test_remove_duplicate_rows():
    df = pd.DataFrame({"A": [1, 1, 2], "B": [3, 3, 4]})
    res = remove_duplicate_rows(df)
    assert len(res) == 2

def test_coerce_year_column():
    df = pd.DataFrame({"year": ["2020", 1990, "bad", 2050]})
    res = coerce_year_column(df, "year", valid_min=2000, valid_max=2024)
    # 2020 is valid, 1990 is below min, 'bad' is NaT/NaN, 2050 is above max
    assert len(res) == 1
    assert res.iloc[0]["year"] == 2020

def test_flag_outliers():
    df = pd.DataFrame({"val": [1, 50, 100]})
    res = flag_outliers(df, "val", min_val=0, max_val=10)
    assert "val_flagged" in res.columns
    assert list(res["val_flagged"]) == [False, True, True]
    assert list(res["val"]) == [1, 10, 10]
