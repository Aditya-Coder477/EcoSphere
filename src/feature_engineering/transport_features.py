"""
transport_features.py
=====================
Feature engineering for the transport domain of the Carbon Footprint
Awareness Platform.

Responsibilities
----------------
* Annualise monthly transport and flight emissions.
* Derive commute-intensity metrics (kg CO₂e per km).
* Flag low-carbon commuters based on their primary commute mode.
* Compute flight-emission share of total transport emissions.
* Enrich the dataset with commute-mode emission factors from a reference
  factors table.

Public API
----------
    build_transport_features(transport_df, factors_df) -> pd.DataFrame
"""

from __future__ import annotations

import logging
from typing import List

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

#: Commute modes considered low-carbon for the
#: :data:`is_low_carbon_commuter` flag.
_LOW_CARBON_MODES: frozenset[str] = frozenset(
    {
        "Walking",
        "Cycling",
        "Bus",
        "Metro/Subway",
        "Electric Train",
    }
)

#: Approximate life-cycle emission factor for commercial aviation
#: (kg CO₂e per passenger-km, including radiative-forcing uplift).
_FLIGHT_FACTOR_KG_PER_KM: float = 0.209

# Column names ---------------------------------------------------------------
_COL_MONTHLY_TRANSPORT_EMISSION = "estimated_monthly_transport_emissions_kg_co2e"
_COL_WEEKLY_COMMUTE_DIST = "weekly_commute_distance_km"
_COL_COMMUTE_MODE = "commute_mode"
_COL_MONTHLY_FLIGHT_DIST = "monthly_flight_distance_km"

_REQUIRED_INPUT_COLS: List[str] = [
    _COL_MONTHLY_TRANSPORT_EMISSION,
    _COL_WEEKLY_COMMUTE_DIST,
    _COL_COMMUTE_MODE,
    _COL_MONTHLY_FLIGHT_DIST,
]

_FACTORS_REQUIRED_COLS: List[str] = ["commute_mode", "commute_mode_emission_factor"]

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def build_transport_features(
    transport_df: pd.DataFrame,
    factors_df: pd.DataFrame,
) -> pd.DataFrame:
    """Build transport-domain features for the carbon footprint pipeline.

    Parameters
    ----------
    transport_df:
        DataFrame containing individual or aggregated transport survey
        records.  Must include the columns listed in
        :data:`_REQUIRED_INPUT_COLS`.
    factors_df:
        Reference table that maps each ``commute_mode`` to an emission
        factor (kg CO₂e per km).  Must contain at minimum the columns
        ``commute_mode`` and ``commute_mode_emission_factor``.

    Returns
    -------
    pd.DataFrame
        A *copy* of ``transport_df`` enriched with the following new
        columns:

        ``annual_transport_emission_kg_co2e``
            Monthly transport emission scaled to a full year (× 12).

        ``commute_intensity_kg_co2e_per_km``
            Average weekly emission divided by weekly commute distance,
            yielding an emission-per-km intensity metric.  Rows with
            zero or missing commute distance receive ``NaN``.

        ``is_low_carbon_commuter``
            Boolean flag; ``True`` when the primary commute mode is one
            of the modes in :data:`_LOW_CARBON_MODES`.

        ``annual_flight_distance_km``
            Monthly flight distance scaled to a full year (× 12).

        ``annual_flight_emission_kg_co2e``
            Flight-related CO₂e emission computed as
            ``annual_flight_distance_km × _FLIGHT_FACTOR_KG_PER_KM``.

        ``flight_emission_share_pct``
            Flight emissions as a percentage of total annual transport
            emissions, clipped to the range [0, 100].

        ``commute_mode_emission_factor``
            Per-km emission factor for the commute mode, merged from
            ``factors_df``.  Rows whose mode is absent in the factors
            table receive ``NaN``.

    Raises
    ------
    ValueError
        If any column listed in :data:`_REQUIRED_INPUT_COLS` is absent
        from ``transport_df``, or if ``factors_df`` is missing
        ``commute_mode`` / ``commute_mode_emission_factor``.

    Examples
    --------
    >>> features = build_transport_features(transport_df, factors_df)
    >>> features["is_low_carbon_commuter"].value_counts()
    """
    # ------------------------------------------------------------------
    # 1. Validate inputs
    # ------------------------------------------------------------------
    _check_required_columns(transport_df, _REQUIRED_INPUT_COLS, label="transport_df")
    factors_df = factors_df.copy().rename(columns={
        "mode": "commute_mode",
        "co2e_kg_per_unit": "commute_mode_emission_factor"
    })

    _check_required_columns(factors_df, _FACTORS_REQUIRED_COLS, label="factors_df")

    df = transport_df.copy()

    # ------------------------------------------------------------------
    # 2. Annual transport emission
    # ------------------------------------------------------------------
    df["annual_transport_emission_kg_co2e"] = (
        df[_COL_MONTHLY_TRANSPORT_EMISSION] * 12
    )
    logger.debug("Computed annual_transport_emission_kg_co2e.")

    # ------------------------------------------------------------------
    # 3. Commute intensity (kg CO₂e per km)
    # ------------------------------------------------------------------
    weekly_emission = df["annual_transport_emission_kg_co2e"] / 52
    commute_dist = df[_COL_WEEKLY_COMMUTE_DIST].replace(0, np.nan)
    df["commute_intensity_kg_co2e_per_km"] = weekly_emission / commute_dist
    logger.debug("Computed commute_intensity_kg_co2e_per_km.")

    # ------------------------------------------------------------------
    # 4. Low-carbon commuter flag
    # ------------------------------------------------------------------
    df["is_low_carbon_commuter"] = df[_COL_COMMUTE_MODE].isin(_LOW_CARBON_MODES)
    logger.debug("Computed is_low_carbon_commuter.")

    # ------------------------------------------------------------------
    # 5. Annual flight distance and emission
    # ------------------------------------------------------------------
    df["annual_flight_distance_km"] = df[_COL_MONTHLY_FLIGHT_DIST] * 12
    df["annual_flight_emission_kg_co2e"] = (
        df["annual_flight_distance_km"] * _FLIGHT_FACTOR_KG_PER_KM
    )
    logger.debug("Computed annual_flight_distance_km and annual_flight_emission_kg_co2e.")

    # ------------------------------------------------------------------
    # 6. Flight emission share (%)
    # ------------------------------------------------------------------
    annual_transport = df["annual_transport_emission_kg_co2e"].replace(0, np.nan)
    raw_share = (df["annual_flight_emission_kg_co2e"] / annual_transport) * 100
    df["flight_emission_share_pct"] = raw_share.clip(lower=0, upper=100)
    logger.debug("Computed flight_emission_share_pct.")

    # ------------------------------------------------------------------
    # 7. Merge commute mode emission factor
    # ------------------------------------------------------------------
    factor_lookup = (
        factors_df[["commute_mode", "commute_mode_emission_factor"]]
        .drop_duplicates(subset=["commute_mode"])
    )
    df = df.merge(factor_lookup, on="commute_mode", how="left")
    logger.debug("Merged commute_mode_emission_factor from factors_df.")

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
        List of column names that must be present.
    label:
        Human-readable name of the DataFrame, used in the error message.

    Raises
    ------
    ValueError
        Listing all missing columns.
    """
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(
            f"{label} is missing required column(s): {missing}"
        )
