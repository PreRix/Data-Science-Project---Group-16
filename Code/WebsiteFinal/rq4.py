import streamlit as st
import polars as pl
import plotly.express as px

st.set_page_config(page_title="Traffic Analysis", layout="wide")
st.markdown("<style>html { font-size: 20px; }</style>", unsafe_allow_html=True)
st.title("Weekend vs. Weekday Traffic Load (A215 - AK Kiel-West)")

st.markdown("**Research Question #4:** How do Saturday and Sunday volumes near Kiel compare to weekday volumes, and has this weekend-to-weekday ration changed significantly over the five-year observation period?")

CSV_HOLYFILE = "https://cloud.rz.uni-kiel.de/public.php/dav/files/NnYrtwJ7FLqC6en/?accept=zip"

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

        .filter(pl.col("Zst") == "1194")

        .with_columns(
            pl.col("date").str.to_datetime("%d.%m.%Y %H:%M").alias("datetime")
        )

        .with_columns(
            pl.col("datetime").dt.year().alias("year"),
            pl.col("datetime").dt.weekday().alias("weekday"),
            pl.col("datetime").dt.date().alias("day")
        )

        .with_columns([
            pl.when(pl.col("K_KFZ_R1").str.strip_chars().is_in(["a","d"]))
            .then(None)
            .otherwise(
                pl.col("KFZ_R1")
                .str.strip_chars()
                .str.extract(r"^(-?\d+)")
                .cast(pl.Float64)
            )
            .alias("KFZ_R1"),

            pl.when(pl.col("K_KFZ_R2").str.strip_chars().is_in(["a","d"]))
            .then(None)
            .otherwise(
                pl.col("KFZ_R2")
                .str.strip_chars()
                .str.extract(r"^(-?\d+)")
                .cast(pl.Float64)
            )
            .alias("KFZ_R2"),
        ])

        .with_columns(
            (pl.col("KFZ_R1") + pl.col("KFZ_R2")).alias("vehicle_count")
        )
    )

    return df

try:
    df_traffic = load_measuring_points_data(CSV_HOLYFILE)
except FileNotFoundError:
    st.error(f"File not found: {CSV_HOLYFILE}")
    st.stop()

def weekday_share(df):

    daily = (
        df
        .group_by(["year","day","weekday"])
        .agg(pl.col("vehicle_count").sum().alias("daily_traffic"))
    )

    daily = daily.with_columns(
        pl.when(pl.col("weekday") <= 5)
        .then(pl.lit("Weekday"))
        .when(pl.col("weekday") == 6)
        .then(pl.lit("Saturday"))
        .otherwise(pl.lit("Sunday"))
        .alias("day_type")
    )

    share = (
        daily
        .group_by(["year","day_type"])
        .agg(pl.col("daily_traffic").mean().alias("vehicle_count"))
        .sort(["year","day_type"])
    )

    return share


df_share = weekday_share(df_traffic)

years = sorted(df_share["year"].unique().to_list())
cols = st.columns(len(years))

for col, year in zip(cols, years):

    with col:

        df_year = df_share.filter(pl.col("year") == year)

        fig = px.pie(
            df_year.to_pandas(),
            values="vehicle_count",
            names="day_type",
            title=str(year),
            category_orders={
                "day_type": ["Weekday", "Saturday", "Sunday"]
            }
        )

        fig.update_traces(textposition="inside", textinfo="percent+label")

        st.plotly_chart(apply_font(fig), use_container_width=True)