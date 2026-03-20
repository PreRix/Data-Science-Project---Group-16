# ====================================
# Imports

import streamlit as st
from pathlib import Path
from utils.navigation import setup

# ====================================
# Website design

setup()
         
st.title("Welcome to the Website of our Data Science Project!")
st.markdown("""
    ### The Topic we performed research on:
    ### "The Personal Traffic around Kiel in the past five years *(2021 - 2025)*".
""")

col_img1, col_img2, col_img3 = st.columns([1, 2.5, 1])

img_path = Path(__file__).parent.parent / "images" / "Kiel_Verkehr.png"

with col_img2:
    st.image(str(img_path), 
        caption = "Image created with Nano Banana 2 (Google Gemini)",
        width = "content")
    
st.markdown("""
    <br>
    
    #### Please check our [GitHub Repository](https://github.com/PreRix/Data-Science-Project---Group-16) for all the code we used and a description of the data pipeline in the [ReadMe](https://github.com/PreRix/Data-Science-Project---Group-16/blob/main/README.md).

    We formulated eight research questions we wanted to answer.
    These are our questions:
    
    1. How do precipitation and temperature affect the hourly vehicle counts near Kiel between 2021 and 2025?
    
    2. To what extent does the hourly NO<sub>2</sub>, CO, PM<sub>2.5</sub> and PM<sub>10</sub> concentration in Kiel correlate with vehicle count?
    
    3. How has the total yearly vehicle count near Kiel changed in the past five years, and does the trend in registered vehicles per year in Kiel predict this change?
    
    4. How do Saturday and Sunday volumes near Kiel compare to weekday volumes, and has this weekend-to-weekday ratio changed significantly over the five-year observation period?
    
    5. Using yearly registration data for Kiel to derive the estimated share of electric vehicles in the regional fleet from 2021 to 2025, is there a measurable downward trend in NO<sub>2</sub> levels 
    on 
    high-traffic roads near Kiel?

    6. How does the ratio of incoming and outgoing traffic around Kiel change during the day?

    7. How does the daily passenger transport and freight transport traffic change during the Kieler Woche compared to the surrounding month (two weeks before and after)?

    8. How did the traffic in rush-hours change on Autobahnen around Kiel over the past five years?  

    9. *A Bonus Question:* How do extreme weather events affect hourly traffic volumes at selected counting stations near Kiel, and how long does it take for traffic to return to normal levels?
""", unsafe_allow_html=True)

st.markdown("""
    ###   
""")

col_qst_btn1, col_qst_btn2, col_qst_btn3, col_qst_btn4 = st.columns([1, 1, 1, 1])

with col_qst_btn2:
    if st.button("Go to the Question Catalog 📒", width = "stretch"):
        st.switch_page("pages/Question_Catalog.py")

with col_qst_btn3:
    if st.button("Go to the Data Sources  📄", width = "stretch"):
        st.switch_page("pages/Data_Sources.py")
st.divider()

col4, col5, col6 = st.columns([1, 0.4, 1])

with col5:
    if st.button("Go to Imprint", width = "stretch"):
        st.switch_page("pages/Imprint.py")