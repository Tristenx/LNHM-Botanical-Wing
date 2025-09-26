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
    live_heatmap_data
)


latest_plant_recordings = load_latest_plant_recordings()

all_plants = load_all_plants(latest_plant_recordings)
chosen_plants = st.multiselect(
    label="Plant Options", options=all_plants, default=all_plants[:10])

st.subheader("Live Plant Data")

st.write("")

left = create_temp_chart(latest_plant_recordings, "plant_name",
                         "temperature", chosen_plants)
right = create_soil_moisture_chart(latest_plant_recordings, "plant_name",
                                   "soil_moisture", chosen_plants)

combined_charts = alt.hconcat(left, right).resolve_legend(
    color="shared"
)
st.altair_chart(combined_charts)

heatmap_df = live_heatmap_data()
st.altair_chart(create_soil_moisture_heatmap_chart(heatmap_df, "hour",
                                                   "plant_id", "soil_moisture", "time"))
