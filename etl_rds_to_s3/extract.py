"""Script that extracts the last 24 hours of data from the RDS."""

from os import environ

from dotenv import load_dotenv
import pyodbc


def get_connection():
    """Returns a connection to the database."""
    conn_str = (f"DRIVER={{{environ['DB_DRIVER']}}};SERVER={environ['DB_HOST']};"
                f"PORT={environ['DB_PORT']};DATABASE={environ['DB_NAME']};"
                f"UID={environ['DB_USERNAME']};PWD={environ['DB_PASSWORD']};Encrypt=no;")
    conn = pyodbc.connect(conn_str)
    return conn


def query_database(conn, sql: str):
    """Returns the result of a query to the database."""
    with conn.cursor() as cursor:
        cursor.execute(sql)
        result = cursor.fetchall()
    return result


if __name__ == "__main__":
    load_dotenv()
    db_conn = get_connection()
    query = "SELECT name FROM sys.databases;"
    print(query_database(db_conn, query))
