"""
food_features.py
================
Feature engineering for the food / diet domain of the Carbon Footprint
Awareness Platform.

Responsibilities
----------------
* Build a GHG-factor lookup from a reference factors table.
* Pivot a food-supply dataset to a tidy country × year × food-group shape.
* Map GHG factors onto food groups and compute per-capita daily emissions.
* Aggregate to country-year level and derive annual emission totals.
* Classify diet carbon intensity into tiers and flag high-meat diets.

Public API
----------
    build_food_features(food_supply_df, food_ghg_factors_df) -> pd.DataFrame
"""

from __future__ import annotations

import logging
import math
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

#: Bin edges (kg CO₂e / capita / year) for diet-carbon-intensity tier.
_DIET_BINS: List[float] = [0, 500, 1_500, 3_000, math.inf]

#: Human-readable labels for :data:`_DIET_BINS`.
_DIET_LABELS: List[str] = [
    "Very Low",   # 0 – 500 kg CO₂e/yr
    "Low",        # 500 – 1 500
    "High",       # 1 500 – 3 000
    "Very High",  # 3 000+
]

#: Food groups associated with high meat consumption.  Used to derive
#: the ``high_meat_diet_flag`` binary feature.
_HIGH_MEAT_GROUPS: frozenset[str] = frozenset(
    {
        "beef",
        "lamb",
        "mutton",
        "pork",
        "poultry",
        "meat",
        "red meat",
        "processed meat",
    }
)

