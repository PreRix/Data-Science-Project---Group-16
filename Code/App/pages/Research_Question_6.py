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
    Hier die Beschreibung für Visualisierung 1
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