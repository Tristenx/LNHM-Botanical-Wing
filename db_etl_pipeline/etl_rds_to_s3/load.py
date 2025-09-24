"""Script that loads the summary csv file into the S3 bucket."""

from os import environ

import boto3
from dotenv import load_dotenv

from extract import get_connection, get_data
from transform import get_summary_plant_data, generate_csv


def get_session() -> boto3.session.Session:
    """Returns a boto3 session for upload."""
    current_session = boto3.session.Session(
        aws_access_key_id=environ["ACCESS_KEY"],
        aws_secret_access_key=environ["SECRET_ACCESS_KEY"]).client("s3")
    return current_session


def handler(event=None, context=None) -> dict[str:str]:
    """Handler function for Lambda that uploads summary data to the S3 bucket."""
    conn = get_connection()
    tables = get_data(conn)
    summary = get_summary_plant_data(tables)
    file_name = generate_csv(summary)
    current_session = get_session()
    current_session.upload_file(file_name, "c19-alpha-s3-bucket", file_name)
    return {
        "message": "Uploaded"
    }


if __name__ == "__main__":
    handler()
