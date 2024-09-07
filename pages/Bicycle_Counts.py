import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(page_title="Bicycle Counts")
st.title("Bicycle Counts")

@st.cache_data
def load_csv(file_path):
    data = pd.read_csv(file_path)
    return data

@st.cache_data
def load_bicycle_counts_data():
    data = load_csv("portland-bicycle-counts-public-data.csv")
    return data

@st.cache_data
def clean_bicycle_counts_data(data):
    # For every column in the data, strip leading and trailing whitespace.
    data = data.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    # For every column in the data, replace "-" with None
    data = data.replace("-", None)
    # Filter out any rows where the latitude or longitude is None
    # For the Lat-Long column, split the column into two separate columns.
    data[['latitude', 'longitude']] = data['Lat-Long'].str.split(', ', expand=True)
    # For the Latitude and Longitude columns, convert the columns to floats.
    data['latitude'] = data['latitude'].astype(float)
    data['longitude'] = data['longitude'].astype(float)
    # Filter out any rows where the latitude or longitude is None
    data = data[data['latitude'].notna() & data['longitude'].notna()]
    # Add a column for 2020 and 2021 with a value of 0
    data['2020'] = None
    data['2021'] = None
    # Convert all year columns to integers
    for year in range(2000, 2024):
        data[str(year)] = data[str(year)].str.replace(',', '')
        data[str(year)] = data[str(year)].fillna(0)
        data[str(year)] = data[str(year)].astype(int)
    return data

if 'year' not in st.session_state:
    st.session_state['year'] = 2023

# Read the data from portland-bicycle-counts-public-data.csv
data = load_bicycle_counts_data()
data = clean_bicycle_counts_data(data)

# Create a sidebar with a slider to select the year
year = st.sidebar.slider("Year", 2000, 2023, st.session_state.year)
year_column = str(year)

# Iterate over all years and find the maximum value
max_value = 0
for year in range(2000, 2024):
    max_value = max(max_value, data[str(year)].max())

# Normalize the values for the selected year to use as sizes
data['size'] = data[year_column] / max_value * 125  # Scale to 0-125 range

# Create a map of the data
st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=pdk.ViewState(
        latitude=data['latitude'].mean(),
        longitude=data['longitude'].mean(),
        zoom=11,
        pitch=0,
    ),
    layers=[
        pdk.Layer(
            'ScatterplotLayer',
            data=data,
            get_position='[longitude, latitude]',
            get_color=[0, 128, 0, 160],  # Changed to green
            get_radius='size',
            radius_scale=6,
            radius_min_pixels=0,
            radius_max_pixels=125,
            pickable=True,
            auto_highlight=True,
        ),
    ],
    tooltip={
        "html": "<b>Location:</b> {Name}<br><b>Count:</b> {" + year_column + "}",
        "style": {"backgroundColor": "steelblue", "color": "white"}
    }
))

st.caption("Data from [Portland Open Data](https://data.portlandoregon.gov/dataset/bicycle-counts).")

with st.popover("View Data"):
    st.write(data)
