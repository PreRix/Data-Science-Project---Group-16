import streamlit as st
# ==============================
# hier nötige Imports hinzufügen
# ==============================

col1_top_btn, col2_top_btn, col3_top_btn = st.columns([1, 3.6, 1])

with col1_top_btn:
    if st.button("⬅️ Previous Question", key = "btn_top1"):
        st.switch_page("pages/Research_Question_6.py")
        
with col3_top_btn:
    if st.button("Next Question ➡️", key = "btn_top2"):
        st.switch_page("pages/Research_Question_8.py")

st.title("Research Question #7")

st.markdown("""
    # *How does the daily passenger transport and freight transport traffic change during Kieler Woche compared to the surrounding month (two weeks before and after)?*
    ## Traffic compared: Kieler Woche vs. Baseline Levels
""")

# ====================================
# Hier Visualisierungs-Code hinzufügen
# ====================================

st.markdown("""
    To analyze the impact of Kieler Woche on traffic we used the *daily vehicle counts* for *every Kieler Woche* from selected counting stations around Kiel.
    Specifically, we used data from the following stations, as they monitor highly frequented roads:

    - station 1194: Autobahn Kreuz Kiel-West on the A215
    - station 1104: Rumohr on the A215
    - station 1156: AS Wankendorf on the A21.

    The counting station for which the data should be displayed can be selected.

    We separated the traffic into passenger transport and freight transport. These had to be defined:

    - Passenger transport includes all vehicles serving the main purpose of transporting people (e.g. cars, motorcycles, buses)
    - Freight transport includes all vehicles serving the main purpose of transporting something else than people (e.g. delivery trucks, heavy trucks).

    In the diagram above, the bars show the actual sum of traffic on each of the Kieler Woche days; the year of Kieler Woche can be selected manually. The dotted 
    lines represent the baseline traffic levels; so the average of the correspondig weekday in the *two weeks* before and after the Kieler Woche.  
    We made this decision to use these time spans, so that the baseline level actually represents meaningful traffic values; so using data from the same season of 
    the year.

    ####
    ### Conclusion:
    For the personal traffic a clear pattern can be identified. It can be observed that the traffic during the Kieler Woche is generally higher than baseline 
    traffic levels. This is especially noticeable on fridays and the weekend, where the baseline traffic decreases. This is expected, as on
    these days fewer people drive to work in Kiel. This also results in a decrease in the overall traffic count during Kieler Woche on these three days.  

    However for freight transport, no such pattern can be observed. The Kieler Woche traffic and basline level traffic are generally very even; with 
    more traffic on weekdays than on weekends, as many of these vehicles are not permitted to drive on these days.
""")

st.divider()

col1_bottom_btn, col2_bottom_btn, col3_bottom_btn = st.columns([1, 3.6, 1])

with col1_bottom_btn:
    if st.button("⬅️ Previous Question", key = "btn_bottom1"):
        st.switch_page("pages/Research_Question_6.py")
        
with col3_bottom_btn:
    if st.button("Next Question ➡️", key = "btn_bottom2"):
        st.switch_page("pages/Research_Question_8.py")
        
st.divider()

col4_bottom_btn, col5_bottom_btn, col6_bottom_btn, col7_bottom_btn = st.columns([1, 0.33, 0.33, 1])

with col5_bottom_btn:
    if st.button("Go to Imprint", use_container_width = True):
        st.switch_page("pages/Imprint.py")

with col6_bottom_btn:
    if st.button("Back to Homepage 🏠", use_container_width = True):
        st.switch_page("pages/homepage.py")