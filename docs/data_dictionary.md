# Carbon Footprint Platform — Data Dictionary

Complete reference for all engineered features in the master dataset.

---

## Transport Features
*Source module: `src/feature_engineering/transport_features.py`*

| Feature | Formula | Unit | Description |
|---|---|---|---|
| `annual_transport_emission_kg_co2e` | `estimated_monthly_transport_emissions_kg_co2e × 12` | kg CO2e/year/user | Annualised transport carbon emission |
| `commute_intensity_kg_co2e_per_km` | `(annual_transport_emission / 52) / weekly_commute_distance_km` | kg CO2e/km/week | Emission per weekly commute km |
| `is_low_carbon_commuter` | `commute_mode ∈ {Walking, Cycling, Bus, Metro/Subway, Electric Train}` | boolean | True if primary commute is non-motorised or public transit |
| `annual_flight_distance_km` | `monthly_flight_distance_km × 12` | km/year | Annualised flight distance |
| `annual_flight_emission_kg_co2e` | `annual_flight_distance_km × 0.209` | kg CO2e/year | Annual flight emission (avg long/short haul factor) |
| `flight_emission_share_pct` | `annual_flight_emission / annual_transport_emission × 100` | % | Share of transport emission from flights |
| `commute_mode_emission_factor` | Looked up from transport_emission_factors | kg CO2e/km | Emission factor for user's commute mode |

---

## Electricity Features
*Source module: `src/feature_engineering/electricity_features.py`*

| Feature | Formula | Unit | Description |
|---|---|---|---|
| `electricity_emission_kg_co2e_per_capita` | `energy_per_capita_kwh × grid_intensity_kg_co2_per_kwh` | kg CO2e/year/capita | Annual per-capita electricity emission |
| `fossil_share_pct` | `coal_share_pct + gas_share_pct + oil_share_pct` | % | Combined fossil fuel generation share |
| `clean_share_pct` | `nuclear_share_pct + renewable_share_pct` | % | Combined clean energy share |
| `grid_intensity_tier` | `cut(grid_intensity, [0, 0.15, 0.30, 0.50, 0.70, ∞])` | categorical | Very Low / Low / Medium / High / Very High |
| `renewable_adoption_potential` | `1 - (renewable_share_pct / 100)` | 0–1 | Headroom remaining for renewable transition |

---

## Food Features
*Source module: `src/feature_engineering/food_features.py`*

| Feature | Formula | Unit | Description |
|---|---|---|---|
| `food_emission_kg_co2e_per_capita_per_year` | `Σ(supply_g/cap/day × greenhouse_gas_emissions_per_kilogram / 1000 × 365)` | kg CO2e/year/capita | Annual per-capita dietary carbon footprint |
| `weighted_avg_food_ghg_factor` | `Σ(supply_g × greenhouse_gas_emissions_per_kilogram) / Σ(supply_g)` | kg CO2e/kg food | Demand-weighted average GHG intensity of diet |
| `diet_carbon_intensity_tier` | `cut(food_emission, [0, 500, 1500, 3000, ∞])` | categorical | Very Low / Low / High / Very High |
| `high_meat_diet_flag` | `meat_groups_supply_g/day > 50 g` | boolean | True if diet is estimated to be meat-heavy |

---

## Waste Features
*Source module: `src/feature_engineering/waste_features.py`*

| Feature | Formula | Unit | Description |
|---|---|---|---|
| `waste_emission_kg_co2e_per_capita_per_year` | `waste_generated_kg_per_capita_per_day × 365 × estimated_waste_emissions_kg_co2e_per_kg_waste` | kg CO2e/year/capita | Annual per-capita waste emission |
| `landfill_emission_kg_co2e_per_capita_per_year` | `waste_generated_kg_per_capita_per_day × 365 × (landfill_rate/100) × 0.50` | kg CO2e/year/capita | Emission from landfill disposal |
| `recycling_potential_score` | `(landfill_rate/100) × waste_generated_kg_per_capita_per_day × 365` | kg/year/capita | Kg of waste that could be diverted from landfill |
| `waste_diversion_rate_pct` | `recycling_rate_pct + composting_rate_pct` | % | Combined recycling + composting rate |
| `waste_management_tier` | `cut(diversion_rate, [0, 20, 40, 60, 100])` | categorical | Poor / Moderate / Good / Excellent |

