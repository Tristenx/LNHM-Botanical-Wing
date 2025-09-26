"""Checks the RDS and if there is an emergency triggers the email step function."""

from datetime import datetime, timedelta
from os import environ
import json

from dotenv import load_dotenv
import pyodbc
import boto3


def get_connection() -> pyodbc.Connection:
    """Returns a connection to the database."""
    conn_str = (f"DRIVER={{{environ['DB_DRIVER']}}};SERVER={environ['DB_HOST']};"
                f"PORT={environ['DB_PORT']};DATABASE={environ['DB_NAME']};"
                f"UID={environ['DB_USERNAME']};PWD={environ['DB_PASSWORD']};Encrypt=no;")
    conn = pyodbc.connect(conn_str)
    return conn


def query_database(conn: pyodbc.Connection, sql: str) -> list[list]:
    """Returns the result of a query to the database."""
    with conn.cursor() as cursor:
        cursor.execute(sql)
        result = cursor.fetchall()
    return result


def get_recordings(conn: pyodbc.Connection, lower_time: datetime):
    """Returns recordings that are greater than a lower bound time."""
    query = f"SELECT * FROM alpha.recording;"
    result = query_database(conn, query)
    relevant_records = []
    for record in result:
        if record[6] > lower_time:
            relevant_records.append(record)
    return relevant_records


def trigger_step_function(emergency_details: dict[str:str]) -> None:
    """Triggers the AWS step function to send an email with emergency details."""
    sf = boto3.client('stepfunctions', region_name='eu-west-2')
    sf.start_execution(
        stateMachineArn='arn:aws:states:eu-west-2:129033205317:stateMachine:c19-alpha-email-notification',
        input=json.dumps(emergency_details))


def good_moisture_level(moisture: float) -> bool:
    """Checks if the moisture level is acceptable for a recording."""
    if moisture > 20:
        return True
    return False


def check_plant_health(recordings: list[tuple]) -> None:
    """Performs health checks on the each of the recordings."""
    for record in recordings:
        if not good_moisture_level(record[5]):
            print("BAD")
            details = dict()
            details["plant"] = record[1]
            details["emergency_type"] = f"Moisture Level: {record[5]}"
            details["botanist"] = record[2]
            details["email"] = "testing@test.com"
            details["phone"] = "999"
            trigger_step_function(details)


def handler(event=None, context=None) -> dict[str:str]:
    """Handler function for Lambda to trigger a step function if theres an emergency."""
    db_conn = get_connection()
    relevant_time = datetime.now() - timedelta(hours=1, minutes=2)
    records = get_recordings(db_conn, relevant_time)
    check_plant_health(records)
    return {
        "message": "Triggered"
    }


if __name__ == "__main__":
    load_dotenv()
    handler()
