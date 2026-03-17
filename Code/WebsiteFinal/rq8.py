import streamlit as st
import polars as pl
import plotly.graph_objects as go

st.set_page_config(page_title="Traffic Analysis", layout="wide")
st.markdown("<style>html { font-size: 20px; }</style>", unsafe_allow_html=True)

st.title("Rush-Hour Traffic & Home Office Effect (2021–2025)")

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


@st.cache_data(show_spinner="Loading Measuring Points data …")
def load_measuring_points_data(path):

    df = (
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
            (pl.col("year").cast(pl.Utf8) + "-" + pl.col("month").cast(pl.Utf8).str.zfill(2)).alias("year_month")
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

st.plotly_chart(apply_font(fig1), use_container_width=True)


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

st.plotly_chart(apply_font(fig2), use_container_width=True)
