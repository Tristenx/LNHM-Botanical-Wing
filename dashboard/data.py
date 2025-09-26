"""Functions to get and manage dashboard data."""

import pandas as pd
import streamlit as st
import pyodbc
from os import environ
from dotenv import load_dotenv


@st.cache_resource
def get_connection() -> pyodbc.Connection:
    """Returns a connection to the database."""
    load_dotenv()
    conn_str = (f"DRIVER={{{environ['DB_DRIVER']}}};SERVER={environ['DB_HOST']};"
                f"PORT={environ['DB_PORT']};DATABASE={environ['DB_NAME']};"
                f"UID={environ['DB_USERNAME']};PWD={environ['DB_PASSWORD']};Encrypt=no;")
    return pyodbc.connect(conn_str)


@st.cache_data(ttl=60)
def load_all_plant_recording_data() -> pd.DataFrame:
    """Returns all plant recording data from the db as a dataframe."""
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT alpha.recording.*, alpha.plant.name FROM alpha.recording JOIN alpha.plant ON alpha.recording.plant_id = alpha.plant.plant_id")
        res = cur.fetchall()

    return format_plant_recording_data(res)


@st.cache_data(ttl=60)
def load_latest_plant_recordings() -> pd.DataFrame:
    """Filters for the latest recording for each plant in the dataframe."""

    df = load_all_plant_recording_data()

    return df.loc[df.groupby('plant_name')['last_watered'].idxmax()]


def format_plant_recording_data(data: list[tuple]) -> pd.DataFrame:
    """Adds the column name and formats the data."""

    records = []
    for recording in data:
        record = {}
        record["recording_id"] = recording[0]
        record["plant_id"] = recording[1]
        record["botanist_id"] = recording[2]
        record["temperature"] = recording[3]
        record["last_watered"] = recording[4]
        record["soil_moisture"] = recording[5]
        record["recording_taken"] = recording[6]
        record["plant_name"] = recording[7]
        records.append(record)

    return pd.DataFrame(records)


@st.cache_data
def load_all_plants(df: pd.DataFrame):
    return df['plant_name'].unique()


@st.cache_data
def live_heatmap_data():
    """Gets the data for the live page heatmap."""
    df = load_all_plant_recording_data()
    df["hour"] = pd.to_datetime(df["recording_taken"]).dt.hour
    df["time"] = pd.to_datetime(df["recording_taken"]).dt.strftime("%H:%M")
    df["soil_moisture"] = pd.to_numeric(df["soil_moisture"])

    heatmap_df = df[["plant_id", "soil_moisture", "hour", "time"]]
    return heatmap_df


@st.cache_data
def get_low_soil_moisture_plants():
    """Gets the plants with soil moistures below 20%."""
    df = load_latest_plant_recordings()
    low_moisture_plants = df[df["soil_moisture"] < 20].sort_values(
        "soil_moisture", ascending=True)
    return low_moisture_plants


@st.cache_data
def get_low_temperature_plants():
    """Gets the plants with temperatures below 5°C."""
    df = load_latest_plant_recordings()
    low_temp_plants = df[df["temperature"] <= 5].sort_values(
        "temperature", ascending=True)
    return low_temp_plants
