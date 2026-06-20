"""
loader.py
=========
Dataset loader for the Carbon Footprint Awareness Platform.

Responsibilities
----------------
* Normalise raw column names to ``snake_case``.
* Dispatch loading by file extension and dataset name.
* Apply FAO wide-to-long pivoting for food-supply datasets.
* Prefer the most relevant sheet when loading GHG-factor Excel workbooks.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

import pandas as pd

from config import CFG
from src.utils import io_utils
from src.utils.logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Column-name helpers
# ---------------------------------------------------------------------------

def _to_snake_case(name: str) -> str:
    """Convert an arbitrary column name to ``snake_case``.

    Steps applied (in order):

    1. Strip leading/trailing whitespace.
    2. Remove parenthesised substrings, e.g. ``"Area (km²)"`` → ``"Area "``.
    3. Insert an underscore between a lowercase letter and an uppercase letter
       to handle ``camelCase`` / ``PascalCase``.
    4. Replace every character that is not alphanumeric or underscore with an
       underscore.
    5. Collapse consecutive underscores to a single one.
    6. Strip leading/trailing underscores and convert to lowercase.

    Parameters
    ----------
    name:
        Raw column label as read from the source file.

    Returns
    -------
    str
        A clean, lowercase, underscore-separated identifier.

    Examples
    --------
    >>> _to_snake_case("GHG Emissions (Mt CO2eq)")
    'ghg_emissions'
    >>> _to_snake_case("totalCO2perCapita")
    'total_c_o2_per_capita'
    """
    # 1. Strip whitespace
    name = name.strip()
    # 2. Remove parenthesised content (including the parens themselves)
    name = re.sub(r"\(.*?\)", "", name)
    # 3. CamelCase → camel_Case (insert underscore before uppercase runs)
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    # 4. Non-alphanumeric chars → underscore
    name = re.sub(r"[^a-zA-Z0-9]", "_", name)
    # 5. Collapse consecutive underscores
    name = re.sub(r"_+", "_", name)
    # 6. Strip edges and lowercase
    return name.strip("_").lower()


def normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename all columns of *df* to ``snake_case``.

    Duplicate column names that emerge after normalisation are disambiguated
    by appending ``_1``, ``_2``, … (starting at ``_1`` for the *second*
    occurrence, so the first occurrence keeps the base name).

    Parameters
    ----------
    df:
        The :class:`~pandas.DataFrame` whose columns should be renamed.

    Returns
    -------
    pd.DataFrame
        A copy of *df* with renamed columns (the data is not modified).
    """
    seen: dict[str, int] = {}
    new_names: list[str] = []

    for col in df.columns:
        snake = _to_snake_case(str(col))
        if snake in seen:
            seen[snake] += 1
            new_names.append(f"{snake}_{seen[snake]}")
        else:
            seen[snake] = 0
            new_names.append(snake)

    df = df.copy()
    df.columns = new_names  # type: ignore[assignment]
    return df


# ---------------------------------------------------------------------------
# FAO wide-to-long pivot
# ---------------------------------------------------------------------------

_FAO_YEAR_PATTERN = re.compile(r"^y(\d{4})$", re.IGNORECASE)
_FAO_FLAG_PATTERN = re.compile(r"^y(\d{4})[fn]$", re.IGNORECASE)


