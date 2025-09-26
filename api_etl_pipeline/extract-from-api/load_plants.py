"""
Load transformed CSVs into SQL Server (safe append) using SQLAlchemy + pyodbc.
Only inserts rows whose primary keys do not already exist.
"""
import os
from pathlib import Path
import urllib
import warnings
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

warnings.filterwarnings("ignore", category=UserWarning, module="urllib3")

load_dotenv()

DB_HOST   = os.getenv("DB_HOST")
DB_PORT   = os.getenv("DB_PORT", "1433")
DB_USERNAME   = os.getenv("DB_USERNAME")
DB_PASS   = os.getenv("DB_PASSWORD")
DB_NAME   = os.getenv("DB_NAME")
DB_SCHEMA = os.getenv("DB_SCHEMA", "alpha")
DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server")

DATA_DIR = Path("/tmp/transformed")

# CSV → Table mappings
TABLES = [
    ("country.csv",   "country",   "country_id"),
    ("city.csv",      "city",      "city_id"),
    ("botanist.csv",  "botanist",  "botanist_id"),
    ("plant.csv",     "plant",     "plant_id"),
    ("recording.csv", "recording", "id"),  # id will autoincrement
]

# CSV column → DB column renames (to match schema.sql)
COLUMN_MAPS = {
    # Country & city stay as 'name'
    "plant": {
        "plant_name": "name"
    },
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
        f"UID={DB_USERNAME};"
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

            # Rename columns to match DB schema if needed
            if table in COLUMN_MAPS:
                df.rename(columns=COLUMN_MAPS[table], inplace=True)

            # For recording table: drop the 'id' column so DB can autogenerate
            if table == "recording" and "id" in df.columns:
                df = df.drop(columns=["id"])

            # Skip rows whose PK already exists (except recording)
            if table != "recording" and pk_col in df.columns:
                existing_keys = set()
                query = text(f"SELECT {pk_col} FROM {DB_SCHEMA}.{table}")
                for row in conn.execute(query):
                    existing_keys.add(row[0])

                before = len(df)
                df = df[~df[pk_col].isin(existing_keys)]
                skipped = before - len(df)
                if skipped:
                    print(f"[LOAD] Skipped {skipped} duplicate rows for {table}.")

            if df.empty:
                print(f"[LOAD] Nothing new to insert into {DB_SCHEMA}.{table}.")
                continue

            print(f"[LOAD] Inserting {len(df)} rows into {DB_SCHEMA}.{table}…")
            try:
                df.to_sql(
                    name=table,
                    con=conn,
                    schema=DB_SCHEMA,
                    if_exists="append",
                    index=False,
                    chunksize=1000,
                    method="multi"
                )
            except Exception as exc:
                raise RuntimeError(f"Failed to insert into {DB_SCHEMA}.{table}: {exc}") from exc

        print("[LOAD] All tables loaded successfully.")


if __name__ == "__main__":
    try:
        load()
    except RuntimeError as exc:
        print(f"[ERROR] Load failed: {exc}")
        raise
