"""
cleaner.py
==========
Data-cleaning pipeline for the Carbon Footprint Awareness Platform.

Architecture
------------
* Generic helpers (``drop_high_null_columns``, ``coerce_year_column``, …) are
  stateless functions that can be composed freely.
* Dataset-specific cleaners (``clean_transport_activity``, …) apply the right
  sequence of generic helpers for a given source.
* :data:`_CLEANERS` maps dataset keys to cleaning callables.
* :data:`_OWID_GENERICS` lists Our World in Data datasets that share a common
  cleaning pathway via ``clean_generic_owid``.
* :class:`CleaningPipeline` orchestrates the full run and writes outputs.
"""

from __future__ import annotations

import functools
from pathlib import Path
from typing import Callable, Optional

import pandas as pd

from config import CFG
from src.cleaning.validators import (
    ValidationResult,
    validate_no_duplicate_keys,
    validate_null_fraction,
    validate_required_columns,
)
from src.utils import io_utils
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Attempt to import country maps; degrade gracefully if not yet available.
try:
    from src.cleaning import country_maps  # type: ignore[import]

    _COUNTRY_MAP: dict[str, str] = country_maps.COUNTRY_NAME_MAP  # type: ignore[attr-defined]
    _REGION_MAP: dict[str, str] = country_maps.REGION_MAP  # type: ignore[attr-defined]
    _HAS_COUNTRY_MAPS = True
except ImportError:
    logger.warning("country_maps module not found — normalise_countries will be a no-op.")
    _COUNTRY_MAP = {}
    _REGION_MAP = {}
    _HAS_COUNTRY_MAPS = False


# ---------------------------------------------------------------------------
# Private helper
# ---------------------------------------------------------------------------

def _log_validation(result: ValidationResult, dataset_name: str) -> None:
    """Log a :class:`~validators.ValidationResult` at the appropriate level.

    Parameters
    ----------
    result:
        The validation outcome to log.
    dataset_name:
        Human-readable label for the dataset being validated.
    """
    if result.passed:
        logger.debug("[%s] Validation passed.", dataset_name)
    else:
        for issue in result.issues:
            logger.warning("[%s] Validation issue: %s", dataset_name, issue)


# ---------------------------------------------------------------------------
# Generic cleaning helpers
# ---------------------------------------------------------------------------

def drop_high_null_columns(
    df: pd.DataFrame,
    max_fraction: float = CFG.MAX_NULL_FRACTION,
    dataset_name: str = "",
) -> pd.DataFrame:
    """Drop columns whose null fraction exceeds *max_fraction*.

    Parameters
    ----------
    df:
        Input :class:`~pandas.DataFrame`.
    max_fraction:
        Columns with ``null_count / len(df) > max_fraction`` are dropped.
        Defaults to :attr:`config.CFG.MAX_NULL_FRACTION`.
    dataset_name:
        Label used in log messages.

    Returns
    -------
    pd.DataFrame
        Frame with high-null columns removed.
    """
    if df.empty:
        return df

    null_fracs = df.isna().mean()
    drop_cols = null_fracs[null_fracs > max_fraction].index.tolist()

    if drop_cols:
        logger.info(
            "[%s] Dropping %d high-null column(s): %s",
            dataset_name,
            len(drop_cols),
            drop_cols,
        )
        df = df.drop(columns=drop_cols)
    else:
        logger.debug("[%s] No high-null columns to drop.", dataset_name)

    return df


def remove_duplicate_rows(
    df: pd.DataFrame,
    subset: Optional[list[str]] = None,
    dataset_name: str = "",
) -> pd.DataFrame:
    """Remove duplicate rows, keeping the first occurrence.

    Parameters
    ----------
    df:
        Input :class:`~pandas.DataFrame`.
    subset:
        Columns to consider for duplication detection.  ``None`` uses all
        columns.
    dataset_name:
        Label used in log messages.

    Returns
    -------
    pd.DataFrame
        Frame with duplicate rows removed.
    """
    n_before = len(df)
    df = df.drop_duplicates(subset=subset, keep="first")
    n_dropped = n_before - len(df)

    if n_dropped:
        logger.info(
            "[%s] Removed %d duplicate row(s).", dataset_name, n_dropped
        )
    else:
        logger.debug("[%s] No duplicate rows found.", dataset_name)

    return df


