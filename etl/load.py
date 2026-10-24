
import sqlite3

from etl.validate import WeatherRecord


def create_table(connection):
    connection.execute("""
        CREATE TABLE IF NOT EXISTS weather (
            city TEXT NOT NULL,
            date TEXT NOT NULL,
            temp_max REAL NOT NULL,
            temp_min REAL NOT NULL,
            precipitation REAL NOT NULL,
            wind REAL NOT NULL,
            PRIMARY KEY (city, date)
        )
    """)


def load_records(connection, records: list[WeatherRecord]):
    connection.executemany("""
        INSERT INTO weather (
            city, date, temp_max, temp_min, precipitation, wind
        )
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(city, date) DO UPDATE SET
            temp_max = excluded.temp_max,
            temp_min = excluded.temp_min,
            precipitation = excluded.precipitation,
            wind = excluded.wind
    """, [
        (
            record.city,
            record.date.isoformat(),
            record.temp_max,
            record.temp_min,
            record.precipitation,
            record.wind,
        )
        for record in records
    ])


def main():
    connection = sqlite3.connect("weather.db")
    try:
        create_table(connection)
        connection.commit()
        print("Weather table is ready.")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