def _pivot_fao_wide_to_long(df: pd.DataFrame) -> pd.DataFrame:
    """Melt FAO-style wide-format data into a long ``(…, year, value)`` table.

    FAO files typically store one column per year, e.g. ``Y2010``, ``Y2011``,
    …, ``Y2023``, alongside flag columns such as ``Y2010F`` and ``Y2010N``
    which are dropped.

    Parameters
    ----------
    df:
        Wide-format FAO :class:`~pandas.DataFrame` with already-normalised
        (snake_case) column names.

    Returns
    -------
    pd.DataFrame
        Long-format frame with an additional ``year`` column typed as
        ``Int64`` (nullable integer).  Value column is named ``value``.
        Flag columns are excluded.
    """
    all_cols = list(df.columns)

    # Separate year-value columns from flag columns and id columns
    year_cols: list[str] = []
    flag_cols: list[str] = []
    id_cols: list[str] = []

    for col in all_cols:
        if _FAO_FLAG_PATTERN.match(col):
            flag_cols.append(col)
        elif _FAO_YEAR_PATTERN.match(col):
            year_cols.append(col)
        else:
            id_cols.append(col)

    if not year_cols:
        logger.warning("No FAO year columns (Y<YYYY>) found — returning df unchanged.")
        return df

    logger.debug(
        "FAO pivot: %d id cols, %d year cols, %d flag cols dropped.",
        len(id_cols),
        len(year_cols),
        len(flag_cols),
    )

    melted = df[id_cols + year_cols].melt(
        id_vars=id_cols,
        value_vars=year_cols,
        var_name="year",
        value_name="value",
    )

    # Extract the numeric year from the column label (e.g. "y2010" → 2010)
    melted["year"] = (
        melted["year"]
        .str.extract(r"(\d{4})", expand=False)
        .astype("Int64")
    )

    return melted.reset_index(drop=True)


# ---------------------------------------------------------------------------
# GHG factor XLSX loader
# ---------------------------------------------------------------------------

_GHG_PREFERRED_KEYWORDS = ("factor", "emission", "ghg", "data")


def _load_ghg_factors_xlsx(path: Path) -> pd.DataFrame:
    """Load an Excel workbook containing GHG emission factors.

    Sheet-selection heuristic: prefer sheets whose **lowercase** name contains
    at least one of the keywords ``'factor'``, ``'emission'``, ``'ghg'``, or
    ``'data'``.  If no such sheet exists the first sheet is used.

    Parameters
    ----------
    path:
        Absolute or relative path to the ``.xlsx`` / ``.xls`` file.

    Returns
    -------
    pd.DataFrame
        The selected sheet loaded into a :class:`~pandas.DataFrame` with
        normalised (snake_case) column names.

    Raises
    ------
    FileNotFoundError
        If *path* does not exist.
    """
    if not path.exists():
        raise FileNotFoundError(f"GHG factors file not found: {path}")

    xl = pd.ExcelFile(path)
    sheet_names: list[str] = xl.sheet_names  # type: ignore[assignment]

    selected_sheet: str = sheet_names[0]  # fallback
    for sheet in sheet_names:
        if any(kw in sheet.lower() for kw in _GHG_PREFERRED_KEYWORDS):
            selected_sheet = sheet
            logger.debug("GHG XLSX: selected sheet '%s' from %s.", selected_sheet, path.name)
            break
    else:
        logger.debug(
            "GHG XLSX: no preferred sheet found in %s; using first sheet '%s'.",
            path.name,
            selected_sheet,
        )

    df = pd.read_excel(path, sheet_name=selected_sheet)
    df = normalise_columns(df)
    logger.info(
        "Loaded GHG factors from '%s' sheet '%s': %d rows × %d cols.",
        path.name,
        selected_sheet,
        len(df),
        len(df.columns),
    )
    return df


# ---------------------------------------------------------------------------
# DatasetLoader
# ---------------------------------------------------------------------------