def coerce_year_column(
    df: pd.DataFrame,
    year_col: str = "year",
    valid_min: int = CFG.VALID_YEAR_MIN,
    valid_max: int = CFG.VALID_YEAR_MAX,
    dataset_name: str = "",
) -> pd.DataFrame:
    """Coerce *year_col* to nullable ``Int64`` and filter to [*valid_min*, *valid_max*].

    Parameters
    ----------
    df:
        Input :class:`~pandas.DataFrame`.
    year_col:
        Name of the year column.
    valid_min:
        Inclusive lower bound on valid years.
    valid_max:
        Inclusive upper bound on valid years.
    dataset_name:
        Label used in log messages.

    Returns
    -------
    pd.DataFrame
        Frame with year column coerced and rows outside the valid range removed.
    """
    if year_col not in df.columns:
        logger.warning("[%s] Year column '%s' not found — skipping.", dataset_name, year_col)
        return df

    df = df.copy()
    df[year_col] = pd.to_numeric(df[year_col], errors="coerce").astype("Int64")

    n_before = len(df)
    df = df[
        df[year_col].notna()
        & (df[year_col] >= valid_min)
        & (df[year_col] <= valid_max)
    ]
    n_dropped = n_before - len(df)

    if n_dropped:
        logger.info(
            "[%s] Dropped %d row(s) with year outside [%d, %d].",
            dataset_name,
            n_dropped,
            valid_min,
            valid_max,
        )
    else:
        logger.debug(
            "[%s] All year values within [%d, %d].", dataset_name, valid_min, valid_max
        )

    return df.reset_index(drop=True)


def coerce_numeric_columns(
    df: pd.DataFrame,
    columns: list[str],
    dataset_name: str = "",
) -> pd.DataFrame:
    """Coerce listed *columns* to ``float64``, silently converting failures to NaN.

    Parameters
    ----------
    df:
        Input :class:`~pandas.DataFrame`.
    columns:
        Column names to coerce.
    dataset_name:
        Label used in log messages.

    Returns
    -------
    pd.DataFrame
        Frame with specified columns cast to ``float64``.
    """
    df = df.copy()
    for col in columns:
        if col not in df.columns:
            logger.warning(
                "[%s] Numeric coercion: column '%s' not found — skipped.", dataset_name, col
            )
            continue
        before_nulls = int(df[col].isna().sum())
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("float64")
        after_nulls = int(df[col].isna().sum())
        new_nulls = after_nulls - before_nulls
        if new_nulls > 0:
            logger.debug(
                "[%s] Column '%s': %d value(s) coerced to NaN.", dataset_name, col, new_nulls
            )
    return df


def normalise_countries(
    df: pd.DataFrame,
    country_col: str = "country",
    dataset_name: str = "",
) -> pd.DataFrame:
    """Standardise country names and add a ``region`` column.

    Uses the ``COUNTRY_NAME_MAP`` and ``REGION_MAP`` imported from
    ``src.cleaning.country_maps``.  If the module is unavailable the function
    is a no-op.

    Parameters
    ----------
    df:
        Input :class:`~pandas.DataFrame`.
    country_col:
        Name of the column containing raw country strings.
    dataset_name:
        Label used in log messages.

    Returns
    -------
    pd.DataFrame
        Frame with standardised country names and a ``region`` column.
    """
    if not _HAS_COUNTRY_MAPS:
        logger.debug("[%s] country_maps unavailable — normalise_countries skipped.", dataset_name)
        return df

    if country_col not in df.columns:
        logger.warning(
            "[%s] Country column '%s' not found — normalise skipped.", dataset_name, country_col
        )
        return df

    df = df.copy()
    df[country_col] = df[country_col].map(
        lambda x: _COUNTRY_MAP.get(str(x).strip(), str(x).strip()) if pd.notna(x) else x
    )
    df["region"] = df[country_col].map(_REGION_MAP)

    unmapped = df.loc[df["region"].isna(), country_col].unique()
    if len(unmapped):
        logger.debug(
            "[%s] %d country name(s) have no region mapping: %s",
            dataset_name,
            len(unmapped),
            list(unmapped)[:10],
        )

    return df


