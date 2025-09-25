# pylint: disable=redefined-outer-name
"""Tests for transform.py"""
import pandas as pd
import pytest

from transform import (
    get_all_plant_ids,
    get_id_map,
    get_records_for_id,
    get_row_by_id,
    clean_plant_records,
)

@pytest.fixture
def plant_data():
    """Fixture to provide sample plant data for testing."""
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
    """Tests that get_all_plant_ids returns all plant IDs."""
    ids = get_all_plant_ids(plant_data["plant"])
    assert set(ids) == {1, 2}


def test_get_id_map(plant_data):
    """Tests that get_id_map correctly creates a mapping."""
    mapping = get_id_map(plant_data, "plant")
    assert mapping[1] == "Ficus"
    assert mapping[2] == "Monstera"


def test_get_records_for_id(plant_data):
    """Tests that get_records_for_id returns a dataframe with only the specified ID."""
    df = get_records_for_id(1, plant_data["recording"])
    assert isinstance(df, pd.DataFrame)
    assert set(df["plant_id"].unique()) == {1}


def test_get_row_by_id(plant_data):
    """Tests that get_row_by_id returns the correct row as a tuple."""
    row = get_row_by_id(1, plant_data, "plant")
    assert isinstance(row, tuple)
    assert row[0] == 1 and row[1] == "Ficus"


def test_clean_plant_records(plant_data):
    """Tests that clean_plant_records correctly processes and summarizes data."""
    df = get_records_for_id(1, plant_data["recording"])
    summary = clean_plant_records(df, plant_data)

    assert summary["plant_id"] == 1
    assert summary["plant_name"] == "Ficus"
    assert summary["botanist_name"] == "Alice"
    assert pytest.approx(summary["avg_temperature"], rel=1e-3) == 21.0
