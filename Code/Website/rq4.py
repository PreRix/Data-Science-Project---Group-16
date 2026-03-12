import streamlit as st
import polars as pl
import plotly.express as px
import os

BASE_DIR = "../../data"

st.set_page_config(page_title="Traffic Analysis", layout="wide")
st.title("Weekend vs. Weekday Traffic Load (A215 - AK Kiel-West)")

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
            pl.col("datetime").dt.weekday().alias("weekday"),
            pl.col("datetime").dt.date().alias("day")
        )

        .with_columns([
            pl.when(pl.col("K_KFZ_R1").str.strip_chars().is_in(["a","d"]))
            .then(None)
            .otherwise(
                pl.col("KFZ_R1")
                .str.strip_chars()
                .str.extract(r"^(-?\d+)")
                .cast(pl.Float64)
            )
            .alias("KFZ_R1"),

            pl.when(pl.col("K_KFZ_R2").str.strip_chars().is_in(["a","d"]))
            .then(None)
            .otherwise(
                pl.col("KFZ_R2")
                .str.strip_chars()
                .str.extract(r"^(-?\d+)")
                .cast(pl.Float64)
            )
            .alias("KFZ_R2"),
        ])

        .with_columns(
            (pl.col("KFZ_R1") + pl.col("KFZ_R2")).alias("vehicle_count")
        )
    )

    return df


df = load_data()


def weekday_share(df):

    daily = (
        df
        .group_by(["year","day","weekday"])
        .agg(pl.col("vehicle_count").sum().alias("daily_traffic"))
    )

    daily = daily.with_columns(
        pl.when(pl.col("weekday") <= 5)
        .then(pl.lit("Weekday"))
        .when(pl.col("weekday") == 6)
        .then(pl.lit("Saturday"))
        .otherwise(pl.lit("Sunday"))
        .alias("day_type")
    )

    share = (
        daily
        .group_by(["year","day_type"])
        .agg(pl.col("daily_traffic").mean().alias("vehicle_count"))
        .sort(["year","day_type"])
    )

    return share


df_share = weekday_share(df)

years = sorted(df_share["year"].unique().to_list())
cols = st.columns(len(years))

for col, year in zip(cols, years):

    with col:

        df_year = df_share.filter(pl.col("year") == year)

        fig = px.pie(
            df_year.to_pandas(),
            values="vehicle_count",
            names="day_type",
            title=str(year),
            category_orders={
                "day_type": ["Weekday", "Saturday", "Sunday"]
            }
        )

        fig.update_traces(textposition="inside", textinfo="percent+label")

        st.plotly_chart(fig, use_container_width=True)
