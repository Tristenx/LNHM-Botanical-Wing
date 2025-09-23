# load_plants.py
"""
Load transformed CSVs into SQL Server (append-only).
"""

from pathlib import Path
import pandas as pd
import pyodbc
from dotenv import load_dotenv
import os

# Load .env
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "1433")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_SCHEMA = os.getenv("DB_SCHEMA", "alpha")
DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server")

DATA_DIR = Path("data/transformed")

def get_conn():
    conn_str = (
        f"DRIVER={{{DB_DRIVER}}};"
        f"SERVER={DB_HOST},{DB_PORT};"
        f"DATABASE={DB_NAME};"
        f"UID={DB_USER};"
        f"PWD={DB_PASSWORD};"
        "TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str)

def load_table(df: pd.DataFrame, table_name: str):
    if df.empty:
        print(f"[LOAD] {table_name} CSV empty, skipping...")
        return

    conn = get_conn()
    cursor = conn.cursor()

    # Build parameterized insert
    columns = list(df.columns)
    placeholders = ", ".join("?" for _ in columns)
    column_names = ", ".join(columns)

    sql = f"INSERT INTO {DB_SCHEMA}.{table_name} ({column_names}) VALUES ({placeholders})"

    rows = [tuple(x) for x in df.to_numpy()]

    try:
        cursor.fast_executemany = True
        cursor.executemany(sql, rows)
        conn.commit()
        print(f"[LOAD] Inserted {len(rows)} rows into {table_name}")
    except pyodbc.IntegrityError as e:
        print(f"[LOAD] IntegrityError for {table_name}: {e}")
    finally:
        cursor.close()
        conn.close()

def load():
    print("[LOAD] Starting append...")
    for file_name in ["country.csv", "city.csv", "botanist.csv", "plant.csv", "recording.csv"]:
        path = DATA_DIR / file_name
        if not path.exists():
            print(f"[LOAD] {file_name} missing, skipping...")
            continue
        df = pd.read_csv(path)
        load_table(df, file_name.replace(".csv",""))
    print("[LOAD] All done!")

if __name__ == "__main__":
    load()
