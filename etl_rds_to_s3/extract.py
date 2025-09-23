"""Script that extracts the last 24 hours of data from the RDS."""

from os import environ

from dotenv import load_dotenv
import pyodbc


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


def get_data(conn: pyodbc.Connection) -> dict[list]:
    """Returns all the data from the database in a dictionary."""
    data = dict()
    data["country"] = query_database(conn, "SELECT * FROM alpha.country;")
    data["city"] = query_database(conn, "SELECT * FROM alpha.city;")
    data["plant"] = query_database(conn, "SELECT * FROM alpha.plant;")
    data["recording"] = query_database(conn, "SELECT * FROM alpha.recording;")
    data["botanist"] = query_database(conn, "SELECT * FROM alpha.botanist;")
    return data


if __name__ == "__main__":
    load_dotenv()
    db_conn = get_connection()
    plant_data = get_data(db_conn)
