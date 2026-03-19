# ====================================
# Imports

import streamlit as st
import polars as pl
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from utils.data_loader import load_traffic_base, load_registrations_fuel

# ====================================
# Website design

col1_top_btn, col2_top_btn, col3_top_btn = st.columns([1, 3.6, 1])

with col1_top_btn:
    if st.button("⬅️ Previous Question", key="btn_top1"):
        st.switch_page("pages/Research_Question_4.py")

with col3_top_btn:
    if st.button("Next Question ➡️", key="btn_top2"):
        st.switch_page("pages/Research_Question_6.py")

st.title("Research Question #5")

st.markdown("""
    # *Using yearly registration data for Kiel to derive the estimated share of battery-electric vehicles in the regional fleet from 2021 to 2025, is there a measurable downward trend in NO<sub>2</sub> levels on high-traffic roads near Kiel?*
    ## Vehicle Registrations in Kiel - by Fuel Type 
""", unsafe_allow_html=True)

# ====================================
# Global variables

FUEL_COLS = {
    "PT_Nach Kraftstoffarten_Benzin":                  "Petrol",
    "PT_Nach Kraftstoffarten_Diesel":                  "Diesel",
    "PT_Nach Kraftstoffarten_Hybrid insgesamt":        "Hybrid (total)",
    "PT_Nach Kraftstoffarten_Elektro (BEV)":           "Electric (BEV)",
    "PT_Nach Kraftstoffarten_Gas (einschl. bivalent)": "Gas (incl. bivalent)",
    "PT_Nach Kraftstoffarten_darunter Plug-in-Hybrid": "Plug-in Hybrid",
    "PT_Nach Kraftstoffarten_sonstige":                "Other",
}

FUEL_COLORS = {
    "Petrol":               "#E85C4C",
    "Diesel":               "#4C9BE8",
    "Hybrid (total)":       "#2DB37A",
    "Electric (BEV)":       "#00C2B2",
    "Gas (incl. bivalent)": "#F5A623",
    "Plug-in Hybrid":       "#A259E8",
    "Other":                "#AAAAAA",
}

BEV_COL = "PT_Nach Kraftstoffarten_Elektro (BEV)"
HIDE_THRESHOLD = 10

# ====================================
# Data collection and helpers

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
    _base = load_traffic_base()

    # Compute NO2/vehicle ratio at hourly level, then aggregate to monthly means
    df_monthly = (
        _base
        .filter(pl.col("Zst") == "1194")
        .drop_nulls(subset=["KFZ_total", "nitrogen_dioxide"])
        .filter(pl.col("KFZ_total") > 0)
        .with_columns(
            (pl.col("nitrogen_dioxide") / pl.col("KFZ_total")).alias("no2_per_veh")
        )
        .group_by(["year", "month"])
        .agg(
            pl.col("no2_per_veh").mean().alias("avg_no2_per_veh"),
            pl.col("nitrogen_dioxide").mean().alias("avg_no2"),
            pl.col("KFZ_total").mean().alias("avg_vehicles"),
        )
        .sort(["year", "month"])
        .with_columns(
            (pl.col("year").cast(pl.Utf8) + "-" +
             pl.col("month").cast(pl.Utf8).str.zfill(2) + "-01").alias("date_str")
        )
    )

    df_registrations = load_registrations_fuel()

except Exception as e:
    st.error(f"Could not load data: {e}")
    st.stop()

# ====================================
# First visualization

