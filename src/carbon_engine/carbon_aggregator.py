"""
carbon_aggregator.py
====================
Aggregates category emissions into a unified footprint report.
"""

from typing import Dict, Any

from .schemas import CategoryEmission, FootprintReport
from .carbon_report import CarbonReportBuilder


class CarbonFootprintAggregator:
    """Aggregates multiple CategoryEmissions into a final footprint."""
    
    def __init__(self):
        self.report_builder = CarbonReportBuilder()

    def aggregate(self, user_id: str, emissions: Dict[str, CategoryEmission]) -> FootprintReport:
        """
        Takes a dict of category emissions (e.g., {'transport': t_em, 'food': f_em})
        and returns a complete FootprintReport.
        """
        total_co2e = sum(cat.emissions_kg_co2e for cat in emissions.values())
        
        shares = {}
        if total_co2e > 0:
            for cat_name, cat_em in emissions.items():
                shares[cat_name] = (cat_em.emissions_kg_co2e / total_co2e) * 100.0
        else:
            for cat_name in emissions.keys():
                shares[cat_name] = 0.0

        dominant_source = "None"
        if total_co2e > 0:
            dominant_source = max(shares.items(), key=lambda x: x[1])[0]

        # Use the builder to attach human readable insights and recommendation hooks
        human_readable = self.report_builder.build_human_readable_summary(dominant_source, total_co2e, shares)
        hooks = self.report_builder.build_recommendation_hooks(dominant_source, shares)

        return FootprintReport(
            user_id=user_id,
            total_emissions_kg_co2e=total_co2e,
            category_emissions=emissions,
            dominant_source=dominant_source,
            category_shares_pct=shares,
            human_readable_summary=human_readable,
            recommendation_hooks=hooks
        )
