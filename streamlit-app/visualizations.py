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

#Load Data
derived_crime = gpd.read_file(derived_data_path / "derived_crime.shp")
derived_station = gpd.read_file(derived_data_path / "derived_stations.shp")
gdf_lines = gpd.read_file(raw_data_path / "CTA_RailLines/CTA_RailLines.shp")

derived_crime

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
        

a = top_stations_fig(derived_crime)

a

# Top 10 crime types near CTA stations — companion to top_stations_fig.
def crime_type_fig(df):
    top = (
        df.groupby("Primary Ty")
        .size()
        .sort_values(ascending=False)
        .head(10)
        .reset_index(name = "crime_count")
    )
    return (
        alt.Chart(top)
        .mark_bar(color="#522398")
        .encode(
            alt.X("crime_count:Q", title="Total Count"),
            alt.Y("Primary Ty:N", title="Crime Type", sort="-x"),
        )
        .properties(
            title="Top 10 Crime Types Near CTA Stations",
            width=500,
            height=320,
        )
    )

t = crime_type_fig(derived_crime)

t

