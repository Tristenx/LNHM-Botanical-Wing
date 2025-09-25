import pandas as pd
import streamlit as st

from data import load_all_plant_recording_data, load_all_plants
from charts import create_bar_chart, create_line_chart


if __name__ == "__main__":

    all_plant_recording_data = load_all_plant_recording_data()

    st.title("Live plant data")

    all_plants = load_all_plants(all_plant_recording_data)
    chosen_plants = st.multiselect(
        label="Chosen plants", options=all_plants, default=all_plants)

    create_line_chart(all_plant_recording_data, "plant_name",
                      "temperature", chosen_plants)
    create_line_chart(all_plant_recording_data, "plant_name",
                      "soil_moisture", chosen_plants)
