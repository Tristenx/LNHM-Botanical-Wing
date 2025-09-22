import requests
import csv
from datetime import datetime

API_URL = "https://sigma-labs-bot.herokuapp.com/api/plants/"
PLANT_COUNT = 50
OUTPUT_FILE = f"plants-raw-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.csv"

def safe_get(d, key):
    return d.get(key) if isinstance(d, dict) else None

def flatten_plant(data: dict) -> dict:
    """Return a flat dict of the fields we want."""
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

    for pid in range(1, PLANT_COUNT + 1):
        url = f"{API_URL}{pid}"
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            data = r.json()

            # skip if API responds with an error message
            if "error" in data:
                print(f"[SKIP] Plant {pid}: {data['error']}")
                continue

            # ensure plant_id present for consistency
            data.setdefault("plant_id", pid)
            rows.append(flatten_plant(data))
            print(f"[OK]   Plant {pid}")

        except requests.RequestException as e:
            # true network/HTTP failures -> skip
            print(f"[SKIP] Plant {pid}: {e}")

    if not rows:
        print("[WARN] No valid plant data retrieved.")
        return

    # Write collected rows to CSV
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"[DONE] {len(rows)} plant records saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    extract_plants()
