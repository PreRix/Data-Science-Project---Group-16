# ====================================
# Imports

import streamlit as st
import polars as pl
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.data_loader import load_traffic_base, AIR_QUALITY_VARS

# ====================================
# Website design

col1_top_btn, col2_top_btn, col3_top_btn = st.columns([1, 3.6, 1])

with col1_top_btn:
    if st.button("⬅️ Previous Question", key="btn_top1"):
        st.switch_page("pages/Research_Question_1.py")

with col3_top_btn:
    if st.button("Next Question ➡️", key="btn_top2"):
        st.switch_page("pages/Research_Question_3.py")

st.title("Research Question #2")

st.markdown("""
    # *To what extent does the hourly NO<sub>2</sub>, CO, PM<sub>2.5</sub> and PM<sub>10</sub> concentration in Kiel correlate with vehicle count?*
    ## Air Quality & Traffic - Hourly Analysis
""", unsafe_allow_html=True)

# ====================================
# Global variables

YEAR_COLORS = ["#4C9BE8", "#E85C4C", "#2DB37A", "#F5A623", "#A259E8"]

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
    df_traffic = load_traffic_base().filter(pl.col("Zst").str.strip_chars() == "1194")
except Exception as e:
    st.error(f"Could not load traffic data: {e}")
    st.stop()

# ====================================
# First visualization

try:
    col1, col2 = st.columns(2)
    aq_label = col1.selectbox("Air quality variable", list(AIR_QUALITY_VARS))
    aq_col   = AIR_QUALITY_VARS[aq_label]

    all_years = sorted(df_traffic["year"].unique().to_list())
    years_sel = col2.multiselect("Years (empty = all)", all_years, default=[])
    active_years = years_sel

    if not active_years:
        st.info("Select at least one year to display data.")
        st.stop()

    kfz_col = "KFZ_total"
    hours   = list(range(24))

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    for i, year in enumerate(active_years):
        color  = YEAR_COLORS[i % len(YEAR_COLORS)]
        subset = df_traffic.filter(pl.col("year") == year)

        hourly = (
            subset.group_by("hour")
            .agg(pl.col(aq_col).mean().alias("aq"), pl.col(kfz_col).mean().alias("kfz"))
            .sort("hour")
        )

        aq_map  = dict(zip(hourly["hour"].to_list(), hourly["aq"].to_list()))
        kfz_map = dict(zip(hourly["hour"].to_list(), hourly["kfz"].to_list()))
        aq_vals  = [aq_map.get(h,  float("nan")) for h in hours]
        kfz_vals = [kfz_map.get(h, float("nan")) for h in hours]

        fig.add_trace(go.Scatter(
            x=hours, y=aq_vals, name=f"{aq_label} {year}",
            mode="lines+markers", line=dict(color=color, width=2), marker=dict(size=4),
        ), secondary_y=False)

        fig.add_trace(go.Scatter(
            x=hours, y=kfz_vals, name=f"Vehicles {year}",
            mode="lines", line=dict(color=color, width=2, dash="dot"), opacity=0.6,
        ), secondary_y=True)

    fig.update_layout(
        xaxis=dict(title="Hour", tickmode="linear", dtick=1, range=[0, 23]),
        hovermode="x unified", plot_bgcolor="white", height=520,
        legend=dict(orientation="h", y=1.08),
    )
    fig.update_yaxes(title_text=aq_label,        secondary_y=False, gridcolor="#eeeeee")
    fig.update_yaxes(title_text="Vehicles/hour", secondary_y=True,  gridcolor="#eeeeee", showgrid=False)

    st.plotly_chart(apply_font(fig), width="stretch")

except Exception as e:
    st.warning("Something went wrong while loading — restarting...")
    st.session_state.clear()
    st.rerun()

# ====================================
# Text

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
# Second visualization

