# ====================================
# Imports

import streamlit as st
import polars as pl
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.navigation import setup

# ====================================
# Website design

setup()

col1_top_btn, col2_top_btn, col3_top_btn = st.columns([1, 3.6, 1])

with col3_top_btn:
    if st.button("Next Question ➡️", key = "btn_top"):
        st.switch_page("pages/Research_Question_2.py")

st.title("Research Question #1")

st.markdown("""
    # *How do precipitation and temperature affect the hourly vehicle counts near Kiel between 2021 and 2025?*
    ## Traffic Volume: Dry vs. Wet
    """)

# ====================================
# Global variables

COL_PRECIP = "precipitation" 
COL_TEMP = "temperature_2m"
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

YEAR_COLORS = ["#4C9BE8", "#E85C4C", "#2DB37A", "#F5A623", "#A259E8"]
ZST_VARS = {
    "Kiel-West": "1194",
    "Rumohr": "1104",
    "AS Wankendorf":      "1156",
}

# ====================================
# Data collection and helpers

def apply_font(fig):
    fig.update_layout(font_size=22, legend_font_size=22)

    if fig.layout.title.text:
        fig.update_layout(title_font_size=34)

    fig.update_xaxes(title_font_size=28, tickfont_size=22)
    fig.update_yaxes(title_font_size=28, tickfont_size=22)
    for annotation in fig.layout.annotations:
        annotation.font.size = 26
    return fig

df_traffic = st.session_state.df_traffic
     
# ====================================
# First visualization

try:
    col1, col2, col3 = st.columns(3)
    zst_label = col1.selectbox("Counting station", list(ZST_VARS))
    zst_col   = ZST_VARS[zst_label]

    rain_threshold = col3.slider(
        "Rain threshold for 'Wet Day' (mm/h)", min_value=0.1, max_value=2.0, value=1.0, step=0.1
    )

    cond_dry = pl.col(COL_PRECIP) == 0
    cond_wet = pl.col(COL_PRECIP) > rain_threshold

    df_selected = df_traffic.filter(pl.col("Zst") == zst_col)
    st.markdown("Average *Vehicle Count* per hour and weekday.")

    def get_heatmap_matrices(df_subset: pl.DataFrame):
        if df_subset.height == 0:
            return np.full((24, 7), np.nan), np.full((24, 7), np.nan)
        grouped = (
            df_subset.group_by(["weekday", "hour"])
            .agg(
                pl.col("KFZ_total").mean().alias("mean_kfz"),
                pl.len().alias("count"),
            )
        )
        matrix_mean  = np.full((24, 7), np.nan)
        matrix_count = np.full((24, 7), np.nan)
        for row in grouped.iter_rows(named=True):
            w = row["weekday"] - 1
            h = row["hour"]
            matrix_mean[h, w]  = row["mean_kfz"]
            matrix_count[h, w] = row["count"]
        return matrix_mean, matrix_count

    matrix_dry_mean,  matrix_dry_count  = get_heatmap_matrices(df_selected.filter(cond_dry))
    matrix_wet_mean,  matrix_wet_count  = get_heatmap_matrices(df_selected.filter(cond_wet))

    with np.errstate(divide="ignore", invalid="ignore"):
        matrix_change_rel = ((matrix_wet_mean / matrix_dry_mean) - 1) * 100
        matrix_change_abs = matrix_wet_mean - matrix_dry_mean

    global_min = np.nanmin([np.nanmin(matrix_dry_mean), np.nanmin(matrix_wet_mean)])
    global_max = np.nanmax([np.nanmax(matrix_dry_mean), np.nanmax(matrix_wet_mean)])

    fig_hm = make_subplots(
        rows=1, cols=3,
        subplot_titles=(
            "Average traffic on a Dry Day (== 0 mm/h)",
            "Average traffic on a Wet Day",
            "Change between Dry and Wet day",
        ),
        horizontal_spacing=0.08,
    )

    hover_template = "<b>%{x}, %{y}:00</b><br>Ø Vehicles: %{z:.0f}<br>Occurrences (Days): %{customdata}<extra></extra>"

    custom_scale = [
        [0.0,  "rgb(179, 0, 0)"],
        [0.3,  "rgb(253, 141, 60)"],
        [0.48, "rgb(255, 245, 235)"],
        [0.5,  "rgb(255, 255, 255)"],
        [0.52, "rgb(247, 247, 247)"],
        [0.7,  "rgb(146, 197, 222)"],
        [1.0,  "rgb(5, 48, 97)"],
    ]

    fig_hm.add_trace(go.Heatmap(
        z=matrix_dry_mean, x=WEEKDAYS, y=list(range(24)),
        customdata=matrix_dry_count, hovertemplate=hover_template,
        colorscale="Viridis", zmin=global_min, zmax=global_max,
        coloraxis="coloraxis",
        colorbar=dict(title="Vehicles", x=0.23, thickness=15, len=0.8),
    ), row=1, col=1)

    fig_hm.add_trace(go.Heatmap(
        z=matrix_wet_mean, x=WEEKDAYS, y=list(range(24)),
        customdata=matrix_wet_count, hovertemplate=hover_template,
        colorscale="Viridis", zmin=global_min, zmax=global_max,
        coloraxis="coloraxis",
    ), row=1, col=2)

    fig_hm.add_trace(go.Heatmap(
        z=matrix_change_rel, x=WEEKDAYS, y=list(range(24)),
        customdata=matrix_change_abs,
        hovertemplate="<b>%{x}, %{y}:00</b><br>Change: %{z:.1f}%<br>Abs. Value: %{customdata:.0f}<extra></extra>",
        colorscale=custom_scale, zmid=0, zmin=-50, zmax=50,
        colorbar=dict(title="Change %", x=1.0),
    ), row=1, col=3)

    fig_hm.update_layout(
        height=500,
        coloraxis=dict(
            colorscale="Viridis",
            colorbar=dict(title="Vehicles", x=0.63, thickness=12, len=0.8),
        ),
        yaxis=dict(title="Hour (0-23)", tickmode="linear", dtick=2),
        yaxis2=dict(tickmode="linear", dtick=2),
        yaxis3=dict(tickmode="linear", dtick=2),
        plot_bgcolor="white",
    )
    fig_hm.update_yaxes(autorange=False, range=[0, 23])

    st.plotly_chart(apply_font(fig_hm), width="stretch")

