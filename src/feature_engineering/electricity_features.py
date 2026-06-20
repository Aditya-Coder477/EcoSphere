"""
electricity_features.py
=======================
Feature engineering for the electricity / energy domain of the Carbon
Footprint Awareness Platform.

Responsibilities
----------------
* Merge per-capita energy consumption data; fall back to regional defaults
  when country-level data is unavailable.
* Compute per-capita electricity-related CO₂e emissions.
* Derive fossil vs. clean energy shares.
* Classify countries into grid-intensity tiers.
* Estimate remaining renewable-adoption potential.

Public API
----------
    build_electricity_features(electricity_df, energy_per_capita_df) -> pd.DataFrame
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

#: Default annual electricity consumption per capita (kWh) keyed by broad
#: geographic region.  Used when country-level data are unavailable.
_REGIONAL_KWH_DEFAULTS: Dict[str, float] = {
    "North America": 12_000.0,
    "Europe": 6_500.0,
    "Asia": 3_500.0,
    "Oceania": 8_000.0,
    "South America": 2_500.0,
    "Africa": 600.0,
    "Middle East": 7_000.0,
    "Central America": 1_800.0,
    "World": 3_300.0,          # fallback-of-last-resort
}

#: Bin edges (kg CO₂ per kWh) for grid-intensity tier classification.
#: Covers the range [0, +∞).
_INTENSITY_BINS: List[float] = [0.0, 0.15, 0.30, 0.50, 0.70, math.inf]

#: Human-readable labels for :data:`_INTENSITY_BINS`.
#: ``len(_INTENSITY_LABELS) == len(_INTENSITY_BINS) - 1``
_INTENSITY_LABELS: List[str] = [
    "Very Low",    # 0.00 – 0.15 kg CO₂/kWh
    "Low",         # 0.15 – 0.30
    "Moderate",    # 0.30 – 0.50
    "High",        # 0.50 – 0.70
    "Very High",   # 0.70+
]

# Column names ---------------------------------------------------------------
_COL_REGION = "region"
_COL_COUNTRY = "country"
_COL_GRID_INTENSITY = "grid_intensity_kg_co2_per_kwh"
_COL_ENERGY_PER_CAPITA = "energy_per_capita_kwh"
_COL_COAL_SHARE = "coal_share_pct"
_COL_GAS_SHARE = "gas_share_pct"
_COL_OIL_SHARE = "oil_share_pct"
_COL_NUCLEAR_SHARE = "nuclear_share_pct"
_COL_RENEWABLE_SHARE = "renewable_share_pct"

_REQUIRED_ELECTRICITY_COLS: List[str] = [
    _COL_GRID_INTENSITY,
    _COL_COAL_SHARE,
    _COL_GAS_SHARE,
    _COL_OIL_SHARE,
    _COL_NUCLEAR_SHARE,
    _COL_RENEWABLE_SHARE,
]

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def build_electricity_features(
    electricity_df: pd.DataFrame,
    energy_per_capita_df: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """Build electricity-domain features for the carbon footprint pipeline.

    Parameters
    ----------
    electricity_df:
        DataFrame containing per-country (or per-region) electricity grid
        characteristics.  Must include the columns listed in
        :data:`_REQUIRED_ELECTRICITY_COLS`.  Optionally may contain
        ``region`` and/or ``country`` columns to support default-filling
        and optional merges.
    energy_per_capita_df:
        Optional DataFrame providing per-capita annual electricity
        consumption in kWh (column ``energy_per_capita_kwh``).  When
        supplied, it is left-joined onto ``electricity_df`` on the
        ``country`` key.  Rows that cannot be matched are filled using
        regional defaults from :data:`_REGIONAL_KWH_DEFAULTS`.

    Returns
    -------
    pd.DataFrame
        A *copy* of ``electricity_df`` enriched with the following new
        columns:

        ``energy_per_capita_kwh``
            Per-capita annual electricity consumption in kWh, sourced
            from ``energy_per_capita_df`` or regional defaults.

        ``electricity_emission_kg_co2e_per_capita``
            Annual per-capita electricity-related emission:
            ``energy_per_capita_kwh × grid_intensity_kg_co2_per_kwh``.

        ``fossil_share_pct``
            Sum of coal, gas, and oil shares (capped at 100 %).

        ``clean_share_pct``
            Sum of nuclear and renewable shares (capped at 100 %).

        ``grid_intensity_tier``
            Categorical tier based on :data:`_INTENSITY_BINS` and
            :data:`_INTENSITY_LABELS`.

        ``renewable_adoption_potential``
            Fraction of the generation mix that is still non-renewable:
            ``1 − renewable_share_pct / 100``.  Values are clipped to
            [0, 1].

    Raises
    ------
    ValueError
        If any column listed in :data:`_REQUIRED_ELECTRICITY_COLS` is
        absent from ``electricity_df``.

    Examples
    --------
    >>> features = build_electricity_features(elec_df, energy_df)
    >>> features["grid_intensity_tier"].value_counts()
    """
    # ------------------------------------------------------------------
    # 1. Validate inputs
    # ------------------------------------------------------------------
    _check_required_columns(
        electricity_df, _REQUIRED_ELECTRICITY_COLS, label="electricity_df"
    )

    df = electricity_df.copy()

    # ------------------------------------------------------------------
    # 2. Merge / fill energy-per-capita data
    # ------------------------------------------------------------------
    if energy_per_capita_df is not None:
        df = _prepare_energy_per_capita(energy_per_capita_df, df)
    else:
        if _COL_ENERGY_PER_CAPITA not in df.columns:
            df[_COL_ENERGY_PER_CAPITA] = np.nan

    df = _fill_energy_with_regional_defaults(df)

    # ------------------------------------------------------------------
    # 3. Per-capita electricity emission
    # ------------------------------------------------------------------
    df["electricity_emission_kg_co2e_per_capita"] = (
        df[_COL_ENERGY_PER_CAPITA] * df[_COL_GRID_INTENSITY]
    )
    logger.debug("Computed electricity_emission_kg_co2e_per_capita.")

    # ------------------------------------------------------------------
    # 4. Fossil and clean shares
    # ------------------------------------------------------------------
    fossil_cols = [_COL_COAL_SHARE, _COL_GAS_SHARE, _COL_OIL_SHARE]
    clean_cols = [_COL_NUCLEAR_SHARE, _COL_RENEWABLE_SHARE]

    df["fossil_share_pct"] = df[fossil_cols].sum(axis=1).clip(upper=100.0)
    df["clean_share_pct"] = df[clean_cols].sum(axis=1).clip(upper=100.0)
    logger.debug("Computed fossil_share_pct and clean_share_pct.")

    # ------------------------------------------------------------------
    # 5. Grid-intensity tier
    # ------------------------------------------------------------------
    df["grid_intensity_tier"] = pd.cut(
        df[_COL_GRID_INTENSITY],
        bins=_INTENSITY_BINS,
        labels=_INTENSITY_LABELS,
        right=False,
    )
    logger.debug("Computed grid_intensity_tier.")

    # ------------------------------------------------------------------
    # 6. Renewable adoption potential
    # ------------------------------------------------------------------
    df["renewable_adoption_potential"] = (
        1.0 - df[_COL_RENEWABLE_SHARE] / 100.0
    ).clip(lower=0.0, upper=1.0)
    logger.debug("Computed renewable_adoption_potential.")

    return df


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _prepare_energy_per_capita(
    energy_per_capita_df: pd.DataFrame,
    base_df: pd.DataFrame,
) -> pd.DataFrame:
    """Left-join ``energy_per_capita_df`` onto ``base_df`` on *country*.

    Only the ``energy_per_capita_kwh`` column is transferred.  Rows in
    ``base_df`` that have no match in ``energy_per_capita_df`` will
    receive ``NaN`` in the merged column (subsequently filled by
    :func:`_fill_energy_with_regional_defaults`).

    Parameters
    ----------
    energy_per_capita_df:
        Must contain ``country`` and ``energy_per_capita_kwh``.
    base_df:
        The working copy of ``electricity_df``.

    Returns
    -------
    pd.DataFrame
        ``base_df`` with ``energy_per_capita_kwh`` merged in (or
        updated, if the column already existed).
    """
    if _COL_COUNTRY not in energy_per_capita_df.columns:
        logger.warning(
            "energy_per_capita_df lacks a 'country' column; skipping merge."
        )
        if _COL_ENERGY_PER_CAPITA not in base_df.columns:
            base_df[_COL_ENERGY_PER_CAPITA] = np.nan
        return base_df

    if _COL_ENERGY_PER_CAPITA not in energy_per_capita_df.columns:
        logger.warning(
            "energy_per_capita_df lacks 'energy_per_capita_kwh'; skipping merge."
        )
        if _COL_ENERGY_PER_CAPITA not in base_df.columns:
            base_df[_COL_ENERGY_PER_CAPITA] = np.nan
        return base_df

    lookup = (
        energy_per_capita_df[[_COL_COUNTRY, _COL_ENERGY_PER_CAPITA]]
        .drop_duplicates(subset=[_COL_COUNTRY])
    )

    # Drop pre-existing column to avoid _x/_y suffixes
    if _COL_ENERGY_PER_CAPITA in base_df.columns:
        base_df = base_df.drop(columns=[_COL_ENERGY_PER_CAPITA])

    if _COL_COUNTRY not in base_df.columns:
        logger.warning(
            "base electricity_df lacks a 'country' column; cannot merge energy data."
        )
        base_df[_COL_ENERGY_PER_CAPITA] = np.nan
        return base_df

    merged = base_df.merge(lookup, on=_COL_COUNTRY, how="left")
    logger.debug("Merged energy_per_capita_kwh from energy_per_capita_df.")
    return merged


def _fill_energy_with_regional_defaults(df: pd.DataFrame) -> pd.DataFrame:
    """Fill missing ``energy_per_capita_kwh`` using :data:`_REGIONAL_KWH_DEFAULTS`.

    The function looks up each row's ``region`` column value in the
    defaults mapping.  Rows whose region is also missing (or not in the
    mapping) fall back to the ``'World'`` average.

    Parameters
    ----------
    df:
        Working DataFrame; must already have the
        ``energy_per_capita_kwh`` column (possibly all-NaN).

    Returns
    -------
    pd.DataFrame
        Same DataFrame with NaN entries in ``energy_per_capita_kwh``
        filled.
    """
    missing_mask = df[_COL_ENERGY_PER_CAPITA].isna()
    if not missing_mask.any():
        return df

    n_missing = missing_mask.sum()
    logger.debug("Filling %d missing energy_per_capita_kwh values with regional defaults.", n_missing)

    world_default = _REGIONAL_KWH_DEFAULTS.get("World", 3_300.0)

    if _COL_REGION in df.columns:
        df.loc[missing_mask, _COL_ENERGY_PER_CAPITA] = df.loc[
            missing_mask, _COL_REGION
        ].map(
            lambda r: _REGIONAL_KWH_DEFAULTS.get(r, world_default)
        )
    else:
        df.loc[missing_mask, _COL_ENERGY_PER_CAPITA] = world_default
        logger.debug("No 'region' column found; used world default for all missing rows.")

    return df


def _check_required_columns(
    df: pd.DataFrame,
    required: List[str],
    label: str = "DataFrame",
) -> None:
    """Raise :class:`ValueError` if any required column is missing.

    Parameters
    ----------
    df:
        DataFrame to validate.
    required:
        Column names that must be present.
    label:
        Human-readable identifier used in the error message.

    Raises
    ------
    ValueError
        Listing all missing columns.
    """
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"{label} is missing required column(s): {missing}")