try:
    is_stacked = st.radio("Bar mode", ["Stacked", "Grouped"], horizontal=True) == "Stacked"

    years = df_registrations["Year"].to_list()
    totals_df = (
        df_registrations
        .with_columns(pl.sum_horizontal(list(FUEL_COLS.keys())).alias("total"))
        .select(["Year", "total"]).to_dict(as_series=False)
    )
    totals = dict(zip(totals_df["Year"], totals_df["total"]))

    fig = go.Figure()
    for col, label in FUEL_COLS.items():
        if col not in df_registrations.columns:
            continue
        values = df_registrations[col].to_list()
        pcts   = [
            round(v / totals[y] * 100, 1) if v is not None and totals.get(y) else None
            for v, y in zip(values, years)
        ]
        if is_stacked:
            text_vals   = [f"{p:.1f}%" if p is not None and p >= HIDE_THRESHOLD else "" for p in pcts]
            text_pos    = "inside"
            text_colors = ["white"] * len(years)
        else:
            text_vals   = [f"{p:.1f}%" if p is not None else "" for p in pcts]
            text_pos    = ["inside"  if p is not None and p >= HIDE_THRESHOLD else "outside" for p in pcts]
            text_colors = ["white"   if p is not None and p >= HIDE_THRESHOLD else "#333333" for p in pcts]

        fig.add_trace(go.Bar(
            name=label, legendgroup=label, showlegend=not is_stacked,
            x=years, y=values, customdata=pcts,
            marker_color=FUEL_COLORS[label],
            text=text_vals, textposition=text_pos,
            insidetextanchor="middle", textfont=dict(size=15, color=text_colors),
            hovertemplate=f"<b>{label}</b><br>Year: %{{x}}<br>Count: %{{y:,}}<br>Share: %{{customdata:.1f}}%<extra></extra>",
            cliponaxis=False,
        ))

    if is_stacked:
        for col, label in FUEL_COLS.items():
            fig.add_trace(go.Scatter(
                x=[None], y=[None], mode="markers",
                marker=dict(size=10, color=FUEL_COLORS[label], symbol="square"),
                name=label, legendgroup=label,
            ))
        fig.update_layout(annotations=[
            dict(x=yr, y=total, text=f"<b>{total:,}</b>", showarrow=False,
                yanchor="bottom", yshift=2, font=dict(size=12, color="#333333"))
            for yr, total in totals.items()
        ])

    fig.update_layout(
        barmode="stack" if is_stacked else "group",
        xaxis=dict(title="Year", tickmode="array", tickvals=years, ticktext=[str(y) for y in years]),
        yaxis=dict(title="Registration Count"),
        legend=dict(orientation="h", y=1.12, x=0, traceorder="normal"),
        plot_bgcolor="white", height=560, hovermode="closest", margin=dict(t=140, b=60),
    )

    st.plotly_chart(apply_font(fig), width="stretch")
    with st.expander("Raw data table"):
        table = df_registrations.select(
            ["Year"] + [c for c in FUEL_COLS if c in df_registrations.columns]
        ).rename({c: l for c, l in FUEL_COLS.items() if c in df_registrations.columns})
        table = table.with_columns(pl.Series("Total", [totals[y] for y in table["Year"].to_list()]))
        st.dataframe(table, width="stretch")

except Exception as e:
    st.warning("Something went wrong while loading — restarting...")
    st.session_state.clear()
    st.rerun()

# ====================================
# Text

st.markdown("""
    ### Description:
    For the first visualization we decided to show the share of *vehicles per fuel type for each year* using the bar chart above.  
    An initial observation is that the share of conventional fuel vehicles (petrol and diesel) decreases steadily every year.
    On the other hand the number of vehicles with (partly) electric drivetrains increases every year, which confirms expectations based on political initiatives in recent 
    years.
""")

st.divider()

st.markdown("""
    ## Battery-Electric Vehicle (BEV) Share vs. Average NO<sub>2</sub> emission per Vehicle
""", unsafe_allow_html=True)

# ====================================
# Second visualization

