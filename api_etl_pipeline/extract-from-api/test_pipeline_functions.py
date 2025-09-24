from extract_plants import safe_get, flatten_plant, fetch_single
from transform_plants import normalise_phone, clean_numeric
import pipeline
import pytest
import subprocess
import sys
from unittest.mock import patch

# Tests for safe_get
def test_safe_get_valid_key():
    """Test safe_get with a valid key."""
    d = {"a": 1, "b": 2}
    assert safe_get(d, "a") == 1

def test_safe_get_invalid_key():
    """Test safe_get with an invalid key."""
    d = {"a": 1, "b": 2}
    assert safe_get(d, "c") is None

def test_safe_get_non_dict_input():
    """Test safe_get with a non-dictionary input."""
    assert safe_get("not_a_dict", "key") is None

def test_safe_get_empty_dict():
    """Test safe_get with an empty dictionary."""
    d = {}
    assert safe_get(d, "a") is None

# Tests for flatten_plant
def test_flatten_plant_valid_data():
    """Test flatten_plant with a complete dictionary."""
    data = {
        "plant_id": 1,
        "name": "Rose",
        "scientific_name": ["Rosa", "sp."],
        "temperature": 25,
        "soil_moisture": 0.5,
        "last_watered": "2023-01-01T10:00:00Z",
        "recording_taken": "2023-01-01T10:05:00Z",
        "origin_location": {
            "latitude": 34.05,
            "longitude": -118.25,
            "city": "Los Angeles",
            "country": "USA"
        },
        "botanist": {
            "name": "Jane Doe",
            "email": "jane.doe@example.com",
            "phone": "123-456-7890"
        }
    }
    expected_output = {
        "plant_id": 1,
        "name": "Rose",
        "scientific_name": "Rosa, sp.",
        "temperature": 25,
        "soil_moisture": 0.5,
        "last_watered": "2023-01-01T10:00:00Z",
        "recording_taken": "2023-01-01T10:05:00Z",
        "latitude": 34.05,
        "longitude": -118.25,
        "origin_city": "Los Angeles",
        "origin_country": "USA",
        "botanist_name": "Jane Doe",
        "botanist_email": "jane.doe@example.com",
        "botanist_phone": "123-456-7890",
    }
    assert flatten_plant(data) == expected_output

def test_flatten_plant_missing_keys():
    """Test flatten_plant with missing keys in nested dictionaries."""
    data = {
        "plant_id": 2,
        "name": "Cactus",
        "scientific_name": "Cactaceae",
        "origin_location": {"city": "Desert"},
        "botanist": {}
    }
    expected_output = {
        "plant_id": 2,
        "name": "Cactus",
        "scientific_name": "Cactaceae",
        "temperature": None,
        "soil_moisture": None,
        "last_watered": None,
        "recording_taken": None,
        "latitude": None,
        "longitude": None,
        "origin_city": "Desert",
        "origin_country": None,
        "botanist_name": None,
        "botanist_email": None,
        "botanist_phone": None,
    }
    assert flatten_plant(data) == expected_output

def test_flatten_plant_empty_input():
    """Test flatten_plant with an empty dictionary."""
    data = {}
    expected_output = {
        "plant_id": None,
        "name": None,
        "scientific_name": None,
        "temperature": None,
        "soil_moisture": None,
        "last_watered": None,
        "recording_taken": None,
        "latitude": None,
        "longitude": None,
        "origin_city": None,
        "origin_country": None,
        "botanist_name": None,
        "botanist_email": None,
        "botanist_phone": None,
    }
    assert flatten_plant(data) == expected_output

def test_flatten_plant_scientific_name_is_string():
    """Test flatten_plant when scientific_name is a string instead of a list."""
    data = {
        "plant_id": 3,
        "name": "Sunflower",
        "scientific_name": "Helianthus annuus",
    }
    expected_output = {
        "plant_id": 3,
        "name": "Sunflower",
        "scientific_name": "Helianthus annuus",
        "temperature": None,
        "soil_moisture": None,
        "last_watered": None,
        "recording_taken": None,
        "latitude": None,
        "longitude": None,
        "origin_city": None,
        "origin_country": None,
        "botanist_name": None,
        "botanist_email": None,
        "botanist_phone": None,
    }
    assert flatten_plant(data) == expected_output


# Tests for normalise_phone
def test_normalise_phone_standard_format():
    """Test normalise_phone with a standard phone number."""
    assert normalise_phone("123-456-7890") == "1234567890"

def test_normalise_phone_with_extension():
    """Test normalise_phone with an extension."""
    assert normalise_phone("123.456.7890 x123") == "1234567890x123"

def test_normalise_phone_missing_extension_prefix():
    """Test normalise_phone with a number and extension, but missing the `x`."""
    assert normalise_phone("1234567890ext123") == "1234567890x123"

def test_normalise_phone_non_string_input():
    """Test normalise_phone with a non-string input."""
    assert normalise_phone(1234567890) is None

def test_normalise_phone_empty_string():
    """Test normalise_phone with an empty string."""
    assert normalise_phone("") == ""

def test_normalise_phone_no_digits():
    """Test normalise_phone with a string containing no digits."""
    assert normalise_phone("abc def") == ""

def test_normalise_phone_with_plus_sign():
    """Test normalise_phone with a plus sign at the start."""
    assert normalise_phone("+1-123-456-7890") == "11234567890"

def test_normalise_phone_with_spaces():
    """Test normalise_phone with extra spaces."""
    assert normalise_phone(" 123 456 7890 ") == "1234567890"

def test_normalise_phone_with_special_characters():
    """Test normalise_phone with various special characters."""
    assert normalise_phone("(123) 456-7890#") == "1234567890"

# Tests for clean_numeric
def test_clean_numeric_valid_string():
    """Test clean_numeric with a valid numeric string."""
    assert clean_numeric("123.45") == 123.45


# Tests for fetch_single
@patch('requests.get')
def test_fetch_single_success(mock_get):
    """Test fetch_single with a successful API response."""
    mock_response = mock_get.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "name": "Rose",
        "scientific_name": ["Rosa", "sp."],
        "origin_location": {"city": "Los Angeles"},
        "botanist": {"name": "Jane Doe"}
    }
    result = fetch_single(1)
    assert result is not None
    assert result["plant_id"] == 1
    assert result["name"] == "Rose"

@patch('requests.get')
def test_fetch_single_api_error(mock_get):
    """Test fetch_single with an API error message in the response."""
    mock_response = mock_get.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {"error": "Plant not found"}
    result = fetch_single(999)
    assert result is None

