# ====================================
# Shared data loading and caching utilities for the Streamlit dashboard.
#
# This module centralizes all dataset loading functions used across the
# application. It loads traffic, vehicle registration, and weather datasets
# from remote sources, performs basic preprocessing (type casting, datetime
# parsing, quality filtering, and feature creation), and caches the results
# using Streamlit's @st.cache_data decorator to ensure efficient reuse across
# multiple dashboard pages.
#
# The module also provides helper functions to guarantee that required
# datasets are available in Streamlit's session state, preventing redundant
# downloads and improving overall application performance.
#
# Developed with the assistance of Claude (Anthropic) [https://claude.ai/].

# ==============================
# Shared data loaders
# All pages import from here so @st.cache_data yields one shared cache entry.

import streamlit as st
import polars as pl

CSV_TRAFFIC      = "https://cloud.rz.uni-kiel.de/public.php/dav/files/NnYrtwJ7FLqC6en/?accept=zip"
CSV_REGISTRATION = "https://cloud.rz.uni-kiel.de/public.php/dav/files/aDAQmERmoBkwepJ/?accept=zip"
CSV_WEATHER_DATA = "https://cloud.rz.uni-kiel.de/public.php/dav/files/dYtnayFdSte8EPN/?accept=zip"

AIR_QUALITY_VARS = {
    "PM10":  "pm10",
    "PM2.5": "pm2_5",
    "NO2":   "nitrogen_dioxide",
    "CO":    "carbon_monoxide",
}

# RQ5
_FUEL_COLS = [
    "PT_Nach Kraftstoffarten_Benzin",
    "PT_Nach Kraftstoffarten_Diesel",
    "PT_Nach Kraftstoffarten_Hybrid insgesamt",
    "PT_Nach Kraftstoffarten_Elektro (BEV)",
    "PT_Nach Kraftstoffarten_Gas (einschl. bivalent)",
    "PT_Nach Kraftstoffarten_darunter Plug-in-Hybrid",
    "PT_Nach Kraftstoffarten_sonstige",
]

# RQ7
_VEHICLE_CLASSES = ["Pkw", "Mot", "Bus", "PmA"]

# ── Base loader ───────────────────────────────────────────────────────────────
# Reads & parses the traffic CSV once. All per-page filtering/casting happens
# on this already-cached DataFrame (fast, in-memory Polars ops).

@st.cache_data(show_spinner="Loading traffic data …")
def load_traffic_base(path: str = CSV_TRAFFIC) -> pl.DataFrame:
    """
    Returns the full traffic CSV with:
      - datetime, hour, weekday, year, month, day columns parsed
      - KFZ_R1, KFZ_R2, KFZ_total (nulls where quality flag is 'a'/'d')
      - Vehicle class columns for RQ7: Pkw/Mot/Bus/PmA _R1/_R2 (if present)
      - All air-quality and weather columns cast to Float64
    """
    weather_cols = ["precipitation", "temperature_2m", "snowfall"]
    aq_cols      = list(AIR_QUALITY_VARS.values())
    float_cols   = weather_cols + aq_cols

    df = pl.read_csv(path, infer_schema_length=0)

    # Add missing float columns as null so downstream code is always safe
    for col in float_cols:
        if col not in df.columns:
            df = df.with_columns(pl.lit(None).cast(pl.Float64).alias(col))

    # Build quality-flag-aware cast expression for any TLS column
    def clean_tls_col(name: str) -> pl.Expr:
        return (
            pl.when(pl.col(f"K_{name}").str.strip_chars().is_in(["a", "d"]))
              .then(None)
              .otherwise(
                  pl.col(name).str.strip_chars().str.extract(r"^(-?\d+)").cast(pl.Float64)
              )
              .alias(name)
        )
    
    # KFZ is always present; vehicle class columns only if the CSV has them
    cols_to_clean = ["KFZ_R1", "KFZ_R2"]
    for cls in _VEHICLE_CLASSES:
        for direction in ("R1", "R2"):
            col = f"{cls}_{direction}"
            if col in df.columns and f"K_{col}" in df.columns:
                cols_to_clean.append(col)

    return (
        df
        .with_columns([clean_tls_col(c) for c in cols_to_clean])
        .with_columns(
            pl.col("date").str.to_datetime("%d.%m.%Y %H:%M").alias("datetime")
        )
        .with_columns(
            pl.col("datetime").dt.hour().alias("hour"),
            pl.col("datetime").dt.weekday().alias("weekday"),
            pl.col("datetime").dt.year().alias("year"),
            pl.col("datetime").dt.month().alias("month"),
            pl.col("datetime").dt.date().alias("day"),
        )
        .with_columns(
            (pl.col("KFZ_R1") + pl.col("KFZ_R2")).alias("KFZ_total")
        )
        .with_columns([
            pl.col(c).cast(pl.Float64, strict=False).fill_nan(None)
            for c in float_cols
        ])
    )

# ── Registration loader with fuel breakdown (RQ5) ─────────────────────────────
 
@st.cache_data(show_spinner="Loading registration data …")
def load_registrations(path: str = CSV_REGISTRATION) -> pl.DataFrame:
    return (
        pl.read_csv(path, infer_schema_length=0)
        .select([
            pl.col("Year").cast(pl.Int64).alias("year"),
            pl.col("VT_Kraftfahrzeuge_insgesamt")
              .str.replace_all(r"\.", "")
              .cast(pl.Int64)
              .alias("registrations"),
        ])
    )

@st.cache_data(show_spinner="Loading registration data (fuel breakdown) …")
def load_registrations_fuel(path: str = CSV_REGISTRATION) -> pl.DataFrame:
    """
    Returns the registration CSV with Year + all per-fuel-type columns,
    numeric strings cleaned (dots removed) and cast to Int64.
    Used by RQ5.
    """
    df = pl.read_csv(path, infer_schema_length=0)
    fuel_cols_present = [c for c in _FUEL_COLS if c in df.columns]
    casts = (
        [pl.col("Year").cast(pl.Int64).alias("Year")]
        + [
            pl.col(c).str.replace_all(r"\.", "").str.strip_chars().cast(pl.Int64, strict=False)
            for c in fuel_cols_present
        ]
    )
    return df.select(casts).sort("Year")

# ── Extreme-weather / events weather loader (RQ9 - Bonus) ─────────────────────

@st.cache_data(show_spinner="Loading weather data …")
def load_weather(path: str = CSV_WEATHER_DATA) -> pl.DataFrame:
    """
    Returns hourly precipitation + snowfall for the Kiel-West station (Zst 1194).
    """
    return (
        pl.read_csv(path)
        .filter(pl.col("location_Zst") == 1194)
        .with_columns(
            pl.col("date").str.to_datetime("%d.%m.%Y %H:%M").alias("datetime")
        )
        .select(["datetime", "precipitation", "snowfall"])
    )

# ── Cache loader helper function ──────────────────────────────────────────────

def ensure_session_data():
    try:
        if "df_traffic" not in st.session_state:
            st.session_state.df_traffic = load_traffic_base()
        if "df_registrations" not in st.session_state:
            st.session_state.df_registrations = load_registrations()
        if "df_registrations_fuel" not in st.session_state:
            st.session_state.df_registrations_fuel = load_registrations_fuel()
        if "df_weather" not in st.session_state:
            st.session_state.df_weather = load_weather()
    except Exception as e:
        st.error(f"Could not load data from the server: {e}")
        st.stop()