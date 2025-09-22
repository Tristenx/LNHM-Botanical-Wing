"""Python script for basic API extraction with a moving plant_id window."""
from datetime import datetime
import csv
import requests

API_URL = "https://sigma-labs-bot.herokuapp.com/api/plants/"
TARGET_COUNT = 50          # aim for roughly 50 valid plants
START_ID     = 1           # where each run begins scanning
MAX_ATTEMPTS = 85         # safety upper bound to avoid infinite loop
OUTPUT_FILE  = f"plants-raw-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.csv"


def safe_get(d, key):
    return d.get(key) if isinstance(d, dict) else None


def flatten_plant(data: dict) -> dict:
    origin   = safe_get(data, "origin_location") or {}
    botanist = safe_get(data, "botanist") or {}

    return {
        "plant_id": data.get("plant_id"),
        "name": data.get("name"),
        "temperature": data.get("temperature"),
        "soil_moisture": data.get("soil_moisture"),
        "last_watered": data.get("last_watered"),
        "recording_taken": data.get("recording_taken"),
        "latitude": origin.get("latitude"),
        "longitude": origin.get("longitude"),
        "origin_city": origin.get("city"),
        "origin_country": origin.get("country"),
        "botanist_name": botanist.get("name"),
        "botanist_email": botanist.get("email"),
        "botanist_phone": botanist.get("phone"),
        "scientific_name": (
            ", ".join(data.get("scientific_name", []))
            if isinstance(data.get("scientific_name"), list) else None
        ),
    }


def extract_plants():
    rows = []
    pid = START_ID
    attempts = 0

    while len(rows) < TARGET_COUNT and attempts < MAX_ATTEMPTS:
        url = f"{API_URL}{pid}"
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            data = r.json()

            if "error" in data:
                print(f"[SKIP] Plant {pid}: {data['error']}")
            else:
                data.setdefault("plant_id", pid)
                rows.append(flatten_plant(data))
                print(f"[OK]   Plant {pid}")
        except requests.RequestException as e:
            print(f"[SKIP] Plant {pid}: {e}")

        pid += 1
        attempts += 1

    if not rows:
        print("[WARN] No valid plant data retrieved.")
        return

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"[DONE] {len(rows)} plant records saved to {OUTPUT_FILE} "
          f"(scanned up to plant_id {pid-1})")


if __name__ == "__main__":
    extract_plants()
