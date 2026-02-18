# CTA Crime Analysis

## Project Overview
This project analyzes how crime exposure near Chicago CTA L stations relates to ridership patterns over time 2024-2025. Using station-level ridership data, geocoded crime incidents, and spatial joins, we produce static visualizations to inform how the City of Chicago and CTA might better allocate transit security resources to improve transit utilization.

This is a descriptive, non-causal analysis focused on visualization and policy interpretation.

## Setup - UPDATE EVERYTHING 

```bash
conda env create -f environment.yml
conda activate fire_analysis
```

## Project Structure

```
data/
  raw-data/           # Raw data files
    fire.csv          # Historical fire perimeter data
    canadian_cpi.csv  # Canadian Consumer Price Index data
  derived-data/       # Filtered data and output plots
    fire_filtered.gpkg  # Fire data filtered to post-2015
    cpi_filtered.csv    # CPI data filtered to 2020 onwards
code/
  preprocessing.py    # Filters fire and CPI data
  plot_fires.py       # Plots fire perimeters
```

## Usage

1. Run preprocessing to filter data:
   ```bash
   python code/preprocessing.py
   ```

2. Generate the fire perimeter plot:
   ```bash
   python code/plot_fires.py
   ```
