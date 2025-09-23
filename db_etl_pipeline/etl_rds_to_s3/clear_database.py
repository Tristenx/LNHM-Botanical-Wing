""""Clears the RDS database."""

from os import environ

from dotenv import load_dotenv
import pyodbc


def get_connection() -> pyodbc.Connection:
    """Returns a connection to the database."""

    conn_str = (f"DRIVER={{{environ['DB_DRIVER']}}};SERVER={environ['DB_HOST']};"
                f"PORT={environ['DB_PORT']};DATABASE={environ['DB_NAME']};"
                f"UID={environ['DB_USERNAME']};PWD={environ['DB_PASSWORD']};Encrypt=no;")
    return pyodbc.connect(conn_str)


def clear_database(conn: pyodbc.Connection) -> None:
    """Clears all of the rows from the database."""

    with conn.cursor() as cur:
        with open("clear.sql", "r", encoding="utf-8") as clear_rows:
            cur.execute(clear_rows.read())

            conn.commit()


if __name__ == "__main__":
    load_dotenv()
    with get_connection() as db_conn:
        clear_database(db_conn)
