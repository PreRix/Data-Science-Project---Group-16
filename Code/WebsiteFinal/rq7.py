import streamlit as st
import polars as pl
import plotly.graph_objects as go
from datetime import date, timedelta

st.set_page_config(page_title="Kieler Woche & transport Traffic", layout="wide")
st.markdown("<style>html { font-size: 20px; }</style>", unsafe_allow_html=True)
st.title("Kieler Woche & transport Traffic")

st.markdown("**Research Question #7:** How does the daily passenger transport and freight transport traffic change during the Kieler Woche compared to the surrounding month (2 weeks before/after)?")

CSV_HOLYFILE = "https://cloud.rz.uni-kiel.de/public.php/dav/files/NnYrtwJ7FLqC6en/?accept=zip"

KIELER_WOCHE_PRESETS = {
    "Kieler Woche 2021": (date(2021, 9, 4), date(2021, 9, 12)),
    "Kieler Woche 2022": (date(2022, 6, 18), date(2022, 6, 26)),
    "Kieler Woche 2023": (date(2023, 6, 17), date(2023, 6, 25)),
    "Kieler Woche 2024": (date(2024, 6, 22), date(2024, 6, 30)),
    "Kieler Woche 2025": (date(2025, 6, 21), date(2025, 6, 29))
}

ZST_VARS = {
    "Kiel-West": "1194",
    "Rumohr": "1104",
    "AS Wankenforf": "1156",
    
    #"Kiel-Holtenau 1": "1111",
    #"Kiel-Holtenau 2": "1112",
    #"Gettorf": "1116",
    #"Raisdorf 1": "1135",       
    
    #"Kiel/Schönkirchen": "1158",
    
}

BUFFER_DAYS = 14

