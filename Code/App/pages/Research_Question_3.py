# ==============================
# Imports

import streamlit as st
import polars as pl
import plotly.graph_objects as go

# ==============================
# Website design

col1_top_btn, col2_top_btn, col3_top_btn = st.columns([1, 3.6, 1])

with col1_top_btn:
    if st.button("⬅️ Previous Question", key = "btn_top1"):
        st.switch_page("pages/Research_Question_2.py")
        
with col3_top_btn:
    if st.button("Next Question ➡️", key = "btn_top2"):
        st.switch_page("pages/Research_Question_4.py")

st.title("Research Question #3")

st.markdown("""
    # *How has the total yearly vehicle count near Kiel changed in the past five years, and does the trend in registered vehicles per year in Kiel predict this change?*
    ## Long-Term Traffic Growth
""")

# ==============================
# Global variables

CSV_HOLYFILE = "https://cloud.rz.uni-kiel.de/public.php/dav/files/NnYrtwJ7FLqC6en/?accept=zip"
CSV_REGISTRATION_DATA = "https://cloud.rz.uni-kiel.de/public.php/dav/files/aDAQmERmoBkwepJ/?accept=zip"

ZST_VARS = {
    
    "Rumohr": "1104",
    "AS Wankendorf":      "1156",
    "Kiel-West": "1194",    
}

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

@st.cache_data(show_spinner="Loading Measuring Points data …")
def load_measuring_points_data(path):
    df = (
        pl.read_csv(path, infer_schema_length=0)
        .with_columns(
            pl.col("date").str.to_datetime("%d.%m.%Y %H:%M").alias("datetime")
        )
        .with_columns(
            pl.col("datetime").dt.year().alias("year"),
            pl.col("datetime").dt.date().alias("day")
        )
        .with_columns([
            pl.when(pl.col("K_KFZ_R1").str.strip_chars().is_in(["a", "d"]))
            .then(None)
            .otherwise(
                pl.col("KFZ_R1").str.strip_chars().str.extract(r"^(-?\d+)").cast(pl.Float64)
            )
            .alias("KFZ_R1"),

            pl.when(pl.col("K_KFZ_R2").str.strip_chars().is_in(["a", "d"]))
            .then(None)
            .otherwise(
                pl.col("KFZ_R2").str.strip_chars().str.extract(r"^(-?\d+)").cast(pl.Float64)
            )
            .alias("KFZ_R2"),
        ])
        .with_columns(
            (pl.col("KFZ_R1") + pl.col("KFZ_R2")).alias("vehicle_count")
        )
    )
    return df

@st.cache_data(show_spinner="Loading Registration data …")
def load_registrations_data(path):
    return (
        pl.read_csv(path, infer_schema_length=0)
        .select([
            pl.col("Year").cast(pl.Int64).alias("year"),
            pl.col("VT_Kraftfahrzeuge_insgesamt")
              .str.replace_all(r"\.", "")
              .cast(pl.Int64)
              .alias("registrations")
        ])
    )

try:
    df_traffic = load_measuring_points_data(CSV_HOLYFILE)
except FileNotFoundError:
    st.error(f"File not found: {CSV_HOLYFILE}")
    st.stop()

try:
    df_registrations = load_registrations_data(CSV_REGISTRATION_DATA)
except FileNotFoundError:
    st.error(f"File not found: {CSV_REGISTRATION_DATA}")
    st.stop()

# ====================================
# First visualisation

def yearly_avg_traffic(df):
    daily = (
        df
        .group_by(["year", "day", "Zst"])
        .agg(pl.col("vehicle_count").sum().alias("daily_traffic"))
    )
    whole = (daily
        .group_by("year", "Zst")
        .agg(pl.col("daily_traffic").mean().alias("avg_daily_traffic"))
        .sort("year"))
    return (
        whole
        .group_by("year")
        .agg(pl.col("avg_daily_traffic").sum().alias("traf"))
        .sort("year")
    )

target_ids = list(ZST_VARS.values())

df_traffic_zst = df_traffic.filter(pl.col("Zst").is_in(target_ids))
df_traffic = yearly_avg_traffic(df_traffic_zst)
df_plot = df_traffic.join(df_registrations, on="year", how="left").sort("year")