def impute_numeric_median(
    df: pd.DataFrame,
    group_by: Optional[list[str]] = None,
    dataset_name: str = "",
) -> pd.DataFrame:
    """Fill NaN values in numeric columns with the column median.

    When *group_by* is provided the median is computed within each group,
    yielding a finer imputation.  Global median is used as a fallback for
    groups that are entirely null.

    Parameters
    ----------
    df:
        Input :class:`~pandas.DataFrame`.
    group_by:
        Column(s) to group by before computing medians.  ``None`` applies a
        global median.
    dataset_name:
        Label used in log messages.

    Returns
    -------
    pd.DataFrame
        Frame with numeric NaNs imputed.
    """
    df = df.copy()
    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    if not numeric_cols:
        logger.debug("[%s] No numeric columns to impute.", dataset_name)
        return df

    if group_by:
        valid_group_cols = [c for c in group_by if c in df.columns]
        if valid_group_cols:
            group_medians = df.groupby(valid_group_cols)[numeric_cols].transform("median")
            global_medians = df[numeric_cols].median()
            # Fill group median, then global median as fallback
            for col in numeric_cols:
                df[col] = df[col].fillna(group_medians[col]).fillna(global_medians[col])
            logger.debug(
                "[%s] Imputed numeric medians grouped by %s.", dataset_name, valid_group_cols
            )
            return df

    global_medians = df[numeric_cols].median()
    df[numeric_cols] = df[numeric_cols].fillna(global_medians)
    logger.debug("[%s] Imputed global numeric medians.", dataset_name)
    return df


def flag_outliers(
    df: pd.DataFrame,
    column: str,
    min_val: Optional[float] = None,
    max_val: Optional[float] = None,
    dataset_name: str = "",
) -> pd.DataFrame:
    """Add a boolean flag column and clip extreme values in *column*.

    A row is flagged when its value falls below *min_val* **or** above
    *max_val* (whichever bounds are supplied).  Flagged values are then
    clipped to the supplied bounds.

    Parameters
    ----------
    df:
        Input :class:`~pandas.DataFrame`.
    column:
        Numeric column to inspect.
    min_val:
        Inclusive lower bound; values below this are flagged and clipped.
    max_val:
        Inclusive upper bound; values above this are flagged and clipped.
    dataset_name:
        Label used in log messages.

    Returns
    -------
    pd.DataFrame
        Frame with an additional ``{column}_flagged`` boolean column and
        clipped values in *column*.
    """
    if column not in df.columns:
        logger.warning(
            "[%s] flag_outliers: column '%s' not found — skipped.", dataset_name, column
        )
        return df

    df = df.copy()
    series = pd.to_numeric(df[column], errors="coerce")

    flag = pd.Series([False] * len(df), index=df.index)
    if min_val is not None:
        flag |= series < min_val
    if max_val is not None:
        flag |= series > max_val

    flag_col = f"{column}_flagged"
    df[flag_col] = flag

    n_flagged = int(flag.sum())
    if n_flagged:
        logger.info(
            "[%s] Flagged %d outlier(s) in '%s' (bounds [%s, %s]).",
            dataset_name,
            n_flagged,
            column,
            min_val,
            max_val,
        )

    df[column] = series.clip(lower=min_val, upper=max_val)
    return df


# ---------------------------------------------------------------------------
# Dataset-specific cleaners
# ---------------------------------------------------------------------------

def clean_transport_activity(df: pd.DataFrame) -> pd.DataFrame:
    """Clean transport activity dataset.

    Steps: drop high-null columns → remove duplicates → coerce year →
    coerce numeric value columns → normalise countries.

    Parameters
    ----------
    df:
        Raw transport-activity :class:`~pandas.DataFrame`.

    Returns
    -------
    pd.DataFrame
        Cleaned frame.
    """
    name = "transport_activity"
    df = drop_high_null_columns(df, dataset_name=name)
    df = remove_duplicate_rows(df, dataset_name=name)
    df = coerce_year_column(df, dataset_name=name)

    string_cols = {"country", "year", "region", "user_id", "occupation", "city_type", "commute_mode", "vehicle_ownership"}
    numeric_cols = [c for c in df.columns if c not in string_cols]
    df = coerce_numeric_columns(df, numeric_cols, dataset_name=name)
    df = normalise_countries(df, dataset_name=name)
    df = impute_numeric_median(df, group_by=["country"], dataset_name=name)

    _log_validation(
        validate_required_columns(df, ["country", "year"], name), name
    )
    return df


