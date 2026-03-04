import sys
import streamlit as st
import pandas as pd
import geopandas as gpd
from pathlib import Path
import altair as alt

from visualizations import map_deck, top_stations_fig, crime_type_fig, correlation_scatter_fig, dual_axis_trend_fig
from analysis import get_station_correlations

#Paths
user_path = Path(__file__).parent.resolve()
raw_data_path = user_path.parent/ "data" / "raw-data" 
derived_data_path = user_path.parent/ "data" / "derived-data"

#Load Data
derived_crime = gpd.read_file(derived_data_path / "derived_crime.shp")

#File Identifiers
RIDERSHIP_CSV  = "CTA_Ridership_L_Station_Entries_Daily_Totals_2022-2026.csv"
DERIVED_SHP    = "derived_crime.shp"

#CRS
SOURCE_CRS = "EPSG:3435"   # Illinois State Plane East (feet)
TARGET_CRS = "EPSG:4326"   # WGS-84

# Shapefile column names 
COL_STATION      = "stationnam"  
COL_LONGNAME     = "LONGNAME_x"  
COL_LINES        = "LINES_x"     
COL_YEAR         = "Year_x"      
COL_MONTH        = "Month"
COL_RIDES        = "rides"
COL_CRIME_ID     = "ID"
COL_PRIMARY_TYPE = "Primary Ty"  

LINE_SUFFIXES = [
    " Line", " (O'Hare)", " (Congress)", " (Lake)", " (Englewood)", " (Express)"
]

LINE_COLORS = {
    "Red":    "#C60C30",
    "Blue":   "#00A1DE",
    "Brown":  "#62361B",
    "Green":  "#009B3A",
    "Orange": "#F9461C",
    "Pink":   "#E27EA6",
    "Purple": "#522398",
    "Yellow": "#F9E300",
}

def load_violent_classify(df):
    df = df[df[COL_CRIME_ID].notna()]
    violent_types = [
        'HOMICIDE', 
        'CRIMINAL SEXUAL ASSAULT', 
        'SEX OFFENSE', 
        'ROBBERY', 
        'ASSAULT', 
        'BATTERY', 
        'KIDNAPPING'
    ]
    df['Crime_Category'] = df['Primary Ty'].apply(
        lambda x: 'Violent' if str(x).upper() in violent_types else 'Non-Violent'
    )
    return df

def year_filter(df,start_yr = 2022,end_yr = 2025):
    df = df[df["Year_x"] >= start_yr]
    df = df[df["Year_x"] <= end_yr]
    return df

def crime_filter(df,crime_type = "All"):
    if crime_type == "All":
        return df
    elif crime_type == "Violent":
        df = df[df['Crime_Category']=="Violent"]
        return df
    elif crime_type == "Non-Violent":
        df = df[df['Crime_Category']=="Non-Violent"]
        return df
    else:
        df = df[df[COL_PRIMARY_TYPE] == crime_type.upper()]
        return df

@st.cache_data
def aggregator(crime_type = "All",start_yr = 2022,end_yr = 2025):
    crime_df = load_violent_classify(derived_crime)
    crime_df = crime_filter(crime_df,crime_type)
    crime_df = year_filter(crime_df,start_yr,end_yr)
    
    ridership_df = year_filter(derived_crime,start_yr,end_yr)

    rides_monthly = (
    ridership_df.drop_duplicates(subset=[COL_STATION, "date"])
    [[COL_STATION, COL_LONGNAME, COL_YEAR, COL_MONTH, COL_RIDES]]
    .groupby([COL_STATION, COL_LONGNAME, COL_YEAR, COL_MONTH])[COL_RIDES]
    .sum()
    .reset_index()
    )
    
    crime_monthly = (
    crime_df
    .groupby([COL_STATION, COL_YEAR, COL_MONTH])
    .size()
    .reset_index(name="crime_count")
    )

    monthly = rides_monthly.merge(crime_monthly, on=[COL_STATION, COL_YEAR, COL_MONTH], how="left")
    monthly["crime_count"] = monthly["crime_count"].fillna(0)
    monthly.rename(columns={
        COL_LONGNAME: "stationname_mapped",
        COL_YEAR:     "year",
        COL_MONTH:    "month",
    }, inplace=True)

    monthly = monthly.groupby("stationname_mapped").agg(crime_count=("crime_count", "sum"), rides=("rides", "sum")).reset_index()

    return monthly

final_data = aggregator(crime_type="Violent",start_yr=2025)

def make_chart(final_data):
    Chart = alt.Chart(final_data).mark_point(filled=True).transform_calculate(
        crime_per_100000 = "datum.crime_count/(datum.rides/100000)"
    ).encode(
        alt.X("crime_per_100000:Q", title="Crime incidents per 100,000 riders"),
        alt.Y("rides:Q", title="Total Rides"),
        tooltip=["stationname_mapped:N", 
                alt.Tooltip("crime_per_100000:Q", format=".0f"),
                "rides:Q"]
        )
    return Chart

# --- STREAMLIT USER INTERFACE ---

st.set_page_config(page_title="CTA Crime & Ridership Dashboard", layout="wide")

st.title("🚇 CTA Station Analysis: Crime vs. Ridership")
st.markdown("""
This dashboard explores the relationship between CTA 'L' station ridership and reported crime incidents.
Select your filters in the sidebar to update the visualization.
""")

# 1. Sidebar Filters
st.sidebar.header("Filter Options")

# Year Range Selector
# Note: Using your default ranges 2022-2025
year_range = st.sidebar.slider(
    "Select Year Range",
    min_value=2022,
    max_value=2025,
    value=(2022, 2025)
)
start_yr, end_yr = year_range

# Crime Type Selector
# We'll include the custom categories and some common primary types
valid_crimes = sorted(derived_crime[COL_PRIMARY_TYPE].dropna().unique().tolist())

crime_options = ["All", "Violent", "Non-Violent"] + valid_crimes
selected_crime = st.sidebar.selectbox("Select Crime Category/Type", options=crime_options)

# 2. Data Processing
# Calling your existing aggregator function with user inputs
with st.spinner("Aggregating data..."):
    filtered_data = aggregator(
        crime_type=selected_crime, 
        start_yr=start_yr, 
        end_yr=end_yr
    )

# 3. Main Dashboard Layout
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader(f"Analysis: {selected_crime} Crimes ({start_yr}-{end_yr})")
    # Calling your existing make_chart function
    chart = make_chart(filtered_data)
    st.altair_chart(chart, use_container_width=True)

with col2:
    st.subheader("Summary Metrics")
    total_rides = filtered_data['rides'].sum()
    total_crimes = filtered_data['crime_count'].sum()
    
    st.metric("Total Ridership", f"{total_rides:,}")
    st.metric("Total Incidents", f"{int(total_crimes):,}")
    
    # Simple calculation for context
    avg_rate = (total_crimes / (total_rides / 100000)) if total_rides > 0 else 0
    st.metric("Avg Crime Rate", f"{avg_rate:.2f}", help="Incidents per 100k riders")

# 4. Data Preview
with st.expander("View Raw Aggregated Data"):
    st.dataframe(filtered_data.sort_values(by="crime_count", ascending=False), use_container_width=True)

derived_crime[COL_PRIMARY_TYPE].unique()


    