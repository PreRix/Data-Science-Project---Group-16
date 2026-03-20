import streamlit as st
from utils.data_loader import load_traffic_base, load_registrations, load_registrations_fuel, load_weather

st.set_page_config(
    page_title = "DSP - Group 16",
    page_icon = "📊",
    layout = "wide",
    menu_items = {
        "About" : "[Check out our GitHub Repository](https://github.com/PreRix/Data-Science-Project---Group-16)"
    }
)

# Preload all data into session_state once
if "df_traffic" not in st.session_state:
    st.session_state.df_traffic = load_traffic_base()

if "df_registrations" not in st.session_state:
    st.session_state.df_registrations = load_registrations()

if "df_registrations_fuel" not in st.session_state:
    st.session_state.df_registrations_fuel = load_registrations_fuel()

if "df_weather" not in st.session_state:
    st.session_state.df_weather = load_weather()

pages = {
    "Home": [
        st.Page("pages/homepage.py", title = "🏠 Homepage", default = True),
        st.Page("pages/Question_Catalog.py", title = "📒 Question Catalog"),
        st.Page("pages/Data_Sources.py", title = "📄 Data Sources")
    ],
    "Questions": [
        st.Page("pages/Research_Question_1.py", title = "📈 RQ1: Weather & Traffic"),
        st.Page("pages/Research_Question_2.py", title = "📈 RQ2: Air Quality & Traffic"),
        st.Page("pages/Research_Question_3.py", title = "📈 RQ3: Long-term Traffic Growth"),
        st.Page("pages/Research_Question_4.py", title = "📈 RQ4: Weekend vs. Weekday Traffic"),
        st.Page("pages/Research_Question_5.py", title = "📈 RQ5: Electric Vehicles & Emissions"),
        st.Page("pages/Research_Question_6.py", title = "📈 RQ6: Incoming vs. Outgoing Traffic"),
        st.Page("pages/Research_Question_7.py", title = "📈 RQ7: Kieler Woche Traffic"),
        st.Page("pages/Research_Question_8.py", title = "📈 RQ8: Rush-Hour Traffic"),
        st.Page("pages/Research_Question_9.py", title = "📈 BONUS RQ: Extreme Weather & Traffic")
    ],
    "About": [
        st.Page("pages/Imprint.py", title = "🧑‍🧑‍🧒‍🧒 Imprint")
    ]
}

pg = st.navigation(pages, position = "sidebar")
pg.run()