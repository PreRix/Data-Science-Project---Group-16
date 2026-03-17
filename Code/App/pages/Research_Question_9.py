import streamlit as st
# ==============================
# hier nötige Imports hinzufügen
# ==============================

col1_top_btn, col2_top_btn, col3_top_btn = st.columns([1, 3.6, 1])

with col1_top_btn:
    if st.button("⬅️ Previous Question", key = "btn_top"):
        st.switch_page("pages/Research_Question_8.py")

st.title("BONUS Research Question")

st.markdown("""
    # *How do extreme weather events affect hourly traffic volumes at selected counting stations near Kiel, and how long does it take for traffic to return to normal levels?*
    ## Relative Traffic around Extreme Weather Events 
""")

# ====================================
# Hier Visualisierungs-Code hinzufügen
# ====================================

st.markdown("""
    Extreme weather events were identified using the following thresholds:

    - for rain: >10mm of rain per hour 
    - for snow: >1cm of snowfall per hour

    For each event *hourly traffic volumes* at counting station 1194 ("Autobahn-Kreuz Kiel-West") were analyzed in a time window of two hours before, and four hours 
    after the start of an extreme weather event. We only took data from this counting station again, as an average over multiple counting stations could cause the 
    results of local extreme weather to cancel each other out.  

    To allow comparison with normal traffic conditions, a median line was calculated. It represents the typical traffic volume for the same hour of the day 
    when the extreme weather event began, using data from all other days at the counting station.  
    In other words, it shows the *average traffic level* that would normally be expected at that specific hour under normal weather conditions.
    The dots represent the vehicle count during extreme weather in relative percentage to the median line.

    ####
    ### No Conclusion can be made
    As we wanted to analyze how long it takes for traffic volumes to return to baseline levels (represented by the median line), we noticed the fact that local extreme 
    weather events often only last a short period of time.  
    To address the research question we would have needed minutely data of weather and vehicle counts. With the given data, no solid analysis can be performed!
""")

st.divider()

col1_bottom_btn, col2_bottom_btn, col3_bottom_btn = st.columns([1, 3.6, 1])

with col1_bottom_btn:
    if st.button("⬅️ Previous Question", key = "btn_bottom"):
        st.switch_page("pages/Research_Question_8.py")

st.divider()

col4_bottom_btn, col5_bottom_btn, col6_bottom_btn, col7_bottom_btn = st.columns([1, 0.33, 0.33, 1])

with col5_bottom_btn:
    if st.button("Go to Imprint", use_container_width = True):
        st.switch_page("pages/Imprint.py")

with col6_bottom_btn:
    if st.button("Back to Homepage 🏠", use_container_width = True):
        st.switch_page("pages/homepage.py")