WEEKDAYS_MAP = {1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat", 7: "Sun"}

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

    classes = ["KFZ", "Pkw", "Mot", "Bus", "PmA"
               #, "Lkw", "LkwA", "Sattel",  "nk", "KFZ"
              ]

    def clean_tls_col(name):
        return (
            pl.when(pl.col(f"K_{name}").str.strip_chars().is_in(["a", "d"]))
            .then(None)
            .otherwise(
                pl.col(name)
                .str.strip_chars()
                .str.extract(r"^(-?\d+)")
                .cast(pl.Float64)
            )
            .alias(name)
        )

    all_cols_to_clean = [f"{c}_R1" for c in classes] + [f"{c}_R2" for c in classes]
    return (
        df
        # Clean all needed
        .with_columns([clean_tls_col(col) for col in all_cols_to_clean])
        # Parse datetime and extract weekdays (1 = Monday, 7 = Sunday)
        .with_columns(pl.col("date").str.to_datetime("%d.%m.%Y %H:%M").alias("datetime"))
        .with_columns([
            pl.col("datetime").dt.weekday().alias("weekday"),
            pl.col("datetime").dt.date().alias("date_only")
        ])

        .with_columns([
            (pl.col("KFZ_R1") + pl.col("KFZ_R2")).alias("Total_Traffic"),
            
            (
                pl.col("Pkw_R1") + pl.col("Pkw_R2") + 
                pl.col("Mot_R1") + pl.col("Mot_R2") + 
                pl.col("Bus_R1") + pl.col("Bus_R2") +
                pl.col("PmA_R1") + pl.col("PmA_R2")
            ).alias("Personal_Traffic"),
        ])
        .with_columns([
            (pl.col("Total_Traffic") - pl.col("Personal_Traffic")).alias("Truck_Traffic")
        ])
    )

try:
    df_traffic = load_measuring_points_data(CSV_HOLYFILE)
except FileNotFoundError:
    st.error(f"File not found: {CSV_HOLYFILE}")
    st.stop()

col1, col2, col3, col4 = st.columns(4)
options = ["All stations"] + list(ZST_VARS.keys())
zst_label = col1.selectbox("Counting station", options)

if zst_label == "All stations":
    zst_choice = list(ZST_VARS.values())
else:
    zst_choice = [ZST_VARS[zst_label]]

#ZST_A215 = "1194"
#df_station = df.filter(pl.col("Zst").str.strip_chars() == zst_col)
df_station = df_traffic.filter(pl.col("Zst").is_in(zst_choice))

with col2:
    event_preset = st.selectbox("Select the year:", list(KIELER_WOCHE_PRESETS.keys()))
    start_date, end_date = KIELER_WOCHE_PRESETS[event_preset]

# Define the baseline: 2 weeks (14 days) before and 2 weeks (14 days) after
baseline_start = start_date - timedelta(days=BUFFER_DAYS)
baseline_end = end_date + timedelta(days=BUFFER_DAYS)

# --- Aggregation ---
# 1. First, calculate the absolute daily sums for EVERY day
df_daily_sums = (
    df_station.group_by(["date_only", "weekday"])
    .agg([
        pl.col("Personal_Traffic").sum().alias("daily_cars"),
        pl.col("Truck_Traffic").sum().alias("daily_trucks")
    ])
)

# 2. Split into Event days and Baseline days (Surrounding Month)
df_event_daily = df_daily_sums.filter(
    (pl.col("date_only") >= start_date) & (pl.col("date_only") <= end_date)
)
df_base_daily = df_daily_sums.filter(
    ((pl.col("date_only") >= baseline_start) & (pl.col("date_only") < start_date)) |
    ((pl.col("date_only") > end_date) & (pl.col("date_only") <= baseline_end))
)


# 3. Keep all 9 event days individual (no averaging for the event)
df_event_9days = (
    df_event_daily
    .sort("date_only")
    .select([
        pl.col("date_only"),
        pl.col("weekday"),
        pl.col("daily_cars").alias("event_cars"),
        pl.col("daily_trucks").alias("event_trucks")
    ])
)

# 4. Baseline: Still aggregate by weekday to get the "typical" Monday, Tuesday, etc., of the month
df_base_wd = (
    df_base_daily.group_by("weekday")
    .agg([
        pl.col("daily_cars").mean().alias("base_cars"),
        pl.col("daily_trucks").mean().alias("base_trucks")
    ])
)

# 5. Merge: Attach the baseline averages to the 9 specific event days based on the weekday
# This correctly maps the average "Baseline Saturday" to BOTH Saturdays of the Kieler Woche.
df_plot = df_event_9days.join(df_base_wd, on="weekday", how="left").sort("date_only")

# Format X-axis labels to show the date and the weekday (e.g., "17.06. (Sat)")
x_labels = [
    f"{d.strftime('%d.%m.')} ({WEEKDAYS_MAP[w]})" 
    for d, w in zip(df_plot["date_only"], df_plot["weekday"])
]

# --- Plotly Visualization ---
fig = go.Figure()

# --- BARS: Event Week ---
# Bar for Cars (Kieler Woche)
fig.add_trace(go.Bar(
    x=x_labels,
    y=df_plot["event_cars"].to_list(),
    name="Passenger Transport (Kieler Woche)",
    marker_color="#4C9BE8",
    offsetgroup=1
))

# Bar for Trucks (Kieler Woche)
fig.add_trace(go.Bar(
    x=x_labels,
    y=df_plot["event_trucks"].to_list(),
    name="Freight Transport (Kieler Woche)",
    marker_color="#2b5c8f",
    offsetgroup=2
))

# --- LINES: Baseline (Surrounding Month) ---
# Line for Cars Baseline
fig.add_trace(go.Scatter(
    x=x_labels,
    y=df_plot["base_cars"].to_list(),
    name="Ø Passenger Transport (Surrounding Month)",
    mode="lines+markers",
    line=dict(color="#E85C4C", width=3, dash="dot"),
    marker=dict(size=8, symbol="diamond"),
    yaxis="y"
))

# Line for Trucks Baseline
fig.add_trace(go.Scatter(
    x=x_labels,
    y=df_plot["base_trucks"].to_list(),
    name="Ø Freight Transport (Surrounding Month)",
    mode="lines+markers",
    line=dict(color="#F5A623", width=3, dash="dot"),
    marker=dict(size=8, symbol="diamond"),
    yaxis="y"
))

# Layout adjustments
fig.update_layout(
    barmode="group", # Place bars side by side
    xaxis_title="Weekday",
    yaxis_title="Number of Vehicles (Daily Sum)",
    hovermode="x unified",
    height=600,
    plot_bgcolor="white",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.05,
        xanchor="center",
        x=0.5
    ),
    margin=dict(t=100)
)

fig.update_xaxes(gridcolor="#eeeeee")
fig.update_yaxes(gridcolor="#eeeeee", zerolinecolor="#cccccc")

st.plotly_chart(apply_font(fig), use_container_width=True)

# Brief explanatory statistics metrics below the chart
#st.divider()
#st.subheader("Quick Overview")
#m1, m2 = st.columns(2)

total_event_cars = df_event_daily["daily_cars"].mean()
total_base_cars = df_base_daily["daily_cars"].mean()
diff_cars = ((total_event_cars / total_base_cars) - 1) * 100 if total_base_cars else 0

total_event_trucks = df_event_daily["daily_trucks"].mean()
total_base_trucks = df_base_daily["daily_trucks"].mean()
diff_trucks = ((total_event_trucks / total_base_trucks) - 1) * 100 if total_base_trucks else 0

col3.metric("Ø Passenger Transport per Day (Kieler Woche vs. Baseline)", 
          f"{total_event_cars:,.0f}", 
          f"{diff_cars:+.1f}%")

col4.metric("Ø Freight Transport per Day (Kieler Woche vs. Baseline)", 
          f"{total_event_trucks:,.0f}", 
          f"{diff_trucks:+.1f}%") 