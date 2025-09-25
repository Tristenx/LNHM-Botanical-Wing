"""Script to display the live data on the Streamlit dashboard."""
import streamlit as st
import pandas as pd

from charts import (
    create_temp_chart,
    create_soil_moisture_chart
)
from data import (
    load_all_plant_recording_data,
    load_all_plants,
    load_latest_plant_recordings
)


latest_plant_recordings = load_latest_plant_recordings()
all_plants = load_all_plants(latest_plant_recordings)
chosen_plants = st.multiselect(
    label="Chosen plants", options=all_plants, default=all_plants[:10])

st.title("Live Plant Data")

st.header("Temperature of each Plant")
create_temp_chart(latest_plant_recordings, "plant_name",
                  "temperature", chosen_plants)

st.header("Soil Moisture of each Plant")
create_soil_moisture_chart(latest_plant_recordings, "plant_name",
                           "soil_moisture", chosen_plants)
