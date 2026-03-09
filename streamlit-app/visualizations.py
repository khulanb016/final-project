import altair as alt
import pandas as pd
import pydeck as pdk
import geopandas as gpd
from pathlib import Path
import webbrowser

#Paths
user_path = Path(__file__).parent.resolve()
raw_data_path = user_path.parent/ "data" / "raw-data"
derived_data_path = user_path.parent/ "data" / "derived-data"

# Shapefile column names 
COL_STATION      = "stationnam"  
COL_LONGNAME     = "LONGNAME_x"  
COL_LINES        = "LINES_x"     
COL_YEAR         = "Year_x"      
COL_MONTH        = "Month"
COL_RIDES        = "rides"
COL_CRIME_ID     = "ID"
COL_PRIMARY_TYPE = "Primary Ty"  

# --- Example Usage ---
# line_colors = {"Red": "#c60c30", "Blue": "#00a1de", "Brown": "#62361b", ...}
# create_cta_browser_map(your_stations_df, "CTA_RailLines.shp", line_colors)

#Load Data
derived_crime = gpd.read_file(derived_data_path / "derived_crime.shp")
derived_station = gpd.read_file(derived_data_path / "derived_stations.shp")
gdf_lines = gpd.read_file(raw_data_path / "CTA_RailLines/CTA_RailLines.shp")

# Shapefile column names 
COL_STATION      = "stationnam"  
COL_LONGNAME     = "LONGNAME_x"  
COL_LINES        = "LINES_x"     
COL_YEAR         = "Year_x"      
COL_MONTH        = "Month"
COL_RIDES        = "rides"
COL_CRIME_ID     = "ID"
COL_PRIMARY_TYPE = "Primary Ty"  

# --- Example Usage ---
# line_colors = {"Red": "#c60c30", "Blue": "#00a1de", "Brown": "#62361b", ...}
# create_cta_browser_map(your_stations_df, "CTA_RailLines.shp", line_colors)

# Top 10 stations by crime rate
def top_stations_fig(df):
    category_map = {
        # Violent Crimes
        'BATTERY': 'VIOLENT', 'ASSAULT': 'VIOLENT', 'HOMICIDE': 'VIOLENT', 
        'CRIMINAL SEXUAL ASSAULT': 'VIOLENT', 'SEX OFFENSE': 'VIOLENT', 
        'STALKING': 'VIOLENT', 'KIDNAPPING': 'VIOLENT', 
        'OFFENSE INVOLVING CHILDREN': 'VIOLENT', 'INTIMIDATION': 'VIOLENT',
        
        # Property Crimes
        'THEFT': 'PROPERTY', 'MOTOR VEHICLE THEFT': 'PROPERTY', 
        'BURGLARY': 'PROPERTY', 'ROBBERY': 'PROPERTY', 
        'CRIMINAL DAMAGE': 'PROPERTY', 'ARSON': 'PROPERTY', 
        'DECEPTIVE PRACTICE': 'PROPERTY',
        
        # Drug & Vice
        'NARCOTICS': 'DRUG_VICE', 'OTHER NARCOTIC VIOLATION': 'DRUG_VICE', 
        'LIQUOR LAW VIOLATION': 'DRUG_VICE', 'GAMBLING': 'DRUG_VICE', 
        'PROSTITUTION': 'DRUG_VICE',
        
        # Public Order & Regulatory
        'WEAPONS VIOLATION': 'PUBLIC_ORDER', 'CONCEALED CARRY LICENSE VIOLATION': 'PUBLIC_ORDER', 
        'PUBLIC_ORDER VIOLATION': 'PUBLIC_ORDER', 'INTERFERENCE WITH PUBLIC OFFICER': 'PUBLIC_ORDER', 
        'CRIMINAL TRESPASS': 'PUBLIC_ORDER', 'PUBLIC INDECENCY': 'PUBLIC_ORDER', 
        'OBSCENITY': 'PUBLIC_ORDER', 'PUBLIC PEACE VIOLATION': 'PUBLIC_ORDER',
        
        # Other
        'OTHER OFFENSE': 'OTHER', 'HUMAN TRAFFICKING': 'OTHER', 
        'NON-CRIMINAL': 'OTHER', None: 'OTHER'
    }
    # Create the new column
    df['crime_category'] = df[COL_PRIMARY_TYPE].map(category_map)

    df_counts = df.groupby([COL_STATION, 'crime_category']).size().reset_index(name='crime_count')

    # 2. Identify the Top 10 Stations based on total volume
    top_10_list = df_counts.groupby(COL_STATION)['crime_count'].sum().nlargest(10).index
    df_final = df_counts[df_counts[COL_STATION].isin(top_10_list)]

    return(alt.Chart(df_final).mark_bar().encode(
        y=alt.Y('stationnam:N', 
                title='Top 10 highest crime stations', 
                sort='-x'), # Sorts highest volume to lowest
        x=alt.X('crime_count:Q', 
                title='Number of incidents'),
        color=alt.Color('crime_category:N', 
                        title='Crime type', 
                        scale=alt.Scale(scheme='category10'),
                        legend=alt.Legend(
            labelExpr=
            "datum.label == 'VIOLENT' ? 'Violent' : "
            "datum.label == 'OTHER' ? 'Other' : "
            "datum.label == 'PUBLIC_ORDER' ? 'Public order' : "
            "datum.label == 'PROPERTY' ? 'Property and Theft' : "
            "datum.label == 'DRUG_VICE' ? 'Drugs and Vices' : datum.label"
            )
    )).properties(
        width=600,
        height=400,
        title='Top 10 Stations by number of crimes'
    ))
top_stations = top_stations_fig(derived_crime)
top_stations

# Top 10 crime types near CTA stations — companion to top_stations_fig.
def crime_type_fig(df):
    top = (
        df.groupby("Primary Ty")
        .size()
        .sort_values(ascending=False)
        .head(10)
        .reset_index(name = "crime_count")
    )
    top["Crime Type"] = top["Primary Ty"].str.title()
    return (
        alt.Chart(top)
        .mark_bar(color="#522398")
        .encode(
            alt.X("crime_count:Q", title="Total Count"),
            alt.Y("Crime Type:N", title="Crime Type", sort="-x"),
        )
        .properties(
            title="Top 10 Crime Types Near CTA Stations",
            width=500,
            height=320,
        )
    )
crime_type = crime_type_fig(derived_crime)
crime_type

def heatmap(df):
    df = df.dropna(subset = "Time")

    df["d_of_week"] = pd.to_datetime(df["date"]).dt.day_name()
    df["hour"] = pd.to_datetime(df['Time'], format='%H:%M:%S').dt.hour
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    heatmap_data = df.groupby(['d_of_week', 'hour']).size().reset_index(name='crime_count')

    chart = alt.Chart(heatmap_data).mark_rect().encode(
    x=alt.X('d_of_week:O', 
            sort=day_order, 
            title='Day of the Week'),
    y=alt.Y('hour:O', 
            title='Hour of the Day (24h)'),
    color=alt.Color('crime_count:Q', 
                    scale=alt.Scale(scheme='oranges'), 
                    title='Number of Crimes'),
    ).properties(
    title='Crime Frequency by Day and Hour',
    width=600,
    height=400
    ).configure_axis(
    labelFontSize=12,
    titleFontSize=14
    )

    return chart
heatmap_crime = heatmap(derived_crime)
heatmap_crime
    