try:
    bev_share = {
        row["Year"]: round(row[BEV_COL] / totals[row["Year"]] * 100, 2)
        for row in df_registrations.select(["Year", BEV_COL]).to_dicts()
        if totals.get(row["Year"]) and row[BEV_COL] is not None
    }

    common_years = sorted(set(bev_share) & set(df_monthly["year"].to_list()))

    if not common_years:
        st.warning("No overlapping years found across the data sources.")
        st.stop()

    monthly = df_monthly.filter(pl.col("year").is_in(common_years))

    x      = monthly["date_str"].to_list()
    y_raw  = monthly["avg_no2_per_veh"].to_list()
    y_roll = monthly.with_columns(
        pl.col("avg_no2_per_veh").rolling_mean(window_size=3).alias("r")
    )["r"].to_list()

    valid_idx, valid_vals = zip(*[(i, v) for i, v in enumerate(y_raw) if v is not None])
    y_trend = np.poly1d(np.polyfit(valid_idx, valid_vals, 1))(range(len(y_raw))).tolist()

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Scatter(
        x=x, y=y_raw, name="NO2 per Vehicle (monthly)", mode="lines",
        line=dict(color="#D44B94", width=1), opacity=1,
        hovertemplate="Month: %{x|%b %Y}<br>NO2/vehicle: %{y:.5f}<extra></extra>",
    ), secondary_y=True)

    fig.add_trace(go.Scatter(
        x=x, y=y_roll, name="NO2 per Vehicle (3-month avg)", mode="lines",
        line=dict(color="#EA4633", width=2.5),
        hovertemplate="Month: %{x|%b %Y}<br>3-month avg: %{y:.5f}<extra></extra>",
    ), secondary_y=True)

    fig.add_trace(go.Scatter(
        x=x, y=y_trend, name="NO2 Trend (linear)", mode="lines",
        line=dict(color="#555555", width=1.5, dash="dash"), hoverinfo="skip",
    ), secondary_y=True)

    fig.add_trace(go.Scatter(
        x=[f"{yr}-01-01" for yr in common_years],
        y=[bev_share[yr] for yr in common_years],
        name="BEV Share (% of fleet)", mode="markers",
        marker=dict(size=12, color="#00C2B2", symbol="diamond"),
        hovertemplate="Year: %{x|%Y}<br>BEV Share: %{y:.2f}%<extra></extra>",
    ), secondary_y=False)

    fig.update_layout(
        legend=dict(orientation="h", y=1.15, x=0),
        xaxis=dict(title="", type="date", tickformat="%Y", dtick="M12"),
        plot_bgcolor="white", height=520, hovermode="x unified", margin=dict(t=140, b=60),
    )
    fig.update_yaxes(title_text="BEV Share (% of fleet)", secondary_y=False)
    fig.update_yaxes(title_text="NO2 per Vehicle (µg/m³ per veh/h)", secondary_y=True, showgrid=False)

    st.plotly_chart(apply_font(fig), width="stretch")
    st.caption(
        "⚠️ **Data limitation:** NO₂ values are sourced from Open-Meteo, which provides "
        "a model-based atmospheric estimate for the Kiel area rather than a measurement "
        "from a specific road-side sensor. As a result, the NO₂ signal may not fully reflect "
        "conditions at individual traffic counting station locations and should be interpreted "
        "as a regional proxy only."
    )

    with st.expander("Underlying data"):
        st.dataframe(
            monthly
            .select(["year", "month", "avg_no2", "avg_vehicles", "avg_no2_per_veh"])
            .rename({"year": "Year", "month": "Month", "avg_no2": "Avg NO₂ (µg/m³)",
                    "avg_vehicles": "Avg Vehicles (veh/h)", "avg_no2_per_veh": "NO₂ per Vehicle"})
            .with_columns([
                pl.col("Avg NO₂ (µg/m³)").round(2),
                pl.col("Avg Vehicles (veh/h)").round(1),
                pl.col("NO₂ per Vehicle").round(5),
            ]),
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
    The data shows that the concentrations vary throughout the year; a slight downward trend is only visible when taking a look at the regression line 
    of the data.

    ####
    ### How we aggregated the Data:
    The visualization shows the average NO<sub>2</sub> emission per vehicle. For each hour at station 1194, we divided the NO₂ concentration by the vehicle count to get an hourly NO₂-per-vehicle ratio. These hourly ratios were then averaged across all hours within each calendar month.  
    This approach avoids the distortion introduced by averaging numerator and denominator separately before dividing, and normalizes the NO₂ signal against traffic volume at the finest available granularity.

    ####
    ### Interpretation:
    As said above, a minor downward trend in NO<sub>2</sub> emissions is noticeable while the number of registered BEV vehicles is increasing.  
    Nevertheless, the data cannot determine whether the growth in battery-electric vehicle share causes the observed decrease in NO<sub>2</sub> levels.  
    This is due to two factors:

    1. The measurement of air pollutants is heavily affected by other metrics, as we discussed in RQ2.
    2. The registration number of battery-electric vehicles does not have to be representative for actual electric traffic load on streets in and around Kiel.

    To answer the question: Yes, a measurable downward trend can be spotted, and it correlates with the increasing numbers of BEV registrations.  
    But no, it can not be determined if this actually is a causation.
    
""", unsafe_allow_html=True)

# ====================================
# Website design

st.divider()

col1_bottom_btn, col2_bottom_btn, col3_bottom_btn = st.columns([1, 3.6, 1])

with col1_bottom_btn:
    if st.button("⬅️ Previous Question", key="btn_bottom1"):
        st.switch_page("pages/Research_Question_4.py")

with col3_bottom_btn:
    if st.button("Next Question ➡️", key="btn_bottom2"):
        st.switch_page("pages/Research_Question_6.py")

st.divider()

col4_bottom_btn, col5_bottom_btn, col6_bottom_btn, col7_bottom_btn = st.columns([1, 0.33, 0.33, 1])

with col5_bottom_btn:
    if st.button("Go to Imprint", width="stretch"):
        st.switch_page("pages/Imprint.py")

with col6_bottom_btn:
    if st.button("Back to Homepage 🏠", width="stretch"):
        st.switch_page("pages/homepage.py")