"""
tests/test_validators.py
========================
Unit tests for data cleaning validators.
"""

import pandas as pd
import pytest
from src.cleaning.validators import (
    validate_required_columns,
    validate_numeric_range,
    validate_no_duplicate_keys,
    validate_column_dtypes,
    validate_null_fraction,
    validate_merge_integrity,
    ValidationResult
)

def test_validate_required_columns():
    df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    res = validate_required_columns(df, ["A", "B"])
    assert res.passed is True
    
    res = validate_required_columns(df, ["A", "C"])
    assert res.passed is False
    assert len(res.issues) == 1

def test_validate_numeric_range():
    df = pd.DataFrame({"val": [1.0, 5.0, 10.0]})
    res = validate_numeric_range(df, "val", 0.0, 10.0)
    assert res.passed is True
    
    res = validate_numeric_range(df, "val", 0.0, 5.0)
    assert res.passed is False
    assert len(res.issues) > 0

def test_validate_no_duplicate_keys():
    df = pd.DataFrame({"key": [1, 2, 2], "val": ["A", "B", "C"]})
    res = validate_no_duplicate_keys(df, ["key"])
    assert res.passed is False
    assert len(res.issues) > 0

    df2 = pd.DataFrame({"key": [1, 2, 3]})
    res2 = validate_no_duplicate_keys(df2, ["key"])
    assert res2.passed is True

def test_validate_column_dtypes():
    df = pd.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]})
    expected = {"A": "int64", "B": "object"}
    res = validate_column_dtypes(df, expected)
    assert res.passed is True

    # Intentionally incompatible dtype
    expected_bad = {"A": "float64", "B": "int64"}
    res2 = validate_column_dtypes(df, expected_bad)
    # B is strings, so casting to int64 should fail or fail validation
    assert res2.passed is False

def test_validate_null_fraction():
    df = pd.DataFrame({
        "good": [1, 2, 3, 4],
        "bad": [1, None, None, None] # 75% nulls
    })
    res = validate_null_fraction(df, max_fraction=0.5)
    assert res.passed is False
    assert any("bad" in issue for issue in res.issues)

    res2 = validate_null_fraction(df, max_fraction=0.8)
    assert res2.passed is True

def test_validate_merge_integrity():
    left = pd.DataFrame({"id": [1, 2, 3], "val_left": ["A", "B", "C"]})
    
    # Matching rows
    merged_ok = pd.DataFrame({"id": [1, 2, 3], "val_left": ["A", "B", "C"], "val_right": [10, 20, 30]})
    res = validate_merge_integrity(left, merged_ok)
    assert res.passed is True

    # Row count mismatch
    merged_bad = pd.DataFrame({"id": [1, 2], "val_left": ["A", "B"], "val_right": [10, 20]})
    res2 = validate_merge_integrity(left, merged_bad)
    assert res2.passed is False
