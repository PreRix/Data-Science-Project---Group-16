import streamlit as st
# ==============================
# hier nötige Imports hinzufügen
import polars as pl
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
# ==============================

col1_top_btn, col2_top_btn, col3_top_btn = st.columns([1, 3.6, 1])

with col3_top_btn:
    if st.button("Next Question ➡️", key = "btn_top"):
        st.switch_page("pages/Research_Question_2.py")

st.title("Research Question #1")

# ==============================
CSV_HOLYFILE = "https://cloud.rz.uni-kiel.de/public.php/dav/files/NnYrtwJ7FLqC6en/?accept=zip"

COL_PRECIP = "precipitation" 
COL_TEMP = "temperature_2m"

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

ZST_VARS = {
    "Kiel-West": "1194",
    "Rumohr": "1104",
    "AS Wankendorf": "1156",
}
# ==============================

st.markdown("""
    # *How do precipitation and temperature affect the hourly vehicle counts near Kiel between 2021 and 2025?*
    ## Traffic Volume: Dry vs. Wet
    """)

# ====================================
# Hier Visualisierungs-Code hinzufügen
@st.cache_data(show_spinner="Loading Measuring Points data …")
def load_measuring_points_data(path):
    df = pl.read_csv(path, infer_schema_length=0)

    if COL_PRECIP not in df.columns:
        df = df.with_columns(pl.lit(0.0).alias(COL_PRECIP))
    if COL_TEMP not in df.columns:
        df = df.with_columns(pl.lit(15.0).alias(COL_TEMP))

    return (
        df
        .with_columns(pl.col("date").str.to_datetime("%d.%m.%Y %H:%M").alias("datetime"))
        .with_columns([
            pl.col("datetime").dt.hour().alias("hour"),
            pl.col("datetime").dt.weekday().alias("weekday"),
            pl.col("datetime").dt.year().alias("year")
        ])
        .with_columns([
            pl.col("KFZ_R1").str.extract(r"^(-?\d+)").cast(pl.Float64),
            pl.col("KFZ_R2").str.extract(r"^(-?\d+)").cast(pl.Float64)
        ])
        .with_columns((pl.col("KFZ_R1") + pl.col("KFZ_R2")).alias("KFZ_total"))
        .with_columns([
            pl.col(COL_PRECIP).cast(pl.Float64, strict=False),
            pl.col(COL_TEMP).cast(pl.Float64, strict=False)
        ])
    )

df_traffic = load_measuring_points_data(CSV_HOLYFILE)

col1, col2, col3 = st.columns(3)

zst_label = col1.selectbox("Counting station", list(ZST_VARS))
zst_col = ZST_VARS[zst_label]

rain_threshold = col3.slider(
    "Rain threshold for 'Wet Day' (mm/h)",
    min_value=0.1,
    max_value=2.0,
    value=1.0,
    step=0.1
)

cond_dry = pl.col(COL_PRECIP) == 0
cond_wet = pl.col(COL_PRECIP) > rain_threshold

df_selected = df_traffic.filter(pl.col("Zst") == zst_col)

def get_heatmap_matrices(df_subset: pl.DataFrame):

    if df_subset.height == 0:
        return np.full((24, 7), np.nan), np.full((24, 7), np.nan)

    grouped = (
        df_subset.group_by(["weekday", "hour"])
        .agg(
            pl.col("KFZ_total").mean().alias("mean_kfz"),
            pl.len().alias("count")
        )
    )

    matrix_mean = np.full((24, 7), np.nan)
    matrix_count = np.full((24, 7), np.nan)

    for row in grouped.iter_rows(named=True):
        w = row["weekday"] - 1
        h = row["hour"]

        matrix_mean[h, w] = row["mean_kfz"]
        matrix_count[h, w] = row["count"]

    return matrix_mean, matrix_count


matrix_dry_mean, matrix_dry_count = get_heatmap_matrices(df_selected.filter(cond_dry))
matrix_wet_mean, matrix_wet_count = get_heatmap_matrices(df_selected.filter(cond_wet))

matrix_change_rel = (((matrix_wet_mean / matrix_dry_mean) - 1) * 100)

global_min = np.nanmin([np.nanmin(matrix_dry_mean), np.nanmin(matrix_wet_mean)])
global_max = np.nanmax([np.nanmax(matrix_dry_mean), np.nanmax(matrix_wet_mean)])

fig_hm = make_subplots(
    rows=1,
    cols=3,
    subplot_titles=("Dry Day", "Wet Day", "Relative Change"),
)

fig_hm.add_trace(
    go.Heatmap(z=matrix_dry_mean, x=WEEKDAYS, y=list(range(24)), colorscale="Viridis",
               zmin=global_min, zmax=global_max),
    row=1, col=1
)

fig_hm.add_trace(
    go.Heatmap(z=matrix_wet_mean, x=WEEKDAYS, y=list(range(24)), colorscale="Viridis",
               zmin=global_min, zmax=global_max),
    row=1, col=2
)

