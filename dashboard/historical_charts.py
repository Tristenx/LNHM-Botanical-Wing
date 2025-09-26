"""Charting functions for the historical data for the dashboard."""

import pandas as pd
import altair as alt
import streamlit as st


@st.cache_data
def create_temp_chart(df: pd.DataFrame, x_axis: str, y_axis: str, chosen: list[str] = None, dates: list[str] = None):
    """Template to create temperature bar chart."""
    if chosen:
        df = df[df["plant_name"].isin(chosen)]

    if dates:
        df = df[df["date"].isin(dates)]

    return alt.Chart(df).mark_bar().encode(
        x=alt.X(x_axis, sort="-y", title="Plant Name",
                axis=alt.Axis(labelAngle=80)),
        y=alt.Y(f"mean({y_axis}):Q", title="Average Temperature (°C)"),
        color=alt.Color("plant_name", title="Plant Name",
                        scale=alt.Scale(scheme='purplebluegreen'))
    ).properties(title="Average Temperature of Each Plant", width=400)


@st.cache_data
def create_soil_moisture_chart(df: pd.DataFrame, x_axis: str, y_axis: str, chosen: list[str] = None, dates: list[str] = None):
    """Template to create soil moisture bar chart."""
    if chosen:
        df = df[df["plant_name"].isin(chosen)]

    if dates:
        df = df[df["date"].isin(dates)]

    return alt.Chart(df).mark_bar().encode(
        x=alt.X(x_axis, sort="-y", title="Plant Name",
                axis=alt.Axis(labelAngle=80)),
        y=alt.Y(f"mean({y_axis}):Q", title="Average Soil Moisture (%)"),
        color=alt.Color("plant_name", title="Plant Name",
                        scale=alt.Scale(scheme='purplebluegreen'))
    ).properties(title="Average Soil Moisture of Each Plant", width=400)


@st.cache_data
def create_at_risk_chart_for_moisture(df: pd.DataFrame, x_axis: str, y_axis: str, dates: list[str] = None):
    """Template to create soil moisture bar chart."""

    if dates:
        df = df[df["date"].isin(dates)]

    df = df.groupby(x_axis)[y_axis].mean(
    ).reset_index().sort_values(by=y_axis).head(5)

    return alt.Chart(df).mark_bar().encode(
        x=alt.X(x_axis, sort="-y", title="Plant Name",
                axis=alt.Axis(labelAngle=80)),
        y=alt.Y(f"mean({y_axis}):Q", title="Lowest Average Soil Moisture"),
        color=alt.Color("plant_name", title="Plant Name",
                        scale=alt.Scale(scheme='purplebluegreen'))
    ).properties(title='Top 5 Lowest Soil Moisture', height=400, width=400)


@st.cache_data
def create_at_risk_chart_for_temperature(df: pd.DataFrame, x_axis: str, y_axis: str, dates: list[str] = None):
    """Template to create temperature bar chart."""

    if dates:
        df = df[df["date"].isin(dates)]

    df = df.groupby(x_axis)[y_axis].mean(
    ).reset_index().sort_values(by=y_axis).head(5)

    return alt.Chart(df).mark_bar().encode(
        x=alt.X(x_axis, sort="-y", title="Plant Name",
                axis=alt.Axis(labelAngle=80)),
        y=alt.Y(f"mean({y_axis}):Q", title="Lowest Average Temperature"),
        color=alt.Color("plant_name", title="Plant Name",
                        scale=alt.Scale(scheme='purplebluegreen'))
    ).properties(title='Top 5 Lowest Temperature', height=400, width=400)
