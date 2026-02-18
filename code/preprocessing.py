#Import relevant packages and setting PATH
import geopandas as gpd
import pandas as pd
PATH = "/Users/kunsh/Desktop/Stats/HW/Kunsh_Git"

#Loading all datasets
df_crime = pd.read_csv(PATH + "/final-project/data/raw-data/Crimes_-_2001_to_Present_20260218.csv")
df_ridership = pd.read_csv(PATH + "/final-project/data/raw-data/Crimes_-_2001_to_Present_20260218.csv")
gdf_station = gpd.read_file(PATH + "/final-project/data/raw-data/CTA_RailStations/CTA_RailStations.shp")
gdf_lines = gpd.read_file(PATH + "/final-project/data/raw-data/CTA_RailLines/CTA_RailLines.shp")

