import streamlit as st
import polars as pl
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os


st.set_page_config(page_title="Traffic Direction Analysis", layout="wide")
st.markdown("<style>html { font-size: 20px; }</style>", unsafe_allow_html=True)
st.title("Kiel Traffic: Inbound vs. Outbound Ratio")

CSV_PATH = CSV_HOLYFILE = "https://cloud.rz.uni-kiel.de/public.php/dav/files/NnYrtwJ7FLqC6en/?accept=zip"

def apply_font(fig):
    fig.update_layout(font_size=22, legend_font_size=22)

    if fig.layout.title.text:
        fig.update_layout(title_font_size=34)

    fig.update_xaxes(title_font_size=28, tickfont_size=22)
    fig.update_yaxes(title_font_size=28, tickfont_size=22)
    for annotation in fig.layout.annotations:
        annotation.font.size = 26
    return fig

    
@st.cache_data(show_spinner="Loading data...")
def load_traffic_ratio_data(path):
    df = pl.read_csv(path, infer_schema_length=0)
    
    return (
        df
        .with_columns(pl.col("date").str.to_datetime("%d.%m.%Y %H:%M").alias("datetime"))
        .with_columns([
            pl.col("datetime").dt.hour().alias("hour"),
            pl.col("datetime").dt.weekday().alias("weekday"),
            pl.col("Zst").str.strip_chars()
        ])
        # Cleaning and casting Direction 1 and Direction 2
        .with_columns([
            pl.when(pl.col("K_KFZ_R1").str.strip_chars().is_in(["a", "d"]))
              .then(None)
              .otherwise(pl.col("KFZ_R1").str.strip_chars().str.extract(r"^(-?\d+)").cast(pl.Float64))
              .alias("R1_Inbound"),
            pl.when(pl.col("K_KFZ_R2").str.strip_chars().is_in(["a", "d"]))
              .then(None)
              .otherwise(pl.col("KFZ_R2").str.strip_chars().str.extract(r"^(-?\d+)").cast(pl.Float64))
              .alias("R2_Outbound"),
        ])
        .drop_nulls(["R1_Inbound", "R2_Outbound"])
        .with_columns((pl.col("R1_Inbound") + pl.col("R2_Outbound")).alias("Total_KFZ"))
        # Ratio: 1.0 = 100% Inbound, 0.0 = 100% Outbound, 0.5 = Equal
        .with_columns(
            pl.when(pl.col("Total_KFZ") > 0) # Prevent rare instant of dividing by zero. (Time change = one hour of 0s)
            .then(pl.col("R1_Inbound") / pl.col("Total_KFZ"))
            .otherwise(None)  
            .alias("Inbound_Ratio")
        )
    )

try:
    df = load_traffic_ratio_data(CSV_PATH)
except FileNotFoundError:
    st.error(f"File not found: {CSV_PATH}")
    st.stop()

# --- UI CONTROLS ---
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
ZST_VARS = {
    "Kiel-West": "1194",
    "Rumohr": "1104",
    "AS Wankendorf": "1156",
}
# For all of these stations R1 is incoming traffic

col1, col2, col3 = st.columns(3)
zst_label = col1.selectbox("Select Counting Station", list(ZST_VARS.keys()))
zst_id = ZST_VARS[zst_label]


# --- YEAR & MONTH SELECTOR ---

available_years = sorted(df["datetime"].dt.year().unique().to_list(), reverse=True)
selected_year = col2.selectbox("Year", ["All Years"] + available_years)

if selected_year == "All Years":
    df_filtered_time = df
    month_options = ["Full Year"]
else:
    df_filtered_time = df.filter(pl.col("datetime").dt.year() == selected_year)
    month_options = ["Full Year"] + [
        "January", "February", "March", "April", "May", "June", 
        "July", "August", "September", "October", "November", "December"
    ]

selected_month = col3.selectbox("Month", month_options)

if selected_month != "Full Year":
    # Monat in Zahl umwandeln (1-12)
    month_idx = month_options.index(selected_month)
    df_filtered_time = df_filtered_time.filter(pl.col("datetime").dt.month() == month_idx)
    
# --- DATA PROCESSING FOR HEATMAP ---
df_filtered = df_filtered_time.filter(pl.col("Zst") == zst_id)

def get_ratio_matrix(df_subset):
    # Aggregate by weekday and hour
    grouped = (
        df_subset.group_by(["weekday", "hour"])
        .agg(pl.col("Inbound_Ratio").mean().alias("avg_ratio"))
    )
    
    # Initialize 24x7 matrix
    matrix = np.full((24, 7), np.nan)
    for row in grouped.iter_rows(named=True):
        d = row["weekday"] - 1 # 0-indexed
        h = row["hour"]
        matrix[h, d] = row["avg_ratio"]
    return matrix

ratio_matrix = get_ratio_matrix(df_filtered)

fig_hm = make_subplots(
    rows=1, cols=1,
    subplot_titles=["Directional traffic split: Percentage of total traffic moving towards Kiel. Blue: higher volume entering Kiel. Red: higher volume leaving Kiel"],
    horizontal_spacing=0.08
)

# Diverging colorscale (Red-White-Blue)
custom_rdbu = [
    [0.0, "rgb(178, 24, 43)"],   # Strong Red (Outbound)
    [0.4, "rgb(244, 165, 130)"],
    [0.5, "rgb(255, 255, 255)"], # White (Equal)
    [0.6, "rgb(146, 197, 222)"],
    [1.0, "rgb(33, 102, 172)"]   # Strong Blue (Inbound)
]

fig_hm.add_trace(go.Heatmap(
    z=ratio_matrix,
    x=WEEKDAYS,
    y=list(range(24)),
    colorscale=custom_rdbu,
    zmin=0.2, # Adjust limits based on typical urban swings
    zmax=0.8,
    hovertemplate="<b>%{x} at %{y}:00</b><br>Inbound Ratio: %{z:.2%}<extra></extra>",
    colorbar=dict(
        title="Ratio Inbound",
        tickformat=".0%",
        ticksuffix=""
    )
))

fig_hm.update_layout(
    height=600,
    xaxis_title="Day of Week",
    yaxis_title="Hour of Day",
    yaxis=dict(tickmode="linear", dtick=1)
)

st.plotly_chart(fig_hm, use_container_width=True)

# --- INSIGHTS ---
avg_in = df_filtered["R1_Inbound"].mean()
avg_out = df_filtered["R2_Outbound"].mean()

st.markdown(f"**Quick Stats for {zst_label}:** Average Inbound: {avg_in:.0f} | Average Outbound: {avg_out:.0f}")