# Column names ---------------------------------------------------------------
_COL_COUNTRY = "country"
_COL_YEAR = "year"
_COL_FOOD_GROUP = "food_group"
_COL_FOOD_TYPE = "entity"
_COL_GHG_FACTOR = "greenhouse_gas_emissions_per_kilogram"
_COL_SUPPLY = "supply_g_per_cap_per_day"
_COL_ELEMENT = "element"                  # FAO-style element column
_ELEMENT_SUPPLY_VALUE = "Food supply quantity (g/capita/day)"

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def build_food_features(
    food_supply_df: pd.DataFrame,
    food_ghg_factors_df: pd.DataFrame,
) -> pd.DataFrame:
    """Build food-domain features for the carbon footprint pipeline.

    Parameters
    ----------
    food_supply_df:
        Raw food-supply dataset (FAO FAOSTAT style or compatible).
        Expected to contain at least: ``country``, ``year``,
        ``food_group`` (or ``food_type``), ``element``, and a value
        column representing g/capita/day supply quantities.
    food_ghg_factors_df:
        Reference table mapping food types to GHG emission factors
        (kg CO₂e per kg of food).  Must contain ``food_type`` and
        ``ghg_factor_kg_co2e_per_kg``.

    Returns
    -------
    pd.DataFrame
        Country-year aggregated DataFrame with columns:

        ``food_emission_kg_co2e_per_capita_per_year``
            Total annual per-capita food-system emission.

        ``weighted_avg_food_ghg_factor``
            Weighted average GHG factor (kg CO₂e/kg), weighted by
            daily supply in grams.

        ``diet_carbon_intensity_tier``
            Categorical tier derived from
            ``food_emission_kg_co2e_per_capita_per_year`` using
            :data:`_DIET_BINS` / :data:`_DIET_LABELS`.

        ``high_meat_diet_flag``
            Boolean; ``True`` when any of the :data:`_HIGH_MEAT_GROUPS`
            contributes > 0 g/cap/day supply.

        Returns an **empty DataFrame** if either input is empty or
        lacks the columns required for pivoting and GHG mapping.

    Examples
    --------
    >>> features = build_food_features(food_supply_df, ghg_factors_df)
    >>> features["diet_carbon_intensity_tier"].value_counts()
    """
    # ------------------------------------------------------------------
    # 0. Guard: return empty frame if inputs are trivially empty
    # ------------------------------------------------------------------
    if food_supply_df is None or food_supply_df.empty:
        logger.warning("food_supply_df is empty; returning empty DataFrame.")
        return pd.DataFrame()
    if food_ghg_factors_df is None or food_ghg_factors_df.empty:
        logger.warning("food_ghg_factors_df is empty; returning empty DataFrame.")
        return pd.DataFrame()

    # ------------------------------------------------------------------
    # 1. Build GHG factor lookup
    # ------------------------------------------------------------------
    ghg_lookup = _build_ghg_lookup(food_ghg_factors_df)
    if not ghg_lookup:
        logger.warning("GHG lookup is empty; returning empty DataFrame.")
        return pd.DataFrame()

    # ------------------------------------------------------------------
    # 2. Pivot food supply to tidy format
    # ------------------------------------------------------------------
    try:
        supply_df = _pivot_food_supply(food_supply_df)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not pivot food_supply_df: %s; returning empty DataFrame.", exc)
        return pd.DataFrame()

    if supply_df.empty:
        logger.warning("Pivoted supply DataFrame is empty; returning empty DataFrame.")
        return pd.DataFrame()

    # ------------------------------------------------------------------
    # 3. Map GHG factor to each food group row
    # ------------------------------------------------------------------
    global_avg_factor = np.mean(list(ghg_lookup.values()))

    supply_df["ghg_factor"] = (
        supply_df[_COL_FOOD_GROUP]
        .str.lower()
        .str.strip()
        .map(ghg_lookup)
        .fillna(global_avg_factor)
    )

    # ------------------------------------------------------------------
    # 4. Daily emission per food group
    # ------------------------------------------------------------------
    # Convert supply from g/day → kg/day before multiplying by factor.
    supply_df["emission_kg_co2e_per_cap_per_day"] = (
        supply_df[_COL_SUPPLY] / 1_000.0 * supply_df["ghg_factor"]
    )

    # ------------------------------------------------------------------
    # 5. Aggregate to country-year level
    # ------------------------------------------------------------------
    group_keys = [_COL_COUNTRY, _COL_YEAR]

    agg = supply_df.groupby(group_keys, observed=True).agg(
        total_daily_emission_kg_co2e=("emission_kg_co2e_per_cap_per_day", "sum"),
        total_supply_g=(_COL_SUPPLY, "sum"),
        weighted_ghg_numerator=(
            "emission_kg_co2e_per_cap_per_day",
            "sum",
        ),
    )

    # Weighted average GHG factor = Σ(supply_g × factor) / Σ(supply_g)
    numerator = supply_df.groupby(group_keys, observed=True).apply(
        lambda g: (g[_COL_SUPPLY] * g["ghg_factor"]).sum()
    ).rename("weighted_num")
    denominator = supply_df.groupby(group_keys, observed=True)[_COL_SUPPLY].sum().rename(
        "total_supply"
    )
    weighted_avg = (numerator / denominator.replace(0, np.nan)).rename(
        "weighted_avg_food_ghg_factor"
    )

    # High-meat flag: any high-meat group with supply > 0
    high_meat_flag = (
        supply_df[
            supply_df[_COL_FOOD_GROUP].str.lower().str.strip().isin(_HIGH_MEAT_GROUPS)
        ]
        .groupby(group_keys, observed=True)[_COL_SUPPLY]
        .sum()
        .gt(0)
        .rename("high_meat_diet_flag")
    )

    result = (
        agg[["total_daily_emission_kg_co2e"]]
        .join(weighted_avg, how="left")
        .join(high_meat_flag, how="left")
        .reset_index()
    )

    # ------------------------------------------------------------------
    # 6. Annual emission
    # ------------------------------------------------------------------
    result["food_emission_kg_co2e_per_capita_per_year"] = (
        result["total_daily_emission_kg_co2e"] * 365
    )
    result.drop(columns=["total_daily_emission_kg_co2e"], inplace=True)

    # ------------------------------------------------------------------
    # 7. Diet carbon intensity tier
    # ------------------------------------------------------------------
    result["diet_carbon_intensity_tier"] = pd.cut(
        result["food_emission_kg_co2e_per_capita_per_year"],
        bins=_DIET_BINS,
        labels=_DIET_LABELS,
        right=False,
    )

    # ------------------------------------------------------------------
    # 8. Fill high_meat_diet_flag NaNs for countries with no meat rows
    # ------------------------------------------------------------------
    result["high_meat_diet_flag"] = result["high_meat_diet_flag"].fillna(False)

    logger.info("build_food_features produced %d country-year rows.", len(result))
    return result


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _build_ghg_lookup(factors_df: pd.DataFrame) -> Dict[str, float]:
    """Build a lowercase food_type → GHG factor mapping.

    Parameters
    ----------
    factors_df:
        Must contain ``food_type`` and ``ghg_factor_kg_co2e_per_kg``.

    Returns
    -------
    dict
        Mapping of lowercase, stripped food-type strings to their GHG
        emission factor (kg CO₂e per kg food).  Returns an empty dict
        when the required columns are absent.
    """
    required = [_COL_FOOD_TYPE, _COL_GHG_FACTOR]
    missing = [c for c in required if c not in factors_df.columns]
    if missing:
        logger.warning(
            "food_ghg_factors_df missing columns %s; returning empty lookup.", missing
        )
        return {}

    lookup: Dict[str, float] = {}
    for _, row in factors_df.iterrows():
        key = str(row[_COL_FOOD_TYPE]).lower().strip()
        val = row[_COL_GHG_FACTOR]
        if pd.notna(val) and key:
            lookup[key] = float(val)

    logger.debug("Built GHG lookup with %d entries.", len(lookup))
    return lookup


