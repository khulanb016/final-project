import sys
import streamlit as st
import pandas as pd
import geopandas as gpd
from pathlib import Path

from visualizations import map_deck, top_stations_fig, crime_type_fig, correlation_scatter_fig, dual_axis_trend_fig
from analysis import get_station_correlations

#Paths
RAW     = Path("data/raw-data")
DERIVED = Path("data/derived-data")

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

def extract_primary_line(line_str):
    if pd.isna(line_str):
        return "Unknown"
    first = line_str.split(",")[0].strip()
    for suffix in LINE_SUFFIXES:
        first = first.replace(suffix, "")
    return first.strip()


#Dashboard Setup
st.set_page_config(page_title="CTA Crime & Ridership", layout="wide")
st.title("CTA L Ridership vs. Crime: A Station-Level Analysis")
st.divider()

# Data Loading with caching
@st.cache_data
def load_ridership():
    df = pd.read_csv(RAW / RIDERSHIP_CSV)
    df[COL_RIDES] = df[COL_RIDES].str.replace(",", "").astype(int)
    df["date"]    = pd.to_datetime(df["date"])
    df["year"]    = df["date"].dt.year
    df["month"]   = df["date"].dt.month
    return df


@st.cache_data
def load_derived():
    path = DERIVED / DERIVED_SHP
    if not path.exists():
        return None, None, None

    gdf = gpd.read_file(path)
    gdf["primary_line"] = gdf[COL_LINES].apply(extract_primary_line)

    # Monthly ridership — one row per station/month
    rides_monthly = (
        gdf.drop_duplicates(subset=[COL_STATION, "date"])
        [[COL_STATION, COL_LONGNAME, "primary_line", COL_YEAR, COL_MONTH, COL_RIDES]]
        .groupby([COL_STATION, COL_LONGNAME, "primary_line", COL_YEAR, COL_MONTH])[COL_RIDES]
        .sum()
        .reset_index()
    )

    # Monthly crime count per station
    crime_monthly = (
        gdf[gdf[COL_CRIME_ID].notna()]
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

    # Crime by type (restore full readable column name)
    crime_types = (
        gdf[gdf[COL_CRIME_ID].notna()]
        .rename(columns={COL_PRIMARY_TYPE: "Primary Type"})
        .assign(crime_count=1)
        [["Primary Type", "crime_count"]]
    )

    # Station map data
    stations = (
        gdf.drop_duplicates(subset=COL_STATION)
        [[COL_STATION, COL_LONGNAME, "primary_line", "geometry"]]
        .copy()
    )
    stations = stations.set_crs(SOURCE_CRS).to_crs(TARGET_CRS)
    stations["lon"] = stations.geometry.x
    stations["lat"] = stations.geometry.y
    stations.rename(columns={COL_LONGNAME: "LONGNAME"}, inplace=True)

    return monthly, crime_types, stations

#Load Data
df_rides = load_ridership()
monthly, crime_types, stations = load_derived()

#Sidebar filters
st.sidebar.header("Filters")
years = sorted(df_rides["year"].unique())
selected_years = st.sidebar.multiselect("Year", years, default=years)

df_rides = df_rides[df_rides["year"].isin(selected_years)]
if monthly is not None:
    monthly = monthly[monthly["year"].isin(selected_years)]

    lines = sorted(monthly["primary_line"].unique())
    selected_lines = st.sidebar.multiselect("Line", lines, default=lines)
    monthly = monthly[monthly["primary_line"].isin(selected_lines)]
    if stations is not None:
        stations = stations[stations["primary_line"].isin(selected_lines)]

    crime_type_options = sorted(crime_types["Primary Type"].unique())
    selected_crime_types = st.sidebar.multiselect("Crime Type", crime_type_options, default=crime_type_options)
    crime_types = crime_types[crime_types["Primary Type"].isin(selected_crime_types)]

#Key Numerical Data
k1, k2, k3 = st.columns(3)
k1.metric("Total Rides", f"{df_rides[COL_RIDES].sum():,.0f}")
k2.metric("Stations Tracked", df_rides["stationname"].nunique())
if monthly is not None:
    k3.metric("Total Crime Incidents", f"{int(monthly['crime_count'].sum()):,}")
else:
    k3.warning("Run preprocessing.py to load crime data")

st.divider()

#Map Visualization
if stations is not None:
    st.subheader("Station Map: Colored by Line")
    st.pydeck_chart(map_deck(stations, LINE_COLORS))
    st.divider()

#Crime Viusalizations and Correlations
if monthly is not None:

    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("Top 10 Stations by Nearby Crime")
        st.altair_chart(top_stations_fig(monthly), use_container_width='stretch)
    with col_right:
        st.subheader("Top 10 Crime Types Near Stations")
        st.altair_chart(crime_type_fig(crime_types), use_container_width='stretch)

    st.divider()

    st.subheader("Total Crime vs. Total Ridership by Station")
    st.altair_chart(correlation_scatter_fig(monthly, LINE_COLORS), use_container_width='stretch)

    st.divider()

    st.subheader("Crime & Ridership Over Time")
    st.altair_chart(dual_axis_trend_fig(monthly), use_container_width='stretch)

    st.divider()

    st.subheader("Correlation Analysis")
    st.markdown("**Per-Station Correlations**")
    corr_df = get_station_correlations(monthly)
    st.dataframe(corr_df, use_container_width='stretch, height=350)

else:
    st.info("Run `python streamlit-app/preprocessing.py` first to enable crime analysis.")
