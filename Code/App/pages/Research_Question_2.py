import streamlit as st
# ==============================
# hier nötige Imports hinzufügen
# ==============================

col1_top_btn, col2_top_btn, col3_top_btn = st.columns([1, 3.6, 1])

with col1_top_btn:
    if st.button("⬅️ Previous Question", key = "btn_top1"):
        st.switch_page("pages/Research_Question_1.py")
        
with col3_top_btn:
    if st.button("Next Question ➡️", key = "btn_top2"):
        st.switch_page("pages/Research_Question_3.py")

st.title("Research Question #2")

st.markdown("""
    # *To what extend does the hourly NO<sub>2</sub>, CO, PM<sub>2,5</sub> and PM<sub>10</sub> concentration in Kiel correlate with vehicle count?*
    ## Air Quality & Traffic - Hourly Analysis
""", unsafe_allow_html = True)

# ====================================
# Hier Visualisierungs-Code hinzufügen
# ====================================

st.markdown("""
    This diagram shows that the hourly data was aggregated into an *average diurnal cycle* for the concentration of air pollutants, while displaying the 
    corresponding *average vehicle count per hour* as well. It can be selected which pollutant should be displayed as well as the year one wants to see 
    (multiple selections possible).
    It can be seen that, interestingly, the concentration of almost all air quality variables is dropping at noon, while the vehicle count starts rising.  
    On the other hand, during night and morning times, these concentrations are increasing.
    At first, this seems to be an error in our data, but some meteorological phenomena actually explain this **interesting** finding:  
    
    1. When the sun sets, the air near the ground gets colder than the air above. The air gets denser and traps the pollutants near the ground, inhibiting
    vertical dispersion.  
    When the sun starts heating up the Earth's surface, the pollutants get carried up with the warmer air and mix with fresh air.
    2. At night time the wind generally subsides, leading to less airflow, and a more stable air layer holding the pollutants and their concentrations higher.  
    During the day, when winds increase, the concentration of pollutants decreases as they mix with fresh air and are more likely to be blown away at the
    local measuring point. 
    
    For this analysis, we used data from the vehicle counting station 1194 ("Autobahnkreuz Kiel-West") alone, as it is one of the main routes in the Kiel area, 
    being highly representative for this question. Therefore we retrieved air quality data for the coordinate sector of this station.  
    Furthermore, we want to mention that the available air quality data is **not** provided by a sensor station right next to the road. The data is provided from 
    different sources via Open-Meteo with spatial resolution showing the "general" air quality of the area.

    ####   
    ### Conclusion:
    The aggregated diurnal profiles suggest that pollutant concentrations do not directly follow traffic intensity. While traffic 
    is a primary source of emissions, its correlation with observed air quality appears to be masked at a regional scale by meteorological processes such as
    atmospheric stability, vertical mixing and wind conditions.
""")

st.divider()

st.markdown("""
    ## Correlation HeatMap - Air Quality vs. Traffic
""")

# ====================================
# Hier Visualisierungs-Code hinzufügen
# ====================================

st.markdown("""
    Correlation-HeatMaps are used to not only illustrate the correlation between the vehicle count and the different air quality variables, but also the 
    correlation among the air quality variables themselves.  
    The diagonal axis is filled with "1s", as each variable is perfectly correlated with itself. This also confirms that the code is working properly.  
    For the vehicle count, we can observe that it is negativeley correlated with all selected air quality variables.  
    This confirms the observations that can be made from the figure above with numerical values as well.
""")

st.divider()

col1_bottom_btn, col2_bottom_btn, col3_bottom_btn = st.columns([1, 3.6, 1])

with col1_bottom_btn:
    if st.button("⬅️ Previous Question", key = "btn_bottom1"):
        st.switch_page("pages/Research_Question_1.py")
        
with col3_bottom_btn:
    if st.button("Next Question ➡️", key = "btn_bottom2"):
        st.switch_page("pages/Research_Question_3.py")

st.divider()

col4_bottom_btn, col5_bottom_btn, col6_bottom_btn, col7_bottom_btn = st.columns([1, 0.33, 0.33, 1])

with col5_bottom_btn:
    if st.button("Go to Imprint", use_container_width = True):
        st.switch_page("pages/Imprint.py")

with col6_bottom_btn:
    if st.button("Back to Homepage 🏠", use_container_width = True):
        st.switch_page("pages/homepage.py")