import streamlit as st
# ==============================
# hier nötige Imports hinzufügen
# ==============================

col1_top_btn, col2_top_btn, col3_top_btn = st.columns([1, 3.6, 1])

with col1_top_btn:
    if st.button("⬅️ Previous Question", key = "btn_top1"):
        st.switch_page("pages/Research_Question_4.py")
        
with col3_top_btn:
    if st.button("Next Question ➡️", key = "btn_top2"):
        st.switch_page("pages/Research_Question_6.py")

st.title("Research Question #5")

st.markdown("""
    # *Using yearly registration data for Kiel to derive the estimated share of battery-electric vehicles in the regional fleet from 2021 to 2025, is there a measurable downward trend in NO<sub>2</sub> levels on high-traffic roads near Kiel?*
    ## Vehicle Registrations in Kiel - by Fuel Type 
""", unsafe_allow_html = True)

# ====================================
# Hier Visualisierungs-Code hinzufügen
# ====================================

st.markdown("""
    For the first visualization we decided to show the share of *vehicles per fuel type for each year* using the bar chart above.  
    An initial observation is that the share of conventional fuel vehicles (petrol and diesel) decreases steadily every year.
    On the other hand the number with (partly) electric drivetrains increases every year, which confirms expectations based on political initiatives in recent 
    years.
""")

st.divider()

st.markdown("""
    ## Battery-Electric Vehicle (BEV) Share vs. Average NO<sub>2</sub> emission per Vehicle
""", unsafe_allow_html = True)

# ====================================
# Hier Visualisierungs-Code hinzufügen
# ====================================

st.markdown("""
    This visualization shows the average NO<sub>2</sub> emission per vehicle. We calculated this by summing up all NO<sub>2</sub> concentration data for *each year* and dividing it by the total vehicle counting data for all available stations *per year*.  
    This approach was chosen to normalize the data against fluctuations in traffic volume, providing a more comparable value for the evolution of NO<sub>2</sub> 
    levels over time.  
    The data shows that the concentrations vary throughout the year; a slight downward trend is only visible when taking a look at the regression line 
    of the data.

    ####
    ### Conclusion:
    As said above, a minor downward trend in NO<sub>2</sub> emissions is noticeable while the number of registered BEV vehicles is increasing.  
    Nevertheless, the data cannot determine whether the growth in battery-electric vehicle share causes the observed decrease in NO<sub>2</sub> levels.  
    This is due to two factors:

    1. The measurement of air pollutants is heavily affected by other metrics, as we discussed in RQ2.
    2. The registration number of battery-electric vehicles does not have to be representative for actual electric traffic load on streets in and around Kiel.

    To answer the question: Yes, a measurable downward trend can be spotted, and it correlates with the increasing numbers of BEV registrations.  
    But no, it can not be determined if this actually is a causation.
    
""", unsafe_allow_html = True)

st.divider()

col1_bottom_btn, col2_bottom_btn, col3_bottom_btn = st.columns([1, 3.6, 1])

with col1_bottom_btn:
    if st.button("⬅️ Previous Question", key = "btn_bottom1"):
        st.switch_page("pages/Research_Question_4.py")
        
with col3_bottom_btn:
    if st.button("Next Question ➡️", key = "btn_bottom2"):
        st.switch_page("pages/Research_Question_6.py")

st.divider()

col4_bottom_btn, col5_bottom_btn, col6_bottom_btn, col7_bottom_btn = st.columns([1, 0.33, 0.33, 1])

with col5_bottom_btn:
    if st.button("Go to Imprint", use_container_width = True):
        st.switch_page("pages/Imprint.py")

with col6_bottom_btn:
    if st.button("Back to Homepage 🏠", use_container_width = True):
        st.switch_page("pages/homepage.py")