"""Extract stage: download daily weather data from the Open-Meteo archive API."""

import json
import logging
import time
from pathlib import Path

import requests

logger = logging.getLogger(__name__)

API_URL = "https://archive-api.open-meteo.com/v1/archive"
DAILY_VARS = (
    "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max"
)
TIMEOUT = 30
MAX_RETRIES = 3
RAW_DIR = Path("data/raw")


def extract_city(city, lat, lon, start, end):
    """Fetch daily weather for one city and return the raw JSON as a dict.

    start / end are strings in YYYY-MM-DD format.
    Retries up to MAX_RETRIES times; the raw response is saved in data/raw/.
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start,
        "end_date": end,
        "daily": DAILY_VARS,
        "timezone": "Asia/Karachi",
    }
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(API_URL, params=params, timeout=TIMEOUT)
            response.raise_for_status()
            data = response.json()
            break
        except (requests.RequestException, ValueError) as err:
            last_error = err
            logger.warning(
                "%s: attempt %d/%d failed: %s", city, attempt, MAX_RETRIES, err
            )
            if attempt < MAX_RETRIES:
                time.sleep(2 * attempt)  # wait a little longer each time
    else:
        raise RuntimeError(
            f"Extraction failed for {city} after {MAX_RETRIES} attempts"
        ) from last_error

    data["city"] = city  # tag the response so later stages know the city
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    out_file = RAW_DIR / f"{city.lower()}.json"
    out_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    logger.info("%s: saved %d days to %s", city, len(data["daily"]["time"]), out_file)
    return data


if __name__ == "__main__":
    # quick test: one city, one month
    logging.basicConfig(level=logging.INFO)
    result = extract_city("Lahore", 31.5204, 74.3587, "2020-01-01", "2020-01-31")
    print(list(result["daily"].keys()))
