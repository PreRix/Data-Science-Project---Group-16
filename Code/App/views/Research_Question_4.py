# ====================================
# Imports
# ====================================
import streamlit as st
import polars as pl
import plotly.express as px

# ====================================
# Website Design & Header Navigation
# ====================================
# Creating a 3-column layout for top navigation buttons
col1_top_btn, col2_top_btn, col3_top_btn = st.columns([1, 3.6, 1])

with col1_top_btn:
    # Button to navigate back to the previous research question
    if st.button("⬅️ Previous Question", key="btn_top1"):
        st.switch_page("views/Research_Question_3.py")

with col3_top_btn:
    # Button to proceed to the next research question
    if st.button("Next Question ➡️", key="btn_top2"):
        st.switch_page("views/Research_Question_5.py")

st.title("Research Question #4")

st.markdown("""
    # *How do Saturday and Sunday volumes near Kiel compare to weekday volumes, and has this weekend-to-weekday ratio changed significantly over the five-year observation period?*
    ## Weekend vs. Weekday Traffic Load on the A215 (AK Kiel-West)
""")

# ====================================
# Data Collection and Helper Functions
# ====================================
def apply_font(fig):
    """
    Ensures consistent and readable font sizes across all Plotly charts.
    """
    fig.update_layout(font_size=22, legend_font_size=22)
    if fig.layout.title.text:
        fig.update_layout(title_font_size=34)
    fig.update_xaxes(title_font_size=28, tickfont_size=22)
    fig.update_yaxes(title_font_size=28, tickfont_size=22)
    for annotation in fig.layout.annotations:
        annotation.font.size = 26
    return fig

# Filter the global dataset to only include the Kiel-West station (1194)
# We rename the count column for better readability in the charts
df_traffic = (
    st.session_state.df_traffic
    .filter(pl.col("Zst") == "1194")
    .rename({"KFZ_total": "vehicle_count"})
)

# ====================================
# Data Aggregation Logic
# ====================================
def weekday_share(df: pl.DataFrame) -> pl.DataFrame:
    """
    Processes raw traffic data into average daily volumes categorized by day type.
    """
    # First aggregation: Calculate total traffic for every individual day in the dataset
    daily = (
        df.group_by(["year", "day", "weekday"])
        .agg(pl.col("vehicle_count").sum().alias("daily_traffic"))
    )
    # Categorize days into 'Weekday' (Mon-Fri), 'Saturday', or 'Sunday'
    daily = daily.with_columns(
        pl.when(pl.col("weekday") <= 5).then(pl.lit("Weekday"))
        .when(pl.col("weekday") == 6).then(pl.lit("Saturday"))
        .otherwise(pl.lit("Sunday"))
        .alias("day_type")
    )
    # Second aggregation: Calculate the MEAN daily traffic for each category per year
    # This allows a fair 1-to-1 comparison between a typical Monday and a typical Sunday
    return (
        daily.group_by(["year", "day_type"])
        .agg(pl.col("daily_traffic").mean().alias("vehicle_count"))
        .sort(["year", "day_type"])
    )

# ====================================
# Visualization: Comparative Pie Charts
# ====================================
try:
    # Prepare the aggregated data
    df_share = weekday_share(df_traffic)
    years    = sorted(df_share["year"].unique().to_list())
    # Create dynamic columns based on the number of years in the data
    cols     = st.columns(len(years))

    for col, year in zip(cols, years):
        with col:
            # Filter data for the specific year
            df_year = df_share.filter(pl.col("year") == year)
            # Generate a pie chart for the current year
            fig = px.pie(
                df_year.to_pandas(),
                values="vehicle_count",
                names="day_type",
                title=str(year),
                # Ensure the order of slices is consistent across all charts
                category_orders={"day_type": ["Weekday", "Saturday", "Sunday"]},
            )
            # Display percentages and labels directly on the slices
            fig.update_traces(textposition="inside", textinfo="percent+label")
            # Apply custom font styling and render in Streamlit
            st.plotly_chart(apply_font(fig), width="stretch")

except Exception:
    # Error handling: If session data is lost, clear remaining keys and refresh the app
    for key in list(st.session_state.keys()):
        if key not in ("df_traffic", "df_registrations", "df_registrations_fuel", "df_weather"):
            del st.session_state[key]
    st.rerun()

# ====================================
# Interpretation and Methodology
# ====================================
st.markdown("""
    ### How we aggregated the Data:
    For this question we decided to use a pie chart for every year.  
    The data we used is from the counting station 1194 alone at the A215 because, as concluded in RQ2, this station is highly representative of commuter traffic 
    and traffic in general. 
    As well, there might be differences for the counting stations for the different days of the week, so effects we aim to capture in the analysis could 
    potentially cancel each other out.  
    To correctly illustrate the traffic volume of a weekday, the average of the data from Monday to Friday were summed up *per day and year* and then divided by 
    five.

    ####
    ### Description + Interpretation:
    It can be seen that the average weekday is always making 40-41% of traffic of the week. This is highly likely due to people working in and around 
    Kiel.  
    Saturdays stay consistent as well, accounting for 32-34% of the weekly traffic, while Sundays account for 25-27%.  
    We assume the average traffic on Saturdays to be greater than on Sundays because many shops and businesses remain open that day; thus people are 
    visiting, or working at those places.  

    As said before, the numbers are equally the same for each year, so no significant change has occured over the years.
""")

# ====================================
# Footer Navigation
# ====================================
st.divider()

col1_bottom_btn, col2_bottom_btn, col3_bottom_btn = st.columns([1, 3.6, 1])

with col1_bottom_btn:
    if st.button("⬅️ Previous Question", key="btn_bottom1"):
        st.switch_page("views/Research_Question_3.py")

with col3_bottom_btn:
    if st.button("Next Question ➡️", key="btn_bottom2"):
        st.switch_page("views/Research_Question_5.py")

st.divider()

# Footer utility links
col4_bottom_btn, col5_bottom_btn, col6_bottom_btn, col7_bottom_btn = st.columns([1, 0.33, 0.33, 1])

with col5_bottom_btn:
    if st.button("Go to Imprint", width="stretch"):
        st.switch_page("views/Imprint.py")

with col6_bottom_btn:
    if st.button("Back to Homepage 🏠", width="stretch"):
        st.switch_page("views/homepage.py")
