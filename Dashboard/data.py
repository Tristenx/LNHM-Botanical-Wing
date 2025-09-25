"""Functions to get and manage dashboard data."""

import pandas as pd
import streamlit as st
import pyodbc
from os import environ
from dotenv import load_dotenv


st.cache_resource


def get_connection() -> pyodbc.Connection:
    """Returns a connection to the database."""
    load_dotenv()
    conn_str = (f"DRIVER={{{environ['DB_DRIVER']}}};SERVER={environ['DB_HOST']};"
                f"PORT={environ['DB_PORT']};DATABASE={environ['DB_NAME']};"
                f"UID={environ['DB_USERNAME']};PWD={environ['DB_PASSWORD']};Encrypt=no;")
    return pyodbc.connect(conn_str)


st.cache_data(ttl=60)


def load_all_plant_recording_data() -> pd.DataFrame:
    """Returns all plant recording data from the db as a dataframe."""
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT alpha.recording.*, alpha.plant.name FROM alpha.recording JOIN alpha.plant ON alpha.recording.plant_id = alpha.plant.plant_id")
        res = cur.fetchall()

    return format_plant_recording_data(res)


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
