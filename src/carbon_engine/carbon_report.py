"""
carbon_report.py
================
Builds human-readable insights and recommendation hooks from footprint data.
"""

from typing import Dict, Any

class CarbonReportBuilder:
    """Helper to convert structured emissions into insights."""

    def build_human_readable_summary(self, dominant_source: str, total_co2e: float, shares: Dict[str, float]) -> str:
        """
        Generate a simple text summary for non-technical users.
        """
        if total_co2e == 0:
            return "No emission data available to calculate a footprint."

        lines = [f"Your estimated annual carbon footprint is {total_co2e:,.1f} kg CO2e."]
        
        if dominant_source != "None":
            pct = shares.get(dominant_source, 0)
            
            if dominant_source == "transport":
                lines.append(f"Transport is your largest emission source ({pct:.1f}%). Consider carpooling, public transit, or electric vehicles.")
            elif dominant_source == "food":
                lines.append(f"Food is your largest emission source ({pct:.1f}%). A shift towards a plant-based diet could significantly reduce your footprint.")
            elif dominant_source == "electricity":
                lines.append(f"Electricity is your largest emission source ({pct:.1f}%). This might be due to a fossil-heavy local energy grid.")
            elif dominant_source == "waste":
                lines.append(f"Waste is your largest emission source ({pct:.1f}%). Increasing your recycling and composting rates can help.")
            else:
                lines.append(f"Your largest emission source is {dominant_source} ({pct:.1f}%).")

        return " ".join(lines)

    def build_recommendation_hooks(self, dominant_source: str, shares: Dict[str, float]) -> Dict[str, Any]:
        """
        Provide structured hints for the recommendation engine.
        """
        return {
            "primary_focus_area": dominant_source,
            "target_reductions": {
                cat: {"suggest_action": share > 20.0} for cat, share in shares.items()
            }
        }