def _pivot_food_supply(food_df: pd.DataFrame) -> pd.DataFrame:
    """Filter food supply rows and return a tidy country/year/group/supply frame.

    The function accepts two layout variants:

    **Variant A – already tidy** (contains ``supply_g_per_cap_per_day``):
        Passes through after selecting the four canonical columns.

    **Variant B – FAO-style** (contains an ``element`` column):
        Filters to rows where ``element == 'Food supply quantity
        (g/capita/day)'`` and renames the value column accordingly.

    Parameters
    ----------
    food_df:
        Raw food supply dataset.

    Returns
    -------
    pd.DataFrame
        Tidy frame with columns: ``country``, ``year``, ``food_group``,
        ``supply_g_per_cap_per_day``.  Returns an empty DataFrame if the
        required columns cannot be resolved.
    """
    # Handle country column
    if "area" in food_df.columns and _COL_COUNTRY not in food_df.columns:
        food_df = food_df.rename(columns={"area": _COL_COUNTRY})
    
    if _COL_COUNTRY not in food_df.columns:
        return pd.DataFrame()

    # FAO-style with 'indicator' and 'unit'
    if "indicator" in food_df.columns and "unit" in food_df.columns:
        # Get rows representing food supply quantity by weight
        # Exclude Protein, Fat, Energy, etc.
        mask = (
            ~food_df["indicator"].str.contains("Protein|Fat|Energy|Carbohydrate|fibre|Calcium|Iron|Zinc|Magnesium", case=False, na=False)
        ) & (food_df["unit"].isin(["kg/cap/yr", "g/cap/d", "kg/capita/yr"]))
        
        supply_rows = food_df[mask].copy()
        if supply_rows.empty:
            logger.warning("No rows matched weight-based food supply indicator.")
            return pd.DataFrame()
            
        value_col = _infer_value_column(supply_rows)
        if value_col is None:
            return pd.DataFrame()
            
        # Convert kg/yr to g/day
        is_kg_yr = supply_rows["unit"].str.contains("kg", case=False, na=False)
        supply_rows.loc[is_kg_yr, value_col] = supply_rows.loc[is_kg_yr, value_col] * (1000.0 / 365.0)
        
        food_group_col = _resolve_food_group_col(supply_rows)
        if food_group_col is None:
            return pd.DataFrame()
            
        # Exclude aggregate 'All food groups' or 'Total' so they don't double count
        supply_rows = supply_rows[~supply_rows[food_group_col].str.contains("All food groups|Total", case=False, na=False)]
        
        tidy = supply_rows[[_COL_COUNTRY, _COL_YEAR, food_group_col, value_col]].copy()
        tidy = tidy.rename(columns={food_group_col: _COL_FOOD_GROUP, value_col: _COL_SUPPLY})
        return tidy.reset_index(drop=True)
        
    return pd.DataFrame()


# ---------------------------------------------------------------------------
# Micro-helpers
# ---------------------------------------------------------------------------


def _resolve_food_group_col(df: pd.DataFrame) -> Optional[str]:
    """Return the first available food-group column name, or *None*."""
    for candidate in (_COL_FOOD_GROUP, _COL_FOOD_TYPE, "item", "commodity"):
        if candidate in df.columns:
            return candidate
    logger.warning("Cannot resolve a food-group column in DataFrame.")
    return None


def _infer_value_column(df: pd.DataFrame) -> Optional[str]:
    """Infer the numeric value column; prefer 'value', else last numeric col."""
    if "value" in df.columns:
        return "value"
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if numeric_cols:
        return numeric_cols[-1]
    logger.warning("No numeric value column found in supply rows.")
    return None
