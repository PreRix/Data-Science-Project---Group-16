import streamlit as st
from pathlib import Path

st.title("The Data we used")
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

    img_path = Path(__file__).parent.parent / "images" / "BASt_example.png"

    st.image(str(img_path), caption = "Sample for BASt data structure", width = "stretch")
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

col4_bottom_btn, col5_bottom_btn, col6_bottom_btn, col7_bottom_btn = st.columns([1, 0.33, 0.33, 1])

with col5_bottom_btn:
    if st.button("Go to Imprint", width = "stretch"):
        st.switch_page("pages/Imprint.py")

with col6_bottom_btn:
    if st.button("Back to Homepage 🏠", width = "stretch"):
        st.switch_page("pages/homepage.py")
