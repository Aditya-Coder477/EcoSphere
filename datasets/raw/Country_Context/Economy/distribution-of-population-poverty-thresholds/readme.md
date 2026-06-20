# Distribution of population between different poverty lines - Data package

This data package contains the data that powers the chart ["Distribution of population between different poverty lines"](https://ourworldindata.org/grapher/distribution-of-population-poverty-thresholds?v=1&csvType=full&useColumnShortNames=false) on the Our World in Data website.

## CSV Structure

The high level structure of the CSV file is that each row is an observation for an entity (usually a country or region) and a timepoint (usually a year).

The first two columns in the CSV file are "Entity" and "Code". "Entity" is the name of the entity (e.g. "United States"). "Code" is the OWID internal entity code that we use if the entity is a country or region. For most countries, this is the same as the [iso alpha-3](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3) code of the entity (e.g. "USA") - for non-standard countries like historical countries these are custom codes.

The third column is either "Year" or "Day". If the data is annual, this is "Year" and contains only the year as an integer. If the column is "Day", the column contains a date string in the form "YYYY-MM-DD".

The remaining columns are the data columns, each of which is a time series. If the CSV data is downloaded using the "full data" option, then each column corresponds to one time series below. If the CSV data is downloaded using the "only selected data visible in the chart" option then the data columns are transformed depending on the chart type and thus the association with the time series might not be as straightforward.


## Metadata.json structure

The .metadata.json file contains metadata about the data package. The "charts" key contains information to recreate the chart, like the title, subtitle etc.. The "columns" key contains information about each of the columns in the csv, like the unit, timespan covered, citation for the data etc..

## About the data

Our World in Data is almost never the original producer of the data - almost all of the data we use has been compiled by others. If you want to re-use data, it is your responsibility to ensure that you adhere to the sources' license and to credit them correctly. Please note that a single time series may have more than one source - e.g. when we stich together data from different time periods by different producers or when we calculate per capita metrics using population data from a second source.

### How we process data at Our World In Data
All data and visualizations on Our World in Data rely on data sourced from one or several original data providers. Preparing this original data involves several processing steps. Depending on the data, this can include standardizing country names and world region definitions, converting units, calculating derived indicators such as per capita measures, as well as adding or adapting metadata such as the name or the description given to an indicator.
[Read about our data pipeline](https://docs.owid.io/projects/etl/)

## Detailed information about each time series


## Above $10 a day
Number of people living in households with an income or consumption above $10 per day.
Last updated: March 24, 2026  
Next update: September 2026  
Date range: 1963–2026  
Unit: people  


### How to cite this data

#### In-line citation
If you have limited space (e.g. in data visualizations), you can use this abbreviated in-line citation:  
World Bank Poverty and Inequality Platform (2026) – with major processing by Our World in Data

#### Full citation
World Bank Poverty and Inequality Platform (2026) – with major processing by Our World in Data. “Above $10 a day – World Bank” [dataset]. World Bank Poverty and Inequality Platform, “World Bank Poverty and Inequality Platform (PIP) 20260324_2021, 20260324_2017” [original data].
Source: World Bank Poverty and Inequality Platform (2026) – with major processing by Our World In Data

### What you should know about this data
* This data is expressed in constant international dollars to adjust for inflation and differences in living costs between countries. Read more in our article, [What are international dollars?](https://ourworldindata.org/international-dollars)
* Many people, today and in the past, have no formal monetary income. This data accounts for that by including the estimated value of non-market income, such as food grown by subsistence farmers for their own use.
* The data comes from the World Bank's Poverty and Inequality Platform (PIP), which draws on national household surveys. Regional and global estimates are extrapolated to the year of the data release using GDP growth estimates and forecasts. For more details about the methodology, please refer to the [World Bank PIP documentation](https://datanalytics.worldbank.org/PIP-Methodology/lineupestimates.html#nowcasts).
* Depending on the country and year, the data refers either to income (after taxes and benefits) or to consumption, [per capita](#dod:per-capita). These are not perfectly comparable — consumption tends to be more evenly distributed than income. For most countries, we have only one option available. But when there is a mix of consumption and income data points, we process the data to keep one observation per country and year.

### Source

#### World Bank Poverty and Inequality Platform – World Bank Poverty and Inequality Platform (PIP)
Retrieved on: 2026-03-24  
Retrieved from: https://pip.worldbank.org  

#### Notes on our processing step for this indicator
For most countries in the dataset, estimates relate to disposable income or consumption, for all available years. Several countries, however, have a mix of income and consumption data points, with both data types sometimes available for particular years.

In most of our charts, we present the data with some data points dropped to present a single series for each country. This allows us to make readable visualizations that combine multiple countries. In choosing which data points to keep, we strike a balance between maintaining comparability over time and showing as long a time series as possible. As such, the exact approach varies across countries.


## $8.30-$10 a day
Number of people living in households with an income or consumption between $8.30 and $10 per day.
Last updated: March 24, 2026  
Next update: September 2026  
Date range: 1963–2026  
Unit: people  


### How to cite this data

#### In-line citation
If you have limited space (e.g. in data visualizations), you can use this abbreviated in-line citation:  
World Bank Poverty and Inequality Platform (2026) – with major processing by Our World in Data

#### Full citation
World Bank Poverty and Inequality Platform (2026) – with major processing by Our World in Data. “$8.30-$10 a day – World Bank” [dataset]. World Bank Poverty and Inequality Platform, “World Bank Poverty and Inequality Platform (PIP) 20260324_2021, 20260324_2017” [original data].
Source: World Bank Poverty and Inequality Platform (2026) – with major processing by Our World In Data

### What you should know about this data
* This data is expressed in constant international dollars to adjust for inflation and differences in living costs between countries. Read more in our article, [What are international dollars?](https://ourworldindata.org/international-dollars)
* Many people, today and in the past, have no formal monetary income. This data accounts for that by including the estimated value of non-market income, such as food grown by subsistence farmers for their own use.
* The data comes from the World Bank's Poverty and Inequality Platform (PIP), which draws on national household surveys. Regional and global estimates are extrapolated to the year of the data release using GDP growth estimates and forecasts. For more details about the methodology, please refer to the [World Bank PIP documentation](https://datanalytics.worldbank.org/PIP-Methodology/lineupestimates.html#nowcasts).
* Depending on the country and year, the data refers either to income (after taxes and benefits) or to consumption, [per capita](#dod:per-capita). These are not perfectly comparable — consumption tends to be more evenly distributed than income. For most countries, we have only one option available. But when there is a mix of consumption and income data points, we process the data to keep one observation per country and year.

### Source

#### World Bank Poverty and Inequality Platform – World Bank Poverty and Inequality Platform (PIP)
Retrieved on: 2026-03-24  
Retrieved from: https://pip.worldbank.org  

#### Notes on our processing step for this indicator
For most countries in the dataset, estimates relate to disposable income or consumption, for all available years. Several countries, however, have a mix of income and consumption data points, with both data types sometimes available for particular years.

In most of our charts, we present the data with some data points dropped to present a single series for each country. This allows us to make readable visualizations that combine multiple countries. In choosing which data points to keep, we strike a balance between maintaining comparability over time and showing as long a time series as possible. As such, the exact approach varies across countries.


## $4.20-$8.30 a day
Number of people living in households with an income or consumption between $4.20 and $8.30 per day.
Last updated: March 24, 2026  
Next update: September 2026  
Date range: 1963–2026  
Unit: people  


### How to cite this data

#### In-line citation
If you have limited space (e.g. in data visualizations), you can use this abbreviated in-line citation:  
World Bank Poverty and Inequality Platform (2026) – with major processing by Our World in Data

#### Full citation
World Bank Poverty and Inequality Platform (2026) – with major processing by Our World in Data. “$4.20-$8.30 a day – World Bank” [dataset]. World Bank Poverty and Inequality Platform, “World Bank Poverty and Inequality Platform (PIP) 20260324_2021, 20260324_2017” [original data].
Source: World Bank Poverty and Inequality Platform (2026) – with major processing by Our World In Data

### What you should know about this data
* This data is expressed in constant international dollars to adjust for inflation and differences in living costs between countries. Read more in our article, [What are international dollars?](https://ourworldindata.org/international-dollars)
* Many people, today and in the past, have no formal monetary income. This data accounts for that by including the estimated value of non-market income, such as food grown by subsistence farmers for their own use.
* The data comes from the World Bank's Poverty and Inequality Platform (PIP), which draws on national household surveys. Regional and global estimates are extrapolated to the year of the data release using GDP growth estimates and forecasts. For more details about the methodology, please refer to the [World Bank PIP documentation](https://datanalytics.worldbank.org/PIP-Methodology/lineupestimates.html#nowcasts).
* Depending on the country and year, the data refers either to income (after taxes and benefits) or to consumption, [per capita](#dod:per-capita). These are not perfectly comparable — consumption tends to be more evenly distributed than income. For most countries, we have only one option available. But when there is a mix of consumption and income data points, we process the data to keep one observation per country and year.

### Source

#### World Bank Poverty and Inequality Platform – World Bank Poverty and Inequality Platform (PIP)
Retrieved on: 2026-03-24  
Retrieved from: https://pip.worldbank.org  

#### Notes on our processing step for this indicator
For most countries in the dataset, estimates relate to disposable income or consumption, for all available years. Several countries, however, have a mix of income and consumption data points, with both data types sometimes available for particular years.

In most of our charts, we present the data with some data points dropped to present a single series for each country. This allows us to make readable visualizations that combine multiple countries. In choosing which data points to keep, we strike a balance between maintaining comparability over time and showing as long a time series as possible. As such, the exact approach varies across countries.


## $3-$4.20 a day
Number of people living in households with an income or consumption between $3 and $4.20 per day.
Last updated: March 24, 2026  
Next update: September 2026  
Date range: 1963–2026  
Unit: people  


### How to cite this data

#### In-line citation
If you have limited space (e.g. in data visualizations), you can use this abbreviated in-line citation:  
World Bank Poverty and Inequality Platform (2026) – with major processing by Our World in Data

#### Full citation
World Bank Poverty and Inequality Platform (2026) – with major processing by Our World in Data. “$3-$4.20 a day – World Bank” [dataset]. World Bank Poverty and Inequality Platform, “World Bank Poverty and Inequality Platform (PIP) 20260324_2021, 20260324_2017” [original data].
Source: World Bank Poverty and Inequality Platform (2026) – with major processing by Our World In Data

### What you should know about this data
* This data is expressed in constant international dollars to adjust for inflation and differences in living costs between countries. Read more in our article, [What are international dollars?](https://ourworldindata.org/international-dollars)
* Many people, today and in the past, have no formal monetary income. This data accounts for that by including the estimated value of non-market income, such as food grown by subsistence farmers for their own use.
* The data comes from the World Bank's Poverty and Inequality Platform (PIP), which draws on national household surveys. Regional and global estimates are extrapolated to the year of the data release using GDP growth estimates and forecasts. For more details about the methodology, please refer to the [World Bank PIP documentation](https://datanalytics.worldbank.org/PIP-Methodology/lineupestimates.html#nowcasts).
* Depending on the country and year, the data refers either to income (after taxes and benefits) or to consumption, [per capita](#dod:per-capita). These are not perfectly comparable — consumption tends to be more evenly distributed than income. For most countries, we have only one option available. But when there is a mix of consumption and income data points, we process the data to keep one observation per country and year.

### Source

#### World Bank Poverty and Inequality Platform – World Bank Poverty and Inequality Platform (PIP)
Retrieved on: 2026-03-24  
Retrieved from: https://pip.worldbank.org  

#### Notes on our processing step for this indicator
For most countries in the dataset, estimates relate to disposable income or consumption, for all available years. Several countries, however, have a mix of income and consumption data points, with both data types sometimes available for particular years.

In most of our charts, we present the data with some data points dropped to present a single series for each country. This allows us to make readable visualizations that combine multiple countries. In choosing which data points to keep, we strike a balance between maintaining comparability over time and showing as long a time series as possible. As such, the exact approach varies across countries.


## Below $3 a day
Number of people living in households with an income or consumption below $3 per day.
Last updated: March 24, 2026  
Next update: September 2026  
Date range: 1963–2026  
Unit: people  


### How to cite this data

#### In-line citation
If you have limited space (e.g. in data visualizations), you can use this abbreviated in-line citation:  
World Bank Poverty and Inequality Platform (2026) – with major processing by Our World in Data

#### Full citation
World Bank Poverty and Inequality Platform (2026) – with major processing by Our World in Data. “Below $3 a day – World Bank” [dataset]. World Bank Poverty and Inequality Platform, “World Bank Poverty and Inequality Platform (PIP) 20260324_2021, 20260324_2017” [original data].
Source: World Bank Poverty and Inequality Platform (2026) – with major processing by Our World In Data

### What you should know about this data
* The World Bank defines extreme poverty as living on less than $3 per day. This threshold, known as the ["International Poverty Line"](#dod:international-poverty-line), is set so that poverty can be compared across countries. This indicator plays an important and successful role in focusing the world's attention on the very poorest people. The UN uses this indicator to track progress towards [ending extreme poverty by 2030](https://ourworldindata.org/sdgs/no-poverty).
* Two centuries ago, most of the world's population was extremely poor. Many believed that widespread poverty was inevitable. But this turned out to be wrong. Economic growth is possible, and poverty can decline. With this poverty line, we can track whether countries are leaving the worst poverty behind.
* This data is expressed in constant international dollars to adjust for inflation and differences in living costs between countries. Read more in our article, [What are international dollars?](https://ourworldindata.org/international-dollars)
* Many people, today and in the past, have no formal monetary income. This data accounts for that by including the estimated value of non-market income, such as food grown by subsistence farmers for their own use.
* The data comes from the World Bank's Poverty and Inequality Platform (PIP), which draws on national household surveys. Regional and global estimates are extrapolated to the year of the data release using GDP growth estimates and forecasts. For more details about the methodology, please refer to the [World Bank PIP documentation](https://datanalytics.worldbank.org/PIP-Methodology/lineupestimates.html#nowcasts).
* Depending on the country and year, the data refers either to income (after taxes and benefits) or to consumption, [per capita](#dod:per-capita). These are not perfectly comparable — consumption tends to be more evenly distributed than income. For most countries, we have only one option available. But when there is a mix of consumption and income data points, we process the data to keep one observation per country and year.

### Source

#### World Bank Poverty and Inequality Platform – World Bank Poverty and Inequality Platform (PIP)
Retrieved on: 2026-03-24  
Retrieved from: https://pip.worldbank.org  

#### Notes on our processing step for this indicator
For most countries in the dataset, estimates relate to disposable income or consumption, for all available years. Several countries, however, have a mix of income and consumption data points, with both data types sometimes available for particular years.

In most of our charts, we present the data with some data points dropped to present a single series for each country. This allows us to make readable visualizations that combine multiple countries. In choosing which data points to keep, we strike a balance between maintaining comparability over time and showing as long a time series as possible. As such, the exact approach varies across countries.


    