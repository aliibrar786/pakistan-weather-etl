
import csv
import logging
from datetime import date
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

logger = logging.getLogger(__name__)


class WeatherRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    city: str = Field(min_length=1)
    date: date
    temp_max: float = Field(ge=-20, le=55)
    temp_min: float = Field(ge=-20, le=55)
    precipitation: float = Field(ge=0)
    wind: float = Field(ge=0)

    @model_validator(mode="after")
    def check_temperatures(self):
        if self.temp_min > self.temp_max:
            raise ValueError("temp_min cannot exceed temp_max")
        return self


def validate_records(raw: dict, city: str | None = None):
    """Return valid and rejected records separately."""

    if not isinstance(raw, dict):
        raise ValueError("Raw weather data must be a dictionary")

    daily = raw.get("daily")
    if not isinstance(daily, dict):
        raise ValueError("Missing or invalid 'daily' object")

    required = [
        "time",
        "temperature_2m_max",
        "temperature_2m_min",
        "precipitation_sum",
        "wind_speed_10m_max",
    ]

    missing = set(required) - daily.keys()
    if missing:
        raise ValueError(f"Missing daily fields: {sorted(missing)}")

    city = city or raw.get("city")
    if not isinstance(city, str) or not city.strip():
        raise ValueError("City is required")

    for field in required:
        if not isinstance(daily[field], list):
            raise ValueError(f"Daily field '{field}' must be a list")

    lengths = {len(daily[field]) for field in required}
    if len(lengths) != 1:
        raise ValueError("All five daily lists must have equal lengths")

    valid_records = []
    rejected_records = []

    for i in range(len(daily["time"])):
        row = {
            "city": city.strip(),
            "date": daily["time"][i],
            "temp_max": daily["temperature_2m_max"][i],
            "temp_min": daily["temperature_2m_min"][i],
            "precipitation": daily["precipitation_sum"][i],
            "wind": daily["wind_speed_10m_max"][i],
        }

        try:
            record = WeatherRecord(**row)
            valid_records.append(record.model_dump(mode="json"))

        except ValidationError as error:
            rejected_row = row.copy()
            rejected_row["reason"] = "; ".join(
                f"{item['loc']}: {item['msg']}"
                for item in error.errors()
            )
            rejected_records.append(rejected_row)

    logger.info(
        "Validation complete: %d valid, %d rejected",
        len(valid_records),
        len(rejected_records),
    )

    if rejected_records:
        csv_path = Path("data/rejected/rejected_records.csv")
        csv_path.parent.mkdir(parents=True, exist_ok=True)

        file_exists = csv_path.exists() and csv_path.stat().st_size > 0

        with csv_path.open("a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "city",
                    "date",
                    "temp_max",
                    "temp_min",
                    "precipitation",
                    "wind",
                    "reason",
                ],
            )

            if not file_exists:
                writer.writeheader()

            writer.writerows(rejected_records)

        logger.warning(
            "Saved %d rejected records to %s",
            len(rejected_records),
            csv_path,
        )

    return valid_records, rejected_records
