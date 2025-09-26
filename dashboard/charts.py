"""Charting functions for the dashboard."""

import pandas as pd
import altair as alt
import streamlit as st


@st.cache_data
def create_temp_chart(df: pd.DataFrame, x_axis: str, y_axis: str, chosen: list[str] = None):
    """Creates a temperature bar chart."""
    if chosen:
        df = df[df["plant_name"].isin(chosen)]

    return alt.Chart(df).mark_bar().encode(
        x=alt.X(x_axis, title="Plant Name", axis=alt.Axis(labelAngle=80)),
        y=alt.Y(f"{y_axis}:Q", title="Temperature (°C)"),
        color=alt.Color("plant_name", title="Plant Name",
                        scale=alt.Scale(scheme='purplebluegreen'))
    ).properties(
        title="Temperature of Each Plant",
        width=400)


@st.cache_data
def create_soil_moisture_chart(df: pd.DataFrame, x_axis: str, y_axis: str, chosen: list[str] = None):
    """Creates a soil moisture bar chart."""
    if chosen:
        df = df[df["plant_name"].isin(chosen)]

    return alt.Chart(df).mark_bar().encode(
        x=alt.X(x_axis, title="Plant Name", axis=alt.Axis(labelAngle=80)),
        y=alt.Y(f"{y_axis}:Q", title="Soil Moisture (%)"),
        color=alt.Color("plant_name", title="Plant Name",
                        scale=alt.Scale(scheme='purplebluegreen'))
    ).properties(
        title="Soil Moisture of Each Plant",
        width=400)


@st.cache_data
def create_soil_moisture_heatmap_chart(df: pd.DataFrame, x_axis: str, y_axis: str, colour: str, time: str):
    """Creates a soil moisture heatmap chart."""
    return alt.Chart(df).mark_rect().encode(
        x=alt.X(f"{x_axis}:O", title="Time (hours)"),
        y=alt.Y(f"{y_axis}:N", title="Plant ID"),
        color=alt.Color(f"{colour}:Q", title="Moisture Levels (%)",
                        scale=alt.Scale(scheme='purplebluegreen')),
        tooltip=["plant_id", "time", "soil_moisture"]
    ).properties(
        title="Hourly Soil Moisture of Each Plant",
        width=400)
