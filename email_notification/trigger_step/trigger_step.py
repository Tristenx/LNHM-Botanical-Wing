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
    query = f"SELECT * FROM alpha.recording;"
    result = query_database(conn, query)
    relevant_records = []
    for record in result:
        if record[6] > lower_time:
            relevant_records.append(record)
    return relevant_records


if __name__ == "__main__":
    load_dotenv()

    db_conn = get_connection()
    relevant_time = datetime.now() - timedelta(hours=1, minutes=1)
    records = get_recordings(db_conn, relevant_time)

    # sf = boto3.client('stepfunctions', region_name='eu-west-2')
    # input_dict = {'plant': 'name',
    #               'emergeny_type': 'type',
    #               'botanist': 'name',
    #               'email': 'email',
    #               'phone': 'phone'}
    # response = sf.start_execution(
    #     stateMachineArn='arn:aws:states:eu-west-2:129033205317:stateMachine:c19-alpha-email-notification',
    #     input=json.dumps(input_dict))
