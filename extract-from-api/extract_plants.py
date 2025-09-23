"""
Extract plant data from the LNMH API and save as data/plants-raw.csv.
Uses multiprocessing to speed up API calls.
"""

from pathlib import Path
import csv
import requests
import multiprocessing as mp

API_URL = "https://sigma-labs-bot.herokuapp.com/api/plants/"
TARGET_COUNT = 50
START_ID = 1
MAX_ATTEMPTS = 85
DATA_DIR = Path("data")
RAW_FILE = DATA_DIR / "plants-raw.csv"

DATA_DIR.mkdir(parents=True, exist_ok=True)


def safe_get(d: dict, k: str):
    return d.get(k) if isinstance(d, dict) else None


def flatten_plant(d: dict) -> dict:
    o = safe_get(d, "origin_location") or {}
    b = safe_get(d, "botanist") or {}
    sci = d.get("scientific_name")
    return {
        "plant_id": d.get("plant_id"),
        "name": d.get("name"),
        "scientific_name": ", ".join(sci) if isinstance(sci, list) else sci,
        "temperature": d.get("temperature"),
        "soil_moisture": d.get("soil_moisture"),
        "last_watered": d.get("last_watered"),
        "recording_taken": d.get("recording_taken"),
        "latitude": o.get("latitude"),
        "longitude": o.get("longitude"),
        "origin_city": o.get("city"),
        "origin_country": o.get("country"),
        "botanist_name": b.get("name"),
        "botanist_email": b.get("email"),
        "botanist_phone": b.get("phone"),
    }


def fetch_single(pid: int) -> dict:
    try:
        r = requests.get(f"{API_URL}{pid}", timeout=10)
        r.raise_for_status()
        data = r.json()
        if "error" not in data:
            data.setdefault("plant_id", pid)
            return flatten_plant(data)
    except Exception:
        return None
    return None


def extract():
    """Fetch plant records in parallel and write plants-raw.csv."""
    ids = list(range(START_ID, START_ID + MAX_ATTEMPTS))
    rows = []

    with mp.Pool(processes=8) as pool:
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


if __name__ == "__main__":
    extract()
