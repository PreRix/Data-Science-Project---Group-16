import streamlit as st
# ==============================
# hier nötige Imports hinzufügen
# ==============================

col1_top_btn, col2_top_btn, col3_top_btn = st.columns([1, 3.6, 1])

with col1_top_btn:
    if st.button("⬅️ Previous Question", key = "btn_top1"):
        st.switch_page("pages/Research_Question_7.py")

with col3_top_btn:
    if st.button("Bonus Question ➡️", key = "btn_top2"):
        st.switch_page("pages/Research_Question_9.py")

st.title("Research Question #8")

st.markdown("""
    # *How did the traffic in rush-hours change on Autobahnen around Kiel over the past five years?*
    ## Average Rush-Hour Traffic on the A215 (AK Kiel-West) on Weekdays only
""")

# ====================================
# Hier Visualisierungs-Code hinzufügen
# ====================================

st.markdown("""
    The two lines in the chart represent the traffic of the two rush-hours each day at the A215, aggregated to an *average day of the month*. No other counting station 
    displays the commuter traffic better than this one, as the A215 is known for being a main commuter route for Kiel.  
    For the morning rush-hour we defined the time window from 6-9 a.m.; only considering the traffic coming to Kiel.  
    For the evening rush-hour we chose 4-6 p.m., while only considering traffic leaving Kiel.  
    Additionally we only took into account data from weekdays (Monday to Friday), so that data from weekends would not bias the result.  
    
    Noticeable is the drop in the month of December for every observed year. This is very likely linked to the Christmas season and holidays. 
    The month before, November, seems to always have an increase in average vehicle counts. Maybe because people try to get most of the work done before the Christmas
    break.  
    As well it can be seen pretty clearly that in August the vehicle counts during morning rush-hour decrease in comparison to the month before and after. This 
    may be correlated with summer holidays. Interestingly, for the evening rush-hour this pattern does not apply this strong. A reason for that might be 
    that on summer evenings the traffic is also including tourists coming to Kiel during noon, and leaving in the evening.

    ####
    ### Conclusion:
    Both lines show a general increase over the observation period. Especially the evening rush-hour in 2021 is having a massive increase. We think this is
    because it was the first summer after the second Corona lockdown which ended mid 2021. So people started coming to work again, while social life increased 
    significantly as well.  
    We think that in the years after the COVID-19 pandemic many companies slowly went back to normal in-person work; so that homeoffice opportunities mostly got 
    reduced in the past years. This may be a reason for the trend the data is showing.
""")

st.divider()

st.markdown("""
    ## Rush-Hour Traffic for one exemplary month - Feb 2023
""")

# ====================================
# Hier Visualisierungs-Code hinzufügen
# ====================================

st.markdown("""
    This figure illustrates the development over an exemplary month without holidays or other special events, allowing for a clearer interpretation of the traffic 
    patterns.
""")

st.divider()

col1_bottom_btn, col2_bottom_btn, col3_bottom_btn = st.columns([1, 3.6, 1])

with col1_bottom_btn:
    if st.button("⬅️ Previous Question", key = "btn_bottom1"):
        st.switch_page("pages/Research_Question_7.py")

with col3_bottom_btn:
    if st.button("Bonus Question ➡️", key = "btn_bottom2"):
        st.switch_page("pages/Research_Question_9.py")

st.divider()

col4_bottom_btn, col5_bottom_btn, col6_bottom_btn, col7_bottom_btn = st.columns([1, 0.33, 0.33, 1])

with col5_bottom_btn:
    if st.button("Go to Imprint", use_container_width = True):
        st.switch_page("pages/Imprint.py")

with col6_bottom_btn:
    if st.button("Back to Homepage 🏠", use_container_width = True):
        st.switch_page("pages/homepage.py")