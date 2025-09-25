"""Charting functions for the dashboard."""

import pandas as pd
import altair as alt
import streamlit as st


@st.cache_data
def create_temp_chart(df: pd.DataFrame, x_axis: str, y_axis: str, chosen: list[str] = None):
    """Template to create temperature bar chart."""
    if chosen:
        df = df[df["plant_name"].isin(chosen)]

    st.altair_chart(alt.Chart(df).mark_bar().encode(
        x=alt.X(x_axis, sort="-y", title="Plant Name"),
        y=alt.Y(f"{y_axis}:Q", title="Temperature"),
        color=alt.Color("plant_name", title="Plant Name")
    ))


@st.cache_data
def create_soil_moisture_chart(df: pd.DataFrame, x_axis: str, y_axis: str, chosen: list[str] = None):
    """Template to create soil moisture bar chart."""
    if chosen:
        df = df[df["plant_name"].isin(chosen)]

    st.altair_chart(alt.Chart(df).mark_bar().encode(
        x=alt.X(x_axis, sort="-y", title="Plant Name"),
        y=alt.Y(f"{y_axis}:Q", title="Soil Moisture"),
        color=alt.Color("plant_name", title="Plant Name")
    ))
