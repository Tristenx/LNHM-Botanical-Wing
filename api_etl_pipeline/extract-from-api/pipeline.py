"""
Pipeline runner to execute: extract -> transform -> load
"""

from extract_plants import extract
from transform_plants import transform
from load_plants import load


def handler(_, __):
    """
    AWS Lambda entry point for the pipeline.
    This function is called by the Lambda runtime.
    """
    print("[PIPELINE] Starting Lambda execution...")
    try:
        extract()
        transform()
        load()
        print("[PIPELINE] Extract + Transform + Load complete.")
    except Exception as e:
        print(f"[ERROR] Pipeline execution failed: {e}")
        raise e


if __name__ == "__main__":
    handler(None, None)
