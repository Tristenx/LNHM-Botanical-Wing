import pandas as pd
import pytest

from transform import (
    get_all_plant_ids,
    get_id_map,
    get_records_for_id,
    get_row_by_id,
    clean_plant_records,
    get_summary_plant_data,
    generate_file_name,
)

@pytest.fixture
def plant_data():
    plants = [
        (1, "Ficus", "Ficus lyrata", 1, 1, 51.5, -0.12),
        (2, "Monstera", "Monstera deliciosa", 2, 2, 40.7, -74.0),
    ]
    botanists = [
        (10, "Alice", "alice@example.com", "123-456"),
    ]
    countries = [
        (1, "UK"),
        (2, "US"),
    ]
    cities = [
        (1, "London"),
        (2, "NYC"),
    ]
    recordings = [
        (100, 1, 10, 20.0, pd.Timestamp("2025-09-24"), 12.3,
         pd.Timestamp("2025-09-24 10:00:00")),
        (101, 1, 10, 22.0, pd.Timestamp("2025-09-25"), 14.5,
         pd.Timestamp("2025-09-25 11:00:00")),
    ]
    return {
        "plant": plants,
        "botanist": botanists,
        "country": countries,
        "city": cities,
        "recording": recordings,
    }


def test_get_all_plant_ids(plant_data):
    ids = get_all_plant_ids(plant_data["plant"])
    assert set(ids) == {1, 2}


def test_get_id_map(plant_data):
    mapping = get_id_map(plant_data, "plant")
    assert mapping[1] == "Ficus"
    assert mapping[2] == "Monstera"


def test_get_records_for_id(plant_data):
    df = get_records_for_id(1, plant_data["recording"])
    assert isinstance(df, pd.DataFrame)
    assert set(df["plant_id"].unique()) == {1}


def test_get_row_by_id(plant_data):
    row = get_row_by_id(1, plant_data, "plant")
    # verify tuple contents directly
    assert isinstance(row, tuple)
    assert row[0] == 1 and row[1] == "Ficus"


def test_clean_plant_records(plant_data):
    df = get_records_for_id(1, plant_data["recording"])
    summary = clean_plant_records(df, plant_data)

    assert summary["plant_id"] == 1
    assert summary["plant_name"] == "Ficus"
    assert summary["botanist_name"] == "Alice"
    assert pytest.approx(summary["avg_temperature"], rel=1e-3) == 21.0
    assert pytest.approx(summary["avg_soil_moisture"], rel=1e-3) == (12.3 + 14.5) / 2
    # ensure last watering date is the maximum of the input
    assert pd.Timestamp(summary["last_watered"]).normalize() == pd.Timestamp("2025-09-25")


def test_get_summary_plant_data_and_generate_file_name(plant_data):
    summary_df = get_summary_plant_data(plant_data)
    assert isinstance(summary_df, pd.DataFrame)
    assert summary_df.shape[0] == 1
    assert set(summary_df["plant_id"].unique()) == {1}

    # take the single date value without iloc
    date_value = summary_df["date"].values[0]
    if isinstance(date_value, pd.Timestamp):
        expected_date = date_value.date().isoformat()
    else:
        expected_date = str(date_value)

    filename = generate_file_name(summary_df)
    assert filename == f"{expected_date}-summary.csv"
