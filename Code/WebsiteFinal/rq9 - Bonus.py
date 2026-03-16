import streamlit as st
import polars as pl
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import plotly.io as pio

pio.templates["custom"] = go.layout.Template(
    layout=go.Layout(
        font=dict(size=18),
        title=dict(font=dict(size=20)),
        legend=dict(font=dict(size=16)),
        xaxis=dict(title=dict(font=dict(size=17)), tickfont=dict(size=15)),
        yaxis=dict(title=dict(font=dict(size=17)), tickfont=dict(size=15)),
    )
)
pio.templates.default = "plotly+custom"

st.set_page_config(page_title="Traffic Analysis", layout="wide")
st.title("Extreme Weather & Traffic Disruption")

st.markdown("""
<style>
    html, body, [class*="css"] {
        font-size: 22px;
    }
</style>
""", unsafe_allow_html=True)

CSV_HOLYFILE = "https://cloud.rz.uni-kiel.de/public.php/dav/files/NnYrtwJ7FLqC6en/?accept=zip"
CSV_WEATHER_DATA = "https://cloud.rz.uni-kiel.de/public.php/dav/files/dYtnayFdSte8EPN/?accept=zip"

RAIN_THRESHOLD = 10.0
SNOW_THRESHOLD = 1.0
WINDOW_BEFORE = 2
WINDOW_AFTER = 4

@st.cache_data(show_spinner="Loading Measuring Points data …")
def load_traffic(path):
    return (
        pl.read_csv(path, infer_schema_length=0)
        .filter(pl.col("Zst") == "1194")
        .with_columns(
            pl.col("date").str.to_datetime("%d.%m.%Y %H:%M").alias("datetime")
        )
        .with_columns([
            pl.when(pl.col("K_KFZ_R1").str.strip_chars().is_in(["a", "d"]))
            .then(None)
            .otherwise(
                pl.col("KFZ_R1").str.strip_chars().str.extract(r"^(-?\d+)").cast(pl.Float64)
            )
            .alias("KFZ_R1"),
            pl.when(pl.col("K_KFZ_R2").str.strip_chars().is_in(["a", "d"]))
            .then(None)
            .otherwise(
                pl.col("KFZ_R2").str.strip_chars().str.extract(r"^(-?\d+)").cast(pl.Float64)
            )
            .alias("KFZ_R2"),
        ])
        .with_columns(
            (pl.col("KFZ_R1") + pl.col("KFZ_R2")).alias("vehicle_count")
        )
        .select(["datetime", "vehicle_count"])
    )

@st.cache_data(show_spinner="Loading Weather data …")
def load_weather(path):
    return (
        pl.read_csv(path)
        .filter(pl.col("location_Zst") == 1194)
        .with_columns(
            pl.col("date").str.to_datetime("%d.%m.%Y %H:%M").alias("datetime")
        )
        .select(["datetime", "precipitation", "snowfall"])
    )

try:
    df_traffic = load_traffic(CSV_HOLYFILE)
except FileNotFoundError:
    st.error(f"File not found: {CSV_HOLYFILE}")
    st.stop()

try:
    df_weather = load_weather(CSV_WEATHER_DATA)
except FileNotFoundError:
    st.error(f"File not found: {CSV_WEATHER_DATA}")
    st.stop()

df = df_traffic.join(df_weather, on="datetime", how="left")

extreme_times = (
    df
    .filter(
        (pl.col("precipitation") > RAIN_THRESHOLD) |
        (pl.col("snowfall") > SNOW_THRESHOLD)
    )
    .select("datetime")
    .to_series()
    .to_list()
)

df_pd = df.select(["datetime", "vehicle_count"]).to_pandas()
df_pd["datetime"] = pd.to_datetime(df_pd["datetime"])
df_pd = df_pd.set_index("datetime").sort_index()

df_pd["hour"] = df_pd.index.hour
hourly_baseline = df_pd.groupby("hour")["vehicle_count"].median()

records = []
for event_time in extreme_times:
    event_pd = pd.Timestamp(event_time)
    for offset in range(-WINDOW_BEFORE, WINDOW_AFTER + 1):
        target = event_pd + pd.Timedelta(hours=offset)
        if target in df_pd.index:
            val = df_pd.loc[target, "vehicle_count"]
            if isinstance(val, pd.Series):
                val = val.iloc[0]
            if pd.notna(val):
                hour_baseline = hourly_baseline[target.hour]
                relative = (val / hour_baseline) * 100
                records.append({"offset": offset, "relative_count": relative})

df_records = pd.DataFrame(records)

if df_records.empty:
    st.warning("Keine Daten im Fenster gefunden.")
else:
    median_line = df_records.groupby("offset")["relative_count"].median().reset_index()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_records["offset"],
        y=df_records["relative_count"],
        mode="markers",
        marker=dict(color="steelblue", size=4, opacity=0.25),
        name="Individual Events",
    ))

    fig.add_trace(go.Scatter(
        x=median_line["offset"],
        y=median_line["relative_count"],
        mode="lines+markers",
        line=dict(color="tomato", width=3),
        marker=dict(size=7),
        name="Median",
    ))

    fig.add_vline(x=0, line_dash="dash", line_color="white", opacity=0.5)
    fig.add_hline(y=100, line_dash="dot", line_color="gray", opacity=0.5)

    fig.update_layout(
        title=f"Relative Traffic around Extreme Weather Events (Zst. 1194, Rain >{RAIN_THRESHOLD}mm/h or Snow >{SNOW_THRESHOLD}cm/h)",
        xaxis=dict(title="Hours relative to Event Start", tickmode="linear", dtick=1),
        yaxis=dict(title="Relative Vehicle Count (% of Hourly Median)"),
        legend=dict(x=0.01, y=0.99),
        height=550,
    )

    st.plotly_chart(fig, use_container_width=True)
