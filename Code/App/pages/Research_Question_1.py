import streamlit as st
# ==============================
# hier nötige Imports hinzufügen
# ==============================

col1_top_btn, col2_top_btn, col3_top_btn = st.columns([1, 3.6, 1])

with col3_top_btn:
    if st.button("Next Question ➡️", key = "btn_top"):
        st.switch_page("pages/Research_Question_2.py")

st.title("Research Question #1")

st.markdown("""
    # *How do precipitation and temperature affect the hourly vehicle counts near Kiel between 2021 and 2025?*
    ## Traffic Volume: Dry vs. Wet
    """)

# ====================================
# Hier Visualisierungs-Code hinzufügen
# ====================================

st.markdown("""
    Two HeatMaps are used to show how the *average vehicle count per hour and weekday* gets impacted by precipitation (rain + snow).  
    To make such a comparison possible, we had to define *dry day* and  *wet day*:  

    - Dry day: 0mm of precipitation per hour
    - Wet day: can be adjusted on a scale from 0.1 to 2mm of precipitation per hour  
    
    A thrid HeatMap shows the relative difference from dry to wet day based on the dry day data for the avergage vehicle count.  
    We only took into account values from counting station 1194 ("Autobahnkreuz Kiel-West") on the A215, 1104 ("Rumohr") on the A215 and 1156 ("AS Wankendorf") 
    on the A21 as these are one of the highly frequented roads; thus, holding the most vehicle counting data.  
    It can be manually selected, which counting station should be displayed.  
    If we would have combined data from multiple counting stations all over Kiel, local weather effects on traffic may cancel each other out when 
    using averages.
""")

st.divider()

st.markdown("""
    ## Traffic Distribution by Daily Average Temperature
""")

# ====================================
# Hier Visualisierungs-Code hinzufügen
# ====================================

st.markdown("""
    The BoxPlots are visualizing how traffic volume is affected by temperature.  
    Therefore we categorized the *daily average temperature* into six temperature ranges; each BoxPlot then showing the respective vehicle volume distribution.  
    We used the *average daily vehicle count* at counting station 1194, 1104 and 1156 again. Reasoning for this decision is the same as above.  
    Additionally, a weekly average distribution can be displayed.  

    It can be seen, that during weekdays, the temperature does not have so much impact on the traffic distribution, as many people have to go to work, 
    not matter the temperature.  
    On the weekend-days, the temperature definitely seems to have an effect, as the traffic distribution increases with temperature.  

    ####   
    ### Conclusion:
    Precipitation seems to have a small to medium effect on the hourly vehicle counts. Especially during rush-hour times it is visible how the 
    vehicle count numbers are not as solidly high when wet compared to a dry day.  
    Temperature seems to have a major effect on the weekend, while weekdays are moderately affected.
""")

st.divider()

col1_bottom_btn, col2_bottom_btn, col3_bottom_btn = st.columns([1, 3.6, 1])

with col3_bottom_btn:
    if st.button("Next Question ➡️", key = "btn_bottom"):
        st.switch_page("pages/Research_Question_2.py")

st.divider()

col4_bottom_btn, col5_bottom_btn, col6_bottom_btn, col7_bottom_btn = st.columns([1, 0.33, 0.33, 1])

with col5_bottom_btn:
    if st.button("Go to Imprint", use_container_width = True):
        st.switch_page("pages/Imprint.py")

with col6_bottom_btn:
    if st.button("Back to Homepage 🏠", use_container_width = True):
        st.switch_page("pages/homepage.py")