# Achsenbereich definieren
min_reg = df_plot["registrations"].min()
min_traffic = df_plot["traf"].min()
min_range = min(min_reg, min_traffic)
max_reg = df_plot["registrations"].max()
max_traffic = df_plot["traf"].max()
max_range = max(max_reg, max_traffic)

fig = go.Figure()

fig.add_trace(go.Bar(
    x=df_plot["year"],
    y=df_plot["registrations"],
    name="Registered Vehicles (Kiel)",
    marker_color="steelblue",
    opacity=0.7,
    yaxis="y1"
))

fig.add_trace(go.Scatter(
    x=df_plot["year"],
    y=df_plot["traf"],
    name="Avg. Daily Traffic",
    mode="lines+markers",
    line=dict(color="tomato", width=3),
    marker=dict(size=8),
    yaxis="y2"
))

fig.update_layout(
    title="Registered Vehicles vs. Avg. Daily Traffic",
    xaxis=dict(
        title="Year",
        tickmode="linear",
        dtick=1
    ),

    yaxis=dict(
        title=dict(text="Registered Vehicles (SH)", font=dict(color="steelblue")),
        tickfont=dict(color="steelblue"),
        range=[min_range * 0.95, max_range * 1.05]
    ),

    yaxis2=dict(
        title=dict(text="Avg. Vehicles / Day", font=dict(color="tomato")),
        tickfont=dict(color="tomato"),
        overlaying="y",
        side="right",
        showgrid=False,
        range=[min_range * 0.95, max_range * 1.05]
    ),

    legend=dict(
    x=0.5,
    y=-0.2,
    xanchor="center",
    yanchor="top",
    orientation="h"
),
    height=550,
)

st.plotly_chart(apply_font(fig), width = "stretch")

# ====================================
# Text

st.markdown("""

    ### Description:  
    It can be seen that the number in registered vehicles increases each year except between 2024 and 2025. However, the increase is very subtle, which becomes
    apparent when considering the scale of the y-axis. Thus, the registration counts stay pretty stable over the years.
    The corresponding vehicle counts for traffic load are increasing over all years in a noticeable wider range.
    From 2023 to 2024 the number of registered vehicles has the "biggest" increase, while this is the year in which the average daily traffic load has the smallest one.
    A similar phenomenon can be observed for the time span from 2024 to 2025, where the registration count is decreasing, while the traffic load has an 
    increase.  

    ####
    ### How we aggregated the Data:
    This Bar-Line-Chart illustrates the evolution of *daily average traffic* in comparison to the registered vehicle counts for Kiel *per year* from 2021 to 2025.  
    As the data for registration counts is only available in yearly sample, we had to aggregate the traffic numbers to a yearly value as well. 

    ####
    ### Interpretation: 
    The total yearly vehicle count did steadily increase over the past years; especially from 2022 to 2023 after the COVID-19 pandemic.
    Vehicle registration counts on the other hand stayed pretty consistent over time.
    The figure shows that traffic volume and vehicle registration counts do not show a strong relationship. A clear correlation can not be derived from the 
    data.  
    What has to be taken into account as well is the fact that registration count for Kiel does not solely influence the vehicle count on streets around Kiel.
    Especially on roads like the A215, where one of the measuring stations for vehicle counting is placed, a lot of commuters pass by; so cars get counted 
    while not being registered for Kiel or vice versa.
""")

# ==============================
# Website design

st.divider()

col1_bottom_btn, col2_bottom_btn, col3_bottom_btn = st.columns([1, 3.6, 1])

with col1_bottom_btn:
    if st.button("⬅️ Previous Question", key = "btn_bottom1"):
        st.switch_page("pages/Research_Question_2.py")
        
with col3_bottom_btn:
    if st.button("Next Question ➡️", key = "btn_bottom2"):
        st.switch_page("pages/Research_Question_4.py")

st.divider()

col4_bottom_btn, col5_bottom_btn, col6_bottom_btn, col7_bottom_btn = st.columns([1, 0.33, 0.33, 1])

with col5_bottom_btn:
    if st.button("Go to Imprint", width = "stretch"):
        st.switch_page("pages/Imprint.py")

with col6_bottom_btn:
    if st.button("Back to Homepage 🏠", width = "stretch"):
        st.switch_page("pages/homepage.py")