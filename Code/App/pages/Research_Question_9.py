# ====================================
# Imports

import streamlit as st
import polars as pl
import plotly.graph_objects as go
from utils.data_loader import load_traffic_base, load_weather

# ====================================
# Website design

col1_top_btn, col2_top_btn, col3_top_btn = st.columns([1, 3.6, 1])

with col1_top_btn:
    if st.button("⬅️ Previous Question", key="btn_top"):
        st.switch_page("pages/Research_Question_8.py")

st.title("BONUS Research Question")

st.markdown("""
    # *How do extreme weather events affect hourly traffic volumes at selected counting stations near Kiel, and how long does it take for traffic to return to normal levels?*
    ## Relative Traffic around Extreme Weather Events 
""")

# ====================================
# Global variables

RAIN_THRESHOLD = 10.0
SNOW_THRESHOLD = 1.0
WINDOW_BEFORE  = 2
WINDOW_AFTER   = 4

# ====================================
# Data collection and help

def apply_font(fig):
    fig.update_layout(font_size=22, legend_font_size=22)
    if fig.layout.title.text:
        fig.update_layout(title_font_size=34)
    fig.update_xaxes(title_font_size=28, tickfont_size=22)
    fig.update_yaxes(title_font_size=28, tickfont_size=22)
    for annotation in fig.layout.annotations:
        annotation.font.size = 26
    return fig

try:
    # Traffic: only need datetime + vehicle_count for Zst 1194
    df_traffic = (
        load_traffic_base()
        .filter(pl.col("Zst") == "1194")
        .select(["datetime", pl.col("KFZ_total").alias("vehicle_count")])
    )
    df_weather = load_weather()
except Exception as e:
    st.error(f"Could not load data: {e}")
    st.stop()

df = df_traffic.join(df_weather, on="datetime", how="left")

# ====================================
# First visualization

try:
    # Per-hour median vehicle count as the baseline
    hourly_baseline = (
        df
        .with_columns(pl.col("datetime").dt.hour().alias("hour"))
        .group_by("hour")
        .agg(pl.col("vehicle_count").median().alias("baseline"))
    )

    offsets = list(range(-WINDOW_BEFORE, WINDOW_AFTER + 1))

    df_events = (
        df
        .filter(
            (pl.col("precipitation") > RAIN_THRESHOLD) |
            (pl.col("snowfall") > SNOW_THRESHOLD)
        )
        .select("datetime")
        .with_columns(pl.lit(offsets).alias("offset"))
        .explode("offset")
        .with_columns(
            (pl.col("datetime") + pl.duration(hours=pl.col("offset"))).alias("target_datetime")
        )
        .join(
            df.select(["datetime", "vehicle_count"]),
            left_on="target_datetime", right_on="datetime", how="left",
        )
        .with_columns(pl.col("target_datetime").dt.hour().alias("hour"))
        .join(hourly_baseline, on="hour", how="left")
        .filter(pl.col("vehicle_count").is_not_null() & pl.col("baseline").is_not_null())
        .with_columns(
            (pl.col("vehicle_count") / pl.col("baseline") * 100).alias("relative_count")
        )
        .select(["offset", "relative_count"])
    )

    if df_events.is_empty():
        st.warning("No data found in the event window.")
    else:
        median_line = (
            df_events.group_by("offset")
            .agg(pl.col("relative_count").median())
            .sort("offset")
        )

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df_events["offset"].to_list(),
            y=df_events["relative_count"].to_list(),
            mode="markers",
            marker=dict(color="steelblue", size=4, opacity=0.25),
            name="Individual Events",
        ))
        fig.add_trace(go.Scatter(
            x=median_line["offset"].to_list(),
            y=median_line["relative_count"].to_list(),
            mode="lines+markers",
            line=dict(color="tomato", width=3),
            marker=dict(size=7),
            name="Median",
        ))

        fig.add_vline(x=0, line_dash="dash",  line_color="white", opacity=0.5)
        fig.add_hline(y=100, line_dash="dot", line_color="gray",  opacity=0.5)

        fig.update_layout(
            title=(" "
            ),
            xaxis=dict(title="Hours relative to Event Start", tickmode="linear", dtick=1),
            yaxis=dict(title="Relative Vehicle Count (% of Hourly Median)"),
            legend=dict(x=0.01, y=0.99),
            height=550,
        )

        st.plotly_chart(apply_font(fig), width="stretch")

except Exception as e:
    st.warning("Something went wrong while loading — restarting...")
    st.session_state.clear()
    st.rerun()

# ====================================
# Text

st.markdown("""
    ### Definitions:
    Extreme weather events were identified using the following thresholds:

    - for rain: >10mm of rain per hour 
    - for snow: >1cm of snowfall per hour

    ####
    ### Description:
    To allow comparison with normal traffic conditions, a median line was calculated. It represents the typical traffic volume for the same hour of the day 
    when the extreme weather event began, using data from all other days at the counting station.  
    In other words, it shows the *average traffic level* that would normally be expected at that specific hour under normal weather conditions.
    The dots represent the vehicle count during extreme weather in relative percentage to the median line.
    
    ####
    ### How we aggregated the Data:
    For each event *hourly traffic volumes* at counting station 1194 ("Autobahn-Kreuz Kiel-West") were analyzed in a time window of two hours before, and four hours 
    after the start of an extreme weather event. We only took data from this counting station again, as an average over multiple counting stations could cause the 
    results of local extreme weather to cancel each other out.  

    ####
    ### No Conclusion can be made:
    As we wanted to analyze how long it takes for traffic volumes to return to baseline levels (represented by the median line), we noticed the fact that local extreme 
    weather events often only last a short period of time.  
    To address the research question we would have needed minutely data of weather and vehicle counts. With the given data, no solid analysis can be performed!
""")

# ====================================
# Website design

st.divider()

col1_bottom_btn, col2_bottom_btn, col3_bottom_btn = st.columns([1, 3.6, 1])

with col1_bottom_btn:
    if st.button("⬅️ Previous Question", key="btn_bottom"):
        st.switch_page("pages/Research_Question_8.py")

st.divider()

col4_bottom_btn, col5_bottom_btn, col6_bottom_btn, col7_bottom_btn = st.columns([1, 0.33, 0.33, 1])

with col5_bottom_btn:
    if st.button("Go to Imprint", width="stretch"):
        st.switch_page("pages/Imprint.py")

with col6_bottom_btn:
    if st.button("Back to Homepage 🏠", width="stretch"):
        st.switch_page("pages/homepage.py")
