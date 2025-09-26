"""Script to display the live data on the Streamlit dashboard."""
import streamlit as st
import altair as alt

from charts import (
    create_temp_chart,
    create_soil_moisture_chart,
    create_soil_moisture_heatmap_chart
)
from data import (
    load_all_plants,
    load_latest_plant_recordings,
    live_heatmap_data,
    get_low_soil_moisture_plants,
    get_low_temperature_plants
)

latest_plant_recordings = load_latest_plant_recordings()
all_plants = load_all_plants(latest_plant_recordings)

st.subheader("Live Plant Data")

st.write("")
st.write("")

if get_low_soil_moisture_plants().empty:
    st.write(
        f":red[CRITICAL LOW MOISTURE:] No plants are below 20% moisture")
else:
    low_moisture_plants = get_low_soil_moisture_plants()
    min_moisture = low_moisture_plants["soil_moisture"].min()
    lowest_moisture_plant = low_moisture_plants[low_moisture_plants["soil_moisture"]
                                                == min_moisture]["plant_name"]
    st.write(
        f":red[CRITICAL LOW MOISTURE:] {lowest_moisture_plant.values[0]} ({min_moisture}%)")

if get_low_temperature_plants().empty:
    st.write(
        f":red[CRITICAL LOW TEMPERATURE:] No plants are at or below 5°C")
else:
    low_temp_plants = get_low_temperature_plants()
    min_temp = low_temp_plants["temperature"].min()
    lowest_temp_plant = low_temp_plants[low_temp_plants["temperature"]
                                        == min_temp]["plant_name"]
    st.write(
        f":red[CRITICAL LOW TEMPERATURE:] {lowest_temp_plant.values[0]} ({min_temp}°C)")

st.write("")
st.write("")

chosen_plants = st.multiselect(
    label="Plant Options", options=all_plants, default=all_plants[:10])

st.write("")
st.write("")

left = create_temp_chart(latest_plant_recordings, "plant_name",
                         "temperature", chosen_plants)
right = create_soil_moisture_chart(latest_plant_recordings, "plant_name",
                                   "soil_moisture", chosen_plants)

combined_charts = alt.hconcat(left, right).resolve_legend(
    color="shared"
)
st.altair_chart(combined_charts)

st.write("")
st.write("")

heatmap_df = live_heatmap_data()
st.altair_chart(create_soil_moisture_heatmap_chart(heatmap_df, "hour",
                                                   "plant_id", "soil_moisture", "time"))
