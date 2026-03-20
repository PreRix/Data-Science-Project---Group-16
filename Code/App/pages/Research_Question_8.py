# ====================================
# Imports

import streamlit as st
import polars as pl
import plotly.graph_objects as go

# ====================================
# Website design

col1_top_btn, col2_top_btn, col3_top_btn = st.columns([1, 3.6, 1])

with col1_top_btn:
    if st.button("⬅️ Previous Question", key="btn_top1"):
        st.switch_page("pages/Research_Question_7.py")

with col3_top_btn:
    if st.button("Bonus Question ➡️", key="btn_top2"):
        st.switch_page("pages/Research_Question_9.py")

st.title("Research Question #8")

st.markdown("""
    # *How did the traffic in rush-hours change on Autobahnen around Kiel over the past five years?*
    ## Average Rush-Hour Traffic on the A215 (AK Kiel-West) on Weekdays only
""")

# ====================================
# Global variables

DETAIL_YEAR  = 2023
DETAIL_MONTH = 2

# ====================================
# Data collection and help

def apply_font(fig):
    fig.update_layout(font_size=22, legend_font_size=22)
    if fig.layout.title.text:
        fig.update_layout(title_font_size=34)
    fig.update_xaxes(title_font_size=28, tickfont_size=22)
    fig.update_yaxes(title_font_size=28, tickfont_size=22)
    return fig

def make_rush_figure(x, y_morning, y_evening, title, x_title):
    fig = go.Figure([
        go.Scatter(x=x, y=y_morning, name="Morning Rush – into Kiel (6:00–8:59 a.m.)",
                   mode="lines+markers", line=dict(color="steelblue", width=3)),
        go.Scatter(x=x, y=y_evening, name="Evening Rush – out of Kiel (3:00–5:59 p.m.)",
                   mode="lines+markers", line=dict(color="tomato", width=3)),
    ])
    fig.update_layout(title=title, xaxis_title=x_title,
                      yaxis_title="Vehicles during Rush Hour", 
                      height=600, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
                      margin=dict(t=100)
                     )
    return apply_font(fig)

try:
    # Filter to Zst 1194, weekdays only — all in-memory on the shared cached base
    df_traffic = (
        st.session_state.df_traffic
        .filter(pl.col("Zst") == "1194")
        .filter(pl.col("weekday") <= 5)
    )
except Exception as e:
    st.error(f"Could not load traffic data: {e}")
    st.stop()

# ====================================
# Helper aggregations

def monthly_avg(df: pl.DataFrame, col: str) -> pl.DataFrame:
    """Daily-then-monthly average of `col` for rush-hour data."""
    return (
        df.group_by(["year", "month", "day"]).agg(pl.col(col).sum().alias("daily"))
        .group_by(["year", "month"]).agg(pl.col("daily").mean().alias("avg"))
        .sort(["year", "month"])
        .with_columns(
            (pl.col("year").cast(pl.Utf8) + "-" + pl.col("month").cast(pl.Utf8).str.zfill(2))
            .alias("year_month")
        )
    )

def daily_avg(df: pl.DataFrame, col: str) -> pl.DataFrame:
    """Per-day average of `col` within a single month's rush-hour data."""
    return (
        df.group_by("day").agg(pl.col(col).sum().alias("avg"))
        .sort("day")
    )

# ====================================
# First visualization — monthly overview 2021–2025

try:
    morning_all = df_traffic.filter(pl.col("hour").is_between(6, 8))
    evening_all = df_traffic.filter(pl.col("hour").is_between(15, 17))

    morning = monthly_avg(morning_all, "KFZ_R1")
    evening = monthly_avg(evening_all, "KFZ_R2")

    st.plotly_chart(
        make_rush_figure(
            morning["year_month"], morning["avg"], evening["avg"],
            title="Monthly Avg. Rush-Hour Traffic on A215 – AK Kiel-West (2021–2025)",
            x_title="Month",
        ),
        width="stretch",
    )

