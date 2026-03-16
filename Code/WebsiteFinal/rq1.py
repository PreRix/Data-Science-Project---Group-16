import streamlit as st
import polars as pl
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

BASE_DIR = "../../data"
CSV_PATH = os.path.join(BASE_DIR, "MergeData", "holy_file.csv")

st.set_page_config(page_title="Weather & Traffic", layout="wide")
st.title("Impact of Weather on Traffic (Station 1194)")

@st.cache_data(show_spinner="Loading and preparing data ...")
def load_weather_traffic_data(path):
    df = pl.read_csv(path, infer_schema_length=0)
    
    # Actual weather column names from your dataset
    COL_PRECIP = "precipitation" 
    COL_TEMP = "temperature_2m"
    
    # Fallback check in case columns are missing (for safety)
    if COL_PRECIP not in df.columns:
        df = df.with_columns(pl.lit(0.0).alias(COL_PRECIP)) 
    if COL_TEMP not in df.columns:
        df = df.with_columns(pl.lit(15.0).alias(COL_TEMP))  
        
    return (
        df
        # Filter for the specific counting station A215 (1194)
        .filter(pl.col("Zst").str.strip_chars() == "1104")
        .with_columns(pl.col("date").str.to_datetime("%d.%m.%Y %H:%M").alias("datetime"))
        .with_columns([
            pl.col("datetime").dt.hour().alias("hour"),
            # dt.weekday() returns 1 (Monday) to 7 (Sunday)
            pl.col("datetime").dt.weekday().alias("weekday"), 
        ])
        .with_columns([
            pl.when(pl.col("K_KFZ_R1").str.strip_chars().is_in(["a", "d"]))
              .then(None)
              .otherwise(pl.col("KFZ_R1").str.strip_chars().str.extract(r"^(-?\d+)").cast(pl.Float64))
              .alias("KFZ_R1"),
            pl.when(pl.col("K_KFZ_R2").str.strip_chars().is_in(["a", "d"]))
              .then(None)
              .otherwise(pl.col("KFZ_R2").str.strip_chars().str.extract(r"^(-?\d+)").cast(pl.Float64))
              .alias("KFZ_R2"),
        ])
        .with_columns((pl.col("KFZ_R1") + pl.col("KFZ_R2")).alias("KFZ_total"))
        # Cast weather columns to Float
        .with_columns([
            pl.col(COL_PRECIP).cast(pl.Float64, strict=False),
            pl.col(COL_TEMP).cast(pl.Float64, strict=False)
        ])
    )

try:
    df = load_weather_traffic_data(CSV_PATH)
except FileNotFoundError:
    st.error(f"File not found: {CSV_PATH}")
    st.stop()

# Constants for later use
COL_PRECIP = "precipitation" 
COL_TEMP = "temperature_2m"
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# ── 1. Heatmap: Rain/Snow vs. Traffic ─────────────────────────────────────────
st.header("Traffic Volume: Dry vs. Wet Days")
st.markdown("Average *Vehicle Count* per hour and weekday.")

def get_heatmap_matrices(df_subset: pl.DataFrame):
    """Aggregates data and builds two 24x7 matrices (Means and Counts)."""
    if df_subset.height == 0:
        return np.full((24, 7), np.nan), np.full((24, 7), np.nan)
        
    grouped = (
        df_subset.group_by(["weekday", "hour"])
        .agg(
            pl.col("KFZ_total").mean().alias("mean_kfz"),
            pl.len().alias("count") # Counts how often this scenario occurred
        )
    )
    
    # 24 hours (Rows), 7 days (Cols)
    matrix_mean = np.full((24, 7), np.nan)
    matrix_count = np.full((24, 7), np.nan)
    
    for row in grouped.iter_rows(named=True):
        w = row["weekday"] - 1  # 0-based for the array
        h = row["hour"]
        matrix_mean[h, w] = row["mean_kfz"]
        matrix_count[h, w] = row["count"]
        
    return matrix_mean, matrix_count

# Define conditions
cond_dry = pl.col(COL_PRECIP) == 0
cond_wet = pl.col(COL_PRECIP) > 2

# Unpack both mean and count matrices
matrix_dry_mean, matrix_dry_count = get_heatmap_matrices(df.filter(cond_dry))
matrix_wet_mean, matrix_wet_count = get_heatmap_matrices(df.filter(cond_wet))

# Calculate a shared color scale for better comparability (based on means)
global_min = np.nanmin([np.nanmin(matrix_dry_mean), np.nanmin(matrix_wet_mean)])
global_max = np.nanmax([np.nanmax(matrix_dry_mean), np.nanmax(matrix_wet_mean)])

fig_hm = make_subplots(
    rows=1, cols=2,
    subplot_titles=("Dry Day (== 0 mm/h)", "Wet Day (> 1.0 mm/h)"),
    horizontal_spacing=0.08
)

# Custom hover template to show the count
hover_template = "<b>%{x}, %{y}:00</b><br>Ø Vehicles: %{z:.0f}<br>Occurrences (Days): %{customdata}<extra></extra>"

fig_hm.add_trace(go.Heatmap(
    z=matrix_dry_mean, x=WEEKDAYS, y=list(range(24)),
    customdata=matrix_dry_count, # Pass the counts to Plotly
    hovertemplate=hover_template,
    colorscale="Viridis", zmin=global_min, zmax=global_max,
    coloraxis="coloraxis"
), row=1, col=1)

fig_hm.add_trace(go.Heatmap(
    z=matrix_wet_mean, x=WEEKDAYS, y=list(range(24)),
    customdata=matrix_wet_count, # Pass the counts to Plotly
    hovertemplate=hover_template,
    colorscale="Viridis", zmin=global_min, zmax=global_max,
    coloraxis="coloraxis"
), row=1, col=2)

fig_hm.update_layout(
    height=500,
    coloraxis=dict(colorscale="Viridis", colorbar_title="Ø Vehicles"),
    yaxis=dict(title="Hour (0-23)", tickmode="linear", dtick=2),
    yaxis2=dict(tickmode="linear", dtick=2),
    plot_bgcolor="white"
)

# Reverse Y-axis so 0:00 is at the bottom
fig_hm.update_yaxes(autorange=False, range=[0, 23])

st.plotly_chart(fig_hm, use_container_width=True)

st.divider()

# ── 2. Boxplot: Temperature vs. Traffic (Daily Aggregation) ───────────────────
st.header("Traffic Distribution by Daily Average Temperature")

# Dropdown menu to filter by a specific weekday or use the whole week
weekday_options = {
    "Whole Week": None,
    "Monday": 1,
    "Tuesday": 2,
    "Wednesday": 3,
    "Thursday": 4,
    "Friday": 5,
    "Saturday": 6,
    "Sunday": 7
}

col_box1, col_box2 = st.columns([1, 3])
with col_box1:
    selected_day_name = st.selectbox("Filter by Weekday:", list(weekday_options.keys()))
    selected_day_val = weekday_options[selected_day_name]

# 1. Extract the date, calculate daily mean temp, total vehicles AND keep the weekday
df_daily = (
    df.with_columns(pl.col("datetime").dt.date().alias("date_only"))
    .group_by("date_only")
    .agg([
        pl.col(COL_TEMP).mean().alias("daily_mean_temp"),
        pl.col("KFZ_total").sum().alias("daily_total_kfz"),
        pl.col("weekday").first().alias("weekday") # Keep the weekday for filtering
    ])
)

# Apply the filter if a specific day is selected
if selected_day_val is not None:
    df_daily = df_daily.filter(pl.col("weekday") == selected_day_val)

# 2. Categorize based on the daily average temperature
df_temp = df_daily.with_columns(
    pl.when(pl.col("daily_mean_temp") < 0).then(pl.lit("< 0°C"))
    .when((pl.col("daily_mean_temp") >= 0) & (pl.col("daily_mean_temp") < 5)).then(pl.lit("0 - 5°C"))
    .when((pl.col("daily_mean_temp") >= 5) & (pl.col("daily_mean_temp") < 10)).then(pl.lit("5 - 10°C"))
    .when((pl.col("daily_mean_temp") >= 10) & (pl.col("daily_mean_temp") < 15)).then(pl.lit("10 - 15°C"))
    .when((pl.col("daily_mean_temp") >= 15) & (pl.col("daily_mean_temp") < 20)).then(pl.lit("15 - 20°C"))
    .otherwise(pl.lit("> 20°C"))
    .alias("temp_category")
)

# Define the order of categories for the Y-axis
temp_categories = ["< 0°C", "0 - 5°C", "5 - 10°C", "10 - 15°C", "15 - 20°C", "> 20°C"]

fig_box = go.Figure()

for cat in temp_categories:
    subset = df_temp.filter(pl.col("temp_category") == cat)["daily_total_kfz"].to_list()
    
    fig_box.add_trace(go.Box(
        x=subset,
        name=cat,
        boxpoints="outliers", 
        marker_color="#4C9BE8",
        line_color="#2b5c8f"
    ))

fig_box.update_layout(
    xaxis_title=f"Daily Total Vehicles ({selected_day_name})",
    yaxis_title="Daily Average Temperature",
    height=450,
    plot_bgcolor="white",
    showlegend=False
)
fig_box.update_xaxes(gridcolor="#eeeeee")

st.plotly_chart(fig_box, use_container_width=True)