def clean_transport_factors(df: pd.DataFrame) -> pd.DataFrame:
    """Clean transport emission-factor dataset.

    Steps: drop high-null columns → remove duplicates → coerce numeric
    value columns → flag outliers in ``emission_factor`` (if present).

    Parameters
    ----------
    df:
        Raw transport emission-factor :class:`~pandas.DataFrame`.

    Returns
    -------
    pd.DataFrame
        Cleaned frame.
    """
    name = "transport_factors"
    df = drop_high_null_columns(df, dataset_name=name)
    df = remove_duplicate_rows(df, dataset_name=name)

    numeric_cols = [c for c in df.columns if c not in ("mode", "fuel_type", "unit")]
    df = coerce_numeric_columns(df, numeric_cols, dataset_name=name)

    if "emission_factor" in df.columns:
        df = flag_outliers(df, "emission_factor", min_val=0.0, dataset_name=name)

    return df


def clean_electricity_mix(df: pd.DataFrame) -> pd.DataFrame:
    """Clean electricity-mix dataset.

    Steps: drop high-null columns → remove duplicates → coerce year →
    coerce share columns → normalise countries → validate required columns.

    Parameters
    ----------
    df:
        Raw electricity-mix :class:`~pandas.DataFrame`.

    Returns
    -------
    pd.DataFrame
        Cleaned frame.
    """
    name = "electricity_mix"
    df = drop_high_null_columns(df, dataset_name=name)
    df = remove_duplicate_rows(df, dataset_name=name)
    df = coerce_year_column(df, dataset_name=name)

    share_cols = [c for c in df.columns if "share" in c or "pct" in c or "fraction" in c]
    df = coerce_numeric_columns(df, share_cols, dataset_name=name)
    df = normalise_countries(df, dataset_name=name)

    result = validate_required_columns(df, ["country", "year"], name)
    _log_validation(result, name)
    return df


def clean_waste(df: pd.DataFrame) -> pd.DataFrame:
    """Clean waste-sector dataset.

    Steps: drop high-null columns → remove duplicates → coerce year →
    coerce numeric columns → normalise countries → impute median.

    Parameters
    ----------
    df:
        Raw waste :class:`~pandas.DataFrame`.

    Returns
    -------
    pd.DataFrame
        Cleaned frame.
    """
    name = "waste"
    df = drop_high_null_columns(df, dataset_name=name)
    df = remove_duplicate_rows(df, dataset_name=name)
    df = coerce_year_column(df, dataset_name=name)

    numeric_cols = [c for c in df.columns if c not in ("country", "year", "region", "waste_type")]
    df = coerce_numeric_columns(df, numeric_cols, dataset_name=name)
    df = normalise_countries(df, dataset_name=name)
    df = impute_numeric_median(df, group_by=["country"], dataset_name=name)
    return df


def clean_behavior(df: pd.DataFrame) -> pd.DataFrame:
    """Clean consumer-behaviour / survey dataset.

    Steps: drop high-null columns → remove duplicates → coerce year →
    coerce numeric columns → normalise countries.

    Parameters
    ----------
    df:
        Raw behaviour :class:`~pandas.DataFrame`.

    Returns
    -------
    pd.DataFrame
        Cleaned frame.
    """
    name = "behavior"
    df = drop_high_null_columns(df, dataset_name=name)
    df = remove_duplicate_rows(df, dataset_name=name)
    df = coerce_year_column(df, dataset_name=name)

    string_cols = {"country", "year", "region", "category", "user_id", "behavior_segment", "top_emission_driver", "preferred_nudge_channel"}
    numeric_cols = [c for c in df.columns if c not in string_cols]
    df = coerce_numeric_columns(df, numeric_cols, dataset_name=name)
    df = normalise_countries(df, dataset_name=name)
    return df


