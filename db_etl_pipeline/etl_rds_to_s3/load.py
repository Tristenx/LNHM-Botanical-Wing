"""Script that loads the summary csv file into the S3 bucket."""

from os import environ

import boto3
from dotenv import load_dotenv

from extract import get_connection, get_data
from transform import get_summary_plant_data, generate_csv


if __name__ == "__main__":
    load_dotenv()
    db_conn = get_connection()
    plant_tables = get_data(db_conn)
    plant_summary = get_summary_plant_data(plant_tables)
    csv_name = generate_csv(plant_summary)
