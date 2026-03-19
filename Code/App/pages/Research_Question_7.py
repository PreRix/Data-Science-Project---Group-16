# ====================================
# Imports

import streamlit as st
import polars as pl
import plotly.graph_objects as go
from datetime import date, timedelta
from utils.data_loader import load_traffic_base

# ====================================
# Website design

col1_top_btn, col2_top_btn, col3_top_btn = st.columns([1, 3.6, 1])

with col1_top_btn:
    if st.button("⬅️ Previous Question", key="btn_top1"):
        st.switch_page("pages/Research_Question_6.py")

with col3_top_btn:
    if st.button("Next Question ➡️", key="btn_top2"):
        st.switch_page("pages/Research_Question_8.py")

st.title("Research Question #7")

st.markdown("""
    # *How does the daily passenger transport and freight transport traffic change during the Kieler Woche compared to the surrounding month (two weeks before and after)?*
    ## Traffic compared: Kieler Woche vs. Baseline Levels
""")

# ====================================
# Global variables

KIELER_WOCHE_PRESETS = {
    "Kieler Woche 2025": (date(2025, 6, 21), date(2025, 6, 29)),
    "Kieler Woche 2024": (date(2024, 6, 22), date(2024, 6, 30)),    
    "Kieler Woche 2023": (date(2023, 6, 17), date(2023, 6, 25)),
    "Kieler Woche 2022": (date(2022, 6, 18), date(2022, 6, 26)),
    "Kieler Woche 2021": (date(2021, 9, 4),  date(2021, 9, 12)),
}

ZST_VARS = {
    "Kiel-West":     "1194",
    "Rumohr":        "1104",
    "AS Wankendorf": "1156",
}

BUFFER_DAYS  = 14
WEEKDAYS_MAP = {1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat", 7: "Sun"}

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
    # The base loader already cleaned Pkw/Mot/Bus/PmA _R1/_R2 if present in the CSV.
    # Compute Personal_Traffic and Truck_Traffic as lightweight in-memory ops.
    _base = load_traffic_base()

    df_traffic = _base.with_columns([
        (
            pl.col("Pkw_R1") + pl.col("Pkw_R2") +
            pl.col("Mot_R1") + pl.col("Mot_R2") +
            pl.col("Bus_R1") + pl.col("Bus_R2") +
            pl.col("PmA_R1") + pl.col("PmA_R2")
        ).alias("Personal_Traffic"),
        (pl.col("KFZ_R1") + pl.col("KFZ_R2")).alias("Total_Traffic"),
    ]).with_columns(
        (pl.col("Total_Traffic") - pl.col("Personal_Traffic")).alias("Truck_Traffic")
    )
except Exception as e:
    st.error(f"Could not load traffic data: {e}")
    st.stop()

# ====================================
# First visualization

try:
    col1, col2, col3, col4 = st.columns(4)
    options   = ["All stations"] + list(ZST_VARS.keys())
    zst_label = col1.selectbox("Counting station", options)
    zst_choice = list(ZST_VARS.values()) if zst_label == "All stations" else [ZST_VARS[zst_label]]

    df_station = df_traffic.filter(pl.col("Zst").is_in(zst_choice))

    with col2:
        event_preset = st.selectbox("Select the year:", list(KIELER_WOCHE_PRESETS.keys()))
        start_date, end_date = KIELER_WOCHE_PRESETS[event_preset]

    baseline_start = start_date - timedelta(days=BUFFER_DAYS)
    baseline_end   = end_date   + timedelta(days=BUFFER_DAYS)

    df_daily_sums = (
        df_station.group_by(["day", "weekday"])
        .agg([
            pl.col("Personal_Traffic").sum().alias("daily_cars"),
            pl.col("Truck_Traffic").sum().alias("daily_trucks"),
        ])
    )

    df_event_daily = df_daily_sums.filter(
        (pl.col("day") >= start_date) & (pl.col("day") <= end_date)
    )
    df_base_daily = df_daily_sums.filter(
        ((pl.col("day") >= baseline_start) & (pl.col("day") < start_date)) |
        ((pl.col("day") > end_date)        & (pl.col("day") <= baseline_end))
    )

    df_event_9days = (
        df_event_daily.sort("day")
        .select(["day", "weekday",
                pl.col("daily_cars").alias("event_cars"),
                pl.col("daily_trucks").alias("event_trucks")])
    )

    df_base_wd = (
        df_base_daily.group_by("weekday")
        .agg([
            pl.col("daily_cars").mean().alias("base_cars"),
            pl.col("daily_trucks").mean().alias("base_trucks"),
        ])
    )

    df_plot = df_event_9days.join(df_base_wd, on="weekday", how="left").sort("day")

    x_labels = [
        f"{d.strftime('%d.%m.')} ({WEEKDAYS_MAP[w]})"
        for d, w in zip(df_plot["day"], df_plot["weekday"])
    ]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=x_labels, y=df_plot["event_cars"].to_list(),
        name="Passenger Transport (Kieler Woche)",
        marker_color="#4C9BE8", offsetgroup=1,
    ))
    fig.add_trace(go.Bar(
        x=x_labels, y=df_plot["event_trucks"].to_list(),
        name="Freight Transport (Kieler Woche)",
        marker_color="#2b5c8f", offsetgroup=2,
    ))
    fig.add_trace(go.Scatter(
        x=x_labels, y=df_plot["base_cars"].to_list(),
        name="Ø Passenger Transport (Surrounding Month)",
        mode="lines+markers",
        line=dict(color="#EA4633", width=3, dash="dot"),
        marker=dict(size=8, symbol="diamond"),
    ))
    fig.add_trace(go.Scatter(
        x=x_labels, y=df_plot["base_trucks"].to_list(),
        name="Ø Freight Transport (Surrounding Month)",
        mode="lines+markers",
        line=dict(color="#2BF15D", width=3, dash="dot"),
        marker=dict(size=8, symbol="diamond"),
    ))

    fig.update_layout(
        barmode="group",
        xaxis_title="Weekday",
        yaxis_title="Number of Vehicles (Daily Sum)",
        hovermode="x unified",
        height=600,
        plot_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5),
        margin=dict(t=100),
    )
    fig.update_xaxes(gridcolor="#eeeeee")
    fig.update_yaxes(gridcolor="#eeeeee", zerolinecolor="#cccccc")

    st.plotly_chart(apply_font(fig), width="stretch")

    total_event_cars   = df_event_daily["daily_cars"].mean()
    total_base_cars    = df_base_daily["daily_cars"].mean()
    diff_cars          = ((total_event_cars / total_base_cars) - 1) * 100 if total_base_cars else 0
    total_event_trucks = df_event_daily["daily_trucks"].mean()
    total_base_trucks  = df_base_daily["daily_trucks"].mean()
    diff_trucks        = ((total_event_trucks / total_base_trucks) - 1) * 100 if total_base_trucks else 0

    col3.metric(
        "Ø Passenger Transport per Day (Kieler Woche vs. Baseline)",
        f"{total_event_cars:,.0f}", f"{diff_cars:+.1f}%",
    )
    col4.metric(
        "Ø Freight Transport per Day (Kieler Woche vs. Baseline)",
        f"{total_event_trucks:,.0f}", f"{diff_trucks:+.1f}%",
    )