def clean_food_ghg_factors(df: pd.DataFrame) -> pd.DataFrame:
    """Clean food-item GHG emission-factor lookup table.

    Steps: drop high-null columns → remove duplicates → coerce numeric
    columns → flag outliers on ``ghg_kg_co2eq`` (if present).

    Parameters
    ----------
    df:
        Raw food-GHG-factor :class:`~pandas.DataFrame`.

    Returns
    -------
    pd.DataFrame
        Cleaned frame.
    """
    name = "food_ghg_factors"
    df = drop_high_null_columns(df, dataset_name=name)
    df = remove_duplicate_rows(df, dataset_name=name)

    numeric_cols = [c for c in df.columns if c not in ("food_item", "category", "unit", "source", "entity")]
    df = coerce_numeric_columns(df, numeric_cols, dataset_name=name)

    if "ghg_kg_co2eq" in df.columns:
        df = flag_outliers(df, "ghg_kg_co2eq", min_val=0.0, dataset_name=name)

    result = validate_no_duplicate_keys(df, ["food_item"], name)
    _log_validation(result, name)
    return df


def clean_food_supply(df: pd.DataFrame) -> pd.DataFrame:
    """Clean FAO food-supply (already pivoted to long format) dataset.

    Steps: drop high-null columns → remove duplicates → coerce year →
    coerce ``value`` column → normalise countries → impute median.

    Parameters
    ----------
    df:
        Raw (long-format) food-supply :class:`~pandas.DataFrame`.

    Returns
    -------
    pd.DataFrame
        Cleaned frame.
    """
    name = "food_supply"
    df = drop_high_null_columns(df, dataset_name=name)
    df = remove_duplicate_rows(df, dataset_name=name)
    df = coerce_year_column(df, dataset_name=name)

    if "value" in df.columns:
        df = coerce_numeric_columns(df, ["value"], dataset_name=name)
        df = flag_outliers(df, "value", min_val=0.0, dataset_name=name)

    df = normalise_countries(df, country_col="area", dataset_name=name)
    df = impute_numeric_median(df, group_by=["area", "item"], dataset_name=name)
    return df


def clean_gdp(df: pd.DataFrame) -> pd.DataFrame:
    """Clean GDP dataset (typically from Our World in Data or World Bank).

    Steps: drop high-null columns → remove duplicates → coerce year →
    coerce GDP column → normalise countries → flag outliers.

    Parameters
    ----------
    df:
        Raw GDP :class:`~pandas.DataFrame`.

    Returns
    -------
    pd.DataFrame
        Cleaned frame.
    """
    name = "gdp"
    df = drop_high_null_columns(df, dataset_name=name)
    df = remove_duplicate_rows(df, dataset_name=name)
    df = coerce_year_column(df, dataset_name=name)

    gdp_cols = [c for c in df.columns if "gdp" in c or "income" in c]
    df = coerce_numeric_columns(df, gdp_cols, dataset_name=name)
    df = normalise_countries(df, dataset_name=name)

    for col in gdp_cols:
        df = flag_outliers(df, col, min_val=0.0, dataset_name=name)

    result = validate_required_columns(df, ["country", "year"], name)
    _log_validation(result, name)
    return df


def clean_hdi(df: pd.DataFrame) -> pd.DataFrame:
    """Clean Human Development Index dataset.

    Steps: drop high-null columns → remove duplicates → coerce year →
    coerce HDI columns → normalise countries.

    Parameters
    ----------
    df:
        Raw HDI :class:`~pandas.DataFrame`.

    Returns
    -------
    pd.DataFrame
        Cleaned frame.
    """
    name = "hdi"
    df = drop_high_null_columns(df, dataset_name=name)
    df = remove_duplicate_rows(df, dataset_name=name)
    df = coerce_year_column(df, dataset_name=name)

    hdi_cols = [c for c in df.columns if "hdi" in c or "index" in c]
    df = coerce_numeric_columns(df, hdi_cols, dataset_name=name)
    df = normalise_countries(df, dataset_name=name)

    for col in hdi_cols:
        df = flag_outliers(df, col, min_val=0.0, max_val=1.0, dataset_name=name)

    return df


