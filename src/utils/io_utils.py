"""
src/utils/io_utils.py
=====================
Safe, memory-conscious file I/O helpers for the Carbon Footprint pipeline.
"""

import os
from pathlib import Path
from typing import Iterator, Optional

import pandas as pd

from src.utils.logger import get_logger

log = get_logger(__name__)

_ALLOWED_EXTENSIONS: frozenset = frozenset({".csv", ".xlsx", ".xls"})


def resolve_path(raw_path: str | Path) -> Path:
    """
    Resolve raw_path to an absolute path.

    Raises
    ------
    FileNotFoundError
        If the path does not exist.
    """
    resolved = Path(raw_path).resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"Path does not exist: {resolved}")
    return resolved


def safe_output_path(directory: str | Path, filename: str) -> Path:
    """
    Build and validate an output file path, creating the directory if needed.

    Parameters
    ----------
    directory : str | Path
        Target output directory.
    filename : str
        Simple filename without path separators.

    Returns
    -------
    Path
    """
    filename = str(filename)
    if os.sep in filename or "/" in filename or ".." in filename:
        raise ValueError(f"filename must not contain path separators: {filename!r}")

    ext = Path(filename).suffix.lower()
    if ext not in _ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported extension '{ext}'.")

    out_dir = Path(directory).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / filename


def load_csv(
    path: str | Path,
    *,
    encoding: str = "utf-8",
    low_memory: bool = False,
    dtype: Optional[dict] = None,
    **kwargs,
) -> pd.DataFrame:
    """
    Load a CSV file into a DataFrame.

    Parameters
    ----------
    path : str | Path
        Path to the CSV file.
    encoding : str
        File encoding.
    low_memory : bool
        Passed to pd.read_csv.
    dtype : dict, optional
        Column dtype overrides.

    Returns
    -------
    pd.DataFrame
    """
    p = Path(path).resolve()
    if not p.exists():
        raise FileNotFoundError(f"CSV file not found: {p}")
    if p.suffix.lower() != ".csv":
        raise ValueError(f"Expected .csv, got: {p.suffix!r}")

    log.debug("Loading CSV: %s", p)
    try:
        df = pd.read_csv(p, encoding=encoding, low_memory=low_memory, dtype=dtype, **kwargs)
    except UnicodeDecodeError:
        log.warning("UTF-8 failed for %s — retrying with latin-1.", p.name)
        df = pd.read_csv(p, encoding="latin-1", low_memory=low_memory, dtype=dtype, **kwargs)

    log.info("Loaded '%s': %d rows × %d cols", p.name, len(df), df.shape[1])
    return df


def load_csv_chunked(
    path: str | Path,
    chunksize: int = 50_000,
    *,
    encoding: str = "utf-8",
    **kwargs,
) -> Iterator[pd.DataFrame]:
    """
    Yield chunks of a large CSV for memory-efficient processing.

    Parameters
    ----------
    path : str | Path
    chunksize : int
    encoding : str

    Yields
    ------
    pd.DataFrame
    """
    p = Path(path).resolve()
    if not p.exists():
        raise FileNotFoundError(f"CSV file not found: {p}")

    reader = pd.read_csv(p, encoding=encoding, chunksize=chunksize, **kwargs)
    for i, chunk in enumerate(reader):
        log.debug("  chunk %d (%d rows)", i, len(chunk))
        yield chunk


def load_xlsx(
    path: str | Path,
    sheet_name: str | int | None = 0,
    *,
    dtype: Optional[dict] = None,
    **kwargs,
) -> pd.DataFrame | dict:
    """
    Load an Excel file.

    Parameters
    ----------
    path : str | Path
    sheet_name : str | int | None
        Sheet to load. None loads all sheets.
    dtype : dict, optional

    Returns
    -------
    pd.DataFrame or dict[str, pd.DataFrame]
    """
    p = Path(path).resolve()
    if not p.exists():
        raise FileNotFoundError(f"Excel file not found: {p}")
    if p.suffix.lower() not in {".xlsx", ".xls"}:
        raise ValueError(f"Expected .xlsx/.xls, got: {p.suffix!r}")

    log.debug("Loading Excel: %s (sheet=%s)", p, sheet_name)
    result = pd.read_excel(p, sheet_name=sheet_name, dtype=dtype, **kwargs)
    if isinstance(result, pd.DataFrame):
        log.info("Loaded '%s': %d rows × %d cols", p.name, len(result), result.shape[1])
    else:
        log.info("Loaded '%s': %d sheets", p.name, len(result))
    return result


def save_csv(
    df: pd.DataFrame,
    directory: str | Path,
    filename: str,
    *,
    index: bool = False,
    encoding: str = "utf-8-sig",
) -> Path:
    """
    Save a DataFrame to CSV.

    Parameters
    ----------
    df : pd.DataFrame
    directory : str | Path
    filename : str
    index : bool
    encoding : str

    Returns
    -------
    Path
    """
    out_path = safe_output_path(directory, filename)
    df.to_csv(out_path, index=index, encoding=encoding)
    log.info("Saved '%s': %d rows × %d cols → %s", filename, len(df), df.shape[1], out_path)
    return out_path


def save_xlsx(
    df: pd.DataFrame,
    directory: str | Path,
    filename: str,
    *,
    sheet_name: str = "Sheet1",
    index: bool = False,
) -> Path:
    """
    Save a DataFrame to Excel.

    Parameters
    ----------
    df : pd.DataFrame
    directory : str | Path
    filename : str
    sheet_name : str
    index : bool

    Returns
    -------
    Path
    """
    out_path = safe_output_path(directory, filename)
    df.to_excel(out_path, sheet_name=sheet_name, index=index)
    log.info("Saved '%s' → %s", filename, out_path)
    return out_path


def discover_csv_files(root: str | Path, recursive: bool = True) -> list:
    """
    Return all CSV files under root.

    Parameters
    ----------
    root : str | Path
    recursive : bool

    Returns
    -------
    list[Path]
    """
    root_path = Path(root).resolve()
    if not root_path.is_dir():
        raise NotADirectoryError(f"Not a directory: {root_path}")

    pattern = "**/*.csv" if recursive else "*.csv"
    files = sorted(root_path.glob(pattern))
    log.debug("Discovered %d CSV files under '%s'", len(files), root_path)
    return files
