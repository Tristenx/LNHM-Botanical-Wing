"""Script that loads the summary csv file into the S3 bucket."""

import awswrangler as wr
from dotenv import load_dotenv

from extract import get_connection, get_data
from transform import get_summary_plant_data, generate_file_name


def handler(event=None, context=None) -> dict[str:str]:
    """Handler function for Lambda that uploads summary data to the S3 bucket."""
    conn = get_connection()
    tables = get_data(conn)
    summary = get_summary_plant_data(tables)
    file_name = generate_file_name(summary)
    wr.s3.to_parquet(df=summary, path=f"s3://c19-alpha-s3-bucket/{file_name}.parquet",
                     dataset=True, mode="overwrite")
    return {
        "message": "Uploaded"
    }


if __name__ == "__main__":
    load_dotenv()
    handler()