def clean_co2_per_capita(df: pd.DataFrame) -> pd.DataFrame:
    """Clean CO₂ per-capita dataset.

    Steps: drop high-null columns → remove duplicates → coerce year →
    coerce CO₂ columns → normalise countries → flag outliers → validate.

    Parameters
    ----------
    df:
        Raw CO₂-per-capita :class:`~pandas.DataFrame`.

    Returns
    -------
    pd.DataFrame
        Cleaned frame.
    """
    name = "co2_per_capita"
    df = drop_high_null_columns(df, dataset_name=name)
    df = remove_duplicate_rows(df, dataset_name=name)
    df = coerce_year_column(df, dataset_name=name)

    co2_cols = [c for c in df.columns if "co2" in c or "emission" in c or "ghg" in c]
    df = coerce_numeric_columns(df, co2_cols, dataset_name=name)
    df = normalise_countries(df, dataset_name=name)

    for col in co2_cols:
        df = flag_outliers(df, col, min_val=0.0, dataset_name=name)

    result = validate_required_columns(df, ["country", "year"], name)
    _log_validation(result, name)
    return df


def clean_generic_owid(df: pd.DataFrame, name: str = "owid") -> pd.DataFrame:
    """Apply a generic OWID-style cleaning pipeline.

    Suitable for Our World in Data exports that follow the standard
    ``entity / year / value`` layout.

    Steps: drop high-null columns → remove duplicates → coerce year →
    coerce all remaining numeric columns → normalise countries.

    Parameters
    ----------
    df:
        Raw OWID :class:`~pandas.DataFrame`.
    name:
        Logical dataset name used in log messages.

    Returns
    -------
    pd.DataFrame
        Cleaned frame.
    """
    df = drop_high_null_columns(df, dataset_name=name)
    df = remove_duplicate_rows(df, dataset_name=name)
    df = coerce_year_column(df, dataset_name=name)

    id_cols = {"country", "entity", "year", "code", "region"}
    numeric_cols = [c for c in df.columns if c not in id_cols]
    df = coerce_numeric_columns(df, numeric_cols, dataset_name=name)
    df = normalise_countries(df, dataset_name=name)
    return df


# ---------------------------------------------------------------------------
# Dispatch tables
# ---------------------------------------------------------------------------

#: Maps dataset keys to their dedicated cleaning callables.
_CLEANERS: dict[str, Callable[[pd.DataFrame], pd.DataFrame]] = {
    "transport_activity": clean_transport_activity,
    "transport_factors": clean_transport_factors,
    "electricity_mix": clean_electricity_mix,
    "waste": clean_waste,
    "behavior": clean_behavior,
    "food_ghg_factors": clean_food_ghg_factors,
    "ghg_factors_xlsx": clean_food_ghg_factors,  # same logic for XLSX variant
    "food_supply": clean_food_supply,
    "gdp_per_capita": clean_gdp,
    "hdi": clean_hdi,
    "co2_per_capita": clean_co2_per_capita,
}

#: Dataset keys that should be routed through :func:`clean_generic_owid`.
_OWID_GENERICS: dict[str, str] = {
    "energy_per_capita": "energy_per_capita",
    "renewable_share": "renewable_share",
    "population": "population",
    "land_use": "land_use",
    "methane": "methane",
    "nitrous_oxide": "nitrous_oxide",
    "temperature_anomaly": "temperature_anomaly",
}


# ---------------------------------------------------------------------------
# CleaningPipeline
# ---------------------------------------------------------------------------

