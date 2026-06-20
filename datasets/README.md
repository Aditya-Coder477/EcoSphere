# Carbon Footprint Platform Datasets

This directory manages the raw and processed data assets for the Carbon Footprint Awareness Platform. The data flows through a structured multi-stage ETL (Extract, Transform, Load) pipeline:
`raw/` (Ingestion) ➔ `cleaned/` (Standardization & Validation) ➔ `engineered/` (Derived Metrics) ➔ `merged/` (Unified Master Dataset).

---

## Dataset Directory Structure

* **`raw/`**: Contains raw immutable data tables from verified scientific providers and synthetic user profiles.
* **`cleaned/`**: Intermediate standardized tables. Columns are mapped to `snake_case`, missing country names normalized, and rows verified.
* **`engineered/`**: Derived domain features including annual emission bounds, commute intensity ratios, clean energy mix shares, and diet-based carbon tiers.
* **`merged/`**: Unified datasets linking user-level behavior profiles to national economic/emission baselines.

---

## Detailed Data Catalog

| Dataset File / Key | Source | Original Provider | File Format | Update Frequency | Purpose in ETL Pipeline |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`ghg-emission-factors-hub-2025.xlsx`** | [EPA GHG Hub](https://www.epa.gov/climateleadership/center-corporate-climate-leadership-power-passenger-and-mobile-source-guidance) | US Environmental Protection Agency (EPA) | XLSX | Annual | Provides official greenhouse gas emission factors for electricity, fuel combustion, and transit modes. |
| **`Supply_Utilization_Accounts_Food_and_Diet_E_All_Data.csv`** | [FAOSTAT](https://www.fao.org/faostat/en/#data/SUA) | Food and Agriculture Organization (FAO) | CSV | Annual | Tracks daily per-capita food supply (in grams) per country to estimate nutritional footprints. |
| **`greenhouse-gas-emissions-per-kilogram-of-food-product.csv`** | [Our World in Data](https://ourworldindata.org/environmental-impacts-of-food) | Poore & Nemecek (2018 Science study) | CSV | Static (Research) | Maps agricultural lifecycle GHG emissions (kg CO2e) per kilogram of specific food product categories. |
| **`gdp-per-capita-maddison-project-database.csv`** | [Maddison Database](https://www.rug.nl/ggdc/historicaldevelopment/maddison/) | Groningen Growth and Development Centre | CSV | Decadal | Provides historical country-level inflation-adjusted GDP per capita for economic contextualization. |
| **`human-development-index.csv`** | [UNDP](https://hdr.undp.org/data-center) | United Nations Development Programme | CSV | Annual | Tracks national Human Development Index (HDI) scores to correlate sustainability and development. |
| **`co-emissions-per-capita.csv`** | [Global Carbon Budget](https://www.globalcarbonproject.org/) | Our World in Data / GCP | CSV | Annual | Serves as the national baseline for per-capita CO2 emissions (tonnes per year) to rank user performance. |
| **`share-of-the-population-with-access-to-electricity.csv`** | [World Bank](https://data.worldbank.org/) | World Bank / Our World in Data | CSV | Annual | Infrastructure baseline metric showing electrification rates. |
| **`cross-country-literacy-rates.csv`** | [UNESCO](https://uis.unesco.org/) | UNESCO Institute for Statistics | CSV | Periodic | National literacy baseline used for behavior change potential indicators. |
| **`transport_activity_synthetic.csv`** | Simulated | Prototyping Engine | CSV | Generated | Synthetic user logs containing monthly mileage, vehicle choices, and public transit usage. |
| **`transport_emission_factors_synthetic.csv`** | Simulated | Prototyping Engine | CSV | Generated | Pre-calculated transit emissions per kilometer for rapid mock calculations. |
| **`electricity_mix_synthetic.csv`** | Simulated | Prototyping Engine | CSV | Generated | Country-level clean/fossil grid energy composition mixes. |
| **`waste_synthetic.csv`** | Simulated | Prototyping Engine | CSV | Generated | Synthetic user municipal solid waste generation rate (kg/day) and recycling shares. |
| **`behavior_synthetic.csv`** | Simulated | Prototyping Engine | CSV | Generated | User profiles tracking willingness to pay, flexibility, and adoption probability. |

---

## Dataset Mapping to Platform Modules

The following matrix illustrates how each dataset feeds into the platform's core functional modules:

| Dataset / Key | Carbon Engine | Recommendation Engine | AI Climate Coach | Analytics Dashboard |
| :--- | :---: | :---: | :---: | :---: |
| **`transport_factors`** | ✔ | | ✔ | |
| **`ghg_factors_xlsx`** | ✔ | | ✔ | |
| **`transport_activity`** | ✔ | ✔ | ✔ | ✔ |
| **`electricity_mix`** | ✔ | ✔ | ✔ | ✔ |
| **`waste`** | ✔ | ✔ | ✔ | ✔ |
| **`food_supply`** | ✔ | | ✔ | |
| **`food_ghg_factors`** | ✔ | | ✔ | |
| **`gdp_per_capita`** | | | ✔ | ✔ |
| **`hdi`** | | | ✔ | ✔ |
| **`co2_per_capita`** | | ✔ | ✔ | ✔ |
| **`electricity_access`** | | | | ✔ |
| **`literacy`** | | | | ✔ |
| **`behavior`** | | ✔ | ✔ | ✔ |
| **`master_dataset` (Merged)** | | ✔ | ✔ | ✔ |