except Exception as e:
    st.warning("Something went wrong while loading — restarting...")
    st.session_state.clear()
    st.rerun()

# ====================================
# Text

st.markdown("""
    ### Definitions + How we aggregated the Data:
    The two lines in the chart represent the traffic of the two rush-hours each day at the A215, aggregated to an *average day of the month*. No other counting station 
    displays the commuter traffic better than this one, as the A215 is known for being a main commuter route for Kiel.  
    For the morning rush-hour we defined the time window from 6:00-8:59 a.m.; only considering the traffic coming to Kiel.  
    For the evening rush-hour we chose 3:00-5:59 p.m., while only considering traffic leaving Kiel.  
    Additionally we only took into account data from weekdays (Monday to Friday), so that data from weekends would not bias the result.  

    ####
    ### Description:
    Noticeable is the drop in the month of December for every observed year. This is very likely linked to the Christmas season and holidays. 
    The month before, November, seems to always have an increase in average vehicle counts. Maybe because people try to get most of the work done before the Christmas
    break.  
    As well it can be seen pretty clearly that in August the vehicle counts during morning rush-hour decrease in comparison to the month before and after. This 
    may be correlated with summer holidays. Interestingly, for the evening rush-hour this pattern does not apply this strong. A reason for that might be 
    that on summer evenings the traffic is also including tourists coming to Kiel during noon, and leaving in the evening.

    ####
    ### Interpretation:
    Both lines show a general increase over the observation period. Especially the evening rush-hour in 2021 is having a massive increase. We think this is
    because it was the first summer after the second Corona lockdown which ended mid 2021. So people started coming to work again, while social life increased 
    significantly as well.  
    We think that in the years after the COVID-19 pandemic many companies slowly went back to normal in-person work; so that home office opportunities mostly got 
    reduced in the past years. This may be a reason for the trend the data is showing.
""")

st.divider()

st.markdown(f"""
    ## Rush-Hour Traffic for one exemplary month - Feb {DETAIL_YEAR}
""")

# ====================================
# Second visualization — daily detail for DETAIL_YEAR / DETAIL_MONTH

try:
    df_month = df_traffic.filter(
        (pl.col("year") == DETAIL_YEAR) & (pl.col("month") == DETAIL_MONTH)
    )

    morning = daily_avg(df_month.filter(pl.col("hour").is_between(6, 8)),   "KFZ_R1")
    evening = daily_avg(df_month.filter(pl.col("hour").is_between(15, 17)), "KFZ_R2")

    st.plotly_chart(
        make_rush_figure(
            morning["day"], morning["avg"], evening["avg"],
            title=f"Daily Rush-Hour Traffic – {DETAIL_YEAR}-{str(DETAIL_MONTH).zfill(2)}",
            x_title="Day of Month",
        ),
        width="stretch",
    )

except Exception as e:
    st.warning("Something went wrong while loading — restarting...")
    st.session_state.clear()
    st.rerun()

# ====================================
# Text

st.markdown("""
    ### Description:
    This figure illustrates the development over an exemplary month without holidays or other special events, allowing for a clearer interpretation of the traffic 
    patterns.
""")

# ====================================
# Website design

st.divider()

col1_bottom_btn, col2_bottom_btn, col3_bottom_btn = st.columns([1, 3.6, 1])

with col1_bottom_btn:
    if st.button("⬅️ Previous Question", key="btn_bottom1"):
        st.switch_page("pages/Research_Question_7.py")

with col3_bottom_btn:
    if st.button("Bonus Question ➡️", key="btn_bottom2"):
        st.switch_page("pages/Research_Question_9.py")

st.divider()

col4_bottom_btn, col5_bottom_btn, col6_bottom_btn, col7_bottom_btn = st.columns([1, 0.33, 0.33, 1])

with col5_bottom_btn:
    if st.button("Go to Imprint", width="stretch"):
        st.switch_page("pages/Imprint.py")

with col6_bottom_btn:
    if st.button("Back to Homepage 🏠", width="stretch"):
        st.switch_page("pages/homepage.py")
