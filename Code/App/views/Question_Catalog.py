# ====================================
# Imports

import streamlit as st

# ====================================
# Website design

st.title("Question Catalog 📒")

st.markdown("## Here you can easily navigate to all of our Research Questions")
st.markdown("""
    ####    
""")

# clickable buttons to directly reach each question
col1_btn, col2_btn, col3_btn, col4_btn = st.columns([1, 1, 1, 1], gap = "large")

with col1_btn:
    if st.button("📈 RQ1: Weather & Traffic", width = "stretch"):
        st.switch_page("views/Research_Question_1.py")

    if st.button("📈 RQ5: Electric Vehicles & Emissions", width = "stretch"):
        st.switch_page("views/Research_Question_5.py")

    if st.button("📈 BONUS RQ: Extreme Weather & Traffic", width = "stretch"):
        st.switch_page("views/Research_Question_9.py")

with col2_btn:
    if st.button("📈 RQ2: Air Quality & Traffic", width = "stretch"):
        st.switch_page("views/Research_Question_2.py")

    if st.button("📈 RQ6: Incoming vs. Outgoing Traffic", width = "stretch"):
        st.switch_page("views/Research_Question_6.py")

with col3_btn:
    if st.button("📈 RQ3: Long-term Traffic Growth", width = "stretch"):
        st.switch_page("views/Research_Question_3.py")

    if st.button("📈 RQ7: Kieler Woche Traffic", width = "stretch"):
        st.switch_page("views/Research_Question_7.py")

with col4_btn:
    if st.button("📈 RQ4: Weekend vs. Weekday Traffic", width = "stretch"):
        st.switch_page("views/Research_Question_4.py")

    if st.button("📈 RQ8: Rush-Hour Traffic", width = "stretch"):
        st.switch_page("views/Research_Question_8.py")

st.divider()

# button layout
col4_bottom_btn, col5_bottom_btn, col6_bottom_btn, col7_bottom_btn = st.columns([1, 0.33, 0.33, 1])

with col5_bottom_btn:
    if st.button("Go to Imprint", width = "stretch"):
        st.switch_page("views/Imprint.py")

with col6_bottom_btn:
    if st.button("Back to Homepage 🏠", width = "stretch"):
        st.switch_page("views/homepage.py")
