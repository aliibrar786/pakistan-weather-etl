"""Run the full ETL pipeline: extract -> validate -> transform -> load."""

import logging
import sys

from etl.extract import extract_city
from etl.load import load_to_db
from etl.transform import transform
from etl.validate import validate_records

logger = logging.getLogger("pipeline")

CITIES = {
    "Lahore": (31.5204, 74.3587),
    "Karachi": (24.8607, 67.0011),
    "Islamabad": (33.6844, 73.0479),
    "Peshawar": (34.0151, 71.5249),
    "Quetta": (30.1798, 66.9750),
    "Multan": (30.1575, 71.5249),
}
START, END = "2020-01-01", "2025-12-31"
DB_PATH = "data/weather.db"


def run_pipeline():
    all_valid, total_rejected, failed = [], 0, []

    for city, (lat, lon) in CITIES.items():
        try:
            raw = extract_city(city, lat, lon, START, END)  # 1. extract
            valid, rejected = validate_records(raw, city)  # 2. validate
        except Exception as err:  # one bad city must not stop the others
            logger.error("%s: skipped (%s)", city, err)
            failed.append(city)
            continue
        all_valid.extend(valid)
        total_rejected += len(rejected)
        logger.info("%s: %d valid, %d rejected", city, len(valid), len(rejected))

    if not all_valid:
        raise RuntimeError("No valid records to load")

    df = transform(all_valid)  # 3. transform
    loaded, in_table = load_to_db(df, DB_PATH)  # 4. load
    logger.info(
        "Done: %d rows loaded, %d rows now in table, %d rejected, failed cities: %s",
        loaded, in_table, total_rejected, failed or "none",
    )
    return in_table


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler("pipeline.log")],
    )
    run_pipeline()
