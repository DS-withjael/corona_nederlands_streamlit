import streamlit as st
import datetime as dt
import pandas as pd
import json
import folium
from streamlit_folium import folium_static
st.set_page_config(layout="wide")

"# Netherlands Corona Data"

##################### LOAD AND PARSE DATA ########################
geo_json_path = "data/raw_data/shapefiles/nl.geojson"
corona_NL_data = pd.read_csv("data/raw_data/corona/nl_corona.csv", sep="\t")

with open("data/raw_data/metadata/nl_metadata.json", "r") as f:
    country_metadata = json.load(f)

# country metadata parsing
region_map = {
    int(country_metadata["country_metadata"][i]["covid_region_code"]): 
    country_metadata["country_metadata"][i]["iso3166-2_code"] for i in range(len(country_metadata["country_metadata"]))
    }

population_map = {
    country_metadata["country_metadata"][i]["iso3166-2_code"]: 
    country_metadata["country_metadata"][i]["population"] for i in range(len(country_metadata["country_metadata"]))
    }

# corona data adding region name and population column
corona_NL_data["region"] = corona_NL_data["region_code"].map(region_map)
corona_NL_data["population"] = corona_NL_data["region"].map(population_map)
corona_NL_data["netto_cases_per_capita"] = corona_NL_data["confirmed_addition"] / corona_NL_data["population"]

################## SLIDER #########################################
with st.container(): # SLIDER CONTAINER
    format = 'YYYY-MM-DD'  # format output
    start_date = dt.date(year=2020,month=2,day=27)  #  I need some range in the past
    end_date = dt.date(year=2021, month=2, day=27)
    max_days = end_date-start_date

    slider = str(st.slider('Slide through the corona pandemic in the Netherlands:', min_value=start_date, value=(start_date/end_date) ,max_value=end_date, format=format))

################## STREAMLIT LAYOUT ####################################

with st.container(): # MAIN CONTAINER

    col1, col2, col3 = st.columns(3)

    ################### st.radio (1. column) #####################
    with col1:

        st.write("Which data you would like to see?")
        select_data = st.radio("",(
            'Total Cases Per Capita', 
            'Total Cases', 
            'Total Hospitalized',
            'Total Hospitalized Cumulative',
            'Total Dead',
            'Total Cumulative Dead',
            'Total Confirmed Cumulative Dead'
            ))
        data_dict = {
            "Total Cases Per Capita" : 'netto_cases_per_capita', 
            "Total Cases" : 'confirmed_addition', 
            "Total Hospitalized" : 'hospitalized_addition',
            "Total Hospitalized Cumulative" : 'hospitalized_cumulative',
            "Total Dead" : 'deceased_addition',
            "Total Cumulative Dead" : 'deceased_cumulative',
            "Total Confirmed Cumulative Dead" : 'confirmed_cumulative'
            }

    ################## MAP VISUALIZING ##############################
    with col2:
        # quick date mask
        date_mask = corona_NL_data["date"] == slider

        corona_map = folium.Map(location = [52, 6], zoom_start = 7, crs = "EPSG3857")

        def visualize(category, legend):
            folium.Choropleth(
                geo_data= geo_json_path,
                name = category,
                data = corona_NL_data[date_mask],
                columns = ["region", category],
                key_on = "properties.iso_3166_2",
                fill_color = "OrRd",
                fill_opacity= 0.7,
                line_opacity= 0.2,
                legend_name= legend,
                nan_fill_color = "Grey"
            ).add_to(corona_map)

            folium_static(corona_map)

        visualize(data_dict[select_data], select_data)

        st.write("N/A Values are coloured in grey.")
