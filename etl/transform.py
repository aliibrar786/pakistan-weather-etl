"""Transform stage: turn validated records into a clean pandas DataFrame."""

import logging

import pandas as pd

logger = logging.getLogger(__name__)

COLUMNS = ["city", "date", "temp_max", "temp_min", "precipitation", "wind"]
NUMERIC = ["temp_max", "temp_min", "precipitation", "wind"]
SEASONS = {
    12: "Winter",
    1: "Winter",
    2: "Winter",
    3: "Spring",
    4: "Spring",
    5: "Spring",
    6: "Summer",
    7: "Summer",
    8: "Summer",
    9: "Autumn",
    10: "Autumn",
    11: "Autumn",
}


def transform(valid_records):
    """Take a list of dicts (city, date, temp_max, temp_min, precipitation, wind)
    and return a clean DataFrame with temp_avg, year, month and season added."""
    df = pd.DataFrame(valid_records, columns=COLUMNS)
    logger.info("Transform: %d records received", len(df))

    # 1. fix data types
    df["city"] = df["city"].astype(str).str.strip()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    for col in NUMERIC:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["city", "date"])

    # 2. remove duplicates (one row per city and date)
    before = len(df)
    df = df.drop_duplicates(subset=["city", "date"], keep="last")
    logger.info("Transform: removed %d duplicate rows", before - len(df))

    # 3. handle missing values (per city, in date order)
    df = df.sort_values(["city", "date"]).reset_index(drop=True)
    missing = int(df[NUMERIC].isna().sum().sum())
    for col in ["temp_max", "temp_min", "wind"]:
        df[col] = df.groupby("city")[col].transform(
            lambda s: s.interpolate(limit_direction="both")
        )
    df["precipitation"] = df["precipitation"].fillna(
        0.0
    )  # assumption: no data = no rain
    logger.info("Transform: filled %d missing values", missing)

    # 4. derived columns
    df["temp_avg"] = ((df["temp_max"] + df["temp_min"]) / 2).round(2)
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["season"] = df["month"].map(SEASONS)

    df["date"] = df["date"].dt.strftime("%Y-%m-%d")  # plain text date for SQLite
    logger.info("Transform: %d clean rows returned", len(df))
    return df


if __name__ == "__main__":
    import json

    logging.basicConfig(level=logging.INFO)
    with open("data/raw/lahore.json", encoding="utf-8") as f:
        raw = json.load(f)
    d = raw["daily"]
    records = [
        {
            "city": raw["city"],
            "date": d["time"][i],
            "temp_max": d["temperature_2m_max"][i],
            "temp_min": d["temperature_2m_min"][i],
            "precipitation": d["precipitation_sum"][i],
            "wind": d["wind_speed_10m_max"][i],
        }
        for i in range(len(d["time"]))
    ]
    records.append(dict(records[0]))  # test duplicate
    records[3]["temp_max"] = None  # test missing value
    print(transform(records).head())
