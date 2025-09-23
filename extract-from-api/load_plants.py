"""Load script to upload the cleaned plants data into the corresponding SQL Server database. """
import os
import pandas as pd
import pyodbc
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Database connection details from .env
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_SCHEMA = os.getenv("DB_SCHEMA")
DRIVER = os.getenv("DB_DRIVER")

DATA_DIR = Path("data/transformed")

TABLES = [
    ("country.csv", "country"),
    ("city.csv", "city"),
    ("botanist.csv", "botanist"),
    ("plant.csv", "plant"),
    ("recording.csv", "recording"),
]


def load():
    """Loads transformed CSV files into the SQL Server database."""
    conn_str = f"DRIVER={DRIVER};SERVER={DB_HOST},{DB_PORT};DATABASE={DB_NAME};UID={DB_USER};PWD={DB_PASSWORD}"

    try:
        with pyodbc.connect(conn_str) as conn:
            print("[LOAD] Connected to the database.")

            for csv_file, table_name in TABLES:
                file_path = DATA_DIR / csv_file
                if not file_path.exists():
                    print(f"[LOAD] Skipping file, not found: {csv_file}")
                    continue

                df = pd.read_csv(file_path)

                # Use to_sql with if_exists='append' to add new data
                df.to_sql(
                    name=table_name,
                    con=conn,
                    schema=DB_SCHEMA,
                    if_exists='append',
                    index=False,
                    chunksize=1000,
                )
                print(f"[LOAD] Loaded '{csv_file}' into '{DB_SCHEMA}.{table_name}'.")

            print("[PIPELINE] Load step complete.")

    except pyodbc.Error as ex:
        print(f"[ERROR] Database error: {ex}")
    except Exception as ex:
        print(f"[ERROR] An unexpected error occurred: {ex}")


if __name__ == "__main__":
    load()