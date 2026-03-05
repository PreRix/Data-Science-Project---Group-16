# Data-Science-Project Group-16

## Introduction

### Who we are

We are a group of four students from the Christian-Albrechts-University to Kiel (CAU) studying computer science and business science.
This project is assigned to the Data-Science-Project which is taking place between the fifth and sixth semester (Feb 23 - Mar 20, 2026).

We had to find a topic which is interesting to us and perform data science on it:
from the collection of raw, non-pre-processed data, through data cleansing and analyzing, to the creation of visualizations for our findings.
Those should then be accessible on a self-programmed website.

*All of us are native-german speakers, so please excuse the maybe non-perfect English :)*

### The Topic
The topic of our project is as follows: The Personal Traffic around Kiel in the past five years *(2021 to 2025)*.

We developed nine plus one bonus research questions that we want to answer with this project [Research Questions](Research-Questions.pdf).

### The Data 
The data we used is freely available. The sources are the following:
- BASt datasets for the vehicle counts on German Autobahnen (motorways) and Bundesstraßen (federal highways):
  https://www.bast.de/DE/Publikationen/Daten/Verkehrstechnik/DZ-Richtung.html?nn=427910
  

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
conda install numpy pandas requests-cache
pip install openmeteo-requests retry-requests
python -m ipykernel install --user --name <kernelname> --display-name "<displayname>"
conda list --export > requirements.txt
```

### For using openmeteo

```powershell
conda install numpy pandas requests-cache
pip install openmeteo-requests retry-requests
```

#### For updating an Environment to a new requirements.txt

```powershell
conda install --name <envname> --file requirements.txt
```

## Information for the selection of the traffic counting stations (so called "Dauermessstellen")

To get a first idea of where the counting stations in and around Kiel are located, we exported one examplary Meta-Data file to Google MyMaps
and identified "the most relevant" counting stations by eye and feeling. 
Because this is no scientific way of selecting the stations providing data the whole project relies on, 
we created a coordinate frame for the Kiel region (+ extra radius for surrounding area) and identiefied the traffic counting stations that are 
located within this frame.

*to be continued*
