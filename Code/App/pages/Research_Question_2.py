import streamlit as st
# ==============================
# hier nötige Imports hinzufügen
import polars as pl
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
# ==============================

col1_top_btn, col2_top_btn, col3_top_btn = st.columns([1, 3.6, 1])

with col1_top_btn:
    if st.button("⬅️ Previous Question", key = "btn_top1"):
        st.switch_page("pages/Research_Question_1.py")
        
with col3_top_btn:
    if st.button("Next Question ➡️", key = "btn_top2"):
        st.switch_page("pages/Research_Question_3.py")

st.title("Research Question #2")

# ==============================
CSV_HOLYFILE = "https://cloud.rz.uni-kiel.de/public.php/dav/files/NnYrtwJ7FLqC6en/?accept=zip"

AIR_QUALITY_VARS = {
    "PM10": "pm10",
    "PM2.5": "pm2_5",
    "NO₂": "nitrogen_dioxide",
    "CO": "carbon_monoxide",
}

YEAR_COLORS = ["#4C9BE8", "#E85C4C", "#2DB37A", "#F5A623", "#A259E8"]
# ==============================

st.markdown("""
    # *To what extend does the hourly NO<sub>2</sub>, CO, PM<sub>2,5</sub> and PM<sub>10</sub> concentration in Kiel correlate with vehicle count?*
    ## Air Quality & Traffic - Hourly Analysis
""", unsafe_allow_html = True)

