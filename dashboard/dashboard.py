"""Dashboard displaying information about plant data."""
import streamlit as st

from data import load_all_plants, load_latest_plant_recordings
from charts import create_bar_chart, create_line_chart

if __name__ == "__main__":

    latest_plant_recordings = load_latest_plant_recordings()

    st.title("Live plant data")

    all_plants = load_all_plants(latest_plant_recordings)
    chosen_plants = st.multiselect(
        label="Chosen plants", options=all_plants, default=all_plants[:10])

    # Chart only showing data with one entry per plant

    create_bar_chart(latest_plant_recordings, "plant_name",
                     "temperature", chosen_plants)

    # moisture graph

    create_bar_chart(latest_plant_recordings, "plant_name",
                     "soil_moisture", chosen_plants)
