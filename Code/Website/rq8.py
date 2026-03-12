import streamlit as st
import polars as pl
import plotly.graph_objects as go
import os

BASE_DIR = "../data"

st.set_page_config(page_title="Traffic Analysis", layout="wide")
st.title("Rush-Hour Traffic & Home Office Effect (2021–2025)")

@st.cache_data
def load_data():
    df = (
        pl.read_csv(os.path.join(BASE_DIR, "MergeData", "holy_file.csv"), infer_schema_length=0)
        .filter(pl.col("Zst") == "1194")
        .with_columns(
            pl.col("date").str.to_datetime("%d.%m.%Y %H:%M").alias("datetime")
        )
        .with_columns(
            pl.col("datetime").dt.year().alias("year"),
            pl.col("datetime").dt.month().alias("month"),
            pl.col("datetime").dt.hour().alias("hour"),
            pl.col("datetime").dt.weekday().alias("weekday"),
            pl.col("datetime").dt.date().alias("day")
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
        .filter(pl.col("weekday") <= 5)
    )
    return df

df = load_data()

morning = df.filter(pl.col("hour").is_between(6, 9))
evening = df.filter(pl.col("hour").is_between(16, 18))

def avg_by_month(df, direction_col):
    return (
        df
        .group_by(["year", "month", "day"])
        .agg(pl.col(direction_col).sum().alias("daily_rush"))
        .group_by(["year", "month"])
        .agg(pl.col("daily_rush").mean().alias("avg_rush"))
        .sort(["year", "month"])
        .with_columns(
            (pl.col("year").cast(pl.Utf8) + "-" + pl.col("month").cast(pl.Utf8).str.zfill(2)).alias("year_month")
        )
        .to_pandas()
    )

df_morning = avg_by_month(morning, "KFZ_R1")
df_evening = avg_by_month(evening, "KFZ_R2")

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df_morning["year_month"],
    y=df_morning["avg_rush"],
    name="Morning Rush – into Kiel (6–9h, R1 North)",
    mode="lines+markers",
    line=dict(color="steelblue", width=2),
    marker=dict(size=5),
))

fig.add_trace(go.Scatter(
    x=df_evening["year_month"],
    y=df_evening["avg_rush"],
    name="Evening Rush – out of Kiel (16–18h, R2 South)",
    mode="lines+markers",
    line=dict(color="tomato", width=2),
    marker=dict(size=5),
))

fig.update_layout(
    title="Avg. Rush-Hour Traffic on A215 – AK Kiel-West (Weekdays only)",
    xaxis=dict(title="Month", tickangle=-45),
    yaxis=dict(title="Avg. Vehicles during Rush Hour", rangemode="tozero"),
    legend=dict(x=0.01, y=0.01),
    height=550,
)

st.plotly_chart(fig, use_container_width=True)
