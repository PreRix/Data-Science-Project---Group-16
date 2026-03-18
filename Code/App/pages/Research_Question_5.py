# ==============================
# Imports

import streamlit as st
import polars as pl
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# ==============================
# Website design

col1_top_btn, col2_top_btn, col3_top_btn = st.columns([1, 3.6, 1])

with col1_top_btn:
    if st.button("⬅️ Previous Question", key = "btn_top1"):
        st.switch_page("pages/Research_Question_4.py")
        
with col3_top_btn:
    if st.button("Next Question ➡️", key = "btn_top2"):
        st.switch_page("pages/Research_Question_6.py")

st.title("Research Question #5")

st.markdown("""
    # *Using yearly registration data for Kiel to derive the estimated share of battery-electric vehicles in the regional fleet from 2021 to 2025, is there a measurable downward trend in NO<sub>2</sub> levels on high-traffic roads near Kiel?*
    ## Vehicle Registrations in Kiel - by Fuel Type 
""")

# ==============================
# Global variables

CSV_HOLYFILE = "https://cloud.rz.uni-kiel.de/public.php/dav/files/NnYrtwJ7FLqC6en/?accept=zip"
CSV_REGISTRATION_DATA = "https://cloud.rz.uni-kiel.de/public.php/dav/files/aDAQmERmoBkwepJ/?accept=zip"
CSV_AIR_QUALITY = "https://cloud.rz.uni-kiel.de/public.php/dav/files/RC9wT3a5Fo7mwbf/?accept=zip"

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

def extract_year(col: str) -> pl.Expr:
    return pl.col(col).str.slice(6, 4).cast(pl.Int32).alias("year")

@st.cache_data(show_spinner="Loading Measuring Points data …")
def load_measuring_points_data(path: str) -> dict[int, float]:
    df = (
        pl.read_csv(path, infer_schema_length=0, ignore_errors=True)
        .with_columns([pl.col(c).str.strip_chars() for c in ["K_KFZ_R1", "K_KFZ_R2", "KFZ_R1", "KFZ_R2"]])
        .filter(~pl.col("K_KFZ_R1").is_in(["a", "d"]) & ~pl.col("K_KFZ_R2").is_in(["a", "d"]))
        .with_columns([
            extract_year("date"),
            pl.col("KFZ_R1").cast(pl.Float64, strict=False).fill_nan(None).alias("kfz_r1"),
            pl.col("KFZ_R2").cast(pl.Float64, strict=False).fill_nan(None).alias("kfz_r2"),
        ])
        .with_columns((pl.col("kfz_r1") + pl.col("kfz_r2")).alias("kfz_total"))
        .drop_nulls(subset=["kfz_total"])
    )
    result = (
        df.group_by("year")
        .agg(pl.col("kfz_total").mean().alias("avg_vehicles"))
        .sort("year").to_dict(as_series=False)
    )
    return dict(zip(result["year"], result["avg_vehicles"]))

@st.cache_data(show_spinner="Loading Registration data …")
def load_registrations_data(path: str) -> pl.DataFrame:
    df = pl.read_csv(path, infer_schema_length=0)
    casts = [pl.col("Year").cast(pl.Int32)] + [
        pl.col(c).str.replace_all(r"\.", "").str.strip_chars().cast(pl.Int64, strict=False)
        for c in FUEL_COLS
    ]
    return df.with_columns(casts).sort("Year")

@st.cache_data(show_spinner="Loading Air Quality data …")
def load_air_quality_data(path: str) -> pl.DataFrame:
    return (
        pl.read_csv(path, infer_schema_length=0)
        .with_columns([
            pl.col("date").str.slice(6, 4).cast(pl.Int32).alias("year"),
            pl.col("date").str.slice(3, 2).cast(pl.Int32).alias("month"),
            pl.col("nitrogen_dioxide").cast(pl.Float64, strict=False).fill_nan(None).alias("no2"),
        ])
        .group_by(["year", "month"])
        .agg(pl.col("no2").mean().alias("avg_no2"))
        .sort(["year", "month"])
        .with_columns(
            (pl.col("year").cast(pl.Utf8) + "-" +
             pl.col("month").cast(pl.Utf8).str.zfill(2) + "-01").alias("date_str")
        )
    )

