import streamlit as st
import polars as pl
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import plotly.io as pio

pio.templates["custom"] = go.layout.Template(
    layout=go.Layout(
        font=dict(size=18),
        title=dict(font=dict(size=20)),
        legend=dict(font=dict(size=16)),
        xaxis=dict(title=dict(font=dict(size=17)), tickfont=dict(size=15)),
        yaxis=dict(title=dict(font=dict(size=17)), tickfont=dict(size=15)),
    )
)
pio.templates.default = "plotly+custom"

st.set_page_config(page_title="Kiel Vehicle Registrations", layout="wide")
st.title("Vehicle Registrations in Kiel – by Fuel Type (2021–2025)")

st.markdown("""
<style>
    html, body, [class*="css"] {
        font-size: 22px;
    }
</style>
""", unsafe_allow_html=True)

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

BEV_COL        = "PT_Nach Kraftstoffarten_Elektro (BEV)"
HIDE_THRESHOLD = 10

# ── Data loading ──────────────────────────────────────────────────────────────

def extract_year(col: str) -> pl.Expr:
    return pl.col(col).str.slice(6, 4).cast(pl.Int32).alias("year")

@st.cache_data(show_spinner="Loading Measuring Points data …")
def load_vehicles_by_year(path: str) -> dict[int, float]:
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
def load_registrations(path: str) -> pl.DataFrame:
    df = pl.read_csv(path, infer_schema_length=0)
    casts = [pl.col("Year").cast(pl.Int32)] + [
        pl.col(c).str.replace_all(r"\.", "").str.strip_chars().cast(pl.Int64, strict=False)
        for c in FUEL_COLS
    ]
    return df.with_columns(casts).sort("Year")

@st.cache_data(show_spinner="Loading Air Quality data …")
def load_no2_monthly(path: str) -> pl.DataFrame:
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

# ── Chart 1: Registration bar chart ──────────────────────────────────────────

def build_registration_chart(df: pl.DataFrame, is_stacked: bool) -> tuple[go.Figure, dict]:
    years     = df["Year"].to_list()
    totals_df = (
        df.with_columns(pl.sum_horizontal(list(FUEL_COLS.keys())).alias("total"))
        .select(["Year", "total"]).to_dict(as_series=False)
    )
    totals = dict(zip(totals_df["Year"], totals_df["total"]))

    fig = go.Figure()

    for col, label in FUEL_COLS.items():
        values = df[col].to_list()
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
            text_pos    = ["inside" if p is not None and p >= HIDE_THRESHOLD else "outside" for p in pcts]
            text_colors = ["white"  if p is not None and p >= HIDE_THRESHOLD else "#333333" for p in pcts]

        fig.add_trace(go.Bar(
            name=label,
            legendgroup=label,
            showlegend=not is_stacked,
            x=years, y=values,
            customdata=pcts,
            marker_color=FUEL_COLORS[label],
            text=text_vals,
            textposition=text_pos,
            insidetextanchor="middle",
            textfont=dict(size=15, color=text_colors),
            hovertemplate=(
                f"<b>{label}</b><br>"
                "Year: %{x}<br>Count: %{y:,}<br>Share: %{customdata:.1f}%"
                "<extra></extra>"
            ),
            cliponaxis=False,
        ))

    if is_stacked:
        # Invisible scatter traces drive the legend so order is correct
        # (Plotly auto-reverses stacked bar legends but not scatter)
        for col, label in FUEL_COLS.items():
            fig.add_trace(go.Scatter(
                x=[None], y=[None],
                mode="markers",
                marker=dict(size=10, color=FUEL_COLORS[label], symbol="square"),
                name=label,
                legendgroup=label,
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
        plot_bgcolor="white",
        height=560,
        hovermode="closest",
        margin=dict(t=140, b=60),
    )
    return fig, totals


# ── Chart 2: BEV share vs NO₂ per vehicle ────────────────────────────────────

def build_bev_no2_chart(
    df: pl.DataFrame,
    totals: dict,
    no2_monthly: pl.DataFrame,
    vehicles: dict[int, float],
) -> tuple[go.Figure, pl.DataFrame, list]:

    bev_share = {
        row["Year"]: round(row[BEV_COL] / totals[row["Year"]] * 100, 2)
        for row in df.select(["Year", BEV_COL]).to_dicts()
        if totals.get(row["Year"]) and row[BEV_COL] is not None
    }

    common_years = sorted(set(bev_share) & set(vehicles) & set(no2_monthly["year"].to_list()))

    if not common_years:
        return None, None, []

    # Divide monthly NO₂ by yearly vehicle average → controls for traffic
    veh_df = pl.DataFrame({"year": list(vehicles.keys()), "avg_vehicles": list(vehicles.values())})
    monthly = (
        no2_monthly
        .filter(pl.col("year").is_in(common_years))
        .join(veh_df, on="year", how="left")
        .with_columns((pl.col("avg_no2") / pl.col("avg_vehicles")).alias("no2_per_veh"))
        .sort(["year", "month"])
    )

    x        = monthly["date_str"].to_list()
    y_raw    = monthly["no2_per_veh"].to_list()
    y_roll   = monthly.with_columns(
        pl.col("no2_per_veh").rolling_mean(window_size=3).alias("r")
    )["r"].to_list()

    # Linear trend line
    valid       = [(i, v) for i, v in enumerate(y_raw) if v is not None]
    xi, yi      = zip(*valid)
    z           = np.polyfit(xi, yi, 1)
    y_trend     = np.poly1d(z)(range(len(y_raw))).tolist()

    # BEV markers at mid-year
    x_bev = [f"{yr}-01-01" for yr in common_years]
    y_bev = [bev_share[yr] for yr in common_years]

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Raw monthly NO₂/vehicle (faint)
    fig.add_trace(go.Scatter(
        x=x, y=y_raw,
        name="NO₂ per Vehicle (monthly)",
        mode="lines",
        line=dict(color="#E85C4C", width=1),
        opacity=0.3,
        hovertemplate="Month: %{x|%b %Y}<br>NO₂/vehicle: %{y:.5f}<extra></extra>",
    ), secondary_y=True)

    # 3-month rolling average
    fig.add_trace(go.Scatter(
        x=x, y=y_roll,
        name="NO₂ per Vehicle (3-month avg)",
        mode="lines",
        line=dict(color="#E85C4C", width=2.5),
        hovertemplate="Month: %{x|%b %Y}<br>3-month avg: %{y:.5f}<extra></extra>",
    ), secondary_y=True)

    # Linear trend
    fig.add_trace(go.Scatter(
        x=x, y=y_trend,
        name="NO₂ Trend (linear)",
        mode="lines",
        line=dict(color="#555555", width=1.5, dash="dash"),
        hoverinfo="skip",
    ), secondary_y=True)

    # BEV share yearly markers
    fig.add_trace(go.Scatter(
        x=x_bev, y=y_bev,
        name="BEV Share (% of fleet)",
        mode="markers",
        marker=dict(size=12, color="#00C2B2", symbol="diamond"),
        hovertemplate="Year: %{x|%Y}<br>BEV Share: %{y:.2f}%<extra></extra>",
    ), secondary_y=False)

    fig.update_layout(
        legend=dict(orientation="h", y=1.15, x=0),
        xaxis=dict(title="", type="date", tickformat="%Y", dtick="M12"),
        plot_bgcolor="white",
        height=520,
        hovermode="x unified",
        margin=dict(t=140, b=60),
    )
    fig.update_yaxes(title_text="BEV Share (% of fleet)",                secondary_y=False)
    fig.update_yaxes(title_text="NO₂ per Vehicle (µg/m³ per veh/h)",    secondary_y=True, showgrid=False)

    summary = (
        monthly
        .select(["year", "month", "avg_no2", "avg_vehicles", "no2_per_veh"])
        .rename({
            "year": "Year", "month": "Month",
            "avg_no2": "Avg NO₂ (µg/m³)",
            "avg_vehicles": "Avg Vehicles (veh/h)",
            "no2_per_veh": "NO₂ per Vehicle",
        })
        .with_columns([
            pl.col("Avg NO₂ (µg/m³)").round(2),
            pl.col("Avg Vehicles (veh/h)").round(1),
            pl.col("NO₂ per Vehicle").round(5),
        ])
    )
    return fig, summary, common_years


# ── App ───────────────────────────────────────────────────────────────────────

try:
    df_registrations = load_registrations(CSV_REGISTRATION_DATA)
except FileNotFoundError:
    st.error(f"CSV not found: {CSV_REGISTRATION_DATA}")
    st.stop()

# Chart 1
is_stacked = st.radio("Bar mode", ["Stacked", "Grouped"], horizontal=True) == "Stacked"

fig1, totals = build_registration_chart(df_registrations, is_stacked)
st.plotly_chart(fig1, use_container_width=True)

with st.expander("Raw data table"):
    table = df_registrations.select(["Year"] + list(FUEL_COLS.keys())).rename(FUEL_COLS)
    table = table.with_columns(pl.Series("Total", [totals[y] for y in table["Year"].to_list()]))
    st.dataframe(table, use_container_width=True)

# Chart 2
st.divider()
st.subheader("BEV Share vs. Average NO₂ per Vehicle (2021–2025)")

try:
    df_traffic    = load_vehicles_by_year(CSV_HOLYFILE)
    df_no2_monthly = load_no2_monthly(CSV_AIR_QUALITY)
    fig2, summary, common_years = build_bev_no2_chart(df_registrations, totals, df_no2_monthly, df_traffic)

    if not common_years:
        st.warning("No overlapping years found across the three data sources.")
    else:
        st.plotly_chart(fig2, use_container_width=True)
        st.caption(
            "⚠️ **Data limitation:** NO₂ values are sourced from Open-Meteo, which provides "
            "a model-based atmospheric estimate for the Kiel area rather than a measurement "
            "from a specific road-side sensor. As a result, the NO₂ signal may not fully reflect "
            "conditions at individual traffic counting station locations and should be interpreted "
            "as a regional proxy only."
        )
        with st.expander("Underlying data"):
            st.dataframe(summary, use_container_width=True)

except FileNotFoundError as e:
    st.error(f"Could not load data file: {e}")