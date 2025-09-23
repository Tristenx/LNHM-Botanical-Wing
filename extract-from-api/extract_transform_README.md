# LNMH Plants – Extract & Transform Pipeline

This project extracts plant data from the **LNMH Plants API** and transforms it into a set of clean, normalised CSV tables ready for downstream analytics or loading into a database.

---

## Overview
The pipeline:
1. **Extracts** up to **50 plant records** from the public API.  
2. Writes a single raw CSV (`data/plants-raw.csv`).  
3. **Transforms** the raw data into a set of **normalised tables** inside `data/transformed/`.  
4. Overwrites all output files on every run for easy scheduling (e.g., Docker + cron).

---

## Output Structure
Each run produces:

```
data/
├─ plants-raw.csv          # Single flattened raw extract
└─ transformed/
   ├─ country.csv          # Country dimension
   ├─ city.csv             # City dimension
   ├─ coordinate.csv       # Latitude/longitude dimension
   ├─ botanist.csv         # Botanist dimension (cleaned phones)
   ├─ plant.csv            # Plant fact table (with foreign keys)
   └─ recording.csv        # Recording fact table
```

### Key Cleaning / Transformation Steps
- **Whitespace stripping** and `nan` → `NULL` handling.
- Numeric conversions for temperature, soil moisture, latitude, longitude.
- UTC timestamp parsing for watering and recording dates.
- Botanist phone numbers normalised to `digits` + optional `xEXT` extension.

---

## ⚡ Quick Start

### 1. Prerequisites
- Python **3.9+**
- Packages:  
  ```
  pip3 install - r requirements.txt
  ```

### 2. Run the pipeline
```bash
python3 extract_transform_plants.py
```

This will:
- Query the API until 50 valid plant records are retrieved.
- Create/update:
  - `data/plants-raw.csv`
  - All normalised CSVs inside `data/transformed/`

---

## Testing
A lightweight **pytest** suite is included (see `test_extract_transform_plants.py`).
Run:
```bash
pytest
```

The tests cover:
- Helper functions (`safe_get`, `flatten_plant`, `normalise_phone`, etc.)
- Data type conversions and phone normalisation edge cases.

---

## Environment & Deployment
- Designed to run safely on a schedule (e.g., **Docker + cron job**) since all outputs overwrite on each run.
- The **load step** (to a database/RDS) can be added later using the CSVs in `data/transformed/`.

---

## API Reference
Data is sourced from:  
[https://sigma-labs-bot.herokuapp.com/api/plants/](https://sigma-labs-bot.herokuapp.com/api/plants/)

---

### Author
Built for the **LNMH Plants Data Pipeline** project.
