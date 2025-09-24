"""Tests for the transform RDS data transform script"""

from transform import get_all_plant_ids


# Tests for the get_all_plants_ids function


def test_get_all_plant_ids_return_list():
    res = get_all_plant_ids([[1], [2], [3]])
    assert isinstance(res, list)


def test_get_all_plant_ids_return_list_of_ints():
    res = get_all_plant_ids([[25, "Laronburgh", None], [1, "Stammside", None], [
                            24, "Adamshaven", "Ficus carica"]])
    # assert isinstance(res, list[int])
    for id in res:
        assert isinstance(id, int)


def test_get_all_plant_ids_valid_input_1():
    res = get_all_plant_ids([[25, "Laronburgh", None], [1, "Stammside", None], [
                            24, "Adamshaven", "Ficus carica"]])
    assert res == [24, 25, 1]


def test_get_all_plant_ids_remove_duplicate_ids():
    res = get_all_plant_ids([[1], [1], [2], [3], [1], [2], [5]])
    assert res == [1, 2, 3, 5]


# Tests for the get_id_map function
