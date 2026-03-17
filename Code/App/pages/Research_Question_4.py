import streamlit as st
# ==============================
# hier nötige Imports hinzufügen
# ==============================

col1_top_btn, col2_top_btn, col3_top_btn = st.columns([1, 3.6, 1])

with col1_top_btn:
    if st.button("⬅️ Previous Question", key = "btn_top1"):
        st.switch_page("pages/Research_Question_3.py")
        
with col3_top_btn:
    if st.button("Next Question ➡️", key = "btn_top2"):
        st.switch_page("pages/Research_Question_5.py")

st.title("Research Question #4")

st.markdown("""
    # *How do Saturday and Sunday volumes near Kiel compare to weekday volumes, and has this weekend-to-weekday ration changed significantly over the five-year observation period?*
    ## Weekend vs. Weekday Traffic Load on the A215 (AK Kiel-West)
""")

# ====================================
# Hier Visualisierungs-Code hinzufügen
# ====================================

st.markdown("""
    For this question we decided to use a pie chart for every year.  
    The data we used is from the counting station 1194 alone at the A215 because, as concluded in RQ4, this station is highly representative of commuter traffic 
    and traffic in general. 
    As well, there might be differences for the counting stations for the different days of the week, so effects we aim to capture in the analysis could 
    potentially cancel each other out.  
    To correctly illustrate the traffic volume of a weekday, the average of the data from monday to friday were summed up *per day and year* and then divided by 
    five.

    ####
    ### Conclusion:
    It can be seen that the average weekday is always making 40-41% of traffic of the week. This is highly likely due to people working in and around 
    Kiel.  
    Saturdays stay consistent as well, accounting for 32-34% of the weekly traffic, while Sundays account for 25-27%.  
    We assume the average traffic on Saturdays to be greater than on Sundays because of many shops and businesses remain open that day; thus people are 
    visiting, or working at those places.  

    As said before, the numbers are equally the same for each year, so no significant change has occured over the years.
""")

st.divider()

col1_bottom_btn, col2_bottom_btn, col3_bottom_btn = st.columns([1, 3.6, 1])

with col1_bottom_btn:
    if st.button("⬅️ Previous Question", key = "btn_bottom1"):
        st.switch_page("pages/Research_Question_3.py")
        
with col3_bottom_btn:
    if st.button("Next Question ➡️", key = "btn_bottom2"):
        st.switch_page("pages/Research_Question_5.py")

st.divider()

col4_bottom_btn, col5_bottom_btn, col6_bottom_btn, col7_bottom_btn = st.columns([1, 0.33, 0.33, 1])

with col5_bottom_btn:
    if st.button("Go to Imprint", use_container_width = True):
        st.switch_page("pages/Imprint.py")

with col6_bottom_btn:
    if st.button("Back to Homepage 🏠", use_container_width = True):
        st.switch_page("pages/homepage.py")