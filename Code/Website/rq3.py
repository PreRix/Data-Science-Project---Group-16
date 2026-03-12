import streamlit as st
import polars as pl
import plotly.graph_objects as go
import os

BASE_DIR         = "../../data"

st.set_page_config(page_title="Traffic Analysis", layout="wide")
st.title("Long-Term Traffic Growth (2021–2025)")

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
        .with_columns(
            (pl.col("KFZ_R1") + pl.col("KFZ_R2")).alias("vehicle_count")
        )
    )
    return df

@st.cache_data
def load_registrations():
    return (
        pl.read_csv(os.path.join(BASE_DIR, "RegistrationData", "kiel_registration_data.CSV"), infer_schema_length=0)
        .select([
            pl.col("Year").cast(pl.Int64).alias("year"),
            pl.col("VT_Kraftfahrzeuge_insgesamt")
              .str.replace_all(r"\.", "")
              .cast(pl.Int64)
              .alias("registrations")
        ])
    )

df = load_data()
df_reg = load_registrations()

def yearly_avg_traffic(df):
    daily = (
        df
        .group_by(["year", "day", "Zst"])
        .agg(pl.col("vehicle_count").sum().alias("daily_traffic"))
    )
    return (
        daily
        .group_by("year")
        .agg(pl.col("daily_traffic").mean().alias("avg_daily_traffic"))
        .sort("year")
    )

df_traffic = yearly_avg_traffic(df)
df_combined = df_traffic.join(df_reg, on="year", how="left").sort("year")
df_pd = df_combined.to_pandas()

fig = go.Figure()

fig.add_trace(go.Bar(
    x=df_pd["year"],
    y=df_pd["registrations"],
    name="Registered Vehicles (Kiel)",
    marker_color="steelblue",
    opacity=0.7,
    yaxis="y1"
))

fig.add_trace(go.Scatter(
    x=df_pd["year"],
    y=df_pd["avg_daily_traffic"],
    name="Avg. Daily Traffic (Zst. 1194)",
    mode="lines+markers",
    line=dict(color="tomato", width=3),
    marker=dict(size=8),
    yaxis="y2"
))

fig.update_layout(
    title="Registered Vehicles vs. Avg. Daily Traffic (Zst. 1194)",
    xaxis=dict(title="Year", tickmode="linear", dtick=1),
    yaxis=dict(
        title=dict(text="Registered Vehicles (Kiel)", font=dict(color="steelblue")),
        tickfont=dict(color="steelblue"),
        range=[130_000, 133_000],
    ),
    yaxis2=dict(
        title=dict(text="Avg. Vehicles / Day", font=dict(color="tomato")),
        tickfont=dict(color="tomato"),
        overlaying="y",
        side="right",
        showgrid=False,
        range=[60_000, 76_000],
    ),
    legend=dict(x=0.01, y=0.99),
    height=550,
)

st.plotly_chart(fig, use_container_width=True)
