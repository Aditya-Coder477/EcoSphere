"""
merger.py
=========
Data integration module for the Carbon Footprint Awareness Platform.

Provides a reusable ``safe_left_merge`` helper and the ``IntegrationPipeline``
orchestrator that joins all engineered feature DataFrames into a single master
dataset ready for analysis and modelling.

Functions
---------
safe_left_merge
    Validated, logged left-merge with automatic suffix resolution.

Classes
-------
IntegrationPipeline
    Orchestrates the full merge sequence across all feature domains.

Usage
-----
>>> from src.integration.merger import IntegrationPipeline
>>> pipeline = IntegrationPipeline()
>>> master = pipeline.run(engineered)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from config import CFG
from src.utils.logger import get_logger
from src.utils.io_utils import save_csv
from src.utils.validators import validate_dataframe

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def safe_left_merge(
    left: pd.DataFrame,
    right: pd.DataFrame,
    on: str | List[str],
    left_name: str = "left",
    right_name: str = "right",
    suffixes: Tuple[str, str] = ("_left", "_right"),
) -> pd.DataFrame:
    """Perform a validated left merge and clean up collision suffixes.

    Steps
    -----
    1. Validate that all keys in *on* are present in both DataFrames.
    2. Execute ``pd.merge`` with the specified *suffixes*.
    3. Drop ``_right``-suffixed duplicate columns.
    4. Strip ``_left`` suffixes from columns that were renamed.
    5. Validate merge integrity (no key duplication in result).
    6. Log row counts and any columns dropped.

    Parameters
    ----------
    left : pd.DataFrame
        Left-side DataFrame (preserved in full).
    right : pd.DataFrame
        Right-side DataFrame (only matched rows contribute).
    on : str or list[str]
        Column name(s) to merge on.
    left_name : str, optional
        Human-readable name for the left DataFrame (used in log messages).
    right_name : str, optional
        Human-readable name for the right DataFrame (used in log messages).
    suffixes : tuple[str, str], optional
        Suffixes appended to overlapping column names
        (default ``('_left', '_right')``).

    Returns
    -------
    pd.DataFrame
        Merged DataFrame with suffix collisions resolved.

    Raises
    ------
    KeyError
        If any key in *on* is absent from either DataFrame.
    ValueError
        If the merge produces more rows than the left DataFrame (indicates
        a one-to-many join that was not expected).
    """
    keys = [on] if isinstance(on, str) else list(on)

    # ── 1. Key validation ──────────────────────────────────────────────
    for key in keys:
        if key not in left.columns:
            raise KeyError(
                f"safe_left_merge: key '{key}' missing from '{left_name}' "
                f"(columns: {left.columns.tolist()})."
            )
        if key not in right.columns:
            raise KeyError(
                f"safe_left_merge: key '{key}' missing from '{right_name}' "
                f"(columns: {right.columns.tolist()})."
            )

    left_rows = len(left)
    logger.debug(
        "Merging '%s' (%d rows) ← '%s' (%d rows) on %s",
        left_name, left_rows, right_name, len(right), keys,
    )

    # ── 2. Merge ───────────────────────────────────────────────────────
    merged = pd.merge(left, right, on=keys, how="left", suffixes=suffixes)

    # ── 3. Drop _right columns ─────────────────────────────────────────
    right_suffix = suffixes[1]
    left_suffix = suffixes[0]
    right_cols = [c for c in merged.columns if c.endswith(right_suffix)]
    if right_cols:
        logger.debug(
            "safe_left_merge: dropping %d '_right' columns: %s",
            len(right_cols), right_cols,
        )
        merged = merged.drop(columns=right_cols)

    # ── 4. Strip _left suffixes ────────────────────────────────────────
    rename_map = {
        c: c[: -len(left_suffix)]
        for c in merged.columns
        if c.endswith(left_suffix)
    }
    if rename_map:
        logger.debug(
            "safe_left_merge: renaming %d '_left' columns back: %s",
            len(rename_map), list(rename_map.keys()),
        )
        merged = merged.rename(columns=rename_map)

    # ── 5. Integrity check ─────────────────────────────────────────────
    if len(merged) > left_rows:
        raise ValueError(
            f"safe_left_merge: row explosion detected — left '{left_name}' had "
            f"{left_rows} rows but result has {len(merged)} rows.  "
            f"Ensure the right table has unique keys on {keys}."
        )

    # ── 6. Log statistics ──────────────────────────────────────────────
    matched = merged[keys[0]].notna().sum() if keys else len(merged)
    logger.info(
        "Merged '%s' ← '%s': %d → %d rows | matched ≈ %d | "
        "new cols: %d",
        left_name, right_name, left_rows, len(merged),
        matched, len(merged.columns) - len(left.columns),
    )
    return merged


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

class IntegrationPipeline:
    """Orchestrates the full cross-domain data integration sequence.

    The pipeline merges all engineered feature DataFrames produced by the
    feature-engineering stage into two artefacts:

    * **country_year** – country × year panel with electricity, waste, food,
      and context features.
    * **master** – user-level table with personal transport/behaviour features
      joined to the latest country-year snapshot.

    Parameters
    ----------
    merged_dir : str or Path or None, optional
        Output directory for saved CSVs.  Defaults to ``CFG.MERGED_DIR``.

    Attributes
    ----------
    merged_dir : Path
        Resolved output directory.
    _report_lines : list[str]
        Accumulator for the text integration report.

    Examples
    --------
    >>> pipeline = IntegrationPipeline()
    >>> master   = pipeline.run(engineered_dict)
    """

    def __init__(self, merged_dir: Optional[str | Path] = None) -> None:
        self.merged_dir: Path = Path(merged_dir or CFG.MERGED_DIR)
        self.merged_dir.mkdir(parents=True, exist_ok=True)
        self._report_lines: List[str] = []
        logger.info("IntegrationPipeline initialised → output dir: %s", self.merged_dir)

    # ------------------------------------------------------------------
    # Public entry-point
    # ------------------------------------------------------------------

    def run(self, engineered: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Execute the full integration pipeline and return the master DataFrame.

        Parameters
        ----------
        engineered : dict[str, pd.DataFrame]
            Mapping produced by the feature-engineering stage.  Expected keys:
            ``"transport"``, ``"electricity"``, ``"food"``, ``"waste"``,
            ``"country_context"``, ``"behavior"``.

        Returns
        -------
        pd.DataFrame
            Master user-level DataFrame with all features joined.

        Raises
        ------
        KeyError
            If a required dataset key is absent from *engineered*.
        """
        self._report_lines.clear()
        self._log_report("=" * 70)
        self._log_report("INTEGRATION PIPELINE REPORT")
        self._log_report("=" * 70)

        # Stage 1 – country × year panel
        country_year = self._build_country_year_base(engineered)
        country_year = self._attach_food(country_year, engineered)
        self._log_report(
            f"[country_year] shape after food join: {country_year.shape}"
        )

        # Stage 2 – user base
        user_base = self._build_user_base(engineered)
        self._log_report(f"[user_base] shape after transport+behavior: {user_base.shape}")

        # Stage 3 – attach country context to users
        master = self._attach_country_context_to_users(user_base, country_year, engineered)
        master = self._add_user_country(master, engineered)
        master = self._final_cleanup(master)
        self._log_report(f"[master] final shape: {master.shape}")

        # Stage 4 – persist
        self._save_outputs(country_year, master, engineered)
        self._write_report()

        logger.info("IntegrationPipeline complete — master shape: %s", master.shape)
        return master

    # ------------------------------------------------------------------
    # Stage builders
    # ------------------------------------------------------------------

    def _build_country_year_base(
        self, engineered: Dict[str, pd.DataFrame]
    ) -> pd.DataFrame:
        """Merge electricity, waste, and country_context into a country-year panel.

        Parameters
        ----------
        engineered : dict[str, pd.DataFrame]
            Full engineered feature dictionary.

        Returns
        -------
        pd.DataFrame
            Country × year panel with electricity + waste + context columns.

        Notes
        -----
        The merge key is ``["country", "year"]``.  All three datasets must
        contain both columns; a ``KeyError`` is raised otherwise.
        """
        self._log_report("[stage 1] Building country-year base …")

        electricity = engineered.get("electricity")
        waste = engineered.get("waste")
        context = engineered.get("country_context")

        for name, df in [("electricity", electricity), ("waste", waste), ("country_context", context)]:
            if df is None:
                raise KeyError(
                    f"IntegrationPipeline._build_country_year_base: "
                    f"'{name}' key missing from engineered dict."
                )
            validate_dataframe(df, name=name)

        merge_keys = ["country", "year"]
        base = safe_left_merge(
            electricity, waste,
            on=merge_keys,
            left_name="electricity",
            right_name="waste",
        )
        base = safe_left_merge(
            base, context,
            on=merge_keys,
            left_name="electricity+waste",
            right_name="country_context",
        )
        self._log_report(
            f"  electricity({electricity.shape}) + waste({waste.shape}) "
            f"+ context({context.shape}) → {base.shape}"
        )
        return base

    def _attach_food(
        self,
        country_year: pd.DataFrame,
        engineered: Dict[str, pd.DataFrame],
    ) -> pd.DataFrame:
        """Join food features onto the country-year panel.

        Parameters
        ----------
        country_year : pd.DataFrame
            Existing country × year panel.
        engineered : dict[str, pd.DataFrame]
            Full engineered feature dictionary.

        Returns
        -------
        pd.DataFrame
            country_year with food feature columns appended.
        """
        self._log_report("[stage 1b] Attaching food features …")
        food = engineered.get("food")
        if food is None:
            logger.warning("_attach_food: 'food' key absent — skipping food join.")
            return country_year

        validate_dataframe(food, name="food")
        result = safe_left_merge(
            country_year, food,
            on=["country", "year"],
            left_name="country_year",
            right_name="food",
        )
        self._log_report(f"  food({food.shape}) attached → {result.shape}")
        return result

    def _build_user_base(
        self, engineered: Dict[str, pd.DataFrame]
    ) -> pd.DataFrame:
        """Merge transport and behavior feature tables on user_id.

        Parameters
        ----------
        engineered : dict[str, pd.DataFrame]
            Full engineered feature dictionary.

        Returns
        -------
        pd.DataFrame
            User-level DataFrame with transport + behavior columns.

        Raises
        ------
        KeyError
            If ``"transport"`` is missing from *engineered*.
        """
        self._log_report("[stage 2] Building user base …")
        transport = engineered.get("transport")
        behavior = engineered.get("behavior")

        if transport is None:
            raise KeyError(
                "IntegrationPipeline._build_user_base: 'transport' key missing."
            )
        validate_dataframe(transport, name="transport")

        if behavior is None:
            logger.warning("_build_user_base: 'behavior' key absent — proceeding without it.")
            return transport.copy()

        validate_dataframe(behavior, name="behavior")
        user_base = safe_left_merge(
            transport, behavior,
            on="user_id",
            left_name="transport",
            right_name="behavior",
        )
        self._log_report(
            f"  transport({transport.shape}) + behavior({behavior.shape}) "
            f"→ {user_base.shape}"
        )
        return user_base

    def _attach_country_context_to_users(
        self,
        user_base: pd.DataFrame,
        country_year: pd.DataFrame,
        engineered: Dict[str, pd.DataFrame],
    ) -> pd.DataFrame:
        """Join the latest country-year snapshot to the user-level table.

        The latest available year for each country is selected from
        *country_year* before joining on the ``"country"`` column.

        Parameters
        ----------
        user_base : pd.DataFrame
            User-level DataFrame produced by :py:meth:`_build_user_base`.
        country_year : pd.DataFrame
            Country × year panel.
        engineered : dict[str, pd.DataFrame]
            Full engineered feature dictionary (unused here but kept for API
            consistency).

        Returns
        -------
        pd.DataFrame
            User table enriched with country-level features.
        """
        self._log_report("[stage 3] Attaching country context to users …")

        if "country" not in user_base.columns:
            logger.warning(
                "_attach_country_context_to_users: 'country' column absent "
                "from user_base — skipping country join."
            )
            return user_base

        if "year" not in country_year.columns:
            logger.warning(
                "_attach_country_context_to_users: 'year' column absent "
                "from country_year — skipping country join."
            )
            return user_base

        # Select the latest snapshot per country
        latest_country = (
            country_year
            .sort_values("year", ascending=False)
            .groupby("country", as_index=False)
            .first()
        )

        master = safe_left_merge(
            user_base, latest_country,
            on="country",
            left_name="user_base",
            right_name="country_year_latest",
        )
        self._log_report(
            f"  user_base({user_base.shape}) + country_year_latest"
            f"({latest_country.shape}) → {master.shape}"
        )
        return master

    def _add_user_country(
        self,
        master: pd.DataFrame,
        engineered: Dict[str, pd.DataFrame],
    ) -> pd.DataFrame:
        """Add a placeholder ``country`` column if one does not yet exist.

        Parameters
        ----------
        master : pd.DataFrame
            Current master DataFrame.
        engineered : dict[str, pd.DataFrame]
            Full engineered feature dictionary.

        Returns
        -------
        pd.DataFrame
            Master DataFrame guaranteed to have a ``"country"`` column.
        """
        if "country" not in master.columns:
            logger.info(
                "_add_user_country: 'country' column missing — adding NaN placeholder."
            )
            master = master.copy()
            master["country"] = pd.NA
        return master

    def _final_cleanup(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate columns, all-null columns, and reset the index.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to clean.

        Returns
        -------
        pd.DataFrame
            Cleaned DataFrame with a fresh integer index.

        Notes
        -----
        * Duplicate column names (keeping the first occurrence) are removed.
        * Columns where every value is null are dropped.
        * The index is reset and the old index column is discarded.
        """
        # Drop duplicate column names (keep first)
        duplicate_cols = df.columns[df.columns.duplicated(keep="first")].tolist()
        if duplicate_cols:
            logger.warning(
                "_final_cleanup: dropping %d duplicate column(s): %s",
                len(duplicate_cols), duplicate_cols,
            )
            df = df.loc[:, ~df.columns.duplicated(keep="first")]

        # Drop all-null columns
        all_null_cols = df.columns[df.isnull().all()].tolist()
        if "country" in all_null_cols:
            all_null_cols.remove("country")
            
        if all_null_cols:
            logger.warning(
                "_final_cleanup: dropping %d all-null column(s): %s",
                len(all_null_cols), all_null_cols,
            )
            df = df.drop(columns=all_null_cols)

        df = df.reset_index(drop=True)
        self._log_report(
            f"  After cleanup: {df.shape[1]} columns, {df.shape[0]} rows."
        )
        return df

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _save_outputs(
        self,
        country_year: pd.DataFrame,
        master: pd.DataFrame,
        engineered: Dict[str, pd.DataFrame],
    ) -> None:
        """Save country_year and master DataFrames as CSVs; write null summary.

        Parameters
        ----------
        country_year : pd.DataFrame
            Country × year panel.
        master : pd.DataFrame
            User-level master DataFrame.
        engineered : dict[str, pd.DataFrame]
            Full engineered feature dictionary (for per-domain null reporting).
        """
        cy_path = self.merged_dir / "country_year_panel.csv"
        master_path = self.merged_dir / "master_dataset.csv"

        save_csv(country_year, self.merged_dir, "country_year_panel.csv")
        save_csv(master, self.merged_dir, "master_dataset.csv")

        self._log_report(f"[output] country_year → {cy_path}")
        self._log_report(f"[output] master       → {master_path}")

        # Null summary for master
        null_pct = master.isnull().mean().mul(100).round(2)
        high_null = null_pct[null_pct > 20].sort_values(ascending=False)
        if not high_null.empty:
            self._log_report("\n[null_summary] Columns with > 20 % nulls in master:")
            for col, pct in high_null.items():
                self._log_report(f"  {col}: {pct:.1f}%")
        else:
            self._log_report("[null_summary] No columns exceed 20% nulls in master.")

        logger.info("Integration outputs saved → %s", self.merged_dir)

    # ------------------------------------------------------------------
    # Report helpers
    # ------------------------------------------------------------------

    def _log_report(self, line: str) -> None:
        """Append *line* to the in-memory integration report.

        Parameters
        ----------
        line : str
            Text line to append.
        """
        self._report_lines.append(line)
        logger.debug(line)

    def _write_report(self) -> None:
        """Flush the in-memory report to ``integration_report.txt``.

        The file is written to :py:attr:`merged_dir`.  Any existing file is
        overwritten.
        """
        report_path = self.merged_dir / "integration_report.txt"
        with open(report_path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(self._report_lines))
        logger.info("Integration report written → %s", report_path)
