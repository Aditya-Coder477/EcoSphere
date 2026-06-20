"""
pipeline.py
===========
Main entry point for the Carbon Footprint Awareness Platform pipeline.

Orchestrates the three major stages:
    1. **Cleaning**  – raw data ingestion and validation.
    2. **Feature Engineering** – domain-specific feature builders.
    3. **Integration** – cross-domain merge into a master dataset.

Run from the project root::

    python pipeline.py --stage all --verbose

Usage
-----
    python pipeline.py [--stage {clean,features,all}] [--verbose]

Stages
------
clean
    Only run data loading and cleaning.
features
    Run cleaning then feature engineering.
all (default)
    Run the full pipeline including integration.
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# sys.path bootstrap — ensure the project root is importable regardless of
# where the script is invoked from.
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# ---------------------------------------------------------------------------
# Project imports
# ---------------------------------------------------------------------------
from config import CFG  # noqa: E402
from src.utils.logger import get_logger  # noqa: E402
from src.utils.io_utils import save_csv  # noqa: E402

# Cleaning
from src.cleaning.loader import DatasetLoader  # noqa: E402
from src.cleaning.cleaner import CleaningPipeline  # noqa: E402

# Feature engineering
from src.feature_engineering.transport_features import build_transport_features  # noqa: E402
from src.feature_engineering.electricity_features import build_electricity_features  # noqa: E402
from src.feature_engineering.food_features import build_food_features  # noqa: E402
from src.feature_engineering.waste_features import build_waste_features  # noqa: E402
from src.feature_engineering.context_features import build_country_context_features, build_behavior_features  # noqa: E402

# Integration
from src.integration.merger import IntegrationPipeline  # noqa: E402
from src.integration.lineage import LineageTracker  # noqa: E402

import pandas as pd  # noqa: E402

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Maps human-readable category labels to the master-dataset column names
#: used when computing per-category emission breakdowns.
EMISSION_COLS: dict[str, str] = {
    "Transport": "annual_transport_emission_kg_co2e",
    "Electricity": "electricity_emission_kg_co2e_per_capita",
    "Food": "food_emission_kg_co2e_per_capita_per_year",
    "Waste": "waste_emission_kg_co2e_per_capita_per_year",
}

# ---------------------------------------------------------------------------
# Stage 1 – Cleaning
# ---------------------------------------------------------------------------


def run_cleaning() -> dict:
    """Load raw datasets and apply the full cleaning pipeline.

    Instantiates :class:`~src.cleaning.loader.DatasetLoader` to read all
    configured raw files, then passes the result through
    :class:`~src.cleaning.pipeline.CleaningPipeline` which handles
    deduplication, type coercion, missing-value imputation, and validation.

    Returns
    -------
    dict[str, pd.DataFrame]
        Mapping from dataset name (e.g. ``"transport_survey"``) to its
        cleaned DataFrame.

    Raises
    ------
    RuntimeError
        Re-raised from the loader or cleaning pipeline on fatal errors.
    """
    logger.info("── Stage 1: Data Cleaning ──────────────────────────────────")
    t0 = time.perf_counter()

    loader = DatasetLoader()
    raw = loader.load_all()
    logger.info("Loaded %d raw dataset(s).", len(raw))

    cleaner = CleaningPipeline()
    cleaned = cleaner.run_all(raw)
    logger.info(
        "Cleaning complete in %.2f s — %d dataset(s) produced.",
        time.perf_counter() - t0, len(cleaned),
    )
    return cleaned


# ---------------------------------------------------------------------------
# Stage 2 – Feature Engineering
# ---------------------------------------------------------------------------


def run_feature_engineering(cleaned: dict) -> dict:
    logger.info("── Stage 2: Feature Engineering ────────────────────────────")
    t0 = time.perf_counter()

    engineered_dir = Path(CFG.ENGINEERED_DIR)
    engineered_dir.mkdir(parents=True, exist_ok=True)

    engineered: dict[str, pd.DataFrame] = {}

    def _safe_build(domain_key: str, build_fn, **kwargs) -> None:
        builder_t0 = time.perf_counter()
        try:
            # Check if required kwargs (not None) are present
            # We assume a kwarg is required if it's passed here (optional ones will be handled gracefully if missing inside)
            df = build_fn(**kwargs)
            if df is None or df.empty:
                logger.warning("Feature builder '%s' returned an empty DataFrame — skipping.", domain_key)
                return

            out_path = engineered_dir / f"{domain_key}_features.csv"
            save_csv(df, engineered_dir, f"{domain_key}_features.csv")
            engineered[domain_key] = df
            logger.info("  %-16s → %s rows × %s cols | %.2f s | saved → %s",
                        domain_key, df.shape[0], df.shape[1],
                        time.perf_counter() - builder_t0, out_path)
        except Exception as exc:
            logger.warning("Feature builder '%s' raised %s: %s", domain_key, type(exc).__name__, exc, exc_info=True)

    if "transport_activity" in cleaned and "transport_factors" in cleaned:
        _safe_build("transport", build_transport_features, transport_df=cleaned["transport_activity"], factors_df=cleaned["transport_factors"])
    
    if "electricity_mix" in cleaned:
        _safe_build("electricity", build_electricity_features, electricity_df=cleaned["electricity_mix"], energy_per_capita_df=cleaned.get("energy_per_capita"))
    
    if "food_supply" in cleaned and "food_ghg_factors" in cleaned:
        _safe_build("food", build_food_features, food_supply_df=cleaned["food_supply"], food_ghg_factors_df=cleaned["food_ghg_factors"])
    
    if "waste" in cleaned:
        _safe_build("waste", build_waste_features, waste_df=cleaned["waste"])
    
    if "gdp_per_capita" in cleaned and "hdi" in cleaned and "co2_per_capita" in cleaned:
        _safe_build("country_context", build_country_context_features, 
                    gdp_df=cleaned["gdp_per_capita"], hdi_df=cleaned["hdi"], co2_df=cleaned["co2_per_capita"],
                    electricity_access_df=cleaned.get("electricity_access"), 
                    literacy_df=cleaned.get("literacy"), 
                    population_df=cleaned.get("population"))
    
    if "behavior" in cleaned:
        _safe_build("behavior", build_behavior_features, behavior_df=cleaned["behavior"])

    logger.info("Feature engineering complete in %.2f s — %d domain(s) produced.", time.perf_counter() - t0, len(engineered))
    return engineered


# ---------------------------------------------------------------------------
# Stage 3 – Integration
# ---------------------------------------------------------------------------


def run_integration(engineered: dict) -> pd.DataFrame:
    """Merge engineered feature tables and export lineage metadata.

    Delegates to :class:`~src.integration.merger.IntegrationPipeline` for
    the cross-domain join, then serialises the
    :class:`~src.integration.lineage.LineageTracker` registry to both JSON
    and CSV so that every feature's provenance is recorded alongside the
    output data.

    Parameters
    ----------
    engineered : dict[str, pd.DataFrame]
        Output of :func:`run_feature_engineering`.

    Returns
    -------
    pd.DataFrame
        Master dataset produced by the integration pipeline.
    """
    logger.info("── Stage 3: Integration ────────────────────────────────────")
    t0 = time.perf_counter()

    # Run merge pipeline
    pipeline = IntegrationPipeline()
    master = pipeline.run(engineered)

    # Export feature lineage
    tracker = LineageTracker()
    reports_dir = Path(CFG.MERGED_DIR) / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    lineage_json = tracker.save(output_dir=reports_dir, filename="feature_lineage.json")
    logger.info("Lineage JSON → %s", lineage_json)

    lineage_csv_path = reports_dir / "feature_lineage.csv"
    lineage_df = tracker.to_dataframe()
    save_csv(lineage_df, reports_dir, "feature_lineage.csv")
    logger.info("Lineage CSV  → %s", lineage_csv_path)

    logger.info(
        "Integration complete in %.2f s — master shape: %s.",
        time.perf_counter() - t0, master.shape,
    )
    return master


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Options
    -------
    --stage : {clean, features, all}
        Pipeline stage to execute (default: ``all``).
    --verbose
        Enable DEBUG-level logging when set.

    Returns
    -------
    argparse.Namespace
        Parsed argument namespace.
    """
    parser = argparse.ArgumentParser(
        prog="pipeline",
        description=(
            "Carbon Footprint Awareness Platform – main pipeline runner.\n"
            "Stages: clean → feature engineering → integration."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--stage",
        choices=["clean", "features", "all"],
        default="all",
        help=(
            "Pipeline stage to run.  "
            "'clean' stops after cleaning; "
            "'features' stops after feature engineering; "
            "'all' runs the full pipeline (default)."
        ),
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=False,
        help="Enable DEBUG-level log output.",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Execute the pipeline according to the selected stage.

    Flow
    ----
    1. Parse CLI arguments and configure logging level.
    2. Run :func:`run_cleaning`.
    3. If ``--stage`` is ``features`` or ``all``, run
       :func:`run_feature_engineering`.
    4. If ``--stage`` is ``all``, run :func:`run_integration`.
    5. Log overall wall-clock time.

    Exit Codes
    ----------
    0
        Pipeline completed successfully.
    1
        An unrecoverable error occurred (logged before exit).
    """
    args = parse_args()

    # Configure root logging level
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    wall_t0 = time.perf_counter()
    logger.info("Carbon Footprint Platform pipeline started (stage=%s).", args.stage)

    try:
        # ── Stage 1: Cleaning ──────────────────────────────────────────
        cleaned = run_cleaning()

        if args.stage == "clean":
            logger.info("Stage 'clean' complete.  Exiting.")
            _log_elapsed(wall_t0)
            return

        # ── Stage 2: Feature Engineering ──────────────────────────────
        engineered = run_feature_engineering(cleaned)

        if args.stage == "features":
            logger.info("Stage 'features' complete.  Exiting.")
            _log_elapsed(wall_t0)
            return

        # ── Stage 3: Integration ───────────────────────────────────────
        master = run_integration(engineered)
        logger.info(
            "Pipeline complete — master dataset: %d rows × %d cols.",
            *master.shape,
        )

    except Exception as exc:  # noqa: BLE001
        logger.critical(
            "Pipeline failed with %s: %s", type(exc).__name__, exc, exc_info=True
        )
        sys.exit(1)

    _log_elapsed(wall_t0)


def _log_elapsed(t0: float) -> None:
    """Log the elapsed wall-clock time since *t0* (in seconds).

    Parameters
    ----------
    t0 : float
        Start timestamp from :func:`time.perf_counter`.
    """
    elapsed = time.perf_counter() - t0
    minutes, seconds = divmod(elapsed, 60)
    logger.info("Total wall-clock time: %d m %.2f s.", int(minutes), seconds)


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    main()
