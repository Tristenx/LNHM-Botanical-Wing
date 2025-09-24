"""

Extract plant data from the LNMH API and save as data/plants-raw.csv.

Uses multiprocessing to speed up API calls.

"""

from pathlib import Path
from typing import Optional, Any
import csv
import multiprocessing as mp
import sys
import requests

# config
API_URL = "https://sigma-labs-bot.herokuapp.com/api/plants/"
TARGET_COUNT = 50
START_ID = 1
MAX_ATTEMPTS = 85
DATA_DIR = Path("data")
RAW_FILE = DATA_DIR / "plants-raw.csv"

# Custom exception
class PlantFetchError(Exception):
    """Custom exception for errors when fetching plant data."""

#API Helper funcs
def safe_get(dictionary: dict, k: str) -> Optional[Any]:
    """Returns dictionary key if dictionary is a dict - else returns None."""
    return dictionary.get(k) if isinstance(dictionary, dict) else None

def flatten_plant(dictionary: dict) -> dict:
    """Flattens output for SQL Server upload."""
    origin = dictionary.get("origin_location", {})
    botanist = dictionary.get("botanist", {})
    sci = dictionary.get("scientific_name")
    return {
        "plant_id": dictionary.get("plant_id"),
        "name": dictionary.get("name"),
        "scientific_name": ", ".join(sci) if isinstance(sci, list) else sci,
        "temperature": dictionary.get("temperature"),
        "soil_moisture": dictionary.get("soil_moisture"),
        "last_watered": dictionary.get("last_watered"),
        "recording_taken": dictionary.get("recording_taken"),
        "latitude": origin.get("latitude"),
        "longitude": origin.get("longitude"),
        "origin_city": origin.get("city"),
        "origin_country": origin.get("country"),
        "botanist_name": botanist.get("name"),
        "botanist_email": botanist.get("email"),
        "botanist_phone": botanist.get("phone"),
    }

def fetch_single(pid: int) -> Optional[dict]:
    """Fetches single plant via its id, returns None on error."""
    try:
        response = requests.get(f"{API_URL}{pid}", timeout=10)
        response.raise_for_status()
        data = response.json()
        if "error" in data:
            print(f"[{pid}] API error: {data['error']}", file=sys.stderr)
            return None
        data.setdefault("plant_id", pid)
        return flatten_plant(data)
    except (requests.exceptions.RequestException, ValueError) as e:
        print(f"[{pid}] Request error: {e}", file=sys.stderr)
        return None

# main logic
def extract():
    """Fetch plant records in parallel and write plants-raw.csv."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ids = list(range(START_ID, START_ID + MAX_ATTEMPTS))
    rows = []

    with mp.Pool(processes=mp.cpu_count()) as pool:
        for result in pool.imap_unordered(fetch_single, ids):
            if result:
                rows.append(result)
                if len(rows) >= TARGET_COUNT:
                    break

    if not rows:
        raise RuntimeError("No valid plant data retrieved.")

    with open(RAW_FILE, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)

    print(f"[DONE] Extracted {len(rows)} → {RAW_FILE}")

#entry point
if __name__ == "__main__":
    extract()
