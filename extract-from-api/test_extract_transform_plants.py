import pandas as pd
import re
import pytest
from extract_transform_plants import (
    safe_get,
    flatten_plant,
    normalise_phone,
    clean_numeric,
)


def test_safe_get():
    d = {"a": 1}
    assert safe_get(d, "a") == 1
    assert safe_get(d, "b") is None
    # Non-dict input should return None
    assert safe_get("notadict", "a") is None


def test_flatten_plant_basic():
    sample = {
        "plant_id": 42,
        "name": "Rose",
        "scientific_name": ["Rosa rubiginosa", "Rosa gallica"],
        "temperature": "25",
        "origin_location": {
            "latitude": 51.5,
            "longitude": -0.1,
            "city": "London",
            "country": "UK",
        },
        "botanist": {
            "name": "Alice",
            "email": "alice@example.com",
            "phone": "+44 (0)20 1234 5678",
        },
    }
    flat = flatten_plant(sample)
    # Keys should exist
    assert flat["plant_id"] == 42
    assert "Rosa rubiginosa" in flat["scientific_name"]
    assert flat["origin_city"] == "London"
    assert flat["botanist_email"] == "alice@example.com"


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("(123) 456-7890", "1234567890"),
        ("123.456.7890 ext42", "1234567890x42"),
        ("7639148635x57724", "7639148635x57724"),
        ("bad number", ""),
        (None, None),
    ],
)
def test_normalise_phone(raw, expected):
    assert normalise_phone(raw) == expected


@pytest.mark.parametrize(
    "val,expected",
    [
        ("42", 42),
        ("3.14", 3.14),
        ("not a number", pd.NA),
        (None, pd.NA),
    ],
)
def test_clean_numeric(val, expected):
    out = clean_numeric(val)
    # compare with pandas.isna to allow NaN/NA
    if pd.isna(expected):
        assert pd.isna(out)
    else:
        assert out == expected
