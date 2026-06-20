"""
config.py
=========
Central, non-secret configuration for the Carbon Footprint Platform pipeline.

All secrets (API keys, tokens, credentials) MUST be provided via environment
variables — never hard-coded here.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List

_HERE: Path = Path(__file__).resolve().parent
_DEFAULT_RAW: Path = _HERE / "datasets" / "raw"


@dataclass(frozen=True)
class PipelineConfig:
    """Immutable configuration for the full ETL pipeline."""

    RAW_DATA_DIR: Path = field(
        default_factory=lambda: Path(
            os.environ.get("RAW_DATA_DIR", str(_DEFAULT_RAW))
        ).resolve()
    )
    CLEANED_DIR: Path = field(
        default_factory=lambda: Path(
            os.environ.get("CLEANED_DIR", str(_HERE / "datasets" / "cleaned"))
        ).resolve()
    )
    ENGINEERED_DIR: Path = field(
        default_factory=lambda: Path(
            os.environ.get("ENGINEERED_DIR", str(_HERE / "datasets" / "engineered"))
        ).resolve()
    )
    MERGED_DIR: Path = field(
        default_factory=lambda: Path(
            os.environ.get("MERGED_DIR", str(_HERE / "datasets" / "merged"))
        ).resolve()
    )
    LOGS_DIR: Path = field(
        default_factory=lambda: Path(
            os.environ.get("LOGS_DIR", str(_HERE / "logs"))
        ).resolve()
    )

    SOURCE_PATHS: Dict[str, str] = field(
        default_factory=lambda: {
            "transport_factors": "Carbon_Factors/transport_emission_factors_synthetic.csv",
            "ghg_factors_xlsx": "Carbon_Factors/ghg-emission-factors-hub-2025.xlsx",
            "transport_activity": "User_Activity_Data/Transport/transport_activity_synthetic.csv",
            "electricity_mix": "User_Activity_Data/Electricity/electricity_mix_synthetic.csv",
            "waste": "User_Activity_Data/Waste/waste_synthetic.csv",
            "food_supply": (
                "User_Activity_Data/Food & Diet Dataset/"
                "Supply_Utilization_Accounts_Food_and_Diet_E_All_Data.csv"
            ),
            "food_ghg_factors": (
                "User_Activity_Data/Food & Diet Dataset/"
                "greenhouse-gas-emissions-per-kilogram-of-food-product/"
                "greenhouse-gas-emissions-per-kilogram-of-food-product.csv"
            ),
            "gdp_per_capita": (
                "Country_Context/Economy/gdp-per-capita-maddison-project-database/"
                "gdp-per-capita-maddison-project-database.csv"
            ),
            "hdi": (
                "Country_Context/Economy/human-development-index/"
                "human-development-index.csv"
            ),
            "co2_per_capita": (
                "Country_Context/Environment/co-emissions-per-capita/"
                "co-emissions-per-capita.csv"
            ),
            "literacy": (
                "Country_Context/Education/cross-country-literacy-rates/"
                "cross-country-literacy-rates.csv"
            ),
            "electricity_access": (
                "Country_Context/Living_Conditions/"
                "share-of-the-population-with-access-to-electricity/"
                "share-of-the-population-with-access-to-electricity.csv"
            ),
            "behavior": "Behavior_and_Recommendation/behavior_synthetic.csv",
        }
    )

    MAX_NULL_FRACTION: float = 0.60
    VALID_YEAR_MIN: int = 2000
    VALID_YEAR_MAX: int = 2030
    MAX_EMISSION_KG_CO2E: float = 200_000.0
    MIN_GRID_INTENSITY: float = 0.0
    MAX_GRID_INTENSITY: float = 2.0
    COUNTRY_YEAR_KEYS: List[str] = field(default_factory=lambda: ["country", "year"])
    USER_KEY: str = "user_id"
    MASTER_DATASET_FILENAME: str = "master_dataset.csv"
    PIPELINE_REPORT_FILENAME: str = "pipeline_report.txt"
    LINEAGE_FILENAME: str = "feature_lineage.json"
    DATA_DICT_FILENAME: str = "data_dictionary.csv"


CFG = PipelineConfig()
