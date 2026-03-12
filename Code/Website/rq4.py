import streamlit as st
import polars as pl
import plotly.express as px

# --------------------------------------------------
# Streamlit Page Config
# --------------------------------------------------

st.set_page_config(
    page_title="Traffic Analysis",
    layout="wide"
)

st.title("Weekend vs. Weekday Traffic Share")

# --------------------------------------------------
# Load Data
# --------------------------------------------------

@st.cache_data
def load_data():

    df = pl.read_csv("holy_file.csv")

    # Spaces entfernen und zu Integer konvertieren
    df = df.with_columns([
        pl.col("KFZ_R1").str.strip_chars().cast(pl.Int64),
        pl.col("KFZ_R2").str.strip_chars().cast(pl.Int64),
    ])

    # Gesamtverkehr
    df = df.with_columns(
        (pl.col("KFZ_R1") + pl.col("KFZ_R2")).alias("vehicle_count")
    )

    # Datum parsen
    df = df.with_columns(
        pl.col("date").str.strptime(pl.Datetime, "%d.%m.%Y %H:%M")
    )

    return df


df = load_data()

# --------------------------------------------------
# Compute Weekday Share (Average Traffic per Day)
# --------------------------------------------------

def weekday_share(df: pl.DataFrame):

    df_daily = (
        df
        .with_columns([
            pl.col("date").dt.date().alias("day"),
            pl.col("date").dt.year().alias("year"),
            pl.col("date").dt.weekday().alias("weekday")
        ])
        # Verkehr pro Tag berechnen
        .group_by(["day", "year", "weekday"])
        .agg(
            pl.col("vehicle_count").sum().alias("daily_traffic")
        )
    )

    df_share = (
        df_daily
        .with_columns([
            pl.when(pl.col("weekday") <= 5)
            .then(pl.lit("Weekday (Mon–Fri)"))
            .when(pl.col("weekday") == 6)
            .then(pl.lit("Saturday"))
            .otherwise(pl.lit("Sunday"))
            .alias("day_type")
        ])
        # Durchschnitt pro Tagestyp
        .group_by(["year", "day_type"])
        .agg(
            pl.col("daily_traffic").mean().alias("vehicle_count")
        )
        .sort(["year", "day_type"])
    )

    return df_share


df_share = weekday_share(df)

# --------------------------------------------------
# Years for Visualization
# --------------------------------------------------

years = sorted(df_share["year"].unique().to_list())

# --------------------------------------------------
# Render Pie Charts
# --------------------------------------------------

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
                "day_type": ["Weekday (Mon–Fri)", "Saturday", "Sunday"]
            },
            color="day_type",
            color_discrete_map={
                "Weekday (Mon–Fri)": "#636EFA",
                "Saturday": "#EF553B",
                "Sunday": "#00CC96"
            }
        )

        fig.update_traces(
            textposition="inside",
            textinfo="percent+label"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )
