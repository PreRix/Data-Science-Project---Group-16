import streamlit as st
import polars as pl
import plotly.graph_objects as go

st.set_page_config(page_title="Traffic Analysis", layout="wide")
st.markdown("<style>html { font-size: 20px; }</style>", unsafe_allow_html=True)
st.title("Rush-Hour Traffic & Home Office Effect (2021–2025)")

st.markdown("**Research Question #8:** How did the traffic in rush-hours changed on Autobahnen (and Bundesstraßen?) around Kiel because of the mobility change?")

CSV_HOLYFILE = "https://cloud.rz.uni-kiel.de/public.php/dav/files/NnYrtwJ7FLqC6en/?accept=zip"

DETAIL_YEAR = 2023
DETAIL_MONTH = 2

def apply_font(fig):
    fig.update_layout(font_size=22, legend_font_size=22)
    if fig.layout.title.text:
        fig.update_layout(title_font_size=34)
    fig.update_xaxes(title_font_size=28, tickfont_size=22)
    fig.update_yaxes(title_font_size=28, tickfont_size=22)
    return fig

def make_rush_figure(x, y_morning, y_evening, title, x_title):
    fig = go.Figure([
        go.Scatter(x=x, y=y_morning, name="Morning Rush – into Kiel (6–9h)",
                   mode="lines+markers", line=dict(color="steelblue", width=3)),
        go.Scatter(x=x, y=y_evening, name="Evening Rush – out of Kiel (16–18h)",
                   mode="lines+markers", line=dict(color="tomato", width=3)),
    ])
    fig.update_layout(title=title, xaxis_title=x_title,
                      yaxis_title="Vehicles during Rush Hour", height=600)
    return apply_font(fig)

@st.cache_data(show_spinner="Loading Measuring Points data …")
def load_measuring_points_data(path):
    return (
        pl.read_csv(path, infer_schema_length=0)
        .filter(pl.col("Zst") == "1194")
        .with_columns(
            pl.col("date").str.to_datetime("%d.%m.%Y %H:%M").alias("datetime")
        )
        .with_columns(
            pl.col("datetime").dt.year().alias("year"),
            pl.col("datetime").dt.month().alias("month"),
            pl.col("datetime").dt.hour().alias("hour"),
            pl.col("datetime").dt.weekday().alias("weekday"),
            pl.col("datetime").dt.date().alias("day"),
        )
        .with_columns(
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
        )
        .filter(pl.col("weekday") <= 5)
    )

def monthly_avg(df, col):
    """Daily-then-monthly average of `col` for rush-hour data."""
    return (
        df.group_by(["year", "month", "day"]).agg(pl.col(col).mean().alias("daily"))
        .group_by(["year", "month"]).agg(pl.col("daily").mean().alias("avg"))
        .sort(["year", "month"])
        .with_columns(
            (pl.col("year").cast(pl.Utf8) + "-" + pl.col("month").cast(pl.Utf8).str.zfill(2))
            .alias("year_month")
        )
    )

def daily_avg(df, col):
    """Per-day average of `col` within a single month's rush-hour data."""
    return (
        df.group_by("day").agg(pl.col(col).mean().alias("avg"))
        .sort("day")
    )

try:
    df = load_measuring_points_data(CSV_HOLYFILE)
except FileNotFoundError:
    st.error(f"File not found: {CSV_HOLYFILE}")
    st.stop()

# ── Chart 1: monthly overview (2021–2025) ────────────────────────────────────

morning_all = df.filter(pl.col("hour").is_between(6, 9))
evening_all = df.filter(pl.col("hour").is_between(16, 18))

m = monthly_avg(morning_all, "KFZ_R1")
e = monthly_avg(evening_all, "KFZ_R2")

st.plotly_chart(
    make_rush_figure(
        m["year_month"], m["avg"], e["avg"],
        title="Monthly Avg. Rush-Hour Traffic on A215 – AK Kiel-West (2021–2025)",
        x_title="Month",
    ),
    use_container_width=True,
)

# ── Chart 2: daily detail for DETAIL_YEAR / DETAIL_MONTH ────────────────────

df_month = df.filter((pl.col("year") == DETAIL_YEAR) & (pl.col("month") == DETAIL_MONTH))

m = daily_avg(df_month.filter(pl.col("hour").is_between(6, 9)),  "KFZ_R1")
e = daily_avg(df_month.filter(pl.col("hour").is_between(16, 18)), "KFZ_R2")

st.plotly_chart(
    make_rush_figure(
        m["day"], m["avg"], e["avg"],
        title=f"Daily Rush-Hour Traffic – {DETAIL_YEAR}-{str(DETAIL_MONTH).zfill(2)}",
        x_title="Day of Month",
    ),
    use_container_width=True,
)