# ====================================
# Hier Visualisierungs-Code hinzufügen
@st.cache_data(show_spinner="Loading Measuring Points data …")
def load_measuring_points_data(path):

    df = pl.read_csv(path, infer_schema_length=0)

    return (
        df
        .filter(pl.col("Zst").str.strip_chars() == "1194")
        .with_columns(
            pl.col("date").str.to_datetime("%d.%m.%Y %H:%M").alias("datetime")
        )
        .with_columns(
            pl.col("datetime").dt.hour().alias("hour"),
            pl.col("datetime").dt.year().alias("year")
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
        .with_columns((pl.col("KFZ_R1") + pl.col("KFZ_R2")).alias("KFZ_total"))
        .with_columns([
            pl.col(c).cast(pl.Float64, strict=False)
            for c in AIR_QUALITY_VARS.values()
        ])
    )

df_traffic = load_measuring_points_data(CSV_HOLYFILE)

col1, col2 = st.columns(2)

aq_label = col1.selectbox("Air quality variable", list(AIR_QUALITY_VARS))
aq_col = AIR_QUALITY_VARS[aq_label]

all_years = sorted(df_traffic["year"].unique().to_list())

years_sel = col2.multiselect(
    "Years",
    all_years,
    default=all_years
)

kfz_col = "KFZ_total"
hours = list(range(24))

fig = make_subplots(specs=[[{"secondary_y": True}]])

for i, year in enumerate(years_sel):

    color = YEAR_COLORS[i % len(YEAR_COLORS)]

    subset = df_traffic.filter(pl.col("year") == year)

    hourly = (
        subset
        .group_by("hour")
        .agg(
            pl.col(aq_col).mean().alias("aq"),
            pl.col(kfz_col).mean().alias("kfz")
        )
        .sort("hour")
    )

    aq_map = dict(zip(hourly["hour"], hourly["aq"]))
    kfz_map = dict(zip(hourly["hour"], hourly["kfz"]))

    aq_vals = [aq_map.get(h, np.nan) for h in hours]
    kfz_vals = [kfz_map.get(h, np.nan) for h in hours]

    fig.add_trace(
        go.Scatter(
            x=hours,
            y=aq_vals,
            name=f"{aq_label} {year}",
            mode="lines+markers",
            line=dict(color=color)
        ),
        secondary_y=False
    )

    fig.add_trace(
        go.Scatter(
            x=hours,
            y=kfz_vals,
            name=f"Vehicles {year}",
            mode="lines",
            line=dict(color=color, dash="dot"),
            opacity=0.6
        ),
        secondary_y=True
    )

fig.update_layout(
    xaxis_title="Hour",
    hovermode="x unified",
    height=520
)

fig.update_yaxes(title_text=aq_label, secondary_y=False)
fig.update_yaxes(title_text="Vehicles/hour", secondary_y=True)

st.plotly_chart(fig, use_container_width=True)
# ====================================

st.markdown("""
    ### Description:
    This diagram shows that the hourly data was aggregated into an *average diurnal cycle* for the concentration of air pollutants, while displaying the 
    corresponding *average vehicle count per hour* as well. It can be selected which pollutant should be displayed as well as the year one wants to see 
    (multiple selections possible).
    It can be seen that, interestingly, the concentration of almost all air quality variables is dropping at noon, while the vehicle count starts rising.  
    On the other hand, during night and morning times, these concentrations are increasing.
    
    ####
    ### Most interesting finding:
    At first, this seems to be an error in our data, but some meteorological phenomena actually explain this **interesting** finding:  
    
    1. When the sun sets, the air near the ground gets colder than the air above. The air gets denser and traps the pollutants near the ground, inhibiting
    vertical dispersion.  
    When the sun starts heating up the Earth's surface, the pollutants get carried up with the warmer air and mix with fresh air.
    2. At night time the wind generally subsides, leading to less airflow, and a more stable air layer holding the pollutants and their concentrations higher.  
    During the day, when winds increase, the concentration of pollutants decreases as they mix with fresh air and are more likely to be blown away at the
    local measuring point. 

    ####
    ### How we aggregated the Data:
    For this analysis, we used data from the vehicle counting station 1194 ("Autobahnkreuz Kiel-West") alone, as it is one of the main routes in the Kiel area, 
    being highly representative for this question. Therefore we retrieved air quality data for the coordinate sector of this station.  
    Furthermore, we want to mention that the available air quality data is **not** provided by a sensor station right next to the road. The data is provided from 
    different sources via Open-Meteo with spatial resolution showing the "general" air quality of the area.

    ####   
    ### Interpretation:
    The aggregated diurnal profiles suggest that pollutant concentrations do not directly follow traffic intensity. While traffic 
    is a primary source of emissions, its correlation with observed air quality appears to be masked at a regional scale by meteorological processes such as
    atmospheric stability, vertical mixing and wind conditions.
""")

st.divider()

st.markdown("""
    ## Correlation HeatMap - Air Quality vs. Traffic
""")

# ====================================
# Hier Visualisierungs-Code hinzufügen
corr_vars = ["KFZ_total"] + list(AIR_QUALITY_VARS.values())
corr_labels = ["Vehicles"] + list(AIR_QUALITY_VARS.keys())

subset = df_traffic.filter(pl.col("year").is_in(years_sel))

cols = []
for c in corr_vars:

    s = subset[c].cast(pl.Float64, strict=False).to_numpy().astype(float)

    cols.append(s)

mat = np.column_stack(cols)

mask = ~np.isnan(mat).any(axis=1)

mat = mat[mask]

corr_matrix = np.corrcoef(mat, rowvar=False)

fig_corr = go.Figure(
    data=go.Heatmap(
        z=corr_matrix,
        x=corr_labels,
        y=corr_labels,
        zmin=-1,
        zmax=1,
        colorscale="RdBu",
        reversescale=True,
        text=np.round(corr_matrix,2),
        texttemplate="%{text}",
    )
)

fig_corr.update_layout(height=450)

st.plotly_chart(fig_corr, use_container_width=True)
# ====================================

st.markdown("""
    ### Description:
    Correlation-HeatMaps are used to not only illustrate the correlation between the vehicle count and the different air quality variables, but also the 
    correlation among the air quality variables themselves.  
    The diagonal axis is filled with "1s", as each variable is perfectly correlated with itself. This also confirms that the code is working properly.  
    For the vehicle count, we can observe that it is negativeley correlated with all selected air quality variables.  
    This confirms the observations that can be made from the figure above with numerical values as well.
""")

st.divider()

col1_bottom_btn, col2_bottom_btn, col3_bottom_btn = st.columns([1, 3.6, 1])

with col1_bottom_btn:
    if st.button("⬅️ Previous Question", key = "btn_bottom1"):
        st.switch_page("pages/Research_Question_1.py")
        
with col3_bottom_btn:
    if st.button("Next Question ➡️", key = "btn_bottom2"):
        st.switch_page("pages/Research_Question_3.py")

st.divider()

col4_bottom_btn, col5_bottom_btn, col6_bottom_btn, col7_bottom_btn = st.columns([1, 0.33, 0.33, 1])

with col5_bottom_btn:
    if st.button("Go to Imprint", use_container_width = True):
        st.switch_page("pages/Imprint.py")

with col6_bottom_btn:
    if st.button("Back to Homepage 🏠", use_container_width = True):
        st.switch_page("pages/homepage.py")
