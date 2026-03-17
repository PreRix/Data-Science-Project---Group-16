import streamlit as st
# ==============================
# hier nötige Imports hinzufügen
# ==============================

col1_top_btn, col2_top_btn, col3_top_btn = st.columns([1, 3.6, 1])

with col1_top_btn:
    if st.button("⬅️ Previous Question", key = "btn_top1"):
        st.switch_page("pages/Research_Question_5.py")
        
with col3_top_btn:
    if st.button("Next Question ➡️", key = "btn_top2"):
        st.switch_page("pages/Research_Question_7.py")

st.title("Research Question #6")

st.markdown("""
    # *How does the ratio of incoming and outgoing traffic around Kiel change during the day?*
    ## Incoming vs. Outgoing Traffic
""")

# ====================================
# Hier Visualisierungs-Code hinzufügen
# ====================================

st.markdown("""
    The HeatMap shows how the traffic load on selected roads changes during the days of an *average week* when splitting for incoming and outgoing traffic.  
    The month, year and counting station for which the data should be displayed can be selected. 
    As data sources we selected the counting stations "Autobahn-Kreuz Kiel West" and "Rumohr" at the A215, as well as "AS Wankendorf" at the A21 as these are main 
    routes connecting Kiel with the rest of the country; while providing large amounts of data for analysis.  
    In our raw data the vehicle count is given per direction of travel, so we checked for each station which counts correspond to incoming and outgoing traffic.

    ####
    ### Conclusion:
    The observations greatly show the rush-hour traffic during the week when people come to Kiel to go to work in the morning and leave in the afternoon.  
    During weekdays the traffic at night is mainly outgoing, while around midnight the traffic is directed more in the other direction. This may be because of people 
    working nightshifts.  
    Additional findings can be observed when exploring different parameter combinations.
    Important to keep in mind: The HeatMap says **nothing about the absolute vehicle count** of one hour, it showcases the relation between the traffic loads on the 
    two directions of travel!
""")

st.divider()

col1_bottom_btn, col2_bottom_btn, col3_bottom_btn = st.columns([1, 3.6, 1])

with col1_bottom_btn:
    if st.button("⬅️ Previous Question", key = "btn_bottom1"):
        st.switch_page("pages/Research_Question_5.py")
        
with col3_bottom_btn:
    if st.button("Next Question ➡️", key = "btn_bottom2"):
        st.switch_page("pages/Research_Question_7.py")

st.divider()

col4_bottom_btn, col5_bottom_btn, col6_bottom_btn, col7_bottom_btn = st.columns([1, 0.33, 0.33, 1])

with col5_bottom_btn:
    if st.button("Go to Imprint", use_container_width = True):
        st.switch_page("pages/Imprint.py")

with col6_bottom_btn:
    if st.button("Back to Homepage 🏠", use_container_width = True):
        st.switch_page("pages/homepage.py")