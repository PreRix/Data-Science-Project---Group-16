import streamlit as st
import polars as pl
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Weather & Traffic", layout="wide")
st.markdown("<style>html { font-size: 20px; }</style>", unsafe_allow_html=True)
st.title("Impact of Weather on Traffic")

st.markdown("**Research Question #1:** How do precipitation and temperature affect the hourly vehicle counts near Kiel between 2021 and 2025?")

CSV_HOLYFILE = "https://cloud.rz.uni-kiel.de/public.php/dav/files/NnYrtwJ7FLqC6en/?accept=zip"

COL_PRECIP = "precipitation" 
COL_TEMP = "temperature_2m"
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

YEAR_COLORS = ["#4C9BE8", "#E85C4C", "#2DB37A", "#F5A623", "#A259E8"]
ZST_VARS = {
    "Kiel-West": "1194",
    "Rumohr": "1104",
    "AS Wankendorf":      "1156",
    
    #"Kiel-Holtenau 1":         "1111",
    #"Kiel-Holtenau 2":        "1112",
    #"Gettorf": "1116",
    #"Raisdorf 1":     "1135",       
    
    #"Kiel/Schönkirchen":  "1158",
    
}

def apply_font(fig):
    fig.update_layout(font_size=22, legend_font_size=22)

    if fig.layout.title.text:
        fig.update_layout(title_font_size=34)

    fig.update_xaxes(title_font_size=28, tickfont_size=22)
    fig.update_yaxes(title_font_size=28, tickfont_size=22)
    for annotation in fig.layout.annotations:
        annotation.font.size = 26
    return fig

@st.cache_data(show_spinner="Loading Measuring Points data …")
def load_measuring_points_data(path):
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
        #.filter(pl.col("Zst").str.strip_chars() == "1194")
        .with_columns(pl.col("date").str.to_datetime("%d.%m.%Y %H:%M").alias("datetime"))
        .with_columns([
            pl.col("datetime").dt.hour().alias("hour"),
            # dt.weekday() returns 1 (Monday) to 7 (Sunday)
            pl.col("datetime").dt.weekday().alias("weekday"),
            pl.col("datetime").dt.year().alias("year")
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
    df_traffic = load_measuring_points_data(CSV_HOLYFILE)
except FileNotFoundError:
    st.error(f"File not found: {CSV_HOLYFILE}")
    st.stop()

# ── 1. Heatmap: Rain/Snow vs. Traffic ─────────────────────────────────────────
st.header("Traffic Volume: Dry vs. Wet Days")

#  selection of zst
col1, col2, col3 = st.columns(3)
zst_label  = col1.selectbox("Counting station", list(ZST_VARS))
zst_col    = ZST_VARS[zst_label]

all_years = sorted(df_traffic["year"].unique().to_list())
min_year = int(df_traffic["year"].min())
max_year = int(df_traffic["year"].max())


rain_threshold = col3.slider("Rain threshold for 'Wet Day' (mm/h)", min_value=0.1, max_value=2.0, value=1.0, step=0.1)

# Define conditions
cond_dry = pl.col(COL_PRECIP) == 0
cond_wet = pl.col(COL_PRECIP) > rain_threshold

#subset = df.filter(pl.col("year").is_in(active_years))


df_selected = df_traffic.filter(pl.col("Zst") == zst_col)
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


# Unpack both mean and count matrices
matrix_dry_mean, matrix_dry_count = get_heatmap_matrices(df_selected.filter(cond_dry))
matrix_wet_mean, matrix_wet_count = get_heatmap_matrices(df_selected.filter(cond_wet))

# Calculate the relative difference
with np.errstate(divide='ignore', invalid='ignore'):
    matrix_change_rel = (
        (((matrix_wet_mean / matrix_dry_mean) - 1) * 100)
    )

with np.errstate(divide='ignore', invalid='ignore'):
    matrix_change_abs = (matrix_wet_mean - matrix_dry_mean) 

# Calculate a shared color scale for better comparability (based on means)
global_min = np.nanmin([np.nanmin(matrix_dry_mean), np.nanmin(matrix_wet_mean)])
global_max = np.nanmax([np.nanmax(matrix_dry_mean), np.nanmax(matrix_wet_mean)])

fig_hm = make_subplots(
    rows=1, cols=3,
    subplot_titles=("Average traffic on a Dry Day (== 0 mm/h)", "Average traffic on a Wet Day", "Change between Dry and Wet day"),
    horizontal_spacing=0.08
)

# Custom hover template to show the count
hover_template = "<b>%{x}, %{y}:00</b><br>Ø Vehicles: %{z:.0f}<br>Occurrences (Days): %{customdata}<extra></extra>"

custom_scale = [
    [0.0, "rgb(179, 0, 0)"],      
    [0.3, "rgb(253, 141, 60)"],  
    [0.48, "rgb(255, 245, 235)"], 
    [0.5, "rgb(255, 255, 255)"],  
    [0.52, "rgb(247, 247, 247)"], 
    [0.7, "rgb(146, 197, 222)"],   
    [1.0, "rgb(5, 48, 97)"]       
]

fig_hm.add_trace(go.Heatmap(
    z=matrix_dry_mean, x=WEEKDAYS, y=list(range(24)),
    customdata=matrix_dry_count, # Pass the counts to Plotly
    hovertemplate=hover_template,
    colorscale="Viridis", zmin=global_min, zmax=global_max,
    coloraxis="coloraxis",
    colorbar=dict(
        title="Vehicles", 
        x=0.43,     
        thickness=15,
        len=0.8
    )
), row=1, col=1)

fig_hm.add_trace(go.Heatmap(
    z=matrix_wet_mean, x=WEEKDAYS, y=list(range(24)),
    customdata=matrix_wet_count, # Pass the counts to Plotly
    hovertemplate=hover_template,
    colorscale="Viridis", zmin=global_min, zmax=global_max,
    coloraxis="coloraxis"
), row=1, col=2)

fig_hm.add_trace(go.Heatmap(
    z=matrix_change_rel, x=WEEKDAYS, y=list(range(24)),
    customdata=matrix_change_abs,
    hovertemplate="<b>%{x}, %{y}:00</b><br>Change: %{z:.1f}%<br>Abs. Value: %{customdata:.0f}<extra></extra>",
    colorscale=custom_scale, zmid=0, zmin = -50, zmax = 50,
    #zmin = np.nanmin(matrix_change_rel), zmax = np.nanmax(matrix_change_rel),
    colorbar=dict(title="Change %", x=1.0)
), row=1, col=3)

fig_hm.update_layout(
    height=500,
    coloraxis=dict(colorscale="Viridis", colorbar_title="Ø Vehicles",colorbar=dict(
        title="Vehicles", 
        x=0.64,          
        thickness=12, 
        len=0.8
    )),
    yaxis=dict(title="Hour (0-23)", tickmode="linear", dtick=2),
    yaxis2=dict(tickmode="linear", dtick=2),
    plot_bgcolor="white"
)

# Reverse Y-axis so 0:00 is at the bottom
fig_hm.update_yaxes(autorange=False, range=[0, 23])

st.plotly_chart(apply_font(fig_hm),  use_container_width=True)

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
    df_selected.with_columns(pl.col("datetime").dt.date().alias("date_only"))
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

st.plotly_chart(apply_font(fig_box), use_container_width=True)
