"""Function that get and manage all of the historical data for the dashboard"""

import pandas as pd
import streamlit as st
import boto3
from os import environ as ENV
import awswrangler as wr


@st.cache_data()
def load_historical_plant_data() -> pd.DataFrame:
    """Loads the historical data stored in the s3 bucket."""

    return wr.athena.read_sql_table(
        table='c19_alpha_s3_bucket', database='c19_alpha_glue_catalog_db'
    )


@st.cache_data
def load_all_plants(df: pd.DataFrame):
    return df['plant_name'].unique()


@st.cache_data
def load_all_dates(df: pd.DataFrame):
    return df['date'].unique()


@st.cache_data
def calculate_most_at_risk_plant_by_moisture(df: pd.DataFrame, dates: list):
    if dates:
        df = df[df["date"].isin(dates)]

    df = df.groupby('plant_name')['avg_soil_moisture'].mean(
    ).reset_index().sort_values(by='avg_soil_moisture').head(1)

    return df.iloc[0]


@st.cache_data
def calculate_most_at_risk_plant_by_temperature(df: pd.DataFrame, dates: list):
    if dates:
        df = df[df["date"].isin(dates)]

    df = df.groupby('plant_name')['avg_temperature'].mean(
    ).reset_index().sort_values(by='avg_temperature').head(1)

    return df.iloc[0]
