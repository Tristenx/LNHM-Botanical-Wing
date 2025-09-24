"""Script that transforms data from the RDS into a summary for long term storage."""

from dotenv import load_dotenv
import pandas as pd

from extract import get_connection, get_data


def get_all_plant_ids(plants: list) -> list[int]:
    """Returns a list of unique plant ids."""
    ids = list(set([plant[0] for plant in plants]))
    return ids


def get_id_map(plant_data: dict[list], subject: str) -> dict[int:str]:
    """Returns a map of ids and names for a subject."""
    subject_rows = plant_data[subject]
    id_map = dict()
    for row in subject_rows:
        id_map[row[0]] = row[1]
    return id_map


def get_records_for_id(plant_id: int, recordings: list) -> pd.DataFrame:
    """Returns a Dataframe containing all the records for a plant."""
    records = []
    for recording in recordings:
        if recording[1] == plant_id:
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


def get_row_by_id(desired_id: int, plant_data: dict[list], subject: str) -> tuple:
    """Returns the row from the plant table which contains the plant id."""
    rows = plant_data[subject]
    for row in rows:
        if row[0] == desired_id:
            return row
    return None


def clean_plant_records(records: pd.DataFrame, plant_data: dict[list]) -> dict:
    """Returns a dictionary containing a summary of the records."""
    plant_map = get_id_map(plant_data, "plant")
    botanist_map = get_id_map(plant_data, "botanist")
    summary = dict()

    summary["plant_id"] = records["plant_id"].iloc()[0]
    summary["plant_name"] = records["plant_id"].map(plant_map).to_list()[0]
    plant_info = get_row_by_id(summary["plant_id"], plant_data, "plant")
    summary["scientific_name"] = plant_info[2]
    summary["country"] = get_id_map(plant_data, "country")[plant_info[3]]
    summary["city"] = get_id_map(plant_data, "city")[plant_info[4]]
    summary["latitude"] = plant_info[5]
    summary["longitude"] = plant_info[6]

    summary["botanist_id"] = records["botanist_id"].iloc()[0]
    summary["botanist_name"] = records["botanist_id"].map(botanist_map).to_list()[
        0]
    botanist_info = get_row_by_id(
        summary["botanist_id"], plant_data, "botanist")
    summary["botanist_email"] = botanist_info[2]
    summary["botanist_phone_number"] = botanist_info[3]

    summary["avg_temperature"] = records["temperature"].mean()
    summary["avg_soil_moisture"] = records["soil_moisture"].mean()

    summary["last_watered"] = records["last_watered"].max()
    summary["date"] = records["recording_taken"].dt.date.min()
    return summary


def get_summary_plant_data(plant_data: dict[list]) -> pd.DataFrame:
    """Returns a dataframe containing a summary of plant recordings over the last 24hrs."""
    plant_ids = get_all_plant_ids(plant_data["plant"])

    summary_data = []
    for plant_id in plant_ids:
        plant_records = get_records_for_id(plant_id, plant_data["recording"])
        if not plant_records.empty:
            plant_records = clean_plant_records(plant_records, plant_data)
            summary_data.append(plant_records)

    return pd.DataFrame(summary_data)


def generate_csv(summary: pd.DataFrame) -> str:
    """Produces a a summary csv for the last 24hrs of data."""
    file_name = f"{summary["date"].iloc()[0]}-summary.csv"
    summary.to_csv(path_or_buf=file_name)
    return file_name


if __name__ == "__main__":
    load_dotenv()
    db_conn = get_connection()
    plant_tables = get_data(db_conn)
    plant_summary = get_summary_plant_data(plant_tables)
    csv_name = generate_csv(plant_summary)