try:
    hm_col1, hm_col2 = st.columns(2)

    if len(active_years) < 2 and st.session_state.get("hm_mode") == "Per year (side by side)":
        st.session_state["hm_mode"] = "Overall (all selected years)"

    hm_options = ["Overall (all selected years)"]
    if len(active_years) > 1:
        hm_options.append("Per year (side by side)")

    hm_mode        = hm_col1.radio("Show correlations", hm_options, horizontal=True, key="hm_mode")
    hm_granularity = hm_col2.radio(
        "Correlate using",
        ["Raw hourly rows", "Hourly means (aggregated)"],
        horizontal=True,
    )

    corr_vars   = [kfz_col] + list(AIR_QUALITY_VARS.values())
    corr_labels = ["Vehicles"] + list(AIR_QUALITY_VARS.keys())

    def compute_corr_matrix(subset: pl.DataFrame) -> np.ndarray:
        if hm_granularity == "Hourly means (aggregated)":
            subset = subset.group_by("hour").agg([pl.col(c).mean() for c in corr_vars])
        cols = [subset[c].cast(pl.Float64, strict=False).to_numpy().astype(float) for c in corr_vars]
        mat  = np.column_stack(cols)
        mat  = mat[~np.isnan(mat).any(axis=1)]
        if mat.shape[0] < 2:
            return np.full((len(corr_vars), len(corr_vars)), np.nan)
        return np.corrcoef(mat, rowvar=False)

    def make_heatmap_trace(matrix: np.ndarray, show_colorbar: bool = True) -> go.Heatmap:
        rounded = np.round(matrix, 2)
        return go.Heatmap(
            z=rounded, x=corr_labels, y=corr_labels,
            zmin=-1, zmax=1, colorscale="RdBu", reversescale=True,
            text=[[f"{v:.2f}" if not np.isnan(v) else "n/a" for v in row] for row in rounded],
            texttemplate="%{text}", textfont=dict(size=15),
            showscale=show_colorbar,
            colorbar=dict(title="r", thickness=14, len=0.9),
        )

    if hm_mode == "Overall (all selected years)":
        matrix = compute_corr_matrix(df_traffic.filter(pl.col("year").is_in(active_years)))
        fig_hm = go.Figure(make_heatmap_trace(matrix))
        fig_hm.update_layout(
            height=450, plot_bgcolor="white",
            margin=dict(l=10, r=10, t=50, b=10),
            yaxis=dict(autorange="reversed"),
            title=dict(
                text=f"Pearson r — {', '.join(str(y) for y in active_years)}",
                font=dict(size=13),
            ),
        )
        st.plotly_chart(apply_font(fig_hm), width="stretch")

    else:
        n_years = len(active_years)
        fig_hm  = make_subplots(
            rows=1, cols=n_years,
            subplot_titles=[str(y) for y in active_years],
            horizontal_spacing=0.06,
        )
        for col_idx, year in enumerate(active_years, start=1):
            matrix = compute_corr_matrix(df_traffic.filter(pl.col("year") == year))
            trace  = make_heatmap_trace(matrix, show_colorbar=(col_idx == n_years))
            fig_hm.add_trace(trace, row=1, col=col_idx)

        fig_hm.update_layout(
            height=450, plot_bgcolor="white",
            margin=dict(l=10, r=10, t=50, b=10),
        )
        for col_idx in range(1, n_years + 1):
            axis_key = "yaxis" if col_idx == 1 else f"yaxis{col_idx}"
            fig_hm.update_layout(**{axis_key: dict(autorange="reversed")})
        st.plotly_chart(apply_font(fig_hm), width="stretch")

    # ── Summary table ──────────────────────────────────────────────────────────────
    with st.expander("Hourly summary table"):
        frames = []
        for year in active_years:
            subset = df_traffic.filter(pl.col("year") == year)
            hourly = (
                subset.group_by("hour")
                .agg(pl.col(aq_col).mean().alias("aq"), pl.col(kfz_col).mean().alias("kfz"))
                .sort("hour")
            )
            aq_map  = dict(zip(hourly["hour"].to_list(), hourly["aq"].to_list()))
            kfz_map = dict(zip(hourly["hour"].to_list(), hourly["kfz"].to_list()))
            frames.append(pl.DataFrame({
                "Year":     [year] * 24,
                "Hour":     hours,
                aq_label:   [round(v, 3) if v is not None and not np.isnan(v) else None
                            for v in [aq_map.get(h, float("nan")) for h in hours]],
                "Vehicles": [round(v, 1) if v is not None and not np.isnan(v) else None
                            for v in [kfz_map.get(h, float("nan")) for h in hours]],
            }))
        st.dataframe(pl.concat(frames), width="stretch")

except Exception as e:
    st.warning("Something went wrong while loading — restarting...")
    st.session_state.clear()
    st.rerun()

# ====================================
# Text

st.markdown("""
    ### Description:
    Correlation-HeatMaps are used to not only illustrate the correlation between the vehicle count and the different air quality variables, but also the 
    correlation among the air quality variables themselves.  
    The diagonal axis is filled with "1s", as each variable is perfectly correlated with itself. This also confirms that the code is working properly.  
    For the vehicle count, we can observe that it is negatively correlated with all selected air quality variables.  
    This confirms the observations that can be made from the figure above with numerical values as well.
""")

# ====================================
# Website design

st.divider()

col1_bottom_btn, col2_bottom_btn, col3_bottom_btn = st.columns([1, 3.6, 1])

with col1_bottom_btn:
    if st.button("⬅️ Previous Question", key="btn_bottom1"):
        st.switch_page("pages/Research_Question_1.py")

with col3_bottom_btn:
    if st.button("Next Question ➡️", key="btn_bottom2"):
        st.switch_page("pages/Research_Question_3.py")

st.divider()

col4_bottom_btn, col5_bottom_btn, col6_bottom_btn, col7_bottom_btn = st.columns([1, 0.33, 0.33, 1])

with col5_bottom_btn:
    if st.button("Go to Imprint", width="stretch"):
        st.switch_page("pages/Imprint.py")

with col6_bottom_btn:
    if st.button("Back to Homepage 🏠", width="stretch"):
        st.switch_page("pages/homepage.py")