except Exception as e:
    st.warning("Something went wrong while loading — restarting...")
    st.session_state.clear()
    st.rerun()

# ====================================
# Text

st.markdown("""
    ### Definitions:
     We separated the traffic into passenger transport and freight transport. These had to be defined:

    - Passenger transport includes all vehicles serving the main purpose of transporting people (e.g. cars, motorcycles, buses)
    - Freight transport includes all vehicles serving the main purpose of transporting something else than people (e.g. delivery trucks, heavy trucks).

    ####
    ### Description:
    In the diagram above, the bars show the actual sum of traffic on each of the Kieler Woche days; the year of Kieler Woche can be selected manually. The dotted 
    lines represent the baseline traffic levels; so the average of the correspondig weekday in the *two weeks* before and after the Kieler Woche.  
    We made this decision to use these time spans, so that the baseline level actually represents meaningful traffic values; so using data from the same season of 
    the year.
    
    ####
    ### How we aggregated the Data:
    To analyze the impact of Kieler Woche on traffic we used the *daily vehicle counts* for *every Kieler Woche* from selected counting stations around Kiel.
    Specifically, we used data from the following stations, as they monitor highly frequented roads:

    - station 1194: Autobahn Kreuz Kiel-West on the A215
    - station 1104: Rumohr on the A215
    - station 1156: AS Wankendorf on the A21.

    The counting station for which the data should be displayed can be selected, as well as the sum over all stations.
    
    ####
    ### Interpretation:
    For the personal traffic a clear pattern can be identified. It can be observed that the traffic during the Kieler Woche is generally higher than baseline 
    traffic levels. This is especially noticeable on fridays and the weekend, where the baseline traffic decreases. This is expected, as on
    these days fewer people drive to work in Kiel. This also results in a decrease in the overall traffic count during Kieler Woche on these three days.  

    However for freight transport, no such pattern can be observed. The Kieler Woche traffic and basline level traffic are generally very even; with 
    more traffic on weekdays than on weekends, as many of these vehicles are not permitted to drive on these days.
""")

st.warning("""
    Keep in mind: The Kieler Woche in 2021 was very different compared to a "normal" situation due to the COVID-19 pandemic. Therefore the data from this year 
    differs quite a lot from the other years.
""")

# ====================================
# Website design

st.divider()

col1_bottom_btn, col2_bottom_btn, col3_bottom_btn = st.columns([1, 3.6, 1])

with col1_bottom_btn:
    if st.button("⬅️ Previous Question", key="btn_bottom1"):
        st.switch_page("pages/Research_Question_6.py")

with col3_bottom_btn:
    if st.button("Next Question ➡️", key="btn_bottom2"):
        st.switch_page("pages/Research_Question_8.py")

st.divider()

col4_bottom_btn, col5_bottom_btn, col6_bottom_btn, col7_bottom_btn = st.columns([1, 0.33, 0.33, 1])

with col5_bottom_btn:
    if st.button("Go to Imprint", width="stretch"):
        st.switch_page("pages/Imprint.py")

with col6_bottom_btn:
    if st.button("Back to Homepage 🏠", width="stretch"):
        st.switch_page("pages/homepage.py")