class CleaningPipeline:
    """Orchestrate cleaning of all raw datasets and persist results.

    Parameters
    ----------
    cleaned_dir:
        Directory where cleaned parquet files are written.  Defaults to
        :attr:`config.CFG.CLEANED_DATA_DIR` when ``None``.

    Examples
    --------
    >>> from src.cleaning.loader import DatasetLoader
    >>> raw = DatasetLoader().load_all()
    >>> pipeline = CleaningPipeline()
    >>> cleaned = pipeline.run_all(raw)
    """

    def __init__(self, cleaned_dir: Optional[Path] = None) -> None:
        self._cleaned_dir: Path = Path(cleaned_dir or CFG.CLEANED_DIR)
        self._cleaned_dir.mkdir(parents=True, exist_ok=True)
        logger.debug("CleaningPipeline initialised. Output dir: %s", self._cleaned_dir)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run_all(self, raw_datasets: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        """Clean every dataset in *raw_datasets* and write output files.

        Parameters
        ----------
        raw_datasets:
            Mapping of ``{dataset_name: raw_DataFrame}`` as returned by
            :meth:`~loader.DatasetLoader.load_all`.

        Returns
        -------
        dict[str, pd.DataFrame]
            Mapping of ``{dataset_name: cleaned_DataFrame}``.
        """
        cleaned: dict[str, pd.DataFrame] = {}

        for name, df in raw_datasets.items():
            logger.info("Cleaning dataset '%s' (%d rows × %d cols)…", name, len(df), len(df.columns))
            try:
                df_clean = self._clean_dispatch(df, name)
                cleaned[name] = df_clean
                self._write(name, df_clean)
            except Exception as exc:  # noqa: BLE001
                logger.error("Failed to clean '%s': %s", name, exc, exc_info=True)

        logger.info(
            "CleaningPipeline complete: %d / %d dataset(s) cleaned.",
            len(cleaned),
            len(raw_datasets),
        )
        return cleaned

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _clean_dispatch(self, df: pd.DataFrame, name: str) -> pd.DataFrame:
        """Route a dataset to the appropriate cleaning function.

        Priority:
        1. Exact match in :data:`_CLEANERS`.
        2. Match in :data:`_OWID_GENERICS`.
        3. Generic fallback via :meth:`_generic_clean`.

        Parameters
        ----------
        df:
            Raw :class:`~pandas.DataFrame`.
        name:
            Logical dataset name.

        Returns
        -------
        pd.DataFrame
            Cleaned frame.
        """
        if name in _CLEANERS:
            logger.debug("Dispatching '%s' to dedicated cleaner.", name)
            return _CLEANERS[name](df)

        if name in _OWID_GENERICS:
            logger.debug("Dispatching '%s' through clean_generic_owid.", name)
            return clean_generic_owid(df, name=name)

        logger.debug("No dedicated cleaner for '%s'; using generic fallback.", name)
        return self._generic_clean(df, name)

    def _generic_clean(self, df: pd.DataFrame, name: str) -> pd.DataFrame:
        """Apply a minimal cleaning pipeline for unknown datasets.

        Steps: validate null fraction → drop high-null columns →
        remove duplicates → coerce year (if column exists) →
        coerce remaining numeric columns.

        Parameters
        ----------
        df:
            Raw :class:`~pandas.DataFrame`.
        name:
            Logical dataset name, used in log messages.

        Returns
        -------
        pd.DataFrame
            Minimally cleaned frame.
        """
        result = validate_null_fraction(df, dataset_name=name)
        _log_validation(result, name)

        df = drop_high_null_columns(df, dataset_name=name)
        df = remove_duplicate_rows(df, dataset_name=name)

        if "year" in df.columns:
            df = coerce_year_column(df, dataset_name=name)

        id_cols = {"country", "entity", "year", "code", "region", "area", "item"}
        numeric_cols = [c for c in df.columns if c not in id_cols]
        df = coerce_numeric_columns(df, numeric_cols, dataset_name=name)
        return df

    def _write(self, name: str, df: pd.DataFrame) -> None:
        """Persist *df* to the cleaned data directory as a parquet file.

        Parameters
        ----------
        name:
            Dataset name used to form the filename ``{name}.parquet``.
        df:
            Cleaned :class:`~pandas.DataFrame` to save.
        """
        out_path = self._cleaned_dir / f"{name}.csv"
        try:
            io_utils.save_csv(df, self._cleaned_dir, f"{name}.csv")
            logger.info("Written cleaned '%s' → %s (%d rows).", name, out_path.name, len(df))
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to write '%s': %s", out_path, exc)
