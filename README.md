# CTA Crime Analysis

## Project Overview
This project analyzes how crime exposure near Chicago CTA L stations relates to ridership patterns over time 2022-onwards. Using station-level ridership data, geocoded crime incidents, and spatial joins, we produce static visualizations to inform how the City of Chicago and CTA might better allocate transit security resources to improve transit utilization.

The external data folder for final project is [here](https://www.dropbox.com/scl/fo/sq360chzws1wlj3o2qyop/AATdS7xIi-0s0bwWrSTLXgI?rlkey=xgfa2m0xq61bxsp7ogfxhpiu0&st=jy69syqm&dl=0)

```bash
app.py - Main Streamlit application
filters.py - Filter components (years, lines, crime types)
plots.py - Visualization functions
analysis.py - Statistical analysis
data_processor.py - Data loading and cleaning
stations.py - Station/line data management
```

## Setup - UPDATE EVERYTHING 

```bash
conda env create -f environment.yml
conda activate fire_analysis
```

## Project Structure

```
draft-final-project/
  code/
    
  data/
    raw-data/           # Raw data files
      CTA_Ridership_L_Station_Entries_Daily_Totals_2022-2026.csv          # Ridership data 2022-2026
      Cpd_Crime_Incidents  #Chicago Crime Data
      CTA_RailStations/
        CTA_RailStations.cpg
        CTA_RailStations.dbf
        CTA_RailStations.prj
        CTA_RailStations.sbn
        CTA_RailStations.sbx
        CTA_RailStations.shp
        CTA_RailStations.shp.xml
        CTA_RailStations.shx  
    derived-data/
        
  code/
    preprocessing.py    # Filters Ridership, L' station locations, and Crime data
    plot_crime.py       # Plots crime perimeters
    config.py           # Data configurations
    filters.py          # filtering multi-select year, L-line, crime type picker
    visualizations.py   # spatial, correlations, crime breakdown visualization plots
    app.py              # Main Streamlit application
```

## Usage

1. Run preprocessing to filter data:
   ```bash
   python code/preprocessing.py
   ```

2. Generate the crime perimeter plot:
   ```bash
   python code/plot_crime.py
   ```
