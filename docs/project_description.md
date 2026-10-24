# Weather Patterns Across Major Pakistani Cities: ETL and EDA Pipeline

## 1. Problem

Weather is different across Pakistan's cities. For example, some cities are hotter, while others are colder or receive different amounts of rain. In this project, we will build an automated pipeline to collect and study daily weather data for six major Pakistani cities from 2020 to 2025. We will focus on temperature, precipitation, and wind speed.

## 2. Data Source and Dataset

We will use the free Open-Meteo Historical Weather API to collect daily weather data for Lahore, Karachi, Islamabad, Peshawar, Quetta, and Multan. The API is free for non-commercial use and requires no API key. We will collect maximum temperature, minimum temperature, total precipitation, and maximum wind speed.

The date range contains 2,192 days per city, including the leap days in 2020 and 2024. For six cities, the expected total is **13,152 daily records**, if data is available for every day. We chose this dataset because it is free to access, covers several cities and years, and is useful for studying weather trends over time.

## 3. ETL Pipeline

The pipeline will have four main steps:

1. **Extract:** Request weather data from the API for each city. Use a timeout and retry failed requests up to three times. Save the original JSON responses.
2. **Validate:** Use Pydantic to check the records. For example, check that temperatures are within the project's chosen range of -20°C to 55°C, precipitation is not negative, and dates are valid. Save rejected records to a CSV file and record the problems in a log.
3. **Transform:** Use pandas to handle missing values, remove duplicate records, correct data types, and create extra columns such as average temperature, year, month, and season.
4. **Load:** Save the cleaned and validated records in a SQLite database.

## 4. Where the Data Will Be Stored

We will store the cleaned data in a SQLite database named `weather.db`, in a table called `daily_weather`. The combination of `city` and `date` will be the primary key, so each city can have only one record for a particular date. We will use an upsert operation so that running the pipeline again updates existing records instead of creating duplicates.

## 5. Exploratory Data Analysis (EDA) Plan

We will use the data to explore these questions:

1. Which city has the highest and lowest average temperature?
2. How does average temperature change from year to year?
3. Which month receives the most precipitation in each city?
4. Is there a relationship between temperature and precipitation?
5. How do summer and winter weather compare across the six cities?

We will present the findings with bar charts, histograms, trend lines, a monthly heatmap, and a correlation matrix. The results will be shown in an interactive Streamlit web app, which we plan to deploy on Streamlit Community Cloud.
