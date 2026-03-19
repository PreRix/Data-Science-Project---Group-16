# ====================================
# Imports

import streamlit as st
import polars as pl
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.data_loader import load_traffic_base

# ====================================
# Website design

col1_top_btn, col2_top_btn, col3_top_btn = st.columns([1, 3.6, 1])

with col1_top_btn:
    if st.button("⬅️ Previous Question", key="btn_top1"):
        st.switch_page("pages/Research_Question_5.py")

with col3_top_btn:
    if st.button("Next Question ➡️", key="btn_top2"):
        st.switch_page("pages/Research_Question_7.py")

st.title("Research Question #6")

st.markdown("""
    # *How does the ratio of incoming and outgoing traffic around Kiel change during the day?*
    ## Incoming vs. Outgoing Traffic
""")

# ====================================
# Global variables

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
ZST_VARS = {
    "Kiel-West":     "1194",
    "Rumohr":        "1104",
    "AS Wankendorf": "1156",
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

try:
    # Rename R1/R2 to inbound/outbound and compute ratio — all in-memory on the cached base
    df_traffic = (
        load_traffic_base()
        .with_columns(pl.col("Zst").str.strip_chars())
        .rename({"KFZ_R1": "R1_Inbound", "KFZ_R2": "R2_Outbound"})
        .drop_nulls(["R1_Inbound", "R2_Outbound"])
        .with_columns(
            (pl.col("R1_Inbound") + pl.col("R2_Outbound")).alias("Total_KFZ")
        )
        .with_columns(
            pl.when(pl.col("Total_KFZ") > 0)
              .then(pl.col("R1_Inbound") / pl.col("Total_KFZ"))
              .otherwise(None)
              .alias("Inbound_Ratio")
        )
    )
except Exception as e:
    st.error(f"Could not load traffic data: {e}")
    st.stop()

# ====================================
# First visualization

try:
    col1, col2, col3 = st.columns(3)
    zst_label = col1.selectbox("Select Counting Station", list(ZST_VARS.keys()))
    zst_id    = ZST_VARS[zst_label]

    available_years  = sorted(df_traffic["datetime"].dt.year().unique().to_list(), reverse=True)
    selected_year    = col2.selectbox("Year", ["All Years"] + available_years)

    if selected_year == "All Years":
        df_filtered_time = df_traffic
        month_options    = ["Full Year"]
    else:
        df_filtered_time = df_traffic.filter(pl.col("datetime").dt.year() == selected_year)
        month_options    = ["Full Year"] + [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December",
        ]

    selected_month = col3.selectbox("Month", month_options)

    if selected_month != "Full Year":
        month_idx        = month_options.index(selected_month)
        df_filtered_time = df_filtered_time.filter(pl.col("datetime").dt.month() == month_idx)

    df_filtered = df_filtered_time.filter(pl.col("Zst") == zst_id)

    def get_ratio_matrix(df_subset: pl.DataFrame) -> np.ndarray:
        grouped = (
            df_subset.group_by(["weekday", "hour"])
            .agg(pl.col("Inbound_Ratio").mean().alias("avg_ratio"))
        )
        matrix = np.full((24, 7), np.nan)
        for row in grouped.iter_rows(named=True):
            d = row["weekday"] - 1
            h = row["hour"]
            matrix[h, d] = row["avg_ratio"]
        return matrix

    ratio_matrix = get_ratio_matrix(df_filtered)

    fig_hm = make_subplots(
        rows=1, cols=1,
        subplot_titles=["Directional traffic split: Percentage of total traffic moving towards Kiel. <br> Blue: higher volume entering Kiel. <br> Red: higher volume leaving Kiel"],
    )

    custom_rdbu = [
        [0.0, "rgb(178, 24, 43)"],
        [0.4, "rgb(244, 165, 130)"],
        [0.5, "rgb(255, 255, 255)"],
        [0.6, "rgb(146, 197, 222)"],
        [1.0, "rgb(33, 102, 172)"],
    ]

    fig_hm.add_trace(go.Heatmap(
        z=ratio_matrix, x=WEEKDAYS, y=list(range(24)),
        colorscale=custom_rdbu, zmin=0.2, zmax=0.8,
        hovertemplate="<b>%{x} at %{y}:00</b><br>Inbound Ratio: %{z:.2%}<extra></extra>",
        colorbar=dict(title="Ratio Inbound", tickformat=".0%"),
    ))

    fig_hm.update_layout(
        height=800,
        xaxis_title="Day of Week",
        yaxis_title="Hour of Day",
        yaxis=dict(tickmode="linear", dtick=1),
    )

    st.plotly_chart(apply_font(fig_hm), width="stretch")

    avg_in  = df_filtered["R1_Inbound"].mean()
    avg_out = df_filtered["R2_Outbound"].mean()
    st.markdown(f"**Quick Stats for {zst_label}:** Average Inbound: {avg_in:.0f} | Average Outbound: {avg_out:.0f}")

except Exception as e:
    st.warning("Something went wrong while loading — restarting...")
    st.session_state.clear()
    st.rerun()

# ====================================
# Text

st.markdown("""
    ### Description:
    The HeatMap shows how the traffic load on selected roads changes during the days of an *average week* when splitting for incoming and outgoing traffic.  
    The month, year and counting station for which the data should be displayed can be selected. 

    ####
    ### How we aggregated the Data:
    As data sources we selected the counting stations "Autobahn-Kreuz Kiel West" and "Rumohr" at the A215, as well as "AS Wankendorf" at the A21 as these are main 
    routes connecting Kiel with the rest of the country; while providing large amounts of data for analysis.  
    In our raw data the vehicle count is given per direction of travel, so we checked for each station which counts correspond to incoming and outgoing traffic.

    ####
    ### Interpretation:
    The observations greatly show the rush-hour traffic during the week when people come to Kiel to go to work in the morning and leave in the afternoon.  
    During weekdays the traffic at night is mainly outgoing, while around midnight the traffic is directed more in the other direction. This may be because of people 
    working nightshifts.  
    Additional findings can be observed when exploring different parameter combinations.
    Important to keep in mind: The HeatMap says **nothing about the absolute vehicle count** of one hour, it showcases the relation between the traffic loads on the 
    two directions of travel!
""")

# ====================================
# Website design

st.divider()

col1_bottom_btn, col2_bottom_btn, col3_bottom_btn = st.columns([1, 3.6, 1])

with col1_bottom_btn:
    if st.button("⬅️ Previous Question", key="btn_bottom1"):
        st.switch_page("pages/Research_Question_5.py")

with col3_bottom_btn:
    if st.button("Next Question ➡️", key="btn_bottom2"):
        st.switch_page("pages/Research_Question_7.py")

st.divider()

col4_bottom_btn, col5_bottom_btn, col6_bottom_btn, col7_bottom_btn = st.columns([1, 0.33, 0.33, 1])

with col5_bottom_btn:
    if st.button("Go to Imprint", width="stretch"):
        st.switch_page("pages/Imprint.py")

with col6_bottom_btn:
    if st.button("Back to Homepage 🏠", width="stretch"):
        st.switch_page("pages/homepage.py")
