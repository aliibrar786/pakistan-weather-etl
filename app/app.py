import os
import sqlite3
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

DB = os.environ.get("WEATHER_DB", Path(__file__).resolve().parent.parent / "data" / "weather.db")

st.set_page_config(page_title="Pakistan Weather 2020-2025", layout="wide")


@st.cache_data
def load():
    with sqlite3.connect(DB) as con:
        df = pd.read_sql("SELECT * FROM daily_weather", con, parse_dates=["date"])
    df["temp_avg"] = (df.temp_max + df.temp_min) / 2
    df["year"], df["month"] = df.date.dt.year, df.date.dt.month
    return df


df = load()
first, last = df.date.min().date(), df.date.max().date()

st.title("Pakistan Weather, 2020-2025")
city = st.sidebar.selectbox("City", sorted(df.city.unique()))
start, end = st.sidebar.slider("Date range", first, last, (first, last))

period = df[df.date.between(pd.Timestamp(start), pd.Timestamp(end))]
d = period[period.city == city]

col1, col2, col3 = st.columns(3)
col1.metric("Average temperature", f"{d.temp_avg.mean():.1f} °C")
col2.metric("Hottest day", f"{d.temp_max.max():.1f} °C")
col3.metric("Total rainfall", f"{d.precipitation.sum():,.0f} mm")

left, right = st.columns(2)

left.subheader(f"Monthly temperature, {city}")
left.line_chart(d.set_index("date")[["temp_max", "temp_avg", "temp_min"]].resample("MS").mean(), y_label="°C")

right.subheader(f"Average rainfall by month, {city}")
rain = d.groupby(["year", "month"]).precipitation.sum().groupby("month").mean()
right.bar_chart(rain, x_label="Month", y_label="mm")

left.subheader(f"Temperature heatmap, {city}")
heat = d.groupby(["year", "month"], as_index=False).temp_avg.mean()
left.altair_chart(
    alt.Chart(heat).mark_rect().encode(
        x="month:O",
        y="year:O",
        color=alt.Color("temp_avg:Q", scale=alt.Scale(scheme="redyellowblue", reverse=True), title="°C"),
        tooltip=["year", "month", alt.Tooltip("temp_avg:Q", format=".1f")],
    )
)

by_city = period.groupby("city").agg(temp=("temp_avg", "mean"), rain=("precipitation", "sum"))
right.subheader("Average temperature, all cities")
right.bar_chart(by_city.temp.sort_values(), x_label="City", y_label="°C")

st.subheader("Key findings for the selected dates")
st.write(
    f"- Hottest city: **{by_city.temp.idxmax()}** ({by_city.temp.max():.1f} °C average); "
    f"coldest: **{by_city.temp.idxmin()}** ({by_city.temp.min():.1f} °C).\n"
    f"- Wettest city: **{by_city.rain.idxmax()}** ({by_city.rain.max():,.0f} mm in total).\n"
    f"- In {city}, the rainiest month is **{pd.Timestamp(2000, int(rain.idxmax()), 1):%B}** "
    f"and the correlation between temperature and rainfall is **{d.temp_avg.corr(d.precipitation, method='spearman'):.2f}**."
)