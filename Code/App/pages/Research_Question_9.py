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
    Hier die Beschreibung für Visualisierung 1
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