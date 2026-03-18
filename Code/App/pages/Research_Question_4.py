# ==============================
# Imports

import streamlit as st
import polars as pl
import plotly.express as px

# ==============================
# Website design

col1_top_btn, col2_top_btn, col3_top_btn = st.columns([1, 3.6, 1])

with col1_top_btn:
    if st.button("⬅️ Previous Question", key = "btn_top1"):
        st.switch_page("pages/Research_Question_3.py")
        
with col3_top_btn:
    if st.button("Next Question ➡️", key = "btn_top2"):
        st.switch_page("pages/Research_Question_5.py")

st.title("Research Question #4")

st.markdown("""
    # *How do Saturday and Sunday volumes near Kiel compare to weekday volumes, and has this weekend-to-weekday ration changed significantly over the five-year observation period?*
    ## Weekend vs. Weekday Traffic Load on the A215 (AK Kiel-West)
""")

# ==============================
# Global variables

CSV_HOLYFILE = "https://cloud.rz.uni-kiel.de/public.php/dav/files/NnYrtwJ7FLqC6en/?accept=zip"

# ====================================
# Data collection and help

CSV_HOLYFILE = "https://cloud.rz.uni-kiel.de/public.php/dav/files/NnYrtwJ7FLqC6en/?accept=zip"

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
    df = (
        pl.read_csv(path, infer_schema_length=0)

        .filter(pl.col("Zst") == "1194")

        .with_columns(
            pl.col("date").str.to_datetime("%d.%m.%Y %H:%M").alias("datetime")
        )

        .with_columns(
            pl.col("datetime").dt.year().alias("year"),
            pl.col("datetime").dt.weekday().alias("weekday"),
            pl.col("datetime").dt.date().alias("day")
        )

        .with_columns([
            pl.when(pl.col("K_KFZ_R1").str.strip_chars().is_in(["a","d"]))
            .then(None)
            .otherwise(
                pl.col("KFZ_R1")
                .str.strip_chars()
                .str.extract(r"^(-?\d+)")
                .cast(pl.Float64)
            )
            .alias("KFZ_R1"),

            pl.when(pl.col("K_KFZ_R2").str.strip_chars().is_in(["a","d"]))
            .then(None)
            .otherwise(
                pl.col("KFZ_R2")
                .str.strip_chars()
                .str.extract(r"^(-?\d+)")
                .cast(pl.Float64)
            )
            .alias("KFZ_R2"),
        ])

        .with_columns(
            (pl.col("KFZ_R1") + pl.col("KFZ_R2")).alias("vehicle_count")
        )
    )

    return df

try:
    df_traffic = load_measuring_points_data(CSV_HOLYFILE)
except FileNotFoundError:
    st.error(f"File not found: {CSV_HOLYFILE}")
    st.stop()

# ====================================
# First visualisation

def weekday_share(df):

    daily = (
        df
        .group_by(["year","day","weekday"])
        .agg(pl.col("vehicle_count").sum().alias("daily_traffic"))
    )

    daily = daily.with_columns(
        pl.when(pl.col("weekday") <= 5)
        .then(pl.lit("Weekday"))
        .when(pl.col("weekday") == 6)
        .then(pl.lit("Saturday"))
        .otherwise(pl.lit("Sunday"))
        .alias("day_type")
    )

    share = (
        daily
        .group_by(["year","day_type"])
        .agg(pl.col("daily_traffic").mean().alias("vehicle_count"))
        .sort(["year","day_type"])
    )

    return share

df_share = weekday_share(df_traffic)

years = sorted(df_share["year"].unique().to_list())
cols = st.columns(len(years))

for col, year in zip(cols, years):

    with col:

        df_year = df_share.filter(pl.col("year") == year)

        fig = px.pie(
            df_year.to_pandas(),
            values="vehicle_count",
            names="day_type",
            title=str(year),
            category_orders={
                "day_type": ["Weekday", "Saturday", "Sunday"]
            }
        )

        fig.update_traces(textposition="inside", textinfo="percent+label")

        st.plotly_chart(apply_font(fig), width=True)
        
# ====================================
# Text

st.markdown("""
    ### How we aggregated the Data:
    For this question we decided to use a pie chart for every year.  
    The data we used is from the counting station 1194 alone at the A215 because, as concluded in RQ4, this station is highly representative of commuter traffic 
    and traffic in general. 
    As well, there might be differences for the counting stations for the different days of the week, so effects we aim to capture in the analysis could 
    potentially cancel each other out.  
    To correctly illustrate the traffic volume of a weekday, the average of the data from monday to friday were summed up *per day and year* and then divided by 
    five.

    ####
    ### Description + Interpretation:
    It can be seen that the average weekday is always making 40-41% of traffic of the week. This is highly likely due to people working in and around 
    Kiel.  
    Saturdays stay consistent as well, accounting for 32-34% of the weekly traffic, while Sundays account for 25-27%.  
    We assume the average traffic on Saturdays to be greater than on Sundays because of many shops and businesses remain open that day; thus people are 
    visiting, or working at those places.  

    As said before, the numbers are equally the same for each year, so no significant change has occured over the years.
""")

# ==============================
# Website design

st.divider()

col1_bottom_btn, col2_bottom_btn, col3_bottom_btn = st.columns([1, 3.6, 1])

with col1_bottom_btn:
    if st.button("⬅️ Previous Question", key = "btn_bottom1"):
        st.switch_page("pages/Research_Question_3.py")
        
with col3_bottom_btn:
    if st.button("Next Question ➡️", key = "btn_bottom2"):
        st.switch_page("pages/Research_Question_5.py")

st.divider()

col4_bottom_btn, col5_bottom_btn, col6_bottom_btn, col7_bottom_btn = st.columns([1, 0.33, 0.33, 1])

with col5_bottom_btn:
    if st.button("Go to Imprint", width = True):
        st.switch_page("pages/Imprint.py")

with col6_bottom_btn:
    if st.button("Back to Homepage 🏠", width = True):
        st.switch_page("pages/homepage.py")