except Exception:
    for key in list(st.session_state.keys()):
        if key not in ("df_traffic", "df_registrations", "df_registrations_fuel", "df_weather"):
            del st.session_state[key]
    st.rerun()

# ====================================
# Text

st.markdown("""
    ### Definitions:
    To make a comparison possible, we had to define *dry day* and  *wet day*:  

    - Dry day: 0mm of precipitation per hour
    - Wet day: can be adjusted on a scale from 0.1 to 2mm of precipitation per hour 

    ####
    ### Description:
    Two HeatMaps are used to show how the *average vehicle count per hour and weekday* gets impacted by precipitation (rain + snow).  
    A third HeatMap shows the relative difference from dry to wet day based on the dry day data for the average vehicle count.  

    ####
    ### How we aggregated the Data:
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
# Second visualization

try:
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
        selected_day_val  = weekday_options[selected_day_name]

    df_daily = (
        df_selected
        .group_by("day")
        .agg([
            pl.col(COL_TEMP).mean().alias("daily_mean_temp"),
            pl.col("KFZ_total").sum().alias("daily_total_kfz"),
            pl.col("weekday").first().alias("weekday"),
        ])
    )

    if selected_day_val is not None:
        df_daily = df_daily.filter(pl.col("weekday") == selected_day_val)

    df_temp = df_daily.with_columns(
        pl.when(pl.col("daily_mean_temp") < 0).then(pl.lit("< 0°C"))
        .when((pl.col("daily_mean_temp") >= 0)  & (pl.col("daily_mean_temp") < 5)).then(pl.lit("0 - 5°C"))
        .when((pl.col("daily_mean_temp") >= 5)  & (pl.col("daily_mean_temp") < 10)).then(pl.lit("5 - 10°C"))
        .when((pl.col("daily_mean_temp") >= 10) & (pl.col("daily_mean_temp") < 15)).then(pl.lit("10 - 15°C"))
        .when((pl.col("daily_mean_temp") >= 15) & (pl.col("daily_mean_temp") < 20)).then(pl.lit("15 - 20°C"))
        .otherwise(pl.lit("> 20°C"))
        .alias("temp_category")
    )

    temp_categories = ["< 0°C", "0 - 5°C", "5 - 10°C", "10 - 15°C", "15 - 20°C", "> 20°C"]
    fig_box = go.Figure()

    for cat in temp_categories:
        subset = df_temp.filter(pl.col("temp_category") == cat)["daily_total_kfz"].to_list()
        fig_box.add_trace(go.Box(
            x=subset, name=cat,
            boxpoints="outliers",
            marker_color="#4C9BE8",
            line_color="#2b5c8f",
        ))

    fig_box.update_layout(
        xaxis_title=f"Daily Total Vehicles ({selected_day_name})",
        yaxis_title="Daily Average Temperature",
        height=450,
        plot_bgcolor="white",
        showlegend=False,
    )
    fig_box.update_xaxes(gridcolor="#eeeeee")

    st.plotly_chart(apply_font(fig_box), width="stretch")

except Exception:
    for key in list(st.session_state.keys()):
        if key not in ("df_traffic", "df_registrations", "df_registrations_fuel", "df_weather"):
            del st.session_state[key]
    st.rerun()

# ====================================
# Text

st.markdown("""
    ### Description:
    It can be seen, that during weekdays, the temperature does not have so much impact on the traffic distribution, as many people have to go to work, 
    no matter the temperature.  
    On the weekend-days, the temperature definitely seems to have an effect, as the traffic distribution increases with temperature.  
    
    ####
    ### How we aggregated the Data:
    The BoxPlots are visualizing how traffic volume is affected by temperature.  
    Therefore we categorized the *daily average temperature* into six temperature ranges; each BoxPlot then showing the respective vehicle volume distribution.  
    We used the *average daily vehicle count* at counting station 1194, 1104 and 1156 again. Reasoning for this decision is the same as above.  
    Additionally, a weekly average distribution can be displayed.  
    
    ####   
    ### Interpretation:
    Precipitation seems to have a small to medium effect on the hourly vehicle counts. Especially during rush-hour times it is visible how the 
    vehicle count numbers are not as solidly high when wet compared to a dry day.  
    Temperature seems to have a major effect on the weekend, while weekdays are moderately affected.
""")

# ====================================
# Website design

st.divider()

col1_bottom_btn, col2_bottom_btn, col3_bottom_btn = st.columns([1, 3.6, 1])

with col3_bottom_btn:
    if st.button("Next Question ➡️", key = "btn_bottom"):
        st.switch_page("pages/Research_Question_2.py")

st.divider()

col4_bottom_btn, col5_bottom_btn, col6_bottom_btn, col7_bottom_btn = st.columns([1, 0.33, 0.33, 1])

with col5_bottom_btn:
    if st.button("Go to Imprint", width = "stretch"):
        st.switch_page("pages/Imprint.py")

with col6_bottom_btn:
    if st.button("Back to Homepage 🏠", width = "stretch"):
        st.switch_page("pages/homepage.py")
