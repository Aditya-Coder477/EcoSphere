"""
lineage.py
==========
Feature lineage tracking module for the Carbon Footprint Awareness Platform.

Tracks the provenance, formula, unit, and metadata of every engineered feature
produced across the pipeline so that outputs are fully auditable and reproducible.

Classes
-------
FeatureRecord
    Lightweight dataclass describing one engineered feature.
LineageTracker
    Registry that stores, queries, and serialises FeatureRecord objects.

Usage
-----
>>> from src.integration.lineage import LineageTracker
>>> tracker = LineageTracker()
>>> rec = tracker.get("annual_transport_emission_kg_co2e")
>>> df  = tracker.to_dataframe()
>>> path = tracker.save(output_dir="outputs/reports")
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import List, Optional

import pandas as pd

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class FeatureRecord:
    """Describes a single engineered feature and its lineage.

    Parameters
    ----------
    feature_name : str
        Canonical column name used throughout the pipeline.
    source_datasets : list[str]
        Names of raw datasets the feature derives from.
    formula : str
        Human-readable description of how the feature is computed.
    module : str
        Python module (dot-path) that produces this feature.
    unit : str
        Physical or logical unit of the feature value.
    description : str
        Plain-language explanation of what the feature represents.
    category : str
        High-level domain bucket (e.g. "transport", "electricity", "food").
    is_derived : bool
        True when the feature is computed from other columns (default True).
    is_raw : bool
        True when the feature is directly ingested from a source dataset.
    notes : str or None
        Any caveats, known data-quality issues, or implementation notes.
    """

    feature_name: str
    source_datasets: List[str]
    formula: str
    module: str
    unit: str
    description: str
    category: str
    is_derived: bool = True
    is_raw: bool = False
    notes: Optional[str] = None


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

class LineageTracker:
    """Registry of FeatureRecord objects for all pipeline features.

    On instantiation the tracker immediately pre-populates itself with every
    known engineered feature via :py:meth:`_register_known_features`.  Callers
    can add or overwrite records at any time with :py:meth:`register`.

    Parameters
    ----------
    None

    Attributes
    ----------
    _registry : dict[str, FeatureRecord]
        Internal mapping from ``feature_name`` to its :py:class:`FeatureRecord`.

    Examples
    --------
    >>> tracker = LineageTracker()
    >>> rec = tracker.get("annual_transport_emission_kg_co2e")
    >>> print(rec.unit)
    kg CO2e / person / year
    """

    def __init__(self) -> None:
        self._registry: dict[str, FeatureRecord] = {}
        self._register_known_features()
        logger.info(
            "LineageTracker initialised with %d pre-registered features.",
            len(self._registry),
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def register(
        self,
        feature_name: str,
        source_datasets: List[str],
        formula: str,
        module: str,
        unit: str,
        description: str,
        category: str,
        is_derived: bool = True,
        is_raw: bool = False,
        notes: Optional[str] = None,
    ) -> FeatureRecord:
        """Add or update a feature record in the registry.

        Parameters
        ----------
        feature_name : str
            Canonical column name.
        source_datasets : list[str]
            Names of raw source datasets.
        formula : str
            Computation formula (human-readable).
        module : str
            Dot-path to the producing module.
        unit : str
            Physical or logical unit.
        description : str
            Plain-language description.
        category : str
            Domain category (e.g. "transport", "food").
        is_derived : bool, optional
            Whether this is a derived feature (default ``True``).
        is_raw : bool, optional
            Whether this is a raw ingested column (default ``False``).
        notes : str or None, optional
            Extra implementation notes.

        Returns
        -------
        FeatureRecord
            The newly stored record.
        """
        record = FeatureRecord(
            feature_name=feature_name,
            source_datasets=source_datasets,
            formula=formula,
            module=module,
            unit=unit,
            description=description,
            category=category,
            is_derived=is_derived,
            is_raw=is_raw,
            notes=notes,
        )
        if feature_name in self._registry:
            logger.debug("LineageTracker: overwriting record for '%s'.", feature_name)
        self._registry[feature_name] = record
        return record

    def get(self, feature_name: str) -> Optional[FeatureRecord]:
        """Return the FeatureRecord for *feature_name*, or ``None`` if absent.

        Parameters
        ----------
        feature_name : str
            The canonical column name to look up.

        Returns
        -------
        FeatureRecord or None
        """
        return self._registry.get(feature_name)

    def all_records(self) -> List[FeatureRecord]:
        """Return a list of all registered FeatureRecord objects.

        Returns
        -------
        list[FeatureRecord]
            Ordered by insertion order (Python 3.7+ dict guarantee).
        """
        return list(self._registry.values())

    def to_dataframe(self) -> pd.DataFrame:
        """Serialise the registry to a tidy pandas DataFrame.

        Each row corresponds to one :py:class:`FeatureRecord`.  The
        ``source_datasets`` column contains JSON-serialised lists so that the
        DataFrame can be saved directly to CSV without losing structure.

        Returns
        -------
        pd.DataFrame
            One row per feature, columns matching FeatureRecord fields.
        """
        rows = [asdict(r) for r in self._registry.values()]
        if not rows:
            return pd.DataFrame()
        df = pd.DataFrame(rows)
        # Serialise list column for flat CSV compatibility
        df["source_datasets"] = df["source_datasets"].apply(json.dumps)
        return df

    def save(
        self,
        output_dir: str | Path,
        filename: str = "feature_lineage.json",
    ) -> Path:
        """Serialise the registry to a JSON file.

        Parameters
        ----------
        output_dir : str or Path
            Directory in which to write the file (created if absent).
        filename : str, optional
            Output filename (default ``"feature_lineage.json"``).

        Returns
        -------
        Path
            Absolute path to the written file.

        Raises
        ------
        OSError
            If the directory cannot be created or the file cannot be written.
        """
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / filename

        payload = {
            "feature_count": len(self._registry),
            "features": {name: asdict(rec) for name, rec in self._registry.items()},
        }

        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, default=str)

        logger.info("LineageTracker: saved %d records → %s", len(self._registry), out_path)
        return out_path

    # ------------------------------------------------------------------
    # Pre-population
    # ------------------------------------------------------------------

    def _register_known_features(self) -> None:  # noqa: C901
        """Pre-populate the registry with all known pipeline features.

        Covers features from every domain module:
        transport, electricity, food, waste, country-context, behaviour, and
        master/integration features.  At least 30 features are registered.
        """

        # ── TRANSPORT ──────────────────────────────────────────────────
        self.register(
            feature_name="annual_transport_emission_kg_co2e",
            source_datasets=["transport_survey"],
            formula=(
                "sum(distance_km * emission_factor_kg_co2e_per_km * trips_per_year) "
                "grouped by user_id"
            ),
            module="src.features.transport_features",
            unit="kg CO2e / person / year",
            description=(
                "Total annual greenhouse-gas emissions from all personal transport "
                "modes recorded in the survey (car, bus, rail, cycling, walking)."
            ),
            category="transport",
        )

        self.register(
            feature_name="commute_intensity_kg_co2e_per_km",
            source_datasets=["transport_survey"],
            formula=(
                "annual_transport_emission_kg_co2e / total_annual_distance_km"
            ),
            module="src.features.transport_features",
            unit="kg CO2e / km",
            description=(
                "Emission intensity per kilometre travelled; higher values indicate "
                "carbon-heavy transport choices."
            ),
            category="transport",
            notes="Set to NaN when total_annual_distance_km == 0.",
        )

        self.register(
            feature_name="is_low_carbon_commuter",
            source_datasets=["transport_survey"],
            formula=(
                "1 if commute_intensity_kg_co2e_per_km < LOW_CARBON_THRESHOLD else 0"
            ),
            module="src.features.transport_features",
            unit="binary flag",
            description=(
                "Binary indicator: 1 if the user's transport emission intensity "
                "falls below the low-carbon threshold (configurable in CFG)."
            ),
            category="transport",
        )

        self.register(
            feature_name="flight_emission_share_pct",
            source_datasets=["transport_survey"],
            formula=(
                "flight_emission_kg_co2e / annual_transport_emission_kg_co2e * 100"
            ),
            module="src.features.transport_features",
            unit="percent",
            description=(
                "Proportion of annual transport emissions attributable to flights; "
                "useful for identifying frequent flyers."
            ),
            category="transport",
            notes="0.0 for users with no recorded flights.",
        )

        # ── ELECTRICITY ────────────────────────────────────────────────
        self.register(
            feature_name="electricity_emission_kg_co2e_per_capita",
            source_datasets=["electricity_generation", "world_population"],
            formula=(
                "total_electricity_ghg_kt_co2e * 1000 / population"
            ),
            module="src.features.electricity_features",
            unit="kg CO2e / person / year",
            description=(
                "Per-capita annual CO₂-equivalent emissions from the national "
                "electricity generation mix."
            ),
            category="electricity",
        )

        self.register(
            feature_name="fossil_share_pct",
            source_datasets=["electricity_generation"],
            formula=(
                "(coal_twh + oil_twh + gas_twh) / total_generation_twh * 100"
            ),
            module="src.features.electricity_features",
            unit="percent",
            description="Share of electricity generation from fossil fuel sources.",
            category="electricity",
        )

        self.register(
            feature_name="clean_share_pct",
            source_datasets=["electricity_generation"],
            formula=(
                "(nuclear_twh + hydro_twh + wind_twh + solar_twh + other_renewables_twh) "
                "/ total_generation_twh * 100"
            ),
            module="src.features.electricity_features",
            unit="percent",
            description=(
                "Share of electricity generation from low- or zero-carbon sources "
                "(nuclear + all renewables)."
            ),
            category="electricity",
        )

        self.register(
            feature_name="grid_intensity_tier",
            source_datasets=["electricity_generation"],
            formula=(
                "pd.cut(electricity_emission_kg_co2e_per_capita, bins=CFG.GRID_TIER_BINS, "
                "labels=['very_clean','clean','moderate','dirty','very_dirty'])"
            ),
            module="src.features.electricity_features",
            unit="ordinal category",
            description=(
                "Five-tier label for grid carbon intensity derived from "
                "electricity_emission_kg_co2e_per_capita."
            ),
            category="electricity",
        )

        self.register(
            feature_name="renewable_adoption_potential",
            source_datasets=["electricity_generation"],
            formula="100 - clean_share_pct",
            module="src.features.electricity_features",
            unit="percent",
            description=(
                "Headroom for expanding renewable/clean energy; complement of "
                "clean_share_pct."
            ),
            category="electricity",
        )

        # ── FOOD ───────────────────────────────────────────────────────
        self.register(
            feature_name="food_emission_kg_co2e_per_capita_per_year",
            source_datasets=["food_supply", "food_emission_factors"],
            formula=(
                "sum(food_supply_kg_per_capita * ghg_factor_kg_co2e_per_kg) "
                "across all food categories"
            ),
            module="src.features.food_features",
            unit="kg CO2e / person / year",
            description=(
                "Estimated annual dietary greenhouse-gas footprint per capita, "
                "computed by multiplying per-capita food supply by category-level "
                "lifecycle emission factors."
            ),
            category="food",
        )

        self.register(
            feature_name="weighted_avg_food_ghg_factor",
            source_datasets=["food_supply", "food_emission_factors"],
            formula=(
                "food_emission_kg_co2e_per_capita_per_year / total_food_supply_kg_per_capita"
            ),
            module="src.features.food_features",
            unit="kg CO2e / kg food",
            description=(
                "Supply-weighted average emission factor across all consumed food "
                "categories; reflects overall diet composition."
            ),
            category="food",
        )

        self.register(
            feature_name="diet_carbon_intensity_tier",
            source_datasets=["food_supply", "food_emission_factors"],
            formula=(
                "pd.cut(food_emission_kg_co2e_per_capita_per_year, "
                "bins=CFG.DIET_TIER_BINS, labels=['very_low','low','medium','high','very_high'])"
            ),
            module="src.features.food_features",
            unit="ordinal category",
            description=(
                "Five-tier carbon intensity label for national diet patterns, "
                "binned from food_emission_kg_co2e_per_capita_per_year."
            ),
            category="food",
        )

        self.register(
            feature_name="high_meat_diet_flag",
            source_datasets=["food_supply"],
            formula=(
                "1 if (beef_supply_kg + sheep_supply_kg + pork_supply_kg) "
                "> CFG.HIGH_MEAT_THRESHOLD_KG else 0"
            ),
            module="src.features.food_features",
            unit="binary flag",
            description=(
                "Binary flag raised when combined red-meat supply per capita "
                "exceeds the configurable high-meat threshold."
            ),
            category="food",
        )

        # ── WASTE ──────────────────────────────────────────────────────
        self.register(
            feature_name="waste_emission_kg_co2e_per_capita_per_year",
            source_datasets=["waste_management", "world_population"],
            formula=(
                "total_waste_ghg_kt_co2e * 1e6 / population"
            ),
            module="src.features.waste_features",
            unit="kg CO2e / person / year",
            description=(
                "Per-capita annual GHG emissions from the full waste management "
                "chain (collection, treatment, disposal)."
            ),
            category="waste",
        )

        self.register(
            feature_name="landfill_emission_kg_co2e_per_capita_per_year",
            source_datasets=["waste_management", "world_population"],
            formula=(
                "landfill_ghg_kt_co2e * 1e6 / population"
            ),
            module="src.features.waste_features",
            unit="kg CO2e / person / year",
            description=(
                "Portion of waste_emission attributable specifically to landfill "
                "disposal; key driver of methane emissions."
            ),
            category="waste",
        )

        self.register(
            feature_name="waste_diversion_rate_pct",
            source_datasets=["waste_management"],
            formula=(
                "(recycled_kt + composted_kt + recovered_kt) / total_waste_kt * 100"
            ),
            module="src.features.waste_features",
            unit="percent",
            description=(
                "Proportion of total waste diverted from landfill through "
                "recycling, composting, or energy recovery."
            ),
            category="waste",
        )

        self.register(
            feature_name="waste_management_tier",
            source_datasets=["waste_management"],
            formula=(
                "pd.cut(waste_diversion_rate_pct, bins=CFG.WASTE_TIER_BINS, "
                "labels=['poor','developing','moderate','good','excellent'])"
            ),
            module="src.features.waste_features",
            unit="ordinal category",
            description=(
                "Five-tier label for national waste management performance "
                "derived from waste_diversion_rate_pct."
            ),
            category="waste",
        )

        self.register(
            feature_name="recycling_potential_score",
            source_datasets=["waste_management"],
            formula="100 - waste_diversion_rate_pct",
            module="src.features.waste_features",
            unit="score (0–100)",
            description=(
                "Headroom for improving waste diversion; complement of "
                "waste_diversion_rate_pct."
            ),
            category="waste",
        )

        # ── COUNTRY CONTEXT ────────────────────────────────────────────
        self.register(
            feature_name="gdp_log",
            source_datasets=["country_context"],
            formula="np.log1p(gdp_per_capita_usd)",
            module="src.features.context_features",
            unit="log(USD + 1)",
            description=(
                "Natural log-transform of GDP per capita (USD); reduces right "
                "skew and improves linear model performance."
            ),
            category="country_context",
        )

        self.register(
            feature_name="gdp_tier",
            source_datasets=["country_context"],
            formula=(
                "pd.cut(gdp_per_capita_usd, bins=CFG.GDP_TIER_BINS, "
                "labels=['low','lower_middle','upper_middle','high'])"
            ),
            module="src.features.context_features",
            unit="ordinal category",
            description=(
                "World-Bank-style income group derived from GDP per capita (USD)."
            ),
            category="country_context",
        )

        self.register(
            feature_name="hdi_normalized",
            source_datasets=["country_context"],
            formula="(hdi - hdi.min()) / (hdi.max() - hdi.min())",
            module="src.features.context_features",
            unit="0–1 normalised score",
            description=(
                "Min-max normalised Human Development Index; enables comparisons "
                "across years with differing raw HDI ranges."
            ),
            category="country_context",
        )

        self.register(
            feature_name="emission_per_gdp_intensity",
            source_datasets=["country_context", "electricity_generation", "waste_management"],
            formula=(
                "total_country_ghg_kg_co2e_per_capita / gdp_per_capita_usd"
            ),
            module="src.features.context_features",
            unit="kg CO2e / USD",
            description=(
                "Carbon intensity of economic output; low values indicate a "
                "decoupling of prosperity from emissions."
            ),
            category="country_context",
        )

        self.register(
            feature_name="co2_country_percentile",
            source_datasets=["country_context"],
            formula=(
                "country_co2_per_capita.rank(pct=True) * 100"
            ),
            module="src.features.context_features",
            unit="percentile (0–100)",
            description=(
                "Global percentile rank of country CO₂ per capita within each "
                "year's cross-section."
            ),
            category="country_context",
        )

        self.register(
            feature_name="electricity_access_gap_pct",
            source_datasets=["country_context"],
            formula="100 - electricity_access_pct",
            module="src.features.context_features",
            unit="percent",
            description=(
                "Proportion of the population without reliable electricity access; "
                "limits ability to adopt electric alternatives."
            ),
            category="country_context",
        )

        # ── BEHAVIOUR ──────────────────────────────────────────────────
        self.register(
            feature_name="effort_score",
            source_datasets=["behavior_survey"],
            formula=(
                "sum(behaviour_weight * response_value) across all survey items, "
                "normalised to 0–100"
            ),
            module="src.features.behavior_features",
            unit="score (0–100)",
            description=(
                "Composite score quantifying individual climate-action effort "
                "derived from weighted survey responses."
            ),
            category="behaviour",
        )

        self.register(
            feature_name="digital_reach_score",
            source_datasets=["behavior_survey"],
            formula=(
                "platform_count * avg_daily_minutes / normalisation_constant"
            ),
            module="src.features.behavior_features",
            unit="score (0–100)",
            description=(
                "Estimated potential digital reach of a user for climate awareness "
                "campaigns based on social-media platform usage."
            ),
            category="behaviour",
        )

        self.register(
            feature_name="behavior_adoption_tier",
            source_datasets=["behavior_survey"],
            formula=(
                "pd.cut(effort_score, bins=CFG.EFFORT_TIER_BINS, "
                "labels=['passive','aware','engaged','advocate','champion'])"
            ),
            module="src.features.behavior_features",
            unit="ordinal category",
            description=(
                "Five-tier label categorising users by their climate-action "
                "engagement level."
            ),
            category="behaviour",
        )

        self.register(
            feature_name="green_readiness_index",
            source_datasets=["behavior_survey", "country_context"],
            formula=(
                "0.5 * effort_score_norm + 0.3 * hdi_normalized + "
                "0.2 * clean_share_pct_norm"
            ),
            module="src.features.behavior_features",
            unit="composite index (0–1)",
            description=(
                "Composite index combining individual effort, national development "
                "level, and grid cleanliness to estimate green transition readiness."
            ),
            category="behaviour",
        )

        # ── MASTER / INTEGRATION ───────────────────────────────────────
        self.register(
            feature_name="total_emission_kg_co2e",
            source_datasets=[
                "transport_survey",
                "electricity_generation",
                "food_supply",
                "waste_management",
            ],
            formula=(
                "annual_transport_emission_kg_co2e + "
                "electricity_emission_kg_co2e_per_capita + "
                "food_emission_kg_co2e_per_capita_per_year + "
                "waste_emission_kg_co2e_per_capita_per_year"
            ),
            module="src.integration.merger",
            unit="kg CO2e / person / year",
            description=(
                "Sum of all domain-level per-capita emission estimates; serves as "
                "the headline carbon footprint indicator."
            ),
            category="master",
        )

        self.register(
            feature_name="dominant_emission_source",
            source_datasets=[
                "transport_survey",
                "electricity_generation",
                "food_supply",
                "waste_management",
            ],
            formula=(
                "argmax(transport_emission, electricity_emission, "
                "food_emission, waste_emission)"
            ),
            module="src.integration.merger",
            unit="category label",
            description=(
                "Name of the emission domain contributing the largest share to "
                "total_emission_kg_co2e for each record."
            ),
            category="master",
            notes=(
                "Resolved at row level; useful for personalising communication "
                "campaigns."
            ),
        )

        logger.debug(
            "LineageTracker: %d features pre-registered.", len(self._registry)
        )
