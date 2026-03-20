import streamlit as st
from utils.data_loader import ensure_session_data

def setup():
    ensure_session_data()

    views = {
        "Home": [
            st.Page("views/homepage.py", title = "🏠 Homepage", default = True),
            st.Page("views/Question_Catalog.py", title = "📒 Question Catalog"),
            st.Page("views/Data_Sources.py", title = "📄 Data Sources")
        ],
        "Questions": [
            st.Page("views/Research_Question_1.py", title = "📈 RQ1: Weather & Traffic"),
            st.Page("views/Research_Question_2.py", title = "📈 RQ2: Air Quality & Traffic"),
            st.Page("views/Research_Question_3.py", title = "📈 RQ3: Long-term Traffic Growth"),
            st.Page("views/Research_Question_4.py", title = "📈 RQ4: Weekend vs. Weekday Traffic"),
            st.Page("views/Research_Question_5.py", title = "📈 RQ5: Electric Vehicles & Emissions"),
            st.Page("views/Research_Question_6.py", title = "📈 RQ6: Incoming vs. Outgoing Traffic"),
            st.Page("views/Research_Question_7.py", title = "📈 RQ7: Kieler Woche Traffic"),
            st.Page("views/Research_Question_8.py", title = "📈 RQ8: Rush-Hour Traffic"),
            st.Page("views/Research_Question_9.py", title = "📈 BONUS RQ: Extreme Weather & Traffic")
        ],
        "About": [
            st.Page("views/Imprint.py", title = "🧑‍🧑‍🧒‍🧒 Imprint")
        ]
    }

    pg = st.navigation(views, position="sidebar")
    pg.run()

    with st.sidebar:
        st.divider()
        st.caption("📁 [GitHub](https://github.com/PreRix/Data-Science-Project---Group-16)")