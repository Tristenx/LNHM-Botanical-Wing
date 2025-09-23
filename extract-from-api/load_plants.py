# Updated load_plants.py
"""
Load transformed CSVs into SQL Server using SQLAlchemy + pyodbc.
Performs an upsert (MERGE) to update existing rows and insert new ones.
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
    """Load CSVs into SQL Server using an upsert (MERGE)."""
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
            
            if df.empty:
                print(f"[LOAD] No data to process for {table}.")
                continue

            # rename columns if needed
            if table in COLUMN_MAPS:
                df.rename(columns=COLUMN_MAPS[table], inplace=True)
            
            # Use a temporary table for the MERGE source
            temp_table = f"#{table}_temp"
            print(f"[LOAD] Loading into temporary table {temp_table}…")
            df.to_sql(
                name=temp_table,
                con=conn,
                schema=DB_SCHEMA,
                if_exists="replace",
                index=False,
                chunksize=1000,
            )

            # Construct the MERGE statement
            columns = ", ".join([f'"{c}"' for c in df.columns])
            update_set = ", ".join([f"TARGET.{c} = SOURCE.{c}" for c in df.columns])
            insert_values = ", ".join([f"SOURCE.{c}" for c in df.columns])

            merge_sql = text(f"""
                MERGE INTO {DB_SCHEMA}.{table} AS TARGET
                USING {temp_table} AS SOURCE
                ON (TARGET.{pk_col} = SOURCE.{pk_col})
                WHEN MATCHED THEN
                    UPDATE SET {update_set}
                WHEN NOT MATCHED THEN
                    INSERT ({columns})
                    VALUES ({insert_values});
            """)

            print(f"[LOAD] Performing upsert for {table}…")
            result = conn.execute(merge_sql)
            print(f"[LOAD] Upserted {result.rowcount} rows into {DB_SCHEMA}.{table}.")
            
        print("[LOAD] All tables loaded successfully.")

if __name__ == "__main__":
    try:
        load()
    except RuntimeError as exc:
        print(f"[ERROR] Load failed: {exc}")