"""Script that loads the summary csv file into the S3 bucket."""

from os import environ
import io

import boto3
from dotenv import load_dotenv

from extract import get_connection, get_data
from transform import get_summary_plant_data, generate_file_name


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
    csv_buffer = io.StringIO()
    summary.to_csv(csv_buffer, index=False)
    file_name = generate_file_name(summary)
    current_session = get_session()
    current_session.put_object(
        Bucket="c19-alpha-s3-bucket", Key=file_name, Body=csv_buffer.getvalue())
    return {
        "message": "Uploaded"
    }


if __name__ == "__main__":
    load_dotenv()
    handler()
