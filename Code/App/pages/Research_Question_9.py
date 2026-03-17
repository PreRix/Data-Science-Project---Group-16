import streamlit as st
# ==============================
# hier nötige Imports hinzufügen
import polars as pl
import plotly.graph_objects as go
# ==============================

col1_top_btn, col2_top_btn, col3_top_btn = st.columns([1, 3.6, 1])

with col1_top_btn:
    if st.button("⬅️ Previous Question", key = "btn_top"):
        st.switch_page("pages/Research_Question_8.py")

st.title("BONUS Research Question")

# ==============================
CSV_HOLYFILE = "https://cloud.rz.uni-kiel.de/public.php/dav/files/NnYrtwJ7FLqC6en/?accept=zip"
CSV_WEATHER_DATA = "https://cloud.rz.uni-kiel.de/public.php/dav/files/dYtnayFdSte8EPN/?accept=zip"

RAIN_THRESHOLD = 10.0
SNOW_THRESHOLD = 1.0
WINDOW_BEFORE = 2
WINDOW_AFTER = 4
# ==============================

st.markdown("""
    # *How do extreme weather events affect hourly traffic volumes at selected counting stations near Kiel, and how long does it take for traffic to return to normal levels?*
    ## Relative Traffic around Extreme Weather Events 
""")

# ====================================
# Hier Visualisierungs-Code hinzufügen
@st.cache_data(show_spinner="Loading Measuring Points data …")
def load_measuring_points_data(path):

    return (
        pl.read_csv(path, infer_schema_length=0)
        .filter(pl.col("Zst").str.strip_chars() == "1194")
        .with_columns(
            pl.col("date").str.to_datetime("%d.%m.%Y %H:%M").alias("datetime")
        )
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
            (pl.col("KFZ_R1") + pl.col("KFZ_R2")).alias("vehicle_count")
        )
        .select(["datetime","vehicle_count"])
    )


@st.cache_data(show_spinner="Loading Weather data …")
def load_weather_data(path):

    return (
        pl.read_csv(path)
        .filter(pl.col("location_Zst") == 1194)
        .with_columns(
            pl.col("date").str.to_datetime("%d.%m.%Y %H:%M").alias("datetime")
        )
        .select(["datetime","precipitation","snowfall"])
    )


df_traffic = load_measuring_points_data(CSV_HOLYFILE)
df_weather = load_weather_data(CSV_WEATHER_DATA)

df = df_traffic.join(df_weather, on="datetime", how="left")


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
        df.select(["datetime","vehicle_count"]),
        left_on="target_datetime",
        right_on="datetime",
        how="left"
    )
    .with_columns(pl.col("target_datetime").dt.hour().alias("hour"))
    .join(hourly_baseline, on="hour", how="left")
    .filter(pl.col("vehicle_count").is_not_null())
    .with_columns(
        (pl.col("vehicle_count") / pl.col("baseline") * 100).alias("relative_count")
    )
    .select(["offset","relative_count"])
)


if df_events.is_empty():

    st.warning("No extreme weather events found in dataset.")

else:

    median_line = (
        df_events
        .group_by("offset")
        .agg(pl.col("relative_count").median())
        .sort("offset")
    )


    fig = go.Figure()


    fig.add_trace(
        go.Scatter(
            x=df_events["offset"].to_list(),
            y=df_events["relative_count"].to_list(),
            mode="markers",
            marker=dict(color="steelblue", size=4, opacity=0.25),
            name="Individual Events"
        )
    )


    fig.add_trace(
        go.Scatter(
            x=median_line["offset"].to_list(),
            y=median_line["relative_count"].to_list(),
            mode="lines+markers",
            line=dict(color="tomato", width=3),
            marker=dict(size=7),
            name="Median"
        )
    )


    fig.add_vline(x=0, line_dash="dash", line_color="white", opacity=0.5)
    fig.add_hline(y=100, line_dash="dot", line_color="gray", opacity=0.5)


    fig.update_layout(
        title="Relative Traffic around Extreme Weather Events (Zst. 1194)",
        xaxis_title="Hours relative to Event Start",
        yaxis_title="Relative Vehicle Count (% of Median)",
        height=550
    )


    st.plotly_chart(fig, use_container_width=True)
# ====================================

st.markdown("""
    Extreme weather events were identified using the following thresholds:

    - for rain: >10mm of rain per hour 
    - for snow: >1cm of snowfall per hour

    For each event *hourly traffic volumes* at counting station 1194 ("Autobahn-Kreuz Kiel-West") were analyzed in a time window of two hours before, and four hours 
    after the start of an extreme weather event. We only took data from this counting station again, as an average over multiple counting stations could cause the 
    results of local extreme weather to cancel each other out.  

    To allow comparison with normal traffic conditions, a median line was calculated. It represents the typical traffic volume for the same hour of the day 
    when the extreme weather event began, using data from all other days at the counting station.  
    In other words, it shows the *average traffic level* that would normally be expected at that specific hour under normal weather conditions.
    The dots represent the vehicle count during extreme weather in relative percentage to the median line.

    ####
    ### No Conclusion can be made
    As we wanted to analyze how long it takes for traffic volumes to return to baseline levels (represented by the median line), we noticed the fact that local extreme 
    weather events often only last a short period of time.  
    To address the research question we would have needed minutely data of weather and vehicle counts. With the given data, no solid analysis can be performed!
""")

st.divider()

col1_bottom_btn, col2_bottom_btn, col3_bottom_btn = st.columns([1, 3.6, 1])

with col1_bottom_btn:
    if st.button("⬅️ Previous Question", key = "btn_bottom"):
        st.switch_page("pages/Research_Question_8.py")

st.divider()

col4_bottom_btn, col5_bottom_btn, col6_bottom_btn, col7_bottom_btn = st.columns([1, 0.33, 0.33, 1])

with col5_bottom_btn:
    if st.button("Go to Imprint", use_container_width = True):
        st.switch_page("pages/Imprint.py")

with col6_bottom_btn:
    if st.button("Back to Homepage 🏠", use_container_width = True):
        st.switch_page("pages/homepage.py")
