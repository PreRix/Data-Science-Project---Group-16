import streamlit as st
# ==============================
# hier nötige Imports hinzufügen
# ==============================

col1_top_btn, col2_top_btn, col3_top_btn = st.columns([1, 3.6, 1])

with col1_top_btn:
    if st.button("⬅️ Previous Question", key = "btn_top1"):
        st.switch_page("pages/Research_Question_2.py")
        
with col3_top_btn:
    if st.button("Next Question ➡️", key = "btn_top2"):
        st.switch_page("pages/Research_Question_4.py")

st.title("Research Question #3")

st.markdown("""
    # *How has the total yearly vehicle count near Kiel changed in the past five years, and does the trend in registered vehicles per year in Kiel predict this change?*
    ## Long-Term Traffic Growth
""")

# ====================================
# Hier Visualisierungs-Code hinzufügen
# ====================================

st.markdown("""
    This Bar-Line-Chart illustrates the evolution of *daily average traffic* in comparison to the registered vehicle counts for Kiel *per year* from 2021 to 2025.  
    As the data for registration counts is only available in yearly sample, we had to aggregate the traffic numbers to a yearly value as well.   
    It can be seen that the number in registered vehicles increases each year except between 2024 and 2025. However, the increase is very subtle, which becomes
    apparent when considering the scale of the y-axis. Thus, the registration counts stay pretty stable over the years.
    The corresponding vehicle counts for traffic load are increasing over all years in a noticeable wider range.
    From 2023 to 2024 the number of registered vehicles has the "biggest" increase, while this is the year in which the average daily traffic load has the smallest one.
    A similar phenomenon can be observed for the time span from 2024 to 2025, where the registration count is decreasing, while the traffic load has an 
    increase.  

    ####
    ### Conclusion: 
    The total yearly vehicle count did steadily increase over the past years; especially from 2022 to 2023 after the Covid19-pandamic.
    Vehicle registration counts on the other hand stayed pretty consistent over time.
    The figure shows that traffic volume and vehicle registration counts do not show a strong relationship. A clear correlation can not be derived from the 
    data.  
    What has to be taken into account as well is the fact that registration count for Kiel does not solely influence the vehicle count on streets around Kiel.
    Especially on roads like the A215, where one of the measuring stations for vehicle counting is placed, a lot of commuters pass by; so cars get counted 
    while not being registered for Kiel or vice versa.
""")

st.divider()

col1_bottom_btn, col2_bottom_btn, col3_bottom_btn = st.columns([1, 3.6, 1])

with col1_bottom_btn:
    if st.button("⬅️ Previous Question", key = "btn_bottom1"):
        st.switch_page("pages/Research_Question_2.py")
        
with col3_bottom_btn:
    if st.button("Next Question ➡️", key = "btn_bottom2"):
        st.switch_page("pages/Research_Question_4.py")

st.divider()

col4_bottom_btn, col5_bottom_btn, col6_bottom_btn, col7_bottom_btn = st.columns([1, 0.33, 0.33, 1])

with col5_bottom_btn:
    if st.button("Go to Imprint", use_container_width = True):
        st.switch_page("pages/Imprint.py")

with col6_bottom_btn:
    if st.button("Back to Homepage 🏠", use_container_width = True):
        st.switch_page("pages/homepage.py")