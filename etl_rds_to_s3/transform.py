"""Script that transforms data from the RDS into a summary for long term storage."""

from dotenv import load_dotenv
import pandas as pd

from extract import get_connection, get_data


def get_all_plant_ids(plants: list) -> list:
    """Returns a list of unique plant ids."""
    ids = list(set([plant[0] for plant in plants]))
    return ids


if __name__ == "__main__":
    load_dotenv()
    db_conn = get_connection()
    plant_data = get_data(db_conn)
    plant_ids = get_all_plant_ids(plant_data["plant"])
