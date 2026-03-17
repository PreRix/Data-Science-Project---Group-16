import streamlit as st
         
st.title("Welcome to the Website of our Data Science Project!")
st.markdown("""
    ### The Topic we performed research on:
    ### "The Personal Traffic around Kiel in the past five years *(2021 - 2025)*".
""")

st.image("images/Kiel_Verkehr.png", 
         caption = "Image created with Nano Banana 2 (Google Gemini)",
         width = "stretch")
    
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

st.markdown(" ### The Data we used")
st.write("Here you can find all raw data we used for this project. Expand on the data you want to know more about.")

with st.expander("Vehicle Counting Data"):
    st.markdown("""
        For information about the vehicle count on the streets in and around Kiel we used the data from BASt, the "Bundesanstalt für Straßen- und Verkehrswesen". 
        The data is provided as zip-archives per year for Autobahnen and Bundesstraßen; each of which contains folders with 12 raw-data files and one corresponding meta-data file explaining the data. 
        The data is organized in .csv-files and is sampled per hour.  
        Furthermore the vehicle count is given per direction of travel and info about the counted vehicle type is given.
        

        The BASt is the national research center for transportaion and traffic in Germany. Therefore we declare the data as reliable.
        For understanding the datasets a data description in form of a PDF file is provded on the BASt website.
    """)
  
    st.image("images/BASt_example.png", caption = "Sample for BASt data structure", width = "stretch")
    st.info("**Source:** https://www.bast.de/DE/Publikationen/Daten/Verkehrstechnik/DZ-Richtung.html?nn=427910")

with st.expander("Vehicle Registration Counts"):
    st.markdown("""
        To retrive information about the vehicle registration counts for Kiel, we took the yearly registration reports from the "Kraftfahrt Bundesamt" (KBA). 
        These are provided in Excel files containing the count of all registered vehicles in Germany. The counts are also differentiated into engine types.

        The KBA is a German federal agency under the jurisdiction of the Ministry for Digtial and Transport. Therefore the data is trustworthy and of quality.
    """)
    st.info("**Source:** https://www.kba.de/DE/Statistik/Produktkatalog/produkte/Fahrzeuge/fz1_b_uebersicht.html?nn=835828")

with st.expander("Weather & Air Quality Data"):
    st.markdown("""
        For collecting historical weather and air quality data we used the APIs from Open-Meteo.com. 
        
        #### Weather API: 
        The Weather API holds the data in hourly and daily sampling. The data is based on reanalysis datasets and combines weather station, aircraft, buoy, radar and satellite observations to create a
        comprehensive record of past weather conditions.
        The spatial resolution is varying between 5 - 10km; therefore the values are not 100% accurate in terms of an explicit location.
        From all selectable data (over 30 variables) we only selected the ones we needed for our research.

        #### Air Quality API:
        The Air Quality API holds the data in hourly sampling. The data is based on reanalysis datasets and forecasts from the "Copernicus Atmosphere Monitoring Service" (CAMS) providing a spatial 
        resolution between 11 - 45km. As for the weather data; the values can not be seen as 100% accurate in terms of an explicit location.
        Here we selected only the variables of interest as well, and not all the API is offering.

        Both APIs provide an interactive web interface for trying the API out. 
    """)
    st.info("**Source Weather data:** https://open-meteo.com/en/docs/historical-weather-api")
    st.info("**Source Air Quality data:** https://open-meteo.com/en/docs/air-quality-api")

with st.expander("Kieler Woche Data"):
    st.markdown("""
        The Kieler Woche data we wanted to retrive was mainly the dates, from when to when the Kieler Woche took place each year. As there is no dataset or API holding this information, 
        we collected the data ourselves from the official Kieler Woche website, together with the provided estimated visitor counts for each year and wrote them into a .csv-file.
    """)
    st.info("**Source:** https://www.kieler-woche.de/de/medien/meldung.php")

st.divider()

col4, col5, col6 = st.columns([1, 0.4, 1])

with col5:
    if st.button("Go to Imprint", use_container_width = True):
        st.switch_page("pages/Imprint.py")