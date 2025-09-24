"""Tests for the transform RDS data transform script"""
import pandas as pd
import pytest
from transform import get_all_plant_ids, get_id_map, get_records_for_id


# Tests for the get_all_plants_ids function


def test_get_all_plant_ids_return_list():
    """Tests whether the function returns a list"""

    res = get_all_plant_ids([[1], [2], [3]])
    assert isinstance(res, list)


def test_get_all_plant_ids_return_list_of_ints():
    """Tests whether the functions returns a list of integers """

    res = get_all_plant_ids([[25, "Laronburgh", None], [1, "Stammside", None], [
                            24, "Adamshaven", "Ficus carica"]])
    # assert isinstance(res, list[int])
    for id in res:
        assert isinstance(id, int)


def test_get_all_plant_ids_valid_input_1():
    """Tests whether the function successfully extracts ids """

    res = get_all_plant_ids([[25, "Laronburgh", None], [1, "Stammside", None], [
                            24, "Adamshaven", "Ficus carica"]])
    assert res == [24, 25, 1]


def test_get_all_plant_ids_remove_duplicate_ids():
    """Tests whether the function only return unique values"""

    res = get_all_plant_ids([[1], [1], [2], [3], [1], [2], [5]])
    assert res == [1, 2, 3, 5]


# Tests for the get_id_map function


# Tests for the get_records_for_id function

# helper function
def get_df_columns(records_df: pd.DataFrame) -> list[str]:
    return records_df.columns.to_list()


def test_get_records_for_id_correct_columns():
    """Checks whether the function creates a df with the correct."""

    res = get_records_for_id(
        1, [[1, 2, 12, "2025-09-23 13:08:03.000", 40, "2025-09-24 08:51:52.632", 23]])

    db_columns = ['plant_id', 'botanist_id', 'temperature',
                  'last_watered', 'soil_moisture', 'recording_taken', 'recording_id']

    assert sorted(get_df_columns(res)) == sorted(db_columns)


# Tests for get_row_by_id function


# Tests for clean_plant_records function


# Tests for get_summary_plant_data function


# Tests for generate_csv function
