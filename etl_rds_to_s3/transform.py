"""Script that transforms data from the RDS into a summary for long term storage."""

from dotenv import load_dotenv
import pandas as pd

from extract import get_connection, get_data


def get_all_plant_ids(plants: list) -> list:
    """Returns a list of unique plant ids."""
    ids = list(set([plant[0] for plant in plants]))
    return ids


def get_records_for_id(plant_id: int, recordings: list) -> pd.DataFrame:
    """Returns a Dataframe containing all the records for a plant."""
    records = []
    for recording in recordings:
        if recording[0] == plant_id:
            record = dict()
            record["recording_id"] = recording[0]
            record["plant_id"] = recording[1]
            record["botanist_id"] = recording[2]
            record["temperature"] = recording[3]
            record["last_watered"] = recording[4]
            record["soil_moisture"] = recording[5]
            record["recording_taken"] = recording[6]
            records.append(record)
    return pd.DataFrame(records)


if __name__ == "__main__":
    load_dotenv()
    db_conn = get_connection()
    plant_data = get_data(db_conn)
    plant_ids = get_all_plant_ids(plant_data["plant"])
    plant_record = get_records_for_id(
        plant_ids[4], plant_data["recording"])
    print(plant_record)
