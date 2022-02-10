import streamlit as st
import pandas as pd
from streamlit_folium import folium_static
import folium, json

st.set_page_config(layout="wide")


"# Netherlands Corona Data"

# load data
geo_json_path = "data/raw_data/shapefiles/nl.geojson"
corona_NL_data = pd.read_csv("data/raw_data/corona/nl_corona.csv", sep="\t").dropna()

with open("data/raw_data/metadata/nl_metadata.json", "r") as f:
    country_metadata = json.load(f)

# create data stuff
region_map = {int(country_metadata["country_metadata"][i]["covid_region_code"]): country_metadata["country_metadata"][i]["iso3166-2_code"] for i in range(len(country_metadata["country_metadata"]))}
corona_NL_data["region"] = corona_NL_data["region_code"].map(region_map)

corona_NL_data_region = corona_NL_data.groupby("region")["confirmed_addition"].sum().reset_index()
population_map = {country_metadata["country_metadata"][i]["iso3166-2_code"]: country_metadata["country_metadata"][i]["population"] for i in range(len(country_metadata["country_metadata"]))}

corona_NL_data_region["population"] = corona_NL_data_region["region"].map(population_map)
corona_NL_data_region["netto_cases_per_capita"] = corona_NL_data_region["confirmed_addition"] / corona_NL_data_region["population"]

# map
capita_corona_m = folium.Map(location = [52, 6], zoom_start = 7, crs = "EPSG3857")

# sidebar
select_data = st.sidebar.radio("What data do you want to see?",('Total Cases Per Capita', 'Total Cases'))
data_dict = {"Total Cases Per Capita" : 'netto_cases_per_capita', "Total Cases" : 'confirmed_addition'}

def show_maps(category, legend):
    folium.Choropleth(
        geo_data= geo_json_path,
        name = category,
        data = corona_NL_data_region,
        columns = ["region", category],
        key_on = "properties.iso_3166_2",
        fill_color = "OrRd",
        fill_opacity= 0.7,
        line_opacity= 0.2,
        legend_name= legend,
    ).add_to(capita_corona_m)

    folium.LayerControl().add_to(capita_corona_m)
    folium_static(capita_corona_m)

show_maps(data_dict[select_data], select_data)

