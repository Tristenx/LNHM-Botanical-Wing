"""Python script for basic API extraction with a moving plant_id window.

This script connects to the Liverpool Natural History Museum (LNHM) plant API
and attempts to extract roughly `TARGET_COUNT` valid plant records per run.
It increments through plant IDs until enough valid rows are collected
or until a safety cap (`MAX_ATTEMPTS`) is reached.
The extracted rows are written to a timestamped CSV file.
"""

from datetime import datetime
import csv
import requests

# Base endpoint for plant sensor data
API_URL = "https://sigma-labs-bot.herokuapp.com/api/plants/"

# Configuration parameters
TARGET_COUNT = 50          # Aim to retrieve roughly 50 valid plant records
START_ID     = 1           # Plant ID to start scanning from
MAX_ATTEMPTS = 85          # Hard upper bound to avoid infinite loops
OUTPUT_FILE  = f"plants-raw-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.csv"


def safe_get(d, key):
    """Safely return a key from a dict, or None if the input is not a dict."""
    return d.get(key) if isinstance(d, dict) else None


def flatten_plant(data: dict) -> dict:
    """Flatten the nested JSON structure returned by the API into a flat dict.

    Parameters
    ----------
    data : dict
        Raw JSON object returned by the API.

    Returns
    -------
    dict
        Flat dictionary of the key fields we want to write to CSV.
    """
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
    """Extract plant records until TARGET_COUNT is reached or MAX_ATTEMPTS is hit.

    Loops through sequential plant IDs, skipping any that return errors,
    and collects valid records into a list. The results are written
    to a CSV file named with the current UTC timestamp.
    """
    rows = []          # list to store flattened plant records
    pid = START_ID     # current plant_id being queried
    attempts = 0       # total number of API calls made

    # Keep scanning IDs until enough valid rows are captured or we hit the safety limit
    while len(rows) < TARGET_COUNT and attempts < MAX_ATTEMPTS:
        url = f"{API_URL}{pid}"
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            data = r.json()

            # Skip rows where the API returns an explicit error message
            if "error" in data:
                print(f"[SKIP] Plant {pid}: {data['error']}")
            else:
                # Ensure plant_id is present in the record for consistency
                data.setdefault("plant_id", pid)
                rows.append(flatten_plant(data))
                print(f"[OK]   Plant {pid}")
        except requests.RequestException as e:
            # Network issues or HTTP errors (404/500 etc.) are skipped
            print(f"[SKIP] Plant {pid}: {e}")

        # Move on to the next plant ID
        pid += 1
        attempts += 1

    if not rows:
        print("[WARN] No valid plant data retrieved.")
        return

    # Write all valid rows to a CSV file
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"[DONE] {len(rows)} plant records saved to {OUTPUT_FILE} "
          f"(scanned up to plant_id {pid-1})")


if __name__ == "__main__":
    extract_plants()
