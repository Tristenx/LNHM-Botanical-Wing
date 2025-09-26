import pandas as pd
import streamlit as st
import altair as alt

from historical_charts import (
    create_temp_chart,
    create_soil_moisture_chart,
    create_at_risk_chart_for_moisture,
    create_at_risk_chart_for_temperature
)
from historical_data import (
    load_historical_plant_data,
    load_all_plants,
    load_all_dates,
    calculate_most_at_risk_plant_by_moisture,
    calculate_most_at_risk_plant_by_temperature
)

# Load all data
hist_plant_recordings = load_historical_plant_data()
all_plants = load_all_plants(hist_plant_recordings)
all_dates = load_all_dates(hist_plant_recordings)

st.title("Historical Plant Data")


left, right = st.columns(2, vertical_alignment='bottom')

with left:
    chosen_plants = st.multiselect(
        label="Chosen plants", options=all_plants, default=all_plants[:5])


with right:
    chosen_dates = st.multiselect(
        label="Chosen dates", options=all_dates, default=all_dates)


first_chart = create_temp_chart(hist_plant_recordings, "plant_name",
                                "avg_temperature", chosen_plants, chosen_dates)
second_chart = create_soil_moisture_chart(
    hist_plant_recordings, "plant_name", "avg_soil_moisture", chosen_plants, chosen_dates)

combined_charts = alt.hconcat(first_chart, second_chart).resolve_legend(
    color="shared"
)
st.altair_chart(combined_charts)

# Chart and metrics about lowest Soil Moisture

most_at_risk_plant_by_moisture = calculate_most_at_risk_plant_by_moisture(
    hist_plant_recordings, chosen_dates)


l2, r2 = st.columns(2, vertical_alignment='top')
with l2:
    st.metric('Most at risk plant by Low Moisture:',
              most_at_risk_plant_by_moisture['plant_name'])


with r2:
    st.metric("Lowest Soil Moisture %:", round(
        most_at_risk_plant_by_moisture['avg_soil_moisture'], 2))


st.altair_chart(create_at_risk_chart_for_moisture(hist_plant_recordings, "plant_name",
                                                  "avg_soil_moisture", chosen_dates))


# Chart and metrics about lowest temperature

most_at_risk_plant_by_temperature = calculate_most_at_risk_plant_by_temperature(
    hist_plant_recordings, chosen_dates)


l3, r3 = st.columns(2, vertical_alignment='top')
with l3:
    st.metric('Most at risk plant by Low Temperature:',
              most_at_risk_plant_by_temperature['plant_name'])

with r3:
    st.metric("Lowest overall temp (C):", round(
        most_at_risk_plant_by_temperature['avg_temperature'], 2))


st.altair_chart(create_at_risk_chart_for_temperature(hist_plant_recordings, "plant_name",
                                                     "avg_temperature", chosen_dates))
