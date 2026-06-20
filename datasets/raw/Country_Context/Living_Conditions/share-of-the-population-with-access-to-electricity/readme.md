# Share of the population with access to electricity - Data package

This data package contains the data that powers the chart ["Share of the population with access to electricity"](https://ourworldindata.org/grapher/share-of-the-population-with-access-to-electricity?v=1&csvType=full&useColumnShortNames=false) on the Our World in Data website. It was downloaded on June 10, 2026.

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


## Share of the population with access to electricity – World Bank
Access to electricity means having an electricity source that can provide very basic lighting, and charge a phone or power a radio for 4 hours per day.
Last updated: February 27, 2026  
Next update: February 2027  
Date range: 1990–2023  
Unit: % of population  


### How to cite this data

#### In-line citation
If you have limited space (e.g. in data visualizations), you can use this abbreviated in-line citation:  
Data compiled from multiple sources by the World Bank – with minor processing by Our World in Data

#### Full citation
Data compiled from multiple sources by the World Bank – with minor processing by Our World in Data. “Share of the population with access to electricity – World Bank” [dataset]. SDG 7.1.1 Electrification Dataset, World Bank, via World Bank, “World Development Indicators 125” [original data].
Source: Data compiled from multiple sources by the World Bank – with minor processing by Our World In Data

### What you should know about this data
* Access to electricity improves people's living conditions in many ways. [Light at night](https://ourworldindata.org/light-at-night) makes it possible to get together after sunset; mobile phones allow us to stay in touch with those far away; refrigeration reduces food waste; and household appliances free up time from chores.
* This data captures whether people have access to the most basic electricity supply — just enough to provide basic lighting and charge a phone or power a radio for 4 hours per day.
* It shows that, especially in several African countries, a large share of the population lacks the benefits of basic electricity.
* Universal access to electricity by 2030 is one of the United Nations [Sustainable Development Goals](https://ourworldindata.org/sdgs/affordable-clean-energy#sdg-indicator-7-1-1-access-to-electricity).
* This data comes from the World Bank's World Development Indicators. Estimates are based on national household surveys, census data, and reports from energy providers or government agencies. Where data is missing, values are estimated by the source using a model based on trends across countries, regions, and time. Countries classified as “developed” by the United Nations are assumed to have universal access.
* To learn more, read our article: [Definitions: access to electricity](https://ourworldindata.org/definition-electricity-access).

### How is this data described by its producer - Data compiled from multiple sources by the World Bank?
Access to electricity is the percentage of population with access to electricity. Electrification data are collected from industry, national surveys and international sources.

### Aggregation method:
Population-weighted average

### Statistical concept and methodology:
Methodology: The World Bank’s Global Electrification Database (GED) compiles nationally representative household survey data, and occasionally census data, from sources going back as far as 1990. The database also incorporates data from the Socio-Economic Database for Latin America and the Caribbean (SEDLAC), Middle East and North Africa Poverty Database (MNAPOV) and the Europe and Central Asia Poverty Database (ECAPOV), which are based on similar surveys. At the time of this analysis, the GED contained 1,375 surveys for 149 countries in 1990-2021.

### Development relevance:
Maintaining reliable and secure electricity services while seeking to rapidly decarbonize power systems is a key challenge for countries throughout the world. More and more countries are becoming increasing dependent on reliable and secure electricity supplies to underpin economic growth and community prosperity. This reliance is set to grow as more efficient and less carbon intensive forms of power are developed and deployed to help decarbonize economies.



















Energy is necessary for creating the conditions for economic growth. It is impossible to operate a factory, run a shop, grow crops or deliver goods to consumers without using some form of energy. Access to electricity is particularly crucial to human development as electricity is, in practice, indispensable for certain basic activities, such as lighting, refrigeration and the running of household appliances, and cannot easily be replaced by other forms of energy. Individuals' access to electricity is one of the most clear and un-distorted indication of a country's energy poverty status.



















Electricity access is increasingly at the forefront of governments' preoccupations, especially in the developing countries. As a consequence, a lot of rural electrification programs and national electrification agencies have been created in these countries to monitor more accurately the needs and the status of rural development and electrification.



















Use of energy is important in improving people's standard of living. But electricity generation also can damage the environment. Whether such damage occurs depends largely on how electricity is generated. For example, burning coal releases twice as much carbon dioxide - a major contributor to global warming - as does burning an equivalent amount of natural gas.

### Source

#### SDG 7.1.1 Electrification Dataset, World Bank, via World Bank – World Development Indicators
Retrieved on: 2026-02-27  
Retrieved from: https://data.worldbank.org/indicator/EG.ELC.ACCS.ZS  


    