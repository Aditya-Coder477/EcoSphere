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
            return "Congratulations on a zero-carbon footprint! Your choices are highly effective at minimizing emissions. Keep up the green lifestyle and inspire others to do the same."

        lines = [f"Your estimated annual carbon footprint is {total_co2e:,.1f} kg CO2e."]
        
        if dominant_source != "None":
            pct = shares.get(dominant_source, 0)
            
            if dominant_source == "transport":
                lines.append(f"Transport is your largest emission source ({pct:.1f}%). You can reduce this by swapping solo driving for carpooling, using public transit, walking/cycling for short trips, or transitioning to an EV.")
            elif dominant_source == "food":
                lines.append(f"Food is your largest emission source ({pct:.1f}%). Shifting towards a plant-based diet, reducing beef consumption, or avoiding food waste will make a significant impact.")
            elif dominant_source == "electricity":
                lines.append(f"Electricity is your largest emission source ({pct:.1f}%). Consider upgrading to LED lighting, adjusting thermostat settings by 1-2 degrees, or choosing a green utility tariff if available.")
            elif dominant_source == "waste":
                lines.append(f"Waste is your largest emission source ({pct:.1f}%). Start composting organic waste to prevent methane generation and ensure all paper, plastics, and metals are recycled properly.")
            else:
                lines.append(f"Your largest emission source is {dominant_source} ({pct:.1f}%). Look for targeted reduction opportunities in this area.")

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
