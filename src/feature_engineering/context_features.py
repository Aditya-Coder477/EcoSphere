"""
context_features.py
===================
Feature engineering for country context, behavioural indicators, and
cross-domain emission integration in the Carbon Footprint Awareness
Platform.

Responsibilities
----------------
* Build macroeconomic context features (GDP, HDI, CO₂ intensity).
* Derive within-year CO₂ country percentile ranks.
* Score individual behavioural readiness for low-carbon adoption.
* Compute total emissions and per-category shares for user records.

Public API
----------
    build_country_context_features(gdp_df, hdi_df, co2_df, ...) -> pd.DataFrame
    build_behavior_features(behavior_df)               -> pd.DataFrame
    compute_total_and_shares(user_df, emission_cols)   -> pd.DataFrame
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

#: Bin edges (USD) for GDP-per-capita tiers.
_GDP_BINS: List[float] = [0.0, 1_000.0, 5_000.0, 15_000.0, 40_000.0, math.inf]

#: Human-readable labels for :data:`_GDP_BINS`.
_GDP_LABELS: List[str] = [
    "Low Income",            # 0 – 1 000
    "Lower Middle Income",   # 1 000 – 5 000
    "Upper Middle Income",   # 5 000 – 15 000
    "High Income",           # 15 000 – 40 000
    "Very High Income",      # 40 000+
]

#: Bin edges (probability, 0–1) for behaviour-adoption-probability tiers.
_ADOPTION_BINS: List[float] = [0.0, 0.25, 0.50, 0.75, 1.0]

#: Human-readable labels for :data:`_ADOPTION_BINS`.
_ADOPTION_LABELS: List[str] = [
    "Unlikely",      # 0.00 – 0.25
    "Possible",      # 0.25 – 0.50
    "Likely",        # 0.50 – 0.75
    "Very Likely",   # 0.75 – 1.00
]

# Shared key columns ---------------------------------------------------------
_COL_COUNTRY = "country"
_COL_YEAR = "year"
_COL_GDP = "gdp_per_capita_usd"
_COL_HDI = "hdi"
_COL_CO2_PER_CAPITA = "co2_per_capita_t"
_COL_ELECTRICITY_ACCESS = "electricity_access_pct"
_COL_LITERACY = "literacy_rate_pct"
_COL_POPULATION = "population"
_COL_ADOPTION_PROB = "adoption_probability"
_COL_AWARENESS = "awareness_score"

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Public API — Country context
# ---------------------------------------------------------------------------


def build_country_context_features(
    gdp_df: pd.DataFrame,
    hdi_df: pd.DataFrame,
    co2_df: pd.DataFrame,
    electricity_access_df: Optional[pd.DataFrame] = None,
    literacy_df: Optional[pd.DataFrame] = None,
    population_df: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """Build country-level macroeconomic and emissions-context features.

    Parameters
    ----------
    gdp_df:
        Base dataset; must contain ``country``, ``year``, and
        ``gdp_per_capita_usd``.  This is the left table for all merges.
    hdi_df:
        Human Development Index table; must contain ``country``,
        ``year``, and ``hdi``.
    co2_df:
        Per-capita CO₂ emissions table; must contain ``country``,
        ``year``, and ``co2_per_capita_t``.
    electricity_access_df:
        Optional; must contain ``country``, ``year``, and
        ``electricity_access_pct``.
    literacy_df:
        Optional; must contain ``country``, ``year``, and
        ``literacy_rate_pct``.
    population_df:
        Optional; must contain ``country``, ``year``, and
        ``population``.

    Returns
    -------
    pd.DataFrame
        Merged and enriched DataFrame with the following new columns:

        ``gdp_log``
            Natural log1p of ``gdp_per_capita_usd``.

        ``gdp_tier``
            Categorical GDP tier from :data:`_GDP_BINS` /
            :data:`_GDP_LABELS`.

        ``hdi_normalized``
            Min-max normalised HDI within the full dataset (0 = minimum
            HDI observed, 1 = maximum).

        ``emission_per_gdp_intensity``
            Emission intensity of economic output:
            ``(co2_per_capita_t × 1 000) / gdp_per_capita_usd``
            (kg CO₂ per USD of GDP per capita).

        ``co2_country_percentile``
            Within-year percentile rank of each country's
            ``co2_per_capita_t`` (0–100).

        ``electricity_access_gap_pct``
            ``100 − electricity_access_pct``; present only when
            ``electricity_access_df`` is provided.

    Examples
    --------
    >>> ctx = build_country_context_features(gdp_df, hdi_df, co2_df)
    >>> ctx["gdp_tier"].value_counts()
    """
    # ------------------------------------------------------------------
    # 1. Normalize and Validate base inputs
    # ------------------------------------------------------------------
    def _prep_context_df(df: pd.DataFrame | None, expected_val_col: str) -> pd.DataFrame | None:
        if df is None: return None
        df = df.copy()
        if "country" not in df.columns and "entity" in df.columns:
            df = df.rename(columns={"entity": "country"})
        if expected_val_col in df.columns:
            return df
        skip = {"country", "year", "region", "code", "index", "entity"}
        val_cols = [c for c in df.columns if c not in skip and pd.api.types.is_numeric_dtype(df[c])]
        if val_cols:
            df = df.rename(columns={val_cols[0]: expected_val_col})
        return df

    gdp_df = _prep_context_df(gdp_df, _COL_GDP)
    hdi_df = _prep_context_df(hdi_df, _COL_HDI)
    co2_df = _prep_context_df(co2_df, _COL_CO2_PER_CAPITA)
    electricity_access_df = _prep_context_df(electricity_access_df, _COL_ELECTRICITY_ACCESS)
    literacy_df = _prep_context_df(literacy_df, _COL_LITERACY)
    population_df = _prep_context_df(population_df, _COL_POPULATION)

    _ensure_key_cols(gdp_df, "gdp_df", extra=[_COL_GDP])
    _ensure_key_cols(hdi_df, "hdi_df", extra=[_COL_HDI])
    _ensure_key_cols(co2_df, "co2_df", extra=[_COL_CO2_PER_CAPITA])

    merge_keys = [_COL_COUNTRY, _COL_YEAR]

    # ------------------------------------------------------------------
    # 2. Build base frame from GDP
    # ------------------------------------------------------------------
    df = gdp_df.copy()

    # ------------------------------------------------------------------
    # 3. Left-merge HDI
    # ------------------------------------------------------------------
    df = _safe_merge(df, hdi_df, on=merge_keys, name="hdi_df")

    # ------------------------------------------------------------------
    # 4. Left-merge CO₂
    # ------------------------------------------------------------------
    df = _safe_merge(df, co2_df, on=merge_keys, name="co2_df")

    # ------------------------------------------------------------------
    # 5. Optional merges
    # ------------------------------------------------------------------
    if electricity_access_df is not None:
        df = _safe_merge(
            df,
            electricity_access_df,
            on=merge_keys,
            name="electricity_access_df",
        )

    if literacy_df is not None:
        df = _safe_merge(df, literacy_df, on=merge_keys, name="literacy_df")

    if population_df is not None:
        df = _safe_merge(df, population_df, on=merge_keys, name="population_df")

    # ------------------------------------------------------------------
    # 6. GDP-derived features
    # ------------------------------------------------------------------
    df["gdp_log"] = np.log1p(df[_COL_GDP])

    df["gdp_tier"] = pd.cut(
        df[_COL_GDP],
        bins=_GDP_BINS,
        labels=_GDP_LABELS,
        right=False,
    )
    logger.debug("Computed gdp_log and gdp_tier.")

    # ------------------------------------------------------------------
    # 7. HDI normalisation (min-max)
    # ------------------------------------------------------------------
    hdi_min = df[_COL_HDI].min()
    hdi_max = df[_COL_HDI].max()
    hdi_range = hdi_max - hdi_min
    if hdi_range > 0:
        df["hdi_normalized"] = (df[_COL_HDI] - hdi_min) / hdi_range
    else:
        df["hdi_normalized"] = 0.0
    logger.debug("Computed hdi_normalized.")

    # ------------------------------------------------------------------
    # 8. Emission per GDP intensity
    # ------------------------------------------------------------------
    gdp_safe = df[_COL_GDP].replace(0, np.nan)
    df["emission_per_gdp_intensity"] = (
        (df[_COL_CO2_PER_CAPITA] * 1_000.0) / gdp_safe
    )
    logger.debug("Computed emission_per_gdp_intensity.")

    # ------------------------------------------------------------------
    # 9. Within-year CO₂ percentile rank
    # ------------------------------------------------------------------
    df["co2_country_percentile"] = df.groupby(_COL_YEAR, observed=True)[
        _COL_CO2_PER_CAPITA
    ].rank(pct=True) * 100.0
    logger.debug("Computed co2_country_percentile.")

    # ------------------------------------------------------------------
    # 10. Electricity access gap (optional)
    # ------------------------------------------------------------------
    if _COL_ELECTRICITY_ACCESS in df.columns:
        df["electricity_access_gap_pct"] = (
            100.0 - df[_COL_ELECTRICITY_ACCESS]
        ).clip(lower=0.0, upper=100.0)
        logger.debug("Computed electricity_access_gap_pct.")

    return df


# ---------------------------------------------------------------------------
# Public API — Behaviour features
# ---------------------------------------------------------------------------


def build_behavior_features(behavior_df: pd.DataFrame) -> pd.DataFrame:
    """Build individual behavioural-readiness features.

    Parameters
    ----------
    behavior_df:
        DataFrame of individual or household behavioural survey
        responses.  Expected columns (all numeric, typically 0–100 or
        0–1 scale):

        * ``price_sensitivity``
        * ``commute_flexibility``
        * ``diet_flexibility``
        * ``digital_engagement``
        * ``social_influence``
        * ``adoption_probability`` (0–1)
        * ``awareness_score`` (0–100)

    Returns
    -------
    pd.DataFrame
        A *copy* of ``behavior_df`` enriched with:

        ``effort_score``
            Mean of ``price_sensitivity``, ``commute_flexibility``, and
            ``diet_flexibility``.  Represents willingness to exert
            effort for low-carbon behaviour change.

        ``digital_reach_score``
            Mean of ``digital_engagement`` and ``social_influence``.
            Represents capacity to influence others via digital channels.

        ``behavior_adoption_tier``
            Categorical tier from :data:`_ADOPTION_BINS` /
            :data:`_ADOPTION_LABELS` applied to
            ``adoption_probability``.

        ``green_readiness_index``
            Combined index:
            ``(awareness_score / 100) × adoption_probability``.
            Values are clipped to [0, 1].

    Notes
    -----
    Missing values in the component columns are handled by ``mean``
    with ``skipna=True``; rows where *all* components are NaN will
    produce NaN for the respective score.

    Examples
    --------
    >>> beh = build_behavior_features(behavior_df)
    >>> beh["behavior_adoption_tier"].value_counts()
    """
    df = behavior_df.copy()

    # ------------------------------------------------------------------
    # 1. Effort score
    # ------------------------------------------------------------------
    effort_cols = ["price_sensitivity", "commute_flexibility", "diet_flexibility"]
    available_effort = [c for c in effort_cols if c in df.columns]
    if available_effort:
        df["effort_score"] = df[available_effort].mean(axis=1, skipna=True)
    else:
        logger.warning("No effort columns found; effort_score set to NaN.")
        df["effort_score"] = np.nan

    # ------------------------------------------------------------------
    # 2. Digital reach score
    # ------------------------------------------------------------------
    digital_cols = ["digital_engagement", "social_influence"]
    available_digital = [c for c in digital_cols if c in df.columns]
    if available_digital:
        df["digital_reach_score"] = df[available_digital].mean(axis=1, skipna=True)
    else:
        logger.warning("No digital-reach columns found; digital_reach_score set to NaN.")
        df["digital_reach_score"] = np.nan

    # ------------------------------------------------------------------
    # 3. Behaviour adoption tier
    # ------------------------------------------------------------------
    if _COL_ADOPTION_PROB in df.columns:
        df["behavior_adoption_tier"] = pd.cut(
            df[_COL_ADOPTION_PROB],
            bins=_ADOPTION_BINS,
            labels=_ADOPTION_LABELS,
            right=False,
            include_lowest=True,
        )
    else:
        logger.warning(
            "'adoption_probability' column not found; behavior_adoption_tier not computed."
        )
        df["behavior_adoption_tier"] = np.nan

    # ------------------------------------------------------------------
    # 4. Green readiness index
    # ------------------------------------------------------------------
    if _COL_AWARENESS in df.columns and _COL_ADOPTION_PROB in df.columns:
        df["green_readiness_index"] = (
            (df[_COL_AWARENESS] / 100.0) * df[_COL_ADOPTION_PROB]
        ).clip(lower=0.0, upper=1.0)
    else:
        missing = [c for c in [_COL_AWARENESS, _COL_ADOPTION_PROB] if c not in df.columns]
        logger.warning(
            "Column(s) %s missing; green_readiness_index set to NaN.", missing
        )
        df["green_readiness_index"] = np.nan

    logger.debug("build_behavior_features complete.")
    return df


# ---------------------------------------------------------------------------
# Public API — Integration / total emissions
# ---------------------------------------------------------------------------


def compute_total_and_shares(
    user_df: pd.DataFrame,
    emission_cols: Dict[str, str],
) -> pd.DataFrame:
    """Compute total emissions and per-category shares across domains.

    Parameters
    ----------
    user_df:
        DataFrame of individual or household records that includes all
        columns referenced in ``emission_cols``.
    emission_cols:
        Mapping of ``category_label -> column_name`` for each emission
        domain, e.g.::

            {
                "transport": "annual_transport_emission_kg_co2e",
                "electricity": "electricity_emission_kg_co2e_per_capita",
                "food": "food_emission_kg_co2e_per_capita_per_year",
                "waste": "waste_emission_kg_co2e_per_capita_per_year",
            }

    Returns
    -------
    pd.DataFrame
        A *copy* of ``user_df`` enriched with:

        ``total_emission_kg_co2e``
            Row-wise sum across all provided emission columns.

        ``dominant_emission_source``
            Category label with the highest emission value in each row.
            Ties are broken by column order.

        ``{category}_emission_share_pct`` (one per category)
            Each category's fraction of ``total_emission_kg_co2e``,
            expressed as a percentage clipped to [0, 100].

    Notes
    -----
    Columns referenced in ``emission_cols`` that are absent from
    ``user_df`` are silently skipped (with a warning), so partial
    merges do not raise.

    Examples
    --------
    >>> totals = compute_total_and_shares(user_df, emission_cols)
    >>> totals["dominant_emission_source"].value_counts()
    """
    df = user_df.copy()

    # ------------------------------------------------------------------
    # 1. Filter to columns present in the DataFrame
    # ------------------------------------------------------------------
    available: Dict[str, str] = {}
    for label, col in emission_cols.items():
        if col in df.columns:
            available[label] = col
        else:
            logger.warning(
                "Emission column '%s' (category '%s') not found in user_df; skipping.",
                col,
                label,
            )

    if not available:
        logger.warning("No valid emission columns found; skipping total computation.")
        df["total_emission_kg_co2e"] = np.nan
        df["dominant_emission_source"] = np.nan
        return df

    # ------------------------------------------------------------------
    # 2. Total emission
    # ------------------------------------------------------------------
    col_list = list(available.values())
    df["total_emission_kg_co2e"] = df[col_list].sum(axis=1, min_count=1)

    # ------------------------------------------------------------------
    # 3. Dominant source
    # ------------------------------------------------------------------
    emission_sub = df[col_list].copy()
    emission_sub.columns = list(available.keys())  # rename to category labels
    df["dominant_emission_source"] = emission_sub.idxmax(axis=1)

    # ------------------------------------------------------------------
    # 4. Per-category share percentages
    # ------------------------------------------------------------------
    total_safe = df["total_emission_kg_co2e"].replace(0, np.nan)
    for label, col in available.items():
        share_col = f"{label}_emission_share_pct"
        df[share_col] = (df[col] / total_safe * 100.0).clip(lower=0.0, upper=100.0)

    logger.debug("compute_total_and_shares complete; %d categories.", len(available))
    return df


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _ensure_key_cols(
    df: pd.DataFrame,
    label: str,
    extra: Optional[List[str]] = None,
) -> None:
    """Raise :class:`ValueError` if ``country`` / ``year`` (or extra cols) missing.

    Parameters
    ----------
    df:
        DataFrame to validate.
    label:
        Human-readable name used in the error message.
    extra:
        Additional column names beyond ``country`` and ``year`` that
        must be present.

    Raises
    ------
    ValueError
        Listing all missing columns.
    """
    required = [_COL_COUNTRY, _COL_YEAR] + (extra or [])
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"{label} is missing required column(s): {missing}")


def _safe_merge(
    left: pd.DataFrame,
    right: pd.DataFrame,
    on: List[str],
    name: str,
) -> pd.DataFrame:
    """Left-merge ``right`` onto ``left`` with column-conflict safety.

    When ``right`` contains columns that already exist in ``left``
    (beyond the join keys), the function drops those columns from
    ``right`` *before* merging to avoid ``_x``/``_y`` suffixes.  A
    warning is logged for each dropped duplicate.

    Parameters
    ----------
    left:
        Left (base) DataFrame.
    right:
        Right DataFrame to merge in.
    on:
        List of join-key column names (must exist in both DataFrames).
    name:
        Human-readable name of ``right``, used in log messages.

    Returns
    -------
    pd.DataFrame
        Result of ``left.merge(right, on=on, how='left')``.
    """
    # Only keep join keys + new columns from right
    right_cols_to_use = on.copy()
    right_extra = [c for c in right.columns if c not in on]
    left_existing = set(left.columns)

    for col in right_extra:
        if col in left_existing:
            logger.warning(
                "Column '%s' in '%s' already exists in left DataFrame; skipping.", col, name
            )
        else:
            right_cols_to_use.append(col)

    right_subset = right[right_cols_to_use].drop_duplicates(subset=on)

    merged = left.merge(right_subset, on=on, how="left")
    logger.debug("Merged '%s' onto base DataFrame (%d rows).", name, len(merged))
    return merged
