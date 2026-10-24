
from datetime import date
from pydantic import BaseModel, ConfigDict, Field, model_validator


class WeatherRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    city: str = Field(min_length=1)
    date: date
    temp_max: float
    temp_min: float
    precipitation: float = Field(ge=0)
    wind: float = Field(ge=0)

    @model_validator(mode="after")
    def check_temperatures(self):
        if self.temp_min > self.temp_max:
            raise ValueError("temp_min cannot exceed temp_max")
        return self


def validate_records(raw: dict, city: str | None = None) -> list[WeatherRecord]:
    if not isinstance(raw, dict):
        raise ValueError("Raw weather data must be a dictionary")

    daily = raw.get("daily")
    if not isinstance(daily, dict):
        raise ValueError("Missing or invalid 'daily' object")

    required = {
        "time",
        "temperature_2m_max",
        "temperature_2m_min",
        "precipitation_sum",
        "wind_speed_10m_max",
    }

    missing = required - daily.keys()
    if missing:
        raise ValueError(f"Missing daily fields: {sorted(missing)}")

    city = city or raw.get("city")
    if not isinstance(city, str) or not city.strip():
        raise ValueError("City is required; pass city='Lahore'")

    dates = daily["time"]
    temp_max = daily["temperature_2m_max"]
    temp_min = daily["temperature_2m_min"]
    precipitation = daily["precipitation_sum"]
    wind = daily["wind_speed_10m_max"]

    lists = {
        "time": dates,
        "temperature_2m_max": temp_max,
        "temperature_2m_min": temp_min,
        "precipitation_sum": precipitation,
        "wind_speed_10m_max": wind,
    }

    for field, values in lists.items():
        if not isinstance(values, list):
            raise ValueError(f"Daily field '{field}' must be a list")

    lengths = {len(values) for values in lists.values()}
    if len(lengths) != 1:
        raise ValueError("All five daily lists must have equal lengths")

    records = []

    for i in range(len(dates)):
        record = WeatherRecord(
            city=city.strip(),
            date=dates[i],
            temp_max=temp_max[i],
            temp_min=temp_min[i],
            precipitation=precipitation[i],
            wind=wind[i],
        )
        records.append(record)

    return records
