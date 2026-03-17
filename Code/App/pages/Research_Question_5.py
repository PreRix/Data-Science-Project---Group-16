import streamlit as st
# ==============================
# hier nötige Imports hinzufügen
import polars as pl
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
# ==============================

col1_top_btn, col2_top_btn, col3_top_btn = st.columns([1, 3.6, 1])

with col1_top_btn:
    if st.button("⬅️ Previous Question", key = "btn_top1"):
        st.switch_page("pages/Research_Question_4.py")
        
with col3_top_btn:
    if st.button("Next Question ➡️", key = "btn_top2"):
        st.switch_page("pages/Research_Question_6.py")

st.title("Research Question #5")

# ==============================
CSV_HOLYFILE = "https://cloud.rz.uni-kiel.de/public.php/dav/files/NnYrtwJ7FLqC6en/?accept=zip"
CSV_REGISTRATION_DATA = "https://cloud.rz.uni-kiel.de/public.php/dav/files/aDAQmERmoBkwepJ/?accept=zip"
CSV_AIR_QUALITY = "https://cloud.rz.uni-kiel.de/public.php/dav/files/RC9wT3a5Fo7mwbf/?accept=zip"
# ==============================

st.markdown("""
    # *Using yearly registration data for Kiel to derive the estimated share of battery-electric vehicles in the regional fleet from 2021 to 2025, is there a measurable downward trend in NO<sub>2</sub> levels on high-traffic roads near Kiel?*
    ## Vehicle Registrations in Kiel - by Fuel Type 
""", unsafe_allow_html = True)

# ====================================
# Hier Visualisierungs-Code hinzufügen
FUEL_COLS = {
    "PT_Nach Kraftstoffarten_Benzin": "Petrol",
    "PT_Nach Kraftstoffarten_Diesel": "Diesel",
    "PT_Nach Kraftstoffarten_Hybrid insgesamt": "Hybrid (total)",
    "PT_Nach Kraftstoffarten_Elektro (BEV)": "Electric (BEV)",
    "PT_Nach Kraftstoffarten_Gas (einschl. bivalent)": "Gas",
    "PT_Nach Kraftstoffarten_darunter Plug-in-Hybrid": "Plug-in Hybrid",
    "PT_Nach Kraftstoffarten_sonstige": "Other",
}

FUEL_COLORS = {
    "Petrol": "#E85C4C",
    "Diesel": "#4C9BE8",
    "Hybrid (total)": "#2DB37A",
    "Electric (BEV)": "#00C2B2",
    "Gas": "#F5A623",
    "Plug-in Hybrid": "#A259E8",
    "Other": "#AAAAAA",
}

BEV_COL = "PT_Nach Kraftstoffarten_Elektro (BEV)"


@st.cache_data
def load_registration_data(path):

    df = pl.read_csv(path, infer_schema_length=0)

    casts = [pl.col("Year").cast(pl.Int32)] + [
        pl.col(c)
        .str.replace_all(r"\.", "")
        .cast(pl.Int64)
        for c in FUEL_COLS
    ]

    return df.with_columns(casts).sort("Year")


df_registrations = load_registration_data(CSV_REGISTRATION_DATA)

years = df_registrations["Year"].to_list()

fig = go.Figure()

for col, label in FUEL_COLS.items():

    values = df_registrations[col].to_list()

    fig.add_trace(
        go.Bar(
            name=label,
            x=years,
            y=values,
            marker_color=FUEL_COLORS[label]
        )
    )

fig.update_layout(
    barmode="stack",
    xaxis_title="Year",
    yaxis_title="Number of Registered Vehicles",
    legend=dict(orientation="h", y=1.1),
    height=550
)

st.plotly_chart(fig, use_container_width=True)
# ====================================

st.markdown("""
    For the first visualization we decided to show the share of *vehicles per fuel type for each year* using the bar chart above.  
    An initial observation is that the share of conventional fuel vehicles (petrol and diesel) decreases steadily every year.
    On the other hand the number with (partly) electric drivetrains increases every year, which confirms expectations based on political initiatives in recent 
    years.
""")

st.divider()

st.markdown("""
    ## Battery-Electric Vehicle (BEV) Share vs. Average NO<sub>2</sub> emission per Vehicle
""", unsafe_allow_html = True)

