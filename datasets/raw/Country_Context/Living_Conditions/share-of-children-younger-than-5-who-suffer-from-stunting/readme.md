# Malnutrition: Share of children who are stunted - Data package

This data package contains the data that powers the chart ["Malnutrition: Share of children who are stunted"](https://ourworldindata.org/grapher/share-of-children-younger-than-5-who-suffer-from-stunting?v=1&csvType=full&useColumnShortNames=false) on the Our World in Data website. It was downloaded on June 10, 2026.

### Active Filters

A filtered subset of the full data was downloaded. The following filters were applied:

## CSV Structure

The high level structure of the CSV file is that each row is an observation for an entity (usually a country or region) and a timepoint (usually a year).

The first two columns in the CSV file are "Entity" and "Code". "Entity" is the name of the entity (e.g. "United States"). "Code" is the OWID internal entity code that we use if the entity is a country or region. For most countries, this is the same as the [iso alpha-3](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3) code of the entity (e.g. "USA") - for non-standard countries like historical countries these are custom codes.

The third column is either "Year" or "Day". If the data is annual, this is "Year" and contains only the year as an integer. If the column is "Day", the column contains a date string in the form "YYYY-MM-DD".

The final column is the data column, which is the time series that powers the chart. If the CSV data is downloaded using the "full data" option, then the column corresponds to the time series below. If the CSV data is downloaded using the "only selected data visible in the chart" option then the data column is transformed depending on the chart type and thus the association with the time series might not be as straightforward.


## Metadata.json structure

The .metadata.json file contains metadata about the data package. The "charts" key contains information to recreate the chart, like the title, subtitle etc.. The "columns" key contains information about each of the columns in the csv, like the unit, timespan covered, citation for the data etc..

## About the data

Our World in Data is almost never the original producer of the data - almost all of the data we use has been compiled by others. If you want to re-use data, it is your responsibility to ensure that you adhere to the sources' license and to credit them correctly. Please note that a single time series may have more than one source - e.g. when we stich together data from different time periods by different producers or when we calculate per capita metrics using population data from a second source.

## Detailed information about the data


## Stunting prevalence among children under 5 years of age (% height-for-age <-2 SD), survey-based estimates - Sex: both sexes
Last updated: May 22, 2026  
Next update: May 2027  
Date range: 1983–2024  
Unit: %  


### How to cite this data

#### In-line citation
If you have limited space (e.g. in data visualizations), you can use this abbreviated in-line citation:  
World Health Organization - Global Health Observatory (2026) – with minor processing by Our World in Data

#### Full citation
World Health Organization - Global Health Observatory (2026) – with minor processing by Our World in Data. “Stunting prevalence among children under 5 years of age (% height-for-age <-2 SD), survey-based estimates - Sex: both sexes – WHO” [dataset]. World Health Organization, “Global Health Observatory” [original data].
Source: World Health Organization - Global Health Observatory (2026) – with minor processing by Our World In Data

### How is this data described by its producer - World Health Organization - Global Health Observatory (2026)?
#### Rationale
Child growth is an internationally accepted outcome reflecting child nutritional status. Child stunting refers to a child who is too short for his or her age and is the result of chronic or recurrent malnutrition. Stunting is a contributing risk factor to child mortality and is also a marker of inequalities in human development. Stunted children fail to reach their physical and cognitive potential. Child stunting is one of the World Health Assembly nutrition target indicators. Child stunting is one of the indicators under Sustainable Development Goal (SDG) indicators target 2.2

#### Definition
Prevalence of stunting (height-for-age <-2 standard deviation from the median of the World Health Organization (WHO) Child Growth Standards) among children under 5 years of age

#### Method of measurement
**Methods and Guidance:**

WHO and UNICEF provide recommendations for data collection, analysis and reporting on anthropometric indicators in children under 5 years old. (Recommendations for data collection, analysis and reporting on anthropometric indicators in children under 5 years old. Geneva: World Health Organization and the United Nations Children’s Fund (UNICEF), 2019. Licence: CC BY-NC-SA 3.0 IGO. )

**Analysis Tool**

To facilitate re-running of nutritional survey data based on standardized approach, WHO has developed an online tool to analyse child anthropometric data. The WHO Anthro Survey Analyzer aims to promote best practices on data collection, analyses and reporting of anthropometric indicators. It offers analysis for four indicators: length/height-for-age, weight-for-age, weight-for-length, weight-for-height and body mass index-for-age. (WHO Anthro Survey Analyser and other tools)

**Global Reporting**

The modelled estimates are the official source used for global reporting on this indicator. (Metadata: SDG 2.2.1)

#### Method of estimation
**Data collection method**

UNICEF and WHO employ their existing networks to obtain data. WHO relies on the organization’s structure and an expanding network developed following the creation of the WHO Global Database on Child Growth and Malnutrition. For UNICEF, the cadre of dedicated data and monitoring specialists working at national, regional and international levels in 190 countries routinely provides technical support to produce child malnutrition estimates through surveys and administrative systems and analyses for improved programme planning. The World Bank Group provides estimates available through the Living Standard Measurement Surveys (LSMS).

**Method of computation**

National estimates from primary sources (e.g., from household surveys) used to generate the JME global estimates are based on standardized methodology using the WHO Child Growth Standards as described in “The UNICEF-WHO-World Bank Joint Child Malnutrition Estimates (JME) standard methodology” (The UNICEF-WHO-World Bank Joint Child Malnutrition Estimates (JME) standard methodology New York: the United Nations Children’s Fund (UNICEF), the World Health Organization and the World Bank, 2024. Licence: CC BY-NC-SA 3.0 IGO. )and WHO Anthro Survey Analyser.

The JME global estimates are generated using smoothing techniques and covariates applied to quality-assured national data to derive trends and up-to-date estimates. Worldwide and regional estimates are derived as the respective country averages weighted by the countries’ under-five population estimates (UNPD-WPP latest available edition) using annual JME global estimates for 205 countries. (The UNICEF-WHO-World Bank Joint Child Malnutrition Estimates (JME) standard methodology New York: the United Nations Children’s Fund (UNICEF), the World Health Organization and the World Bank, 2024. Licence: CC BY-NC-SA 3.0 IGO. ) However, estimates are only presented in the cases where a country has input data.

In line with WHO’s data principle to use transparent models and methods, all codes used to generate estimates for the latest round and prior rounds are openly available on WHO’s GitHub repository. (UNICEF-WHO-World Bank Joint Child Malnutrition Estimates- Stunting and Overweight Global Health Estimates. )

### Source

#### World Health Organization – Global Health Observatory
Retrieved on: 2026-05-22  
Retrieved from: https://www.who.int/data/gho  


    