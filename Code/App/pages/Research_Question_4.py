# ====================================
# Imports

import streamlit as st
import polars as pl
import plotly.express as px
from utils.data_loader import load_traffic_base

# ====================================
# Website design

col1_top_btn, col2_top_btn, col3_top_btn = st.columns([1, 3.6, 1])

with col1_top_btn:
    if st.button("⬅️ Previous Question", key="btn_top1"):
        st.switch_page("pages/Research_Question_3.py")

with col3_top_btn:
    if st.button("Next Question ➡️", key="btn_top2"):
        st.switch_page("pages/Research_Question_5.py")

st.title("Research Question #4")

st.markdown("""
    # *How do Saturday and Sunday volumes near Kiel compare to weekday volumes, and has this weekend-to-weekday ratio changed significantly over the five-year observation period?*
    ## Weekend vs. Weekday Traffic Load on the A215 (AK Kiel-West)
""")

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
    # Filter to station 1194
    df_traffic = (
        load_traffic_base()
        .filter(pl.col("Zst") == "1194")
        .rename({"KFZ_total": "vehicle_count"})
    )
except Exception as e:
    st.error(f"Could not load traffic data: {e}")
    st.stop()

# ====================================
# Helper aggregations

def weekday_share(df: pl.DataFrame) -> pl.DataFrame:
    daily = (
        df.group_by(["year", "day", "weekday"])
        .agg(pl.col("vehicle_count").sum().alias("daily_traffic"))
    )
    daily = daily.with_columns(
        pl.when(pl.col("weekday") <= 5).then(pl.lit("Weekday"))
        .when(pl.col("weekday") == 6).then(pl.lit("Saturday"))
        .otherwise(pl.lit("Sunday"))
        .alias("day_type")
    )
    return (
        daily.group_by(["year", "day_type"])
        .agg(pl.col("daily_traffic").mean().alias("vehicle_count"))
        .sort(["year", "day_type"])
    )

# ====================================
# First visualisation

try:
    df_share = weekday_share(df_traffic)
    years    = sorted(df_share["year"].unique().to_list())
    cols     = st.columns(len(years))

    for col, year in zip(cols, years):
        with col:
            df_year = df_share.filter(pl.col("year") == year)
            fig = px.pie(
                df_year.to_pandas(),
                values="vehicle_count",
                names="day_type",
                title=str(year),
                category_orders={"day_type": ["Weekday", "Saturday", "Sunday"]},
            )
            fig.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(apply_font(fig), width="stretch")

except Exception as e:
    st.warning("Something went wrong while loading — restarting...")
    st.session_state.clear()
    st.rerun()

# ====================================
# Text

st.markdown("""
    ### How we aggregated the Data:
    For this question we decided to use a pie chart for every year.  
    The data we used is from the counting station 1194 alone at the A215 because, as concluded in RQ?XY?, this station is highly representative of commuter traffic 
    and traffic in general. 
    As well, there might be differences for the counting stations for the different days of the week, so effects we aim to capture in the analysis could 
    potentially cancel each other out.  
    To correctly illustrate the traffic volume of a weekday, the average of the data from Monday to Friday were summed up *per day and year* and then divided by 
    five.

    ####
    ### Description + Interpretation:
    It can be seen that the average weekday is always making 40-41% of traffic of the week. This is highly likely due to people working in and around 
    Kiel.  
    Saturdays stay consistent as well, accounting for 32-34% of the weekly traffic, while Sundays account for 25-27%.  
    We assume the average traffic on Saturdays to be greater than on Sundays because many shops and businesses remain open that day; thus people are 
    visiting, or working at those places.  

    As said before, the numbers are equally the same for each year, so no significant change has occured over the years.
""")

# ====================================
# Website design

st.divider()

col1_bottom_btn, col2_bottom_btn, col3_bottom_btn = st.columns([1, 3.6, 1])

with col1_bottom_btn:
    if st.button("⬅️ Previous Question", key="btn_bottom1"):
        st.switch_page("pages/Research_Question_3.py")

with col3_bottom_btn:
    if st.button("Next Question ➡️", key="btn_bottom2"):
        st.switch_page("pages/Research_Question_5.py")

st.divider()

col4_bottom_btn, col5_bottom_btn, col6_bottom_btn, col7_bottom_btn = st.columns([1, 0.33, 0.33, 1])

with col5_bottom_btn:
    if st.button("Go to Imprint", width="stretch"):
        st.switch_page("pages/Imprint.py")

with col6_bottom_btn:
    if st.button("Back to Homepage 🏠", width="stretch"):
        st.switch_page("pages/homepage.py")