"""
Extract + Transform pipeline for LNMH plants API → normalised CSVs.

Each run overwrites these outputs:
    data/transformed/
        country.csv
        city.csv
        plant.csv
        recording.csv
        botanist.csv
"""

from pathlib import Path
import csv
import re
import requests
import pandas as pd

API_URL = "https://sigma-labs-bot.herokuapp.com/api/plants/"
TARGET_COUNT = 50
START_ID = 1
MAX_ATTEMPTS = 85
DATA_DIR = Path("data")
RAW_FILE = DATA_DIR / "plants-raw.csv"
OUT_DIR = DATA_DIR / "transformed"

DATA_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)


def safe_get(d: dict, k: str):
    """Return value of key k if d is a dict, else None."""
    return d.get(k) if isinstance(d, dict) else None


def flatten_plant(d: dict) -> dict:
    """Flatten nested plant API record into a single flat dictionary."""
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


def extract() -> None:
    """Extract plant records from the API and save a single raw CSV."""
    rows = []
    pid = START_ID
    attempts = 0
    while len(rows) < TARGET_COUNT and attempts < MAX_ATTEMPTS:
        try:
            r = requests.get(f"{API_URL}{pid}", timeout=10)
            r.raise_for_status()
            data = r.json()
            if "error" not in data:
                data.setdefault("plant_id", pid)
                rows.append(flatten_plant(data))
                print(f"[OK] Plant {pid}")
            else:
                print(f"[SKIP] Plant {pid}: {data['error']}")
        except Exception as e:
            print(f"[SKIP] Plant {pid}: {e}")
        pid += 1
        attempts += 1
    if not rows:
        raise RuntimeError("No valid plant data.")
    with open(RAW_FILE, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    print(f"[DONE] Extracted {len(rows)} → {RAW_FILE}")


def normalise_phone(phone: str) -> str:
    """Return digits-only phone number with optional xEXT extension."""
    if not isinstance(phone, str):
        return None
    phone = phone.lower().replace("ext", "x")
    digits = re.sub(r"[^\dx]", "", phone)
    match = re.match(r"(\d{3,})(x\d+)?", digits)
    return match.group(1) + (match.group(2) or "") if match else digits


def clean_numeric(s):
    """Convert to numeric; return NaN if conversion fails."""
    return pd.to_numeric(s, errors="coerce")


def transform() -> None:
    """Transform raw CSV into normalised tables and write to /data/transformed."""
    df = pd.read_csv(RAW_FILE)

    # Strip whitespace and replace string 'nan' with None
    for col in df.select_dtypes("object").columns:
        df[col] = df[col].astype(str).str.strip().replace({"nan": None})

    # Numeric conversions
    for col in ["temperature", "soil_moisture", "latitude", "longitude"]:
        df[col] = clean_numeric(df[col])

    # Timestamp conversions
    for col in ["last_watered", "recording_taken"]:
        df[col] = pd.to_datetime(df[col], errors="coerce", utc=True)

    # Dimension tables
    country = (
        df[["origin_country"]]
        .dropna()
        .drop_duplicates()
        .rename(columns={"origin_country": "name"})
        .reset_index(drop=True)
    )
    country["country_id"] = country.index + 1

    city = (
        df[["origin_city"]]
        .dropna()
        .drop_duplicates()
        .rename(columns={"origin_city": "name"})
        .reset_index(drop=True)
    )
    city["city_id"] = city.index + 1

    botanist = (
        df[["botanist_name", "botanist_email", "botanist_phone"]]
        .dropna(how="all")
        .drop_duplicates(subset="botanist_email")
        .rename(
            columns={
                "botanist_name": "name",
                "botanist_email": "email",
                "botanist_phone": "phone_number",
            }
        )
        .reset_index(drop=True)
    )
    botanist["phone_number"] = botanist["phone_number"].apply(normalise_phone)
    botanist["botanist_id"] = botanist.index + 1

    # Add foreign keys
    df = (
        df.merge(country, left_on="origin_country", right_on="name", how="left")
        .merge(city, left_on="origin_city", right_on="name", how="left", suffixes=("", "_city"))
        .merge(botanist[["botanist_id", "email"]],
               left_on="botanist_email", right_on="email", how="left")
    )

    # Plant table now contains latitude & longitude directly
    plant = df[
        [
            "plant_id",
            "name",
            "scientific_name",
            "latitude",
            "longitude",
            "country_id",
            "city_id",
        ]
    ]

    recording = df[
        [
            "plant_id",
            "botanist_id",
            "temperature",
            "last_watered",
            "soil_moisture",
            "recording_taken",
        ]
    ].copy()
    recording["recording_id"] = recording.index + 1

    # Write output tables
    country.to_csv(OUT_DIR / "country.csv", index=False)
    city.to_csv(OUT_DIR / "city.csv", index=False)
    plant.to_csv(OUT_DIR / "plant.csv", index=False)
    recording.to_csv(OUT_DIR / "recording.csv", index=False)
    botanist.to_csv(OUT_DIR / "botanist.csv", index=False)

    print(f"[DONE] Transform complete → {OUT_DIR}")


if __name__ == "__main__":
    extract()
    transform()
