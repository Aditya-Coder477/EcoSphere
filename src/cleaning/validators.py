"""
validators.py
=============
Validation helpers for the Carbon Footprint Awareness Platform cleaning pipeline.

Every public function returns a :class:`ValidationResult` so results can be
accumulated and merged across multiple checks before a caller decides whether
to raise, warn, or silently continue.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

import pandas as pd

from src.utils.logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# ValidationResult
# ---------------------------------------------------------------------------

@dataclass
class ValidationResult:
    """Aggregated outcome of one or more validation checks.

    Attributes
    ----------
    passed:
        ``True`` when **no** issues have been recorded.
    issues:
        Human-readable descriptions of every problem found.
    """

    passed: bool = True
    issues: list[str] = field(default_factory=list)

    # ------------------------------------------------------------------
    # Mutation helpers
    # ------------------------------------------------------------------

    def add_issue(self, msg: str) -> None:
        """Append *msg* to :attr:`issues` and set :attr:`passed` to ``False``.

        Parameters
        ----------
        msg:
            A plain-English description of the validation failure.
        """
        self.issues.append(msg)
        self.passed = False

    def merge(self, other: "ValidationResult") -> "ValidationResult":
        """Return a **new** :class:`ValidationResult` combining *self* and *other*.

        The merged result fails when either operand fails.

        Parameters
        ----------
        other:
            Another :class:`ValidationResult` whose issues will be appended.

        Returns
        -------
        ValidationResult
            A fresh instance aggregating both sets of issues.
        """
        merged = ValidationResult(
            passed=self.passed and other.passed,
            issues=self.issues + other.issues,
        )
        return merged

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __bool__(self) -> bool:  # noqa: D105
        return self.passed

    def __repr__(self) -> str:  # noqa: D105
        status = "PASSED" if self.passed else f"FAILED ({len(self.issues)} issue(s))"
        return f"ValidationResult({status})"


# ---------------------------------------------------------------------------
# Individual validators
# ---------------------------------------------------------------------------

def validate_required_columns(
    df: pd.DataFrame,
    required: Sequence[str],
    dataset_name: str = "",
) -> ValidationResult:
    """Check that every column in *required* is present in *df*.

    Parameters
    ----------
    df:
        The :class:`~pandas.DataFrame` to inspect.
    required:
        Column names that **must** exist.
    dataset_name:
        Optional label used in log/issue messages.

    Returns
    -------
    ValidationResult
        Fails if any column is missing; each missing column produces one issue.
    """
    result = ValidationResult()
    prefix = f"[{dataset_name}] " if dataset_name else ""
    missing = [col for col in required if col not in df.columns]
    if missing:
        msg = f"{prefix}Missing required column(s): {missing}"
        logger.warning(msg)
        result.add_issue(msg)
    else:
        logger.debug("%sAll %d required column(s) present.", prefix, len(required))
    return result


def validate_numeric_range(
    df: pd.DataFrame,
    column: str,
    min_val: float | None,
    max_val: float | None,
    dataset_name: str = "",
) -> ValidationResult:
    """Flag rows where *column* falls outside [*min_val*, *max_val*].

    Either bound may be ``None`` to indicate an open interval.

    Parameters
    ----------
    df:
        The :class:`~pandas.DataFrame` to inspect.
    column:
        Name of the numeric column to check.
    min_val:
        Inclusive lower bound, or ``None`` for no lower bound.
    max_val:
        Inclusive upper bound, or ``None`` for no upper bound.
    dataset_name:
        Optional label used in log/issue messages.

    Returns
    -------
    ValidationResult
        Fails if any out-of-range rows are detected.
    """
    result = ValidationResult()
    prefix = f"[{dataset_name}] " if dataset_name else ""

    if column not in df.columns:
        msg = f"{prefix}Column '{column}' not found — range check skipped."
        logger.warning(msg)
        result.add_issue(msg)
        return result

    series = pd.to_numeric(df[column], errors="coerce")
    mask = pd.Series([False] * len(df), index=df.index)

    if min_val is not None:
        mask |= series < min_val
    if max_val is not None:
        mask |= series > max_val

    n_bad = int(mask.sum())
    if n_bad:
        bounds = f"[{min_val}, {max_val}]"
        msg = (
            f"{prefix}Column '{column}' has {n_bad} row(s) outside expected range {bounds}."
        )
        logger.warning(msg)
        result.add_issue(msg)
    else:
        logger.debug(
            "%sColumn '%s' range check passed (bounds %s).",
            prefix,
            column,
            f"[{min_val}, {max_val}]",
        )
    return result


def validate_no_duplicate_keys(
    df: pd.DataFrame,
    key_columns: Sequence[str],
    dataset_name: str = "",
) -> ValidationResult:
    """Detect rows that share the same combination of *key_columns*.

    Parameters
    ----------
    df:
        The :class:`~pandas.DataFrame` to inspect.
    key_columns:
        Columns whose combination should be unique across all rows.
    dataset_name:
        Optional label used in log/issue messages.

    Returns
    -------
    ValidationResult
        Fails if any duplicate key combination is detected.
    """
    result = ValidationResult()
    prefix = f"[{dataset_name}] " if dataset_name else ""

    missing = [c for c in key_columns if c not in df.columns]
    if missing:
        msg = f"{prefix}Key column(s) not found for duplicate check: {missing}"
        logger.warning(msg)
        result.add_issue(msg)
        return result

    dupes = df.duplicated(subset=list(key_columns), keep=False)
    n_dupes = int(dupes.sum())
    if n_dupes:
        msg = (
            f"{prefix}{n_dupes} duplicate row(s) found for key column(s) {list(key_columns)}."
        )
        logger.warning(msg)
        result.add_issue(msg)
    else:
        logger.debug(
            "%sNo duplicate keys detected for %s.", prefix, list(key_columns)
        )
    return result


def validate_column_dtypes(
    df: pd.DataFrame,
    expected_dtypes: dict[str, type | str],
    dataset_name: str = "",
) -> ValidationResult:
    """Check whether columns can be cast to their expected dtypes.

    The check uses :func:`pandas.to_numeric` for numeric targets and
    :func:`pandas.to_datetime` for datetime targets; everything else is
    attempted via :meth:`pandas.Series.astype`.

    Parameters
    ----------
    df:
        The :class:`~pandas.DataFrame` to inspect.
    expected_dtypes:
        Mapping of ``{column_name: expected_dtype}``.  The dtype may be a
        Python type (e.g. ``float``) or a string understood by pandas
        (e.g. ``"Int64"``, ``"datetime64[ns]"``).
    dataset_name:
        Optional label used in log/issue messages.

    Returns
    -------
    ValidationResult
        Fails for every column that cannot be safely cast.
    """
    result = ValidationResult()
    prefix = f"[{dataset_name}] " if dataset_name else ""

    for col, expected in expected_dtypes.items():
        if col not in df.columns:
            msg = f"{prefix}Column '{col}' missing — dtype check skipped."
            logger.warning(msg)
            result.add_issue(msg)
            continue

        dtype_str = str(expected).lower()
        try:
            if any(t in dtype_str for t in ("float", "int", "numeric")):
                coerced = pd.to_numeric(df[col], errors="coerce")
                n_failed = int(coerced.isna().sum() - df[col].isna().sum())
                if n_failed > 0:
                    raise ValueError(f"{n_failed} value(s) could not be cast to numeric.")
            elif "datetime" in dtype_str:
                coerced = pd.to_datetime(df[col], errors="coerce")
                n_failed = int(coerced.isna().sum() - df[col].isna().sum())
                if n_failed > 0:
                    raise ValueError(f"{n_failed} value(s) could not be parsed as datetime.")
            else:
                df[col].astype(expected)
        except Exception as exc:  # noqa: BLE001
            msg = f"{prefix}Column '{col}' failed dtype cast to '{expected}': {exc}"
            logger.warning(msg)
            result.add_issue(msg)
        else:
            logger.debug(
                "%sColumn '%s' dtype check passed (expected '%s').", prefix, col, expected
            )

    return result


def validate_null_fraction(
    df: pd.DataFrame,
    max_fraction: float = 0.60,
    dataset_name: str = "",
) -> ValidationResult:
    """Report columns whose null fraction exceeds *max_fraction*.

    Parameters
    ----------
    df:
        The :class:`~pandas.DataFrame` to inspect.
    max_fraction:
        Threshold in the range ``[0, 1]``.  Columns with a null rate **above**
        this value are flagged.  Defaults to ``0.60``.
    dataset_name:
        Optional label used in log/issue messages.

    Returns
    -------
    ValidationResult
        Fails for every column that exceeds the null-fraction threshold.
    """
    result = ValidationResult()
    prefix = f"[{dataset_name}] " if dataset_name else ""

    if df.empty:
        logger.debug("%sDataFrame is empty — null fraction check skipped.", prefix)
        return result

    null_fractions = df.isna().mean()
    high_null = null_fractions[null_fractions > max_fraction]

    if not high_null.empty:
        for col, frac in high_null.items():
            msg = (
                f"{prefix}Column '{col}' has {frac:.1%} null values "
                f"(threshold: {max_fraction:.1%})."
            )
            logger.warning(msg)
            result.add_issue(msg)
    else:
        logger.debug(
            "%sAll columns within null-fraction threshold (%.0f%%).",
            prefix,
            max_fraction * 100,
        )
    return result


def validate_merge_integrity(
    left: pd.DataFrame,
    merged: pd.DataFrame,
    left_name: str = "left",
) -> ValidationResult:
    """Verify that a merge did not silently drop rows from *left*.

    A row-count drop often indicates a key mismatch between the two sides of a
    join, which can lead to silently missing data in downstream analysis.

    Parameters
    ----------
    left:
        The left-hand :class:`~pandas.DataFrame` **before** merging.
    merged:
        The resulting :class:`~pandas.DataFrame` **after** merging.
    left_name:
        Human-readable name for *left*, used in log/issue messages.

    Returns
    -------
    ValidationResult
        Fails if ``len(merged) < len(left)``.
    """
    result = ValidationResult()
    n_left = len(left)
    n_merged = len(merged)

    if n_merged < n_left:
        dropped = n_left - n_merged
        msg = (
            f"Merge dropped {dropped} row(s) from '{left_name}' "
            f"({n_left} → {n_merged} rows). Possible key mismatch."
        )
        logger.warning(msg)
        result.add_issue(msg)
    elif n_merged > n_left:
        # Fan-out is not necessarily wrong but worth logging
        logger.debug(
            "Merge expanded '%s' from %d to %d rows (fan-out detected).",
            left_name,
            n_left,
            n_merged,
        )
    else:
        logger.debug(
            "Merge integrity check passed for '%s' (%d rows preserved).",
            left_name,
            n_left,
        )
    return result
