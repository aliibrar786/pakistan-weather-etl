import sqlite3
from pathlib import Path


def load_to_db(df, db_path="data/weather.db"):
    """Create daily_weather (PK city+date) and upsert every row of df.
    Returns the number of rows loaded."""

    columns = [
        "city", "date", "temp_max", "temp_min",
        "precipitation", "wind", "temp_avg",
        "year", "month", "season"
    ]

    rows = [
        tuple(r)
        for r in df[columns].itertuples(index=False, name=None)
    ]

    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS daily_weather (
                city TEXT NOT NULL,
                date TEXT NOT NULL,
                temp_max REAL,
                temp_min REAL,
                precipitation REAL,
                wind REAL,
                temp_avg REAL,
                year INTEGER,
                month INTEGER,
                season TEXT,
                PRIMARY KEY (city, date)
            )
        """)

        con.executemany(
            "INSERT OR REPLACE INTO daily_weather VALUES (?,?,?,?,?,?,?,?,?,?)",
            rows
        )

        count = con.execute(
            "SELECT COUNT(*) FROM daily_weather"
        ).fetchone()[0]

    return len(rows), count