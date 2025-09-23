""""Clears the rds database"""

from os import environ

from dotenv import load_dotenv
from pyodbc import connect, Connection


def get_connection() -> Connection:
    """Returns a connection to the database."""

    conn_str = (f"DRIVER={{{environ['DB_DRIVER']}}};SERVER={environ['DB_HOST']};"
                f"PORT={environ['DB_PORT']};DATABASE={environ['DB_NAME']};"
                f"UID={environ['DB_USERNAME']};PWD={environ['DB_PASSWORD']};Encrypt=no;")
    conn = connect(conn_str)
    return conn


def clear_database(conn: Connection) -> None:
    """Clears all of the rows from the database."""

    with conn.cursor() as cur:
        cur.execute(open("clear.sql", "r").read())

        conn.commit()


if __name__ == "__main__":
    load_dotenv()
    with get_connection() as conn:
        clear_database(conn)
