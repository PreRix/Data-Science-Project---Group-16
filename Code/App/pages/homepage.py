import streamlit as st
         
st.title("Welcome to the Website of our Data Science Project!")
st.markdown("""
    ### The Topic we performed research on:
    ### "The Personal Traffic around Kiel in the past five years *(2021 - 2025)*".
""")

st.image("images/Kiel_Verkehr.png", 
         caption = "Image created with Nano Banana 2 (Google Gemini)",
         width = 300)
    
st.markdown("""
    <br>
    
    #### Please check our [GitHub Repository](https://github.com/PreRix/Data-Science-Project---Group-16) for all the code we used and a description of the data pipeline in the [ReadMe](https://github.com/PreRix/Data-Science-Project---Group-16/blob/main/README.md).

    We formulated eight research questions we wanted to answer.
    These are our questions
    
    1. How do precipitation and temperature affect the hourly vehicle counts near Kiel between 2021 and 2025?
    
    2. To what extend does the hourly NO<sub>2</sub>, CO, PM<sub>2,5</sub> and PM<sub>10</sub> concentration in Kiel correlate with vehicle count?
    
    3. How has the total monthly vehicle count near Kiel changed in the past five years, and does the trend in registered vehicles per year in Kiel predict this change?
    
    4. How do Saturday and Sunday volumes near Kiel compare to weekday volumes, and has this weekend-to-weekday ration changed significantly over the five-year observation period?
    
    5. Using yearly registration data for Kiel to derive the estimated share of electric vehicles in the regional fleet from 2021 to 2025, is there a measurable downward trend in NO<sub>2</sub> levels 
    on 
    high-traffic roads near Kiel?

    6. How do extreme weather events affect hourly traffic volumes at selected counting stations near Kiel, and how long does it take for traffic to return to normal levels?

    7. How does the Kieler Woche influence truck traffic and personal traffic volume at nearby counting stations in Kiel, and how does this period compare to typical weeks during the same season?

    8. How did the traffic in rush-hours changed on Autobahnen around Kiel because of the mobility change?
""", unsafe_allow_html = True)

st.markdown("""
    ###   
""")
col_qst_btn1, col_qst_btn2, col_qst_btn3 = st.columns([1, 0.4, 1])

with col_qst_btn2:
    if st.button("Go to the Question Catalog 📒", use_container_width = True):
        st.switch_page("pages/Question_Catalog.py")

st.divider()

col4, col5, col6 = st.columns([1, 0.4, 1])

with col5:
    if st.button("Go to Imprint", use_container_width = True):
        st.switch_page("pages/Imprint.py")
