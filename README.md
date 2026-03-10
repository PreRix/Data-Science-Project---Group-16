# Data-Science-Project Group-16

## Introduction

### Who we are

We are a group of four students from the Christian-Albrechts-University to Kiel (CAU) studying computer science and business information systems.
This project is assigned to the Data-Science-Project which is taking place between the fifth and sixth semester (Feb 23 - Mar 20, 2026).

We had to find a topic which is interesting to us and perform data science on it:
from the collection of raw, non-pre-processed data, through data cleansing and analyzing, to the creation of visualizations for our findings.
Those should then be accessible on a self-programmed website.

*All of us are native-german speakers, so please excuse the maybe non-perfect English :)*

### The Topic
The topic of our project is as follows: The Personal Traffic around Kiel in the past five years *(2021 to 2025)*.

We developed nine plus one bonus [research questions](Research-Questions.pdf) from which we want to answer eight with this project.

### The Data 
The data we used is freely available. The sources are the following:
- [BASt datasets for the vehicle counts on German Autobahnen (motorways) and Bundesstraßen (federal highways)](https://www.bast.de/DE/Publikationen/Daten/Verkehrstechnik/DZ-Richtung.html?nn=427910)
- [KBA datasets for the vehicle registration count in Kiel](https://www.kba.de/DE/Statistik/Produktkatalog/produkte/Fahrzeuge/fz1_b_uebersicht.html?nn=835828)
- [Open-Meteo Weather data in Kiel](https://open-meteo.com/en/docs/historical-weather-api)
- [Open-Meteo Air Quality data in Kiel](https://open-meteo.com/en/docs/air-quality-api)
- [OpenStreetMap Bounding Box data for Kiel](https://nominatim.openstreetmap.org/search)
- [OpenLigaDB Football data for games in the Bundesliga 1/2 played in Kiel](https://openligadb.de)
- [Kieler Woche data for visitor count and date](https://www.kieler-woche.de/de/medien/meldung.php)


## Data Pipeline
We began by downloading all traffic datasets of the past five years from BASt.de. The data is provided as zip-archives per year for Autobahnen and Bundesstraßen; each of which contains folders with 12 raw-data files and one corresponding meta-data file explaining the data. The data is organized in .csv-files. The data is sampled per hour.
As we only consider data for Schleswig-Holstein, we aggregated each data file to only contain rows with information corresponding to Schleswig-Holstein.
To make sure the data is consistant, we also checked if the ID for Schleswig-Holstein in the meta-data stayed consistent over all datasets.
This was done using the script in [this Jupyter Notebook](Code/BASt_Data_Aggregation/BAStDataSHAggregation.ipynb).

-----

## Information for the selection of the traffic measuring points / counting stations ("Dauerzählstellen")

To get a first idea of where the counting stations in and around Kiel are located, we exported one examplary Meta-Data file from BASt to Google MyMaps
and identified "the most relevant" measuring points by eye and feeling.

![](measuring_points_map_kiel.png)

Because this is no scientific way of selecting the measuring points providing data the whole project relies on, 
we created a coordinate frame for the Kiel region (+ extra radius for surrounding area) and identiefied the traffic measuring points that are 
located within this frame.

This coordinate frame has the following coordinates:
- min_latitude: 54.068086300000004
- max_latidude: 54.61594389999999

- min_longitude: 9.8472391
- max_longitude: 10.404307


The counting stations within this frame then got analyized by us in terms of usefullness for our project.
We selected the following stations as relevant:
- **1104: "Rumohr" on the A215** -> a main route when traveling the North-South-Axis; e.g. it is the direct linkage to the A7 from Kiel.
- **1111: "Kiel-Holtenau I" on the B503** -> counting station on the Holtenauer bridge to count vehicles to the North of Kiel. This station is before a road branches off to Holstein Stadion.
- **1112: "Kiel-Holtenau 2" on the B503** -> counting station next to station #1111 but after the branch to Holstein Stadion. We selected this station as well to have the opportunity to answer questions where the information might be helpful, how many vehicles took the branch.
- **1116: "Gettorf (Wulfshagen)" on the B76** -> the only counting station covering the vehicle counts for the North-West-Axis from Kiel.
- **1135: "Raisdorf I" on the B76** -> the closest of the counting stations in the East of Kiel; and one that got used over all five years of the observation period.
- **1156: "AS Wankendorf (Stolpe)" on the A21** -> counting station covering the traffic coming from the East via the Autobahn (e.g. trips from Berlin).
- **1158: "Kiel/Schönkirchen" on the B502** -> only counting station in the North-East of Kiel.
- **1162: "Melsdorf" on the A210** -> counting vehicles on the West-Axis of Kiel. 
- **1194: "Kiel-West" on the A215** -> counting station directly in front of Kiel, where the A215 and A210 merge together.




-----

## Using Anaconda

### Copying an existing Environment

```powershell
conda create --name <envname> --file requirements.txt
python -m ipykernel install --user --name <kernelname> --display-name "<displayname>"
```

### Creating a new Environment

```powershell
conda create --name <name> python=3.11
conda activate <name>
conda install numpy
conda install jupyter
conda install matplotlib
conda install polars
conda install ipykernel
conda install requests-cache
conda install pyproj
pip install openmeteo-requests
pip install retry-requests
python -m ipykernel install --user --name <kernelname> --display-name "<displayname>"
conda list --export > requirements.txt
```

### For updating an Environment to a new requirements.txt

```powershell
conda install --name <envname> --file requirements.txt
```



*to be continued*
