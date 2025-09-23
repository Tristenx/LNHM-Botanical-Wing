"""
Transform plants-raw.csv → normalised tables in data/transformed/.
"""

from pathlib import Path
import pandas as pd
import re

DATA_DIR = Path("data")
RAW_FILE = DATA_DIR / "plants-raw.csv"
OUT_DIR = DATA_DIR / "transformed"

OUT_DIR.mkdir(parents=True, exist_ok=True)


def normalise_phone(phone: str) -> str:
    if not isinstance(phone, str):
        return None
    phone = phone.lower().replace("ext", "x")
    digits = re.sub(r"[^\dx]", "", phone)
    match = re.match(r"(\d{3,})(x\d+)?", digits)
    return match.group(1) + (match.group(2) or "") if match else digits


def clean_numeric(s):
    return pd.to_numeric(s, errors="coerce")


def transform():
    df = pd.read_csv(RAW_FILE)

    #  lean strings
    for col in df.select_dtypes("object").columns:
        df[col] = df[col].astype(str).str.strip().replace({"nan": None})

    # numeric + datetime
    for col in ["temperature", "soil_moisture", "latitude", "longitude"]:
        df[col] = clean_numeric(df[col])
    for col in ["last_watered", "recording_taken"]:
        df[col] = pd.to_datetime(df[col], errors="coerce", utc=True)

    # dimension tables
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

    # join to map foreign keys
    df = (
        df.merge(country, left_on="origin_country", right_on="name", how="left")
          .merge(city, left_on="origin_city", right_on="name", how="left", suffixes=("", "_city"))
          .merge(botanist[["botanist_id", "email"]],
                 left_on="botanist_email", right_on="email", how="left")
    )

    # plant table includes latitude/longitude directly
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

    # save outputs
    country.to_csv(OUT_DIR / "country.csv", index=False)
    city.to_csv(OUT_DIR / "city.csv", index=False)
    plant.to_csv(OUT_DIR / "plant.csv", index=False)
    botanist.to_csv(OUT_DIR / "botanist.csv", index=False)
    recording.to_csv(OUT_DIR / "recording.csv", index=False)

    print(f"[DONE] Transform complete → {OUT_DIR}")


if __name__ == "__main__":
    transform()
