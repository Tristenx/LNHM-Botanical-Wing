"""Charting functions for the dashboard."""

import pandas as pd
import altair as alt
import streamlit as st


@st.cache_data
def create_bar_chart(df: pd.DataFrame, x_axis: str, y_axis: str, chosen: list[str] = None):
    if chosen:
        df = df[df["plant_name"].isin(chosen)]

    st.altair_chart(alt.Chart(df).mark_bar().encode(
        x=x_axis,
        y=y_axis
    ))


@st.cache_data
def create_line_chart(df: pd.DataFrame, x_axis: str, y_axis: str, chosen: list[str] = None):
    if chosen:
        df = df[df["plant_name"].isin(chosen)]

    st.altair_chart(alt.Chart(df).mark_line().encode(
        x=x_axis,
        y=y_axis
    ))