# ====================================
# Hier Visualisierungs-Code hinzufügen
@st.cache_data
def load_traffic_data(path):

    df = (
        pl.read_csv(path, infer_schema_length=0)
        .with_columns(
            pl.col("date").str.slice(6,4).cast(pl.Int32).alias("year")
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
            (pl.col("KFZ_R1") + pl.col("KFZ_R2")).alias("vehicles")
        )
    )

    return (
        df.group_by("year")
        .agg(pl.col("vehicles").mean().alias("avg_vehicles"))
        .sort("year")
    )


@st.cache_data
def load_no2_data(path):

    return (
        pl.read_csv(path, infer_schema_length=0)
        .with_columns(
            pl.col("date").str.slice(6,4).cast(pl.Int32).alias("year"),
            pl.col("nitrogen_dioxide").cast(pl.Float64).alias("no2")
        )
        .group_by("year")
        .agg(pl.col("no2").mean().alias("avg_no2"))
        .sort("year")
    )


df_traffic = load_traffic_data(CSV_HOLYFILE)
df_no2 = load_no2_data(CSV_AIR_QUALITY)

df_plot = df_registrations.join(df_no2, left_on="Year", right_on="year")

bev_share = (
    df_plot
    .select([
        "Year",
        BEV_COL,
        pl.sum_horizontal(list(FUEL_COLS.keys())).alias("total")
    ])
    .with_columns(
        (pl.col(BEV_COL) / pl.col("total") * 100).alias("bev_share")
    )
)

fig2 = make_subplots(specs=[[{"secondary_y": True}]])

fig2.add_trace(
    go.Scatter(
        x=bev_share["Year"],
        y=bev_share["bev_share"],
        name="BEV Share (%)",
        mode="lines+markers",
        line=dict(color="#00C2B2", width=3)
    ),
    secondary_y=False
)

fig2.add_trace(
    go.Scatter(
        x=df_no2["year"],
        y=df_no2["avg_no2"],
        name="Average NO₂",
        mode="lines+markers",
        line=dict(color="#E85C4C", width=3)
    ),
    secondary_y=True
)

fig2.update_layout(
    height=520,
    legend=dict(orientation="h", y=1.1),
)

fig2.update_yaxes(title_text="BEV Share (%)", secondary_y=False)
fig2.update_yaxes(title_text="Average NO₂ (µg/m³)", secondary_y=True)

st.plotly_chart(fig2, use_container_width=True)
# ====================================

st.markdown("""
    This visualization shows the average NO<sub>2</sub> emission per vehicle. We calculated this by summing up all NO<sub>2</sub> concentration data for *each year* and dividing it by the total vehicle counting data for all available stations *per year*.  
    This approach was chosen to normalize the data against fluctuations in traffic volume, providing a more comparable value for the evolution of NO<sub>2</sub> 
    levels over time.  
    The data shows that the concentrations vary throughout the year; a slight downward trend is only visible when taking a look at the regression line 
    of the data.

    ####
    ### Conclusion:
    As said above, a minor downward trend in NO<sub>2</sub> emissions is noticeable while the number of registered BEV vehicles is increasing.  
    Nevertheless, the data cannot determine whether the growth in battery-electric vehicle share causes the observed decrease in NO<sub>2</sub> levels.  
    This is due to two factors:

    1. The measurement of air pollutants is heavily affected by other metrics, as we discussed in RQ2.
    2. The registration number of battery-electric vehicles does not have to be representative for actual electric traffic load on streets in and around Kiel.

    To answer the question: Yes, a measurable downward trend can be spotted, and it correlates with the increasing numbers of BEV registrations.  
    But no, it can not be determined if this actually is a causation.
    
""", unsafe_allow_html = True)

st.divider()

col1_bottom_btn, col2_bottom_btn, col3_bottom_btn = st.columns([1, 3.6, 1])

with col1_bottom_btn:
    if st.button("⬅️ Previous Question", key = "btn_bottom1"):
        st.switch_page("pages/Research_Question_4.py")
        
with col3_bottom_btn:
    if st.button("Next Question ➡️", key = "btn_bottom2"):
        st.switch_page("pages/Research_Question_6.py")

st.divider()

col4_bottom_btn, col5_bottom_btn, col6_bottom_btn, col7_bottom_btn = st.columns([1, 0.33, 0.33, 1])

with col5_bottom_btn:
    if st.button("Go to Imprint", use_container_width = True):
        st.switch_page("pages/Imprint.py")

with col6_bottom_btn:
    if st.button("Back to Homepage 🏠", use_container_width = True):
        st.switch_page("pages/homepage.py")
