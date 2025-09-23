"""
Load transformed CSVs into SQL Server (safe append) using SQLAlchemy + pyodbc.
Only inserts rows whose primary keys do not already exist.
"""

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="urllib3")

import os
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import urllib

load_dotenv()

DB_HOST   = os.getenv("DB_HOST")
DB_PORT   = os.getenv("DB_PORT")
DB_USER   = os.getenv("DB_USER")
DB_PASS   = os.getenv("DB_PASSWORD")
DB_NAME   = os.getenv("DB_NAME")
DB_SCHEMA = os.getenv("DB_SCHEMA")
DB_DRIVER = os.getenv("DB_DRIVER")

DATA_DIR = Path("data/transformed")

# CSV → Table mappings
TABLES = [
    ("country.csv",   "country",   "country_id"),
    ("city.csv",      "city",      "city_id"),
    ("botanist.csv",  "botanist",  "botanist_id"),
    ("plant.csv",     "plant",     "plant_id"),
    ("recording.csv", "recording", "id"),
]

#CSV column → DB column renames
COLUMN_MAPS = {
    "botanist": {
        "name": "botanist_name",
        "phone_number": "phone"
    },
    "recording": {
        "recording_id": "id"
    }
}

def load():
    """Load CSVs into SQL Server using SQLAlchemy (safe append)."""
    odbc_str = (
        f"DRIVER={{{DB_DRIVER}}};"
        f"SERVER={DB_HOST},{DB_PORT};"
        f"DATABASE={DB_NAME};"
        f"UID={DB_USER};"
        f"PWD={DB_PASS};"
        "Encrypt=yes;TrustServerCertificate=yes;Connection Timeout=30;"
    )
    engine = create_engine(
        f"mssql+pyodbc:///?odbc_connect={urllib.parse.quote_plus(odbc_str)}",
        fast_executemany=True
    )

    with engine.begin() as conn:
        print("[LOAD] Connected to database. Starting upload…")

        for csv_file, table, pk_col in TABLES:
            file_path = DATA_DIR / csv_file
            if not file_path.exists():
                print(f"[LOAD] Skipping missing file: {csv_file}")
                continue

            df = pd.read_csv(file_path)

            # rename columns if needed
            if table in COLUMN_MAPS:
                df.rename(columns=COLUMN_MAPS[table], inplace=True)

            # fetch existing primary keys to avoid duplicates
            existing_keys = set()
            query = text(f"SELECT {pk_col} FROM {DB_SCHEMA}.{table}")
            for row in conn.execute(query):
                existing_keys.add(row[0])

            # filter out rows whose primary key already exists
            if pk_col in df.columns:
                before = len(df)
                df = df[~df[pk_col].isin(existing_keys)]
                skipped = before - len(df)
                if skipped:
                    print(f"[LOAD] Skipped {skipped} duplicate rows for {table}.")

            if df.empty:
                print(f"[LOAD] Nothing new to insert into {DB_SCHEMA}.{table}.")
                continue

            print(f"[LOAD] Inserting {len(df)} rows into {DB_SCHEMA}.{table}…")
            df.to_sql(
                name=table,
                con=conn,
                schema=DB_SCHEMA,
                if_exists="append",
                index=False,
                chunksize=1000,
                method="multi"
            )

        print("[LOAD] All tables loaded successfully.")

if __name__ == "__main__":
    try:
        load()
    except Exception as exc:
        print(f"[ERROR] Load failed: {exc}")