import streamlit as st
# ==============================
# hier nötige Imports hinzufügen
import polars as pl
import plotly.graph_objects as go
# ==============================

col1_top_btn, col2_top_btn, col3_top_btn = st.columns([1, 3.6, 1])

with col1_top_btn:
    if st.button("⬅️ Previous Question", key = "btn_top1"):
        st.switch_page("pages/Research_Question_7.py")

with col3_top_btn:
    if st.button("Bonus Question ➡️", key = "btn_top2"):
        st.switch_page("pages/Research_Question_9.py")

st.title("Research Question #8")

# ==============================
CSV_HOLYFILE = "https://cloud.rz.uni-kiel.de/public.php/dav/files/NnYrtwJ7FLqC6en/?accept=zip"

DETAIL_YEAR = 2023
DETAIL_MONTH = 2
# ==============================

st.markdown("""
    # *How did the traffic in rush-hours change on Autobahnen around Kiel over the past five years?*
    ## Average Rush-Hour Traffic on the A215 (AK Kiel-West) on Weekdays only
""")

# ====================================
# Hier Visualisierungs-Code hinzufügen
@st.cache_data(show_spinner="Loading Measuring Points data …")
def load_measuring_points_data(path):

    df = (
        pl.read_csv(path, infer_schema_length=0)
        .filter(pl.col("Zst").str.strip_chars() == "1194")
        .with_columns(
            pl.col("date").str.to_datetime("%d.%m.%Y %H:%M").alias("datetime")
        )
        .with_columns(
            pl.col("datetime").dt.year().alias("year"),
            pl.col("datetime").dt.month().alias("month"),
            pl.col("datetime").dt.hour().alias("hour"),
            pl.col("datetime").dt.weekday().alias("weekday"),
            pl.col("datetime").dt.date().alias("day")
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
        .filter(pl.col("weekday") <= 5)
    )

    return df


df_traffic = load_measuring_points_data(CSV_HOLYFILE)


morning = df_traffic.filter(pl.col("hour").is_between(6, 9))
evening = df_traffic.filter(pl.col("hour").is_between(16, 18))


def avg_by_month(df, direction_col):

    return (
        df
        .group_by(["year", "month", "day"])
        .agg(pl.col(direction_col).sum().alias("daily_rush"))
        .group_by(["year", "month"])
        .agg(pl.col("daily_rush").mean().alias("avg_rush"))
        .sort(["year", "month"])
        .with_columns(
            (pl.col("year").cast(pl.Utf8) + "-" +
             pl.col("month").cast(pl.Utf8).str.zfill(2)).alias("year_month")
        )
        .to_pandas()
    )


df_morning_month = avg_by_month(morning, "KFZ_R1")
df_evening_month = avg_by_month(evening, "KFZ_R2")


fig1 = go.Figure()

fig1.add_trace(go.Scatter(
    x=df_morning_month["year_month"],
    y=df_morning_month["avg_rush"],
    name="Morning Rush – into Kiel (6–9h)",
    mode="lines+markers",
    line=dict(color="steelblue", width=3),
))

fig1.add_trace(go.Scatter(
    x=df_evening_month["year_month"],
    y=df_evening_month["avg_rush"],
    name="Evening Rush – out of Kiel (16–18h)",
    mode="lines+markers",
    line=dict(color="tomato", width=3),
))

fig1.update_layout(
    title="Monthly Avg. Rush-Hour Traffic on A215 – AK Kiel-West (2021–2025)",
    xaxis_title="Month",
    yaxis_title="Vehicles during Rush Hour",
    height=600
)

st.plotly_chart(fig1, use_container_width=True)
# ====================================

st.markdown("""
    The two lines in the chart represent the traffic of the two rush-hours each day at the A215, aggregated to an *average day of the month*. No other counting station 
    displays the commuter traffic better than this one, as the A215 is known for being a main commuter route for Kiel.  
    For the morning rush-hour we defined the time window from 6-9 a.m.; only considering the traffic coming to Kiel.  
    For the evening rush-hour we chose 4-6 p.m., while only considering traffic leaving Kiel.  
    Additionally we only took into account data from weekdays (Monday to Friday), so that data from weekends would not bias the result.  
    
    Noticeable is the drop in the month of December for every observed year. This is very likely linked to the Christmas season and holidays. 
    The month before, November, seems to always have an increase in average vehicle counts. Maybe because people try to get most of the work done before the Christmas
    break.  
    As well it can be seen pretty clearly that in August the vehicle counts during morning rush-hour decrease in comparison to the month before and after. This 
    may be correlated with summer holidays. Interestingly, for the evening rush-hour this pattern does not apply this strong. A reason for that might be 
    that on summer evenings the traffic is also including tourists coming to Kiel during noon, and leaving in the evening.

    ####
    ### Conclusion:
    Both lines show a general increase over the observation period. Especially the evening rush-hour in 2021 is having a massive increase. We think this is
    because it was the first summer after the second Corona lockdown which ended mid 2021. So people started coming to work again, while social life increased 
    significantly as well.  
    We think that in the years after the COVID-19 pandemic many companies slowly went back to normal in-person work; so that homeoffice opportunities mostly got 
    reduced in the past years. This may be a reason for the trend the data is showing.
""")

st.divider()

st.markdown("""
    ## Rush-Hour Traffic for one exemplary month - Feb 2023
""")

# ====================================
# Hier Visualisierungs-Code hinzufügen
df_month = df_traffic.filter(
    (pl.col("year") == DETAIL_YEAR) &
    (pl.col("month") == DETAIL_MONTH)
)


morning_month = df_month.filter(pl.col("hour").is_between(6, 9))
evening_month = df_month.filter(pl.col("hour").is_between(16, 18))


def avg_by_day(df, direction_col):

    return (
        df
        .group_by("day")
        .agg(pl.col(direction_col).sum().alias("daily_rush"))
        .sort("day")
        .to_pandas()
    )


df_morning_day = avg_by_day(morning_month, "KFZ_R1")
df_evening_day = avg_by_day(evening_month, "KFZ_R2")


fig2 = go.Figure()

fig2.add_trace(go.Scatter(
    x=df_morning_day["day"],
    y=df_morning_day["daily_rush"],
    name="Morning Rush – into Kiel (6–9h)",
    mode="lines+markers",
    line=dict(color="steelblue", width=3),
))

fig2.add_trace(go.Scatter(
    x=df_evening_day["day"],
    y=df_evening_day["daily_rush"],
    name="Evening Rush – out of Kiel (16–18h)",
    mode="lines+markers",
    line=dict(color="tomato", width=3),
))

fig2.update_layout(
    title=f"Daily Rush-Hour Traffic – {DETAIL_YEAR}-{str(DETAIL_MONTH).zfill(2)}",
    xaxis_title="Day of Month",
    yaxis_title="Vehicles during Rush Hour",
    height=600
)

st.plotly_chart(fig2, use_container_width=True)
# ====================================

st.markdown("""
    This figure illustrates the development over an exemplary month without holidays or other special events, allowing for a clearer interpretation of the traffic 
    patterns.
""")

st.divider()

col1_bottom_btn, col2_bottom_btn, col3_bottom_btn = st.columns([1, 3.6, 1])

with col1_bottom_btn:
    if st.button("⬅️ Previous Question", key = "btn_bottom1"):
        st.switch_page("pages/Research_Question_7.py")

with col3_bottom_btn:
    if st.button("Bonus Question ➡️", key = "btn_bottom2"):
        st.switch_page("pages/Research_Question_9.py")

st.divider()

col4_bottom_btn, col5_bottom_btn, col6_bottom_btn, col7_bottom_btn = st.columns([1, 0.33, 0.33, 1])

with col5_bottom_btn:
    if st.button("Go to Imprint", use_container_width = True):
        st.switch_page("pages/Imprint.py")

with col6_bottom_btn:
    if st.button("Back to Homepage 🏠", use_container_width = True):
        st.switch_page("pages/homepage.py")
