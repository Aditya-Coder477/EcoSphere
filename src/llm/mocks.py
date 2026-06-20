"""
src/llm/mocks.py
================
Python equivalent of frontend mocks to allow backend fallback when DB is empty.
"""

mock_user_profile = {
    "user_id": "mock_user_aditya",
    "name": "Aditya Raj",
    "email": "aditya.raj@example.com",
    "occupation": "Software Engineer",
    "preferences": {
        "country": "IND",
        "household_size": 2,
        "diet": "average",
        "commute_mode": "car",
        "budget_level": "medium",
        "electricity_source": "grid",
        "electricity_kwh_per_year": 4200,
    }
}

mock_carbon_summary = {
    "user_id": "mock_user_aditya",
    "total_emissions_kg_co2e": 7240.0,
    "category_emissions": {
        "transport": 3850.0,
        "food": 1810.0,
        "electricity": 1020.0,
        "waste": 560.0,
    },
    "category_shares_pct": {
        "transport": 53.2,
        "food": 25.0,
        "electricity": 14.1,
        "waste": 7.7,
    },
    "dominant_source": "transport",
    "human_readable_summary": (
        "Your biggest impact area is transport at 53% of your footprint. "
        "Switching to public transit for your commute just 3 days per week could save "
        "over 800 kg CO2e annually. Your food and electricity footprints are near "
        "the national average for a 2-person household in India."
    ),
    "month_over_month_change_pct": -4.7,
    "monthly_goal_kg": 544.0,
}

mock_recommendations = [
    {
        "action_id": "rec_001",
        "title": "Switch to Public Transit 3 Days/Week",
        "category": "transport",
        "description": "Taking the metro or bus three days per week instead of driving reduces fuel burn and lowers your per-km emission factor.",
        "why_explanation": "Your daily car commute alone contributes 2,600 kg/yr — the single largest item in your footprint.",
        "carbon_savings_kg": 860.0,
        "impact_score": 9.2,
        "effort_level": "medium",
        "cost_level": "free",
        "adoption_probability": 0.72,
        "annual_cost_savings_usd": 320.0,
    },
    {
        "action_id": "rec_002",
        "title": "Eliminate Beef Twice a Week",
        "category": "food",
        "description": "Swapping two weekly beef meals for chicken, legumes, or paneer reduces dietary emissions by 15–18%.",
        "why_explanation": "Beef produces 27 kg CO2e per kg of food — roughly 20x more than lentils.",
        "carbon_savings_kg": 180.0,
        "impact_score": 7.8,
        "effort_level": "low",
        "cost_level": "free",
        "adoption_probability": 0.85,
        "annual_cost_savings_usd": 90.0,
    },
    {
        "action_id": "rec_003",
        "title": "Install a Solar Rooftop Panel (2 kW)",
        "category": "electricity",
        "description": "A 2 kW rooftop solar system covers ~40% of average household electricity needs in India.",
        "why_explanation": "India's grid has a high carbon intensity (~0.82 kg CO2/kWh). Solar generation offsets grid usage.",
        "carbon_savings_kg": 420.0,
        "impact_score": 8.5,
        "effort_level": "high",
        "cost_level": "medium",
        "adoption_probability": 0.42,
        "annual_cost_savings_usd": 210.0,
    }
]

mock_journey_data = {
    "cumulative_savings_kg": 558.0,
    "streak_months": 5,
    "monthly_history": [
        {"month": "Jul 2024", "emissions_kg": 675.0, "savings_kg": 0.0},
        {"month": "Dec 2024", "emissions_kg": 620.0, "savings_kg": 55.0},
        {"month": "Jun 2025", "emissions_kg": 603.0, "savings_kg": 72.0},
    ]
}