try:
    df_traffic = load_measuring_points_data(CSV_HOLYFILE)
except FileNotFoundError:
    st.error(f"CSV not found: {CSV_HOLYFILE}")
    st.stop()

try:
    df_registrations = load_registrations_data(CSV_REGISTRATION_DATA)
except FileNotFoundError:
    st.error(f"CSV not found: {CSV_REGISTRATION_DATA}")
    st.stop()

try:
    df_no2_monthly = load_air_quality_data(CSV_AIR_QUALITY)
except FileNotFoundError:
    st.error(f"CSV not found: {CSV_AIR_QUALITY}")
    st.stop()

# ====================================
# First visualisation

is_stacked = st.radio("Bar mode", ["Stacked", "Grouped"], horizontal=True) == "Stacked"

# --- Prepare data ---
years = df_registrations["Year"].to_list()
totals_df = (
    df_registrations
    .with_columns(pl.sum_horizontal(list(FUEL_COLS.keys())).alias("total"))
    .select(["Year", "total"]).to_dict(as_series=False)
)
totals = dict(zip(totals_df["Year"], totals_df["total"]))

# --- Build chart ---
fig = go.Figure()
for col, label in FUEL_COLS.items():
    values = df_registrations[col].to_list()
    pcts   = [
        round(v / totals[y] * 100, 1) if v is not None and totals.get(y) else None
        for v, y in zip(values, years)
    ]
    if is_stacked:
        text_vals = [f"{p:.1f}%" if p is not None and p >= HIDE_THRESHOLD else "" for p in pcts]
        text_pos = "inside"
        text_colors = ["white"] * len(years)
    else:
        text_vals = [f"{p:.1f}%" if p is not None else "" for p in pcts]
        text_pos = ["inside" if p is not None and p >= HIDE_THRESHOLD else "outside" for p in pcts]
        text_colors = ["white"  if p is not None and p >= HIDE_THRESHOLD else "#333333" for p in pcts]
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

# --- Render ---
st.plotly_chart(apply_font(fig), width=True)
with st.expander("Raw data table"):
    table = df_registrations.select(["Year"] + list(FUEL_COLS.keys())).rename(FUEL_COLS)
    table = table.with_columns(pl.Series("Total", [totals[y] for y in table["Year"].to_list()]))
    st.dataframe(table, width=True)

# ====================================
# Text

st.markdown("""
    ### Description:
    For the first visualization we decided to show the share of *vehicles per fuel type for each year* using the bar chart above.  
    An initial observation is that the share of conventional fuel vehicles (petrol and diesel) decreases steadily every year.
    On the other hand the number with (partly) electric drivetrains increases every year, which confirms expectations based on political initiatives in recent 
    years.
""")

st.divider()

st.markdown("""
    ## Battery-Electric Vehicle (BEV) Share vs. Average NO<sub>2</sub> emission per Vehicle
""")

# ====================================
# Second visualisation

# --- Prepare data ---
bev_share = {
    row["Year"]: round(row[BEV_COL] / totals[row["Year"]] * 100, 2)
    for row in df_registrations.select(["Year", BEV_COL]).to_dicts()
    if totals.get(row["Year"]) and row[BEV_COL] is not None
}

common_years = sorted(set(bev_share) & set(df_traffic) & set(df_no2_monthly["year"].to_list()))

if not common_years:
    st.warning("No overlapping years found across the three data sources.")
    st.stop()

veh_df = pl.DataFrame({"year": list(df_traffic.keys()), "avg_vehicles": list(df_traffic.values())})
monthly = (
    df_no2_monthly
    .filter(pl.col("year").is_in(common_years))
    .join(veh_df, on="year", how="left")
    .with_columns((pl.col("avg_no2") / pl.col("avg_vehicles")).alias("no2_per_veh"))
    .sort(["year", "month"])
)

x      = monthly["date_str"].to_list()
y_raw  = monthly["no2_per_veh"].to_list()
y_roll = monthly.with_columns(pl.col("no2_per_veh").rolling_mean(window_size=3).alias("r"))["r"].to_list()

valid_idx, valid_vals = zip(*[(i, v) for i, v in enumerate(y_raw) if v is not None])
y_trend = np.poly1d(np.polyfit(valid_idx, valid_vals, 1))(range(len(y_raw))).tolist()

# --- Build chart ---
fig = make_subplots(specs=[[{"secondary_y": True}]])

fig.add_trace(go.Scatter(
    x=x, y=y_raw, name="NO₂ per Vehicle (monthly)", mode="lines",
    line=dict(color="#D44B94", width=1), opacity=1,
    hovertemplate="Month: %{x|%b %Y}<br>NO₂/vehicle: %{y:.5f}<extra></extra>",
), secondary_y=True)

fig.add_trace(go.Scatter(
    x=x, y=y_roll, name="NO₂ per Vehicle (3-month avg)", mode="lines",
    line=dict(color="#EA4633", width=2.5),
    hovertemplate="Month: %{x|%b %Y}<br>3-month avg: %{y:.5f}<extra></extra>",
), secondary_y=True)

fig.add_trace(go.Scatter(
    x=x, y=y_trend, name="NO₂ Trend (linear)", mode="lines",
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
fig.update_yaxes(title_text="NO₂ per Vehicle (µg/m³ per veh/h)", secondary_y=True, showgrid=False)

# --- Render ---
st.plotly_chart(apply_font(fig), width=True)
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
        .select(["year", "month", "avg_no2", "avg_vehicles", "no2_per_veh"])
        .rename({"year": "Year", "month": "Month", "avg_no2": "Avg NO₂ (µg/m³)",
                 "avg_vehicles": "Avg Vehicles (veh/h)", "no2_per_veh": "NO₂ per Vehicle"})
        .with_columns([pl.col("Avg NO₂ (µg/m³)").round(2),
                       pl.col("Avg Vehicles (veh/h)").round(1),
                       pl.col("NO₂ per Vehicle").round(5)]),
        width=True,
    )

# ====================================
# Text

st.markdown("""
    ### Description: 
    The data shows that the concentrations vary throughout the year; a slight downward trend is only visible when taking a look at the regression line 
    of the data.

    ####
    ### How we aggregated the Data:
    The visualization shows the average NO<sub>2</sub> emission per vehicle. We calculated this by summing up all NO<sub>2</sub> concentration data for *each year* and dividing it by the total vehicle counting data for all available stations *per year*.  
    This approach was chosen to normalize the data against fluctuations in traffic volume, providing a more comparable value for the evolution of NO<sub>2</sub> 
    levels over time. 

    ####
    ### Interpretation:
    As said above, a minor downward trend in NO<sub>2</sub> emissions is noticeable while the number of registered BEV vehicles is increasing.  
    Nevertheless, the data cannot determine whether the growth in battery-electric vehicle share causes the observed decrease in NO<sub>2</sub> levels.  
    This is due to two factors:

    1. The measurement of air pollutants is heavily affected by other metrics, as we discussed in RQ2.
    2. The registration number of battery-electric vehicles does not have to be representative for actual electric traffic load on streets in and around Kiel.

    To answer the question: Yes, a measurable downward trend can be spotted, and it correlates with the increasing numbers of BEV registrations.  
    But no, it can not be determined if this actually is a causation.
    
""")

# ====================================
# Website design

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
    if st.button("Go to Imprint", width = True):
        st.switch_page("pages/Imprint.py")

with col6_bottom_btn:
    if st.button("Back to Homepage 🏠", width = True):
        st.switch_page("pages/homepage.py")