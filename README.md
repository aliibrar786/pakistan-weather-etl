# Pakistan Weather ETL + EDA

ETL pipeline and exploratory analysis of daily weather for six Pakistani cities
(Lahore, Karachi, Islamabad, Peshawar, Quetta, Multan), 2020-2025, using the free
[Open-Meteo](https://open-meteo.com/) archive API (no API key needed).

**Pipeline:** extract (API, timeout + 3 retries) -> validate (Pydantic, rejected rows saved to CSV)
-> transform (pandas: types, duplicates, missing values, temp_avg/year/month/season)
-> load (SQLite `data/weather.db`, table `daily_weather`, primary key `city, date`, upsert).

## Setup
```
git clone https://github.com/aliibrar786/pakistan-weather-etl.git
cd pakistan-weather-etl
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Run
```
python run_pipeline.py          # builds data/weather.db (needs internet)
streamlit run app/app.py        # opens the web app
```
Pipeline log: `pipeline.log`. Rejected records: `data/rejected/rejected_records.csv`.

## Project layout
| Path | Purpose |
|---|---|
| `etl/extract.py` | Download raw JSON from Open-Meteo |
| `etl/validate.py` | Pydantic `WeatherRecord` validation |
| `etl/transform.py` | pandas cleaning and derived columns |
| `etl/load.py` | SQLite loading (upsert) |
| `run_pipeline.py` | Runs all four stages with logging |
| `eda/eda_basic.ipynb`, `eda/eda_advanced.ipynb` | EDA notebooks |
| `app/app.py` | Streamlit web app |
| `docs/project_description.md` | Project description |

## Team
Muhammad Ali (ETL core, integration), Asjad Rauf (validation, loading), Rao (EDA, web app), Asfand (docs, testing).

## Web app
Live link: https://pakistan-weather-ali.streamlit.app/
