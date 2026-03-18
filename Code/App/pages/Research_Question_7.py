import streamlit as st
# ==============================
# hier nötige Imports hinzufügen
import polars as pl
import plotly.graph_objects as go
from datetime import date, timedelta
# ==============================

col1_top_btn, col2_top_btn, col3_top_btn = st.columns([1, 3.6, 1])

with col1_top_btn:
    if st.button("⬅️ Previous Question", key = "btn_top1"):
        st.switch_page("pages/Research_Question_6.py")
        
with col3_top_btn:
    if st.button("Next Question ➡️", key = "btn_top2"):
        st.switch_page("pages/Research_Question_8.py")

st.title("Research Question #7")

# ==============================
CSV_HOLYFILE = "https://cloud.rz.uni-kiel.de/public.php/dav/files/NnYrtwJ7FLqC6en/?accept=zip"
# ==============================

st.markdown("""
    # *How does the daily passenger transport and freight transport traffic change during Kieler Woche compared to the surrounding month (two weeks before and after)?*
    ## Traffic compared: Kieler Woche vs. Baseline Levels
""")

# ====================================
# Hier Visualisierungs-Code hinzufügen
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
    "AS Wankendorf": "1156",
}

BUFFER_DAYS = 14

WEEKDAYS_MAP = {
    1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu",
    5: "Fri", 6: "Sat", 7: "Sun"
}


@st.cache_data(show_spinner="Loading Measuring Points data …")
def load_measuring_points_data(path):

    df = pl.read_csv(path, infer_schema_length=0)

    return (
        df
        .with_columns(
            pl.col("date").str.to_datetime("%d.%m.%Y %H:%M").alias("datetime")
        )
        .with_columns([
            pl.col("datetime").dt.weekday().alias("weekday"),
            pl.col("datetime").dt.date().alias("date_only")
        ])
        .with_columns([
            pl.col("KFZ_R1")
            .str.strip_chars()
            .str.extract(r"^(-?\d+)")
            .cast(pl.Float64),

            pl.col("KFZ_R2")
            .str.strip_chars()
            .str.extract(r"^(-?\d+)")
            .cast(pl.Float64)
        ])
        .with_columns(
            (pl.col("KFZ_R1") + pl.col("KFZ_R2")).alias("Total_Traffic")
        )
    )


df_traffic = load_measuring_points_data(CSV_HOLYFILE)


col1, col2 = st.columns(2)

zst_label = col1.selectbox(
    "Counting station",
    list(ZST_VARS.keys())
)

zst_id = ZST_VARS[zst_label]

event_preset = col2.selectbox(
    "Select the year:",
    list(KIELER_WOCHE_PRESETS.keys())
)

start_date, end_date = KIELER_WOCHE_PRESETS[event_preset]


df_station = df_traffic.filter(pl.col("Zst") == zst_id)


baseline_start = start_date - timedelta(days=BUFFER_DAYS)
baseline_end = end_date + timedelta(days=BUFFER_DAYS)


df_daily = (
    df_station
    .group_by(["date_only","weekday"])
    .agg(pl.col("Total_Traffic").sum().alias("daily_traffic"))
)


df_event = df_daily.filter(
    (pl.col("date_only") >= start_date) &
    (pl.col("date_only") <= end_date)
)

df_base = df_daily.filter(
    ((pl.col("date_only") >= baseline_start) & (pl.col("date_only") < start_date)) |
    ((pl.col("date_only") > end_date) & (pl.col("date_only") <= baseline_end))
)


df_event_days = df_event.sort("date_only")


df_base_wd = (
    df_base
    .group_by("weekday")
    .agg(pl.col("daily_traffic").mean().alias("baseline"))
)


df_plot = df_event_days.join(df_base_wd, on="weekday", how="left")


x_labels = [
    f"{d.strftime('%d.%m.')} ({WEEKDAYS_MAP[w]})"
    for d, w in zip(df_plot["date_only"], df_plot["weekday"])
]


fig = go.Figure()

fig.add_trace(
    go.Bar(
        x=x_labels,
        y=df_plot["daily_traffic"],
        name="Traffic (Kieler Woche)",
        marker_color="#4C9BE8"
    )
)

fig.add_trace(
    go.Scatter(
        x=x_labels,
        y=df_plot["baseline"],
        name="Baseline Traffic",
        mode="lines+markers",
        line=dict(color="#E85C4C", width=3, dash="dot"),
        marker=dict(size=8)
    )
)

fig.update_layout(
    barmode="group",
    xaxis_title="Weekday",
    yaxis_title="Number of Vehicles",
    hovermode="x unified",
    height=600,
    legend=dict(
        orientation="h",
        y=1.05,
        x=0.5,
        xanchor="center"
    )
)

st.plotly_chart(fig, use_container_width=True)
# ====================================

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

    The counting station for which the data should be displayed can be selected.
    
    ####
    ### Interpretation:
    For the personal traffic a clear pattern can be identified. It can be observed that the traffic during the Kieler Woche is generally higher than baseline 
    traffic levels. This is especially noticeable on fridays and the weekend, where the baseline traffic decreases. This is expected, as on
    these days fewer people drive to work in Kiel. This also results in a decrease in the overall traffic count during Kieler Woche on these three days.  

    However for freight transport, no such pattern can be observed. The Kieler Woche traffic and basline level traffic are generally very even; with 
    more traffic on weekdays than on weekends, as many of these vehicles are not permitted to drive on these days.
""")

st.divider()

col1_bottom_btn, col2_bottom_btn, col3_bottom_btn = st.columns([1, 3.6, 1])

with col1_bottom_btn:
    if st.button("⬅️ Previous Question", key = "btn_bottom1"):
        st.switch_page("pages/Research_Question_6.py")
        
with col3_bottom_btn:
    if st.button("Next Question ➡️", key = "btn_bottom2"):
        st.switch_page("pages/Research_Question_8.py")
        
st.divider()

col4_bottom_btn, col5_bottom_btn, col6_bottom_btn, col7_bottom_btn = st.columns([1, 0.33, 0.33, 1])

with col5_bottom_btn:
    if st.button("Go to Imprint", use_container_width = True):
        st.switch_page("pages/Imprint.py")

with col6_bottom_btn:
    if st.button("Back to Homepage 🏠", use_container_width = True):
        st.switch_page("pages/homepage.py")
