Synthetic Missing Categories Dataset Pack
=========================================

Purpose
-------
This pack contains synthetic datasets for the missing categories in your carbon footprint platform:
1. Transport
2. Electricity Mix
3. Waste
4. User Behavior

Important
---------
- These are synthetic/demo datasets for prototyping, visualization, and ML pipeline testing.
- Do not use the synthetic emission factors as scientific ground truth in a final carbon accounting system.
- Replace factor tables with verified sources (EPA, DEFRA, IEA, Ember, World Bank, etc.) before deployment.

Files
-----
- transport_emission_factors_synthetic.csv
- transport_activity_synthetic.csv
- electricity_mix_synthetic.csv
- waste_synthetic.csv
- behavior_synthetic.csv

Suggested usage
---------------
Transport:
- Use transport_emission_factors_synthetic.csv for demo calculations.
- Use transport_activity_synthetic.csv for commute/travel behavior and ranking models.

Electricity:
- Use electricity_mix_synthetic.csv for grid-intensity features, regional comparison, and recommendation context.

Waste:
- Use waste_synthetic.csv for disposal behavior and waste-emission insights.

Behavior:
- Use behavior_synthetic.csv for ranking model features and personalization.

