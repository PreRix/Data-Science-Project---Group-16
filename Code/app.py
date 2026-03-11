import streamlit as st
import polars as pl
import plotly.express as px


# Page configuration
st.set_page_config(page_title="Traffic Data Visualization", layout="wide")
st.title("Vehicle Count Analysis")

# Data loading & pre-processing
@st.cache_data
def load_data():
    # Loads the CSV file and prepares the data
    df = pl.read_csv("holy_file.csv")
    
    # Remove spaces and cast to Integer
    df = df.with_columns([
        pl.col("KFZ_R1").str.strip_chars().cast(pl.Int64),
        pl.col("KFZ_R2").str.strip_chars().cast(pl.Int64),
    ])

    # Number of vehicles in both directions to sum
    df = df.with_columns(
        (pl.col("KFZ_R1") + pl.col("KFZ_R2")).alias("vehicle_count")
    )

    # Date parsen (German format: DD.MM.YYYY HH:MM)
    df = df.with_columns(
        pl.col("date").str.strptime(pl.Datetime, "%d.%m.%Y %H:%M").alias("date")
    )

    # Year as separate column for the annual comparisons
    df = df.with_columns(
        pl.col("date").dt.year().alias("year")
    )
    return df


# Aggregation functions
def bin_by_temperature(df_polars, bin_size=2):

    # Round temperature to nearest bin_size°C step
    return (
        df_polars
        
        # Create temp_bin column by rounding temperature down to nearest bin
        .with_columns(
            (pl.col("temperature_2m") // bin_size * bin_size).alias("temp_bin")
        )
        # group_by groups all rows that share the same bin AND year together
        .group_by(["temp_bin", "year"])
        
        # agg calculates the mean vehicle_count per group
        .agg(pl.col("vehicle_count").mean().alias("vehicle_count"))
        
        # sort ascending so the line is drawn correctly left to right
        .sort("temp_bin")
        
        # convert to Pandas because Plotly does not accept Polars as input
        .to_pandas()
    )


def bin_by_precipitation(df_polars, bin_size=2):

    # Round precipitation to nearest bin_size mm step
    return (
        df_polars
        
        # Create precip_bin column by rounding precipitation down to nearest bin
        .with_columns(
            (pl.col("precipitation") // bin_size * bin_size).alias("precip_bin")
        )
        
        # group_by groups all rows that share the same bin AND year together
        .group_by(["precip_bin", "year"])
        
        # agg calculates the mean vehicle_count per group
        .agg(pl.col("vehicle_count").mean().alias("vehicle_count"))
        
        # sort ascending so the line is drawn correctly left to right
        .sort("precip_bin")
        
        # convert to Pandas because Plotly does not accept Polars as input
        .to_pandas()
    )


# Load data
df = load_data()

# Extract sorted list of all available years for the chart legend
years = sorted(df.select("year").unique().to_series().to_list())

#Visualisation
col1, col2 = st.columns(2)

with col1:
    st.subheader("Vehicle Count vs Temperature")

    # Aggregate full dataset by temperature bins
    df_temp = bin_by_temperature(df, bin_size=2)
    fig_temp = px.line(
        df_temp,
        x="temp_bin",        # x-axis: temperature bin
        y="vehicle_count",   # y-axis: average vehicle count
        color="year",        # one colored line per year
        labels={"temp_bin": "Temperature (2°C bins)", "vehicle_count": "Avg Vehicle Count", "year": "Year"}
    )
    st.plotly_chart(fig_temp, use_container_width=True)

with col2:
    st.subheader("Vehicle Count vs Precipitation")

    # Aggregate full dataset by precipitation bins
    df_precip = bin_by_precipitation(df, bin_size=2)
    fig_rain = px.line(
        df_precip,
        x="precip_bin",      # x-axis: precipitation bin
        y="vehicle_count",   # y-axis: average vehicle count
        color="year",        # one colored line per year
        labels={"precip_bin": "Precipitation (2mm bins)", "vehicle_count": "Avg Vehicle Count", "year": "Year"}
    )
    st.plotly_chart(fig_rain, use_container_width=True)