---

## Country Context Features
*Source module: `src/feature_engineering/context_features.py`*

| Feature | Formula | Unit | Description |
|---|---|---|---|
| `gdp_log` | `log1p(gdp_per_capita_usd)` | log(USD+1) | Log-transformed GDP per capita (reduces right-skew) |
| `gdp_tier` | `cut(gdp, [0, 1000, 5000, 15000, 40000, ∞])` | categorical | Low / Lower-Middle / Upper-Middle / High / Very High |
| `hdi_normalized` | `(hdi - min) / (max - min)` | 0–1 | Min-max normalised Human Development Index |
| `emission_per_gdp_intensity` | `(co2_per_capita_t × 1000) / gdp_per_capita_usd` | kg CO2 / USD | Carbon efficiency of economic output |
| `co2_country_percentile` | `rank(co2_per_capita_t, pct=True)` within year | 0–1 | Country's CO2 per capita percentile rank |
| `electricity_access_gap_pct` | `100 - electricity_access_pct` | % | Share of population without electricity access |

---

## Behavior & Recommendation Features
*Source module: `src/feature_engineering/context_features.py`*

| Feature | Formula | Unit | Description |
|---|---|---|---|
| `effort_score` | `mean(price_sensitivity, commute_flexibility, diet_flexibility)` | 0–100 | Composite score of behaviour change difficulty |
| `digital_reach_score` | `mean(digital_engagement_score, social_influence_score)` | 0–100 | Receptiveness to digital outreach channels |
| `behavior_adoption_tier` | `cut(green_adoption_probability, [0, 0.5, 0.75, 0.9, 1.0])` | categorical | Low / Medium / High / Champion |
| `green_readiness_index` | `(carbon_awareness_score / 100) × green_adoption_probability` | 0–1 | Combined awareness and adoption readiness |

---

## Integration-Level Features
*Source module: `src/feature_engineering/context_features.py` via `pipeline.py`*

| Feature | Formula | Unit | Description |
|---|---|---|---|
| `total_emission_kg_co2e` | `transport + electricity + food + waste` | kg CO2e/year | Total annual carbon footprint |
| `dominant_emission_source` | `argmax(transport, electricity, food, waste)` | categorical | Category with highest emission |
| `transport_emission_share_pct` | `transport / total × 100` | % | Transport's share of total footprint |
| `electricity_emission_share_pct` | `electricity / total × 100` | % | Electricity's share of total footprint |
| `food_emission_share_pct` | `food / total × 100` | % | Food's share of total footprint |
| `waste_emission_share_pct` | `waste / total × 100` | % | Waste's share of total footprint |

---

## Notes on Units

All emission features are in **kg CO2e** (kilograms of CO2 equivalent), which accounts
for all greenhouse gases (CO2, CH4, N2O, etc.) weighted by their 100-year Global
Warming Potential (GWP100).

To convert to tonnes: divide by 1,000.

---

## Data Sources

| Dataset | Original Source |
|---|---|
| `transport_activity_synthetic.csv` | Synthetic (generated for platform) |
| `transport_emission_factors_synthetic.csv` | Synthetic (generated for platform) |
| `electricity_mix_synthetic.csv` | Synthetic (generated for platform) |
| `waste_synthetic.csv` | Synthetic (generated for platform) |
| `behavior_synthetic.csv` | Synthetic (generated for platform) |
| `ghg-emission-factors-hub-2025.xlsx` | EPA GHG Emission Factors Hub 2025 |
| `Supply_Utilization_Accounts_Food_and_Diet_E_All_Data.csv` | FAO (Food and Agriculture Organization) |
| `greenhouse-gas-emissions-per-kilogram-of-food-product.csv` | Our World in Data / Poore & Nemecek (2018) |
| `gdp-per-capita-maddison-project-database.csv` | Our World in Data / Maddison Project |
| `human-development-index.csv` | Our World in Data / UNDP |
| `co-emissions-per-capita.csv` | Our World in Data / Global Carbon Project |
| `population.csv` | Our World in Data / UN |
| `cross-country-literacy-rates.csv` | Our World in Data / UNESCO |
| `share-of-the-population-with-access-to-electricity.csv` | Our World in Data / World Bank |
