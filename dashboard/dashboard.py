"""Dashboard displaying information about plant data."""
import streamlit as st

from data import load_all_plants, load_latest_plant_recordings
from charts import create_temp_chart, create_soil_moisture_chart

if __name__ == "__main__":
    st.title("How to Use")

    latest_plant_recordings = load_latest_plant_recordings()
    all_plants = load_all_plants(latest_plant_recordings)
