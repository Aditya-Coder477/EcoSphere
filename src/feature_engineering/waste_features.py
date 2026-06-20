"""
waste_features.py
=================
Feature engineering for the waste-management domain of the Carbon
Footprint Awareness Platform.

Responsibilities
----------------
* Compute per-capita annual waste-related CO₂e emissions from generation
  rates, emission factors, and landfill rates.
* Estimate landfill-specific emissions and recycling/diversion potential.
* Classify waste-management maturity into tiered categories.

Public API
----------
    build_waste_features(waste_df) -> pd.DataFrame
"""

from __future__ import annotations

import logging
from typing import List

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

#: Default emission factor for landfill disposal (kg CO₂e per kg of waste).
#: Accounts for methane generation and incomplete capture.
_LANDFILL_FACTOR_KG_CO2E_PER_KG: float = 0.50

#: Bin edges (%) for waste-diversion-rate tier classification.
#: A diversion rate of 0 % means everything goes to landfill/incineration;
#: 100 % means all waste is recycled or composted.
_DIVERSION_BINS: List[float] = [0.0, 20.0, 40.0, 60.0, 100.0]

#: Human-readable labels for :data:`_DIVERSION_BINS`.
_DIVERSION_LABELS: List[str] = [
    "Poor",          # 0 – 20 %
    "Developing",    # 20 – 40 %
    "Moderate",      # 40 – 60 %
    "Advanced",      # 60 – 100 %
]

# Column names ---------------------------------------------------------------
_COL_WASTE_KG_CAP_DAY = "waste_generated_kg_per_capita_per_day"
_COL_EMISSION_FACTOR = "estimated_waste_emissions_kg_co2e_per_kg_waste"
_COL_LANDFILL_RATE = "landfill_rate_pct"
_COL_RECYCLING_RATE = "recycling_rate_pct"
_COL_COMPOSTING_RATE = "composting_rate_pct"

_REQUIRED_COLS: List[str] = [
    _COL_WASTE_KG_CAP_DAY,
    _COL_EMISSION_FACTOR,
    _COL_LANDFILL_RATE,
    _COL_RECYCLING_RATE,
    _COL_COMPOSTING_RATE,
]

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def build_waste_features(waste_df: pd.DataFrame) -> pd.DataFrame:
    """Build waste-domain features for the carbon footprint pipeline.

    Parameters
    ----------
    waste_df:
        DataFrame containing per-country (or per-region, per-city) waste
        management statistics.  Must include the columns listed in
        :data:`_REQUIRED_COLS`.

    Returns
    -------
    pd.DataFrame
        A *copy* of ``waste_df`` enriched with the following new
        columns:

        ``waste_emission_kg_co2e_per_capita_per_year``
            Total annual per-capita waste emission:
            ``waste_kg/cap/day × 365 × waste_emission_factor``.

        ``landfill_emission_kg_co2e_per_capita_per_year``
            Annual per-capita emission attributable solely to landfill
            disposal:
            ``waste_kg/day × 365 × (landfill_rate / 100) × _LANDFILL_FACTOR``.

        ``recycling_potential_score``
            A score representing the absolute mass of waste currently
            sent to landfill (and therefore recoverable by diversion):
            ``(landfill_rate / 100) × waste_kg/day × 365``.  Higher
            values indicate greater untapped recycling potential.

        ``waste_diversion_rate_pct``
            Sum of recycling and composting rates (capped at 100 %).
            Represents the fraction of waste diverted from
            landfill/incineration.

        ``waste_management_tier``
            Categorical tier derived from ``waste_diversion_rate_pct``
            using :data:`_DIVERSION_BINS` / :data:`_DIVERSION_LABELS`.

    Raises
    ------
    ValueError
        If any column listed in :data:`_REQUIRED_COLS` is absent from
        ``waste_df``.

    Examples
    --------
    >>> features = build_waste_features(waste_df)
    >>> features["waste_management_tier"].value_counts()
    """
    # ------------------------------------------------------------------
    # 1. Validate inputs
    # ------------------------------------------------------------------
    _check_required_columns(waste_df, _REQUIRED_COLS, label="waste_df")

    df = waste_df.copy()

    # ------------------------------------------------------------------
    # 2. Total annual waste emission per capita
    # ------------------------------------------------------------------
    df["waste_emission_kg_co2e_per_capita_per_year"] = (
        df[_COL_WASTE_KG_CAP_DAY] * 365.0 * df[_COL_EMISSION_FACTOR]
    )
    logger.debug("Computed waste_emission_kg_co2e_per_capita_per_year.")

    # ------------------------------------------------------------------
    # 3. Landfill-specific emission per capita
    # ------------------------------------------------------------------
    df["landfill_emission_kg_co2e_per_capita_per_year"] = (
        df[_COL_WASTE_KG_CAP_DAY]
        * 365.0
        * (df[_COL_LANDFILL_RATE] / 100.0)
        * _LANDFILL_FACTOR_KG_CO2E_PER_KG
    )
    logger.debug("Computed landfill_emission_kg_co2e_per_capita_per_year.")

    # ------------------------------------------------------------------
    # 4. Recycling potential score
    # ------------------------------------------------------------------
    df["recycling_potential_score"] = (
        (df[_COL_LANDFILL_RATE] / 100.0)
        * df[_COL_WASTE_KG_CAP_DAY]
        * 365.0
    )
    logger.debug("Computed recycling_potential_score.")

    # ------------------------------------------------------------------
    # 5. Waste diversion rate (recycling + composting, capped at 100 %)
    # ------------------------------------------------------------------
    df["waste_diversion_rate_pct"] = (
        df[_COL_RECYCLING_RATE] + df[_COL_COMPOSTING_RATE]
    ).clip(upper=100.0)
    logger.debug("Computed waste_diversion_rate_pct.")

    # ------------------------------------------------------------------
    # 6. Waste management tier
    # ------------------------------------------------------------------
    df["waste_management_tier"] = pd.cut(
        df["waste_diversion_rate_pct"],
        bins=_DIVERSION_BINS,
        labels=_DIVERSION_LABELS,
        right=False,
        include_lowest=True,
    )
    logger.debug("Computed waste_management_tier.")

    return df


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


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