class DatasetLoader:
    """Load all raw datasets declared in :attr:`config.CFG.SOURCE_PATHS`.

    Parameters
    ----------
    raw_data_dir:
        Override for the raw data directory.  Defaults to
        :attr:`config.CFG.RAW_DATA_DIR` when ``None``.

    Examples
    --------
    >>> loader = DatasetLoader()
    >>> datasets = loader.load_all()
    >>> df_co2 = datasets["co2_per_capita"]
    """

    def __init__(self, raw_data_dir: Optional[Path] = None) -> None:
        self._raw_data_dir: Path = Path(raw_data_dir or CFG.RAW_DATA_DIR)
        logger.debug("DatasetLoader initialised with raw_data_dir=%s", self._raw_data_dir)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load_all(self) -> dict[str, pd.DataFrame]:
        """Load every dataset listed in :attr:`config.CFG.SOURCE_PATHS`.

        Missing or unreadable files are skipped with a warning; they will not
        appear in the returned mapping.

        Returns
        -------
        dict[str, pd.DataFrame]
            Mapping of ``{dataset_name: DataFrame}``.
        """
        datasets: dict[str, pd.DataFrame] = {}
        source_paths: dict[str, str] = CFG.SOURCE_PATHS  # type: ignore[attr-defined]

        for name, rel_path in source_paths.items():
            df = self.load_single(name)
            if df is not None:
                datasets[name] = df

        logger.info("load_all: loaded %d / %d dataset(s).", len(datasets), len(source_paths))
        return datasets

    def load_single(self, name: str) -> Optional[pd.DataFrame]:
        """Load a single dataset by its logical *name*.

        Parameters
        ----------
        name:
            Key in :attr:`config.CFG.SOURCE_PATHS`.

        Returns
        -------
        pd.DataFrame or None
            The loaded frame, or ``None`` if the dataset is unknown or the
            file could not be read.
        """
        source_paths: dict[str, str] = CFG.SOURCE_PATHS  # type: ignore[attr-defined]
        if name not in source_paths:
            logger.warning("load_single: unknown dataset name '%s'.", name)
            return None

        path = self._raw_data_dir / source_paths[name]
        return self._load_single(name, path)

    # ------------------------------------------------------------------
    # Internal dispatch
    # ------------------------------------------------------------------

    def _load_single(self, name: str, path: Path) -> Optional[pd.DataFrame]:
        """Dispatch loading to the appropriate helper based on file extension.

        Parameters
        ----------
        name:
            Logical dataset name (used for special-case routing).
        path:
            Resolved filesystem path to the raw file.

        Returns
        -------
        pd.DataFrame or None
        """
        if not path.exists():
            logger.warning("_load_single: file not found — %s", path)
            return None

        suffix = path.suffix.lower()
        try:
            if suffix == ".csv":
                return self._load_csv_by_name(name, path)
            elif suffix in (".xlsx", ".xls"):
                return self._load_xlsx_by_name(name, path)
            else:
                logger.warning(
                    "_load_single: unsupported extension '%s' for '%s'.", suffix, name
                )
                return None
        except Exception as exc:  # noqa: BLE001
            logger.error("_load_single: failed to load '%s' (%s): %s", name, path, exc)
            return None

    def _load_csv_by_name(self, name: str, path: Path) -> pd.DataFrame:
        """Load a CSV file, applying FAO pivot for ``food_supply`` datasets.

        Parameters
        ----------
        name:
            Logical dataset name used to trigger special-case handling.
        path:
            Path to the CSV file.

        Returns
        -------
        pd.DataFrame
            Loaded and column-normalised :class:`~pandas.DataFrame`.
        """
        df = io_utils.load_csv(path)  # type: ignore[attr-defined]
        df = normalise_columns(df)

        if name == "food_supply":
            logger.debug("Applying FAO wide-to-long pivot for '%s'.", name)
            df = _pivot_fao_wide_to_long(df)

        logger.info(
            "Loaded CSV '%s': %d rows × %d cols.", name, len(df), len(df.columns)
        )
        return df

    def _load_xlsx_by_name(self, name: str, path: Path) -> pd.DataFrame:
        """Load an XLSX file, using the GHG-aware sheet selector for ``ghg_factors_xlsx``.

        Parameters
        ----------
        name:
            Logical dataset name used to trigger special-case handling.
        path:
            Path to the XLSX file.

        Returns
        -------
        pd.DataFrame
            Loaded and column-normalised :class:`~pandas.DataFrame`.
        """
        if name == "ghg_factors_xlsx":
            return _load_ghg_factors_xlsx(path)

        # Generic XLSX: load first sheet and normalise columns
        df = pd.read_excel(path)
        df = normalise_columns(df)
        logger.info(
            "Loaded XLSX '%s': %d rows × %d cols.", name, len(df), len(df.columns)
        )
        return df