fig_hm.add_trace(
    go.Heatmap(z=matrix_change_rel, x=WEEKDAYS, y=list(range(24)),
               colorscale="RdBu", zmid=0),
    row=1, col=3
)

fig_hm.update_layout(height=500)

st.plotly_chart(fig_hm, use_container_width=True)
# ====================================

st.markdown("""
    Two HeatMaps are used to show how the *average vehicle count per hour and weekday* gets impacted by precipitation (rain + snow).  
    To make such a comparison possible, we had to define *dry day* and  *wet day*:  

    - Dry day: 0mm of precipitation per hour
    - Wet day: can be adjusted on a scale from 0.1 to 2mm of precipitation per hour  
    
    A thrid HeatMap shows the relative difference from dry to wet day based on the dry day data for the avergage vehicle count.  
    We only took into account values from counting station 1194 ("Autobahnkreuz Kiel-West") on the A215, 1104 ("Rumohr") on the A215 and 1156 ("AS Wankendorf") 
    on the A21 as these are one of the highly frequented roads; thus, holding the most vehicle counting data.  
    It can be manually selected, which counting station should be displayed.  
    If we would have combined data from multiple counting stations all over Kiel, local weather effects on traffic may cancel each other out when 
    using averages.
""")

st.divider()

st.markdown("""
    ## Traffic Distribution by Daily Average Temperature
""")

# ====================================
# Hier Visualisierungs-Code hinzufügen
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

col_box1, col_box2 = st.columns([1,3])

selected_day_name = col_box1.selectbox(
    "Filter by Weekday:",
    list(weekday_options.keys())
)

selected_day_val = weekday_options[selected_day_name]

df_daily = (
    df_selected
    .with_columns(pl.col("datetime").dt.date().alias("date_only"))
    .group_by("date_only")
    .agg([
        pl.col(COL_TEMP).mean().alias("daily_mean_temp"),
        pl.col("KFZ_total").sum().alias("daily_total_kfz"),
        pl.col("weekday").first().alias("weekday")
    ])
)

if selected_day_val is not None:
    df_daily = df_daily.filter(pl.col("weekday") == selected_day_val)

df_temp = df_daily.with_columns(
    pl.when(pl.col("daily_mean_temp") < 0).then("<0°C")
    .when(pl.col("daily_mean_temp") < 5).then("0-5°C")
    .when(pl.col("daily_mean_temp") < 10).then("5-10°C")
    .when(pl.col("daily_mean_temp") < 15).then("10-15°C")
    .when(pl.col("daily_mean_temp") < 20).then("15-20°C")
    .otherwise(">20°C")
    .alias("temp_category")
)

categories = ["<0°C","0-5°C","5-10°C","10-15°C","15-20°C",">20°C"]

fig_box = go.Figure()

for cat in categories:
    subset = df_temp.filter(pl.col("temp_category")==cat)["daily_total_kfz"].to_list()

    fig_box.add_trace(go.Box(
        x=subset,
        name=cat,
        boxpoints="outliers"
    ))

fig_box.update_layout(
    xaxis_title=f"Daily Total Vehicles ({selected_day_name})",
    yaxis_title="Temperature Range",
    height=450
)

st.plotly_chart(fig_box, use_container_width=True)
# ====================================

st.markdown("""
    The BoxPlots are visualizing how traffic volume is affected by temperature.  
    Therefore we categorized the *daily average temperature* into six temperature ranges; each BoxPlot then showing the respective vehicle volume distribution.  
    We used the *average daily vehicle count* at counting station 1194, 1104 and 1156 again. Reasoning for this decision is the same as above.  
    Additionally, a weekly average distribution can be displayed.  

    It can be seen, that during weekdays, the temperature does not have so much impact on the traffic distribution, as many people have to go to work, 
    not matter the temperature.  
    On the weekend-days, the temperature definitely seems to have an effect, as the traffic distribution increases with temperature.  

    ####   
    ### Conclusion:
    Precipitation seems to have a small to medium effect on the hourly vehicle counts. Especially during rush-hour times it is visible how the 
    vehicle count numbers are not as solidly high when wet compared to a dry day.  
    Temperature seems to have a major effect on the weekend, while weekdays are moderately affected.
""")

st.divider()

col1_bottom_btn, col2_bottom_btn, col3_bottom_btn = st.columns([1, 3.6, 1])

with col3_bottom_btn:
    if st.button("Next Question ➡️", key = "btn_bottom"):
        st.switch_page("pages/Research_Question_2.py")

st.divider()

col4_bottom_btn, col5_bottom_btn, col6_bottom_btn, col7_bottom_btn = st.columns([1, 0.33, 0.33, 1])

with col5_bottom_btn:
    if st.button("Go to Imprint", use_container_width = True):
        st.switch_page("pages/Imprint.py")

with col6_bottom_btn:
    if st.button("Back to Homepage 🏠", use_container_width = True):
        st.switch_page("pages/homepage.py")
