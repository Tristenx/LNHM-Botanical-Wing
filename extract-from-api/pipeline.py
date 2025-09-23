"""
Pipeline runner to execute: extract → transform
"""

from extract_plants import extract
from transform_plants import transform
from load_plants import load

if __name__ == "__main__":
    extract()
    transform()
    load()
    print("[PIPELINE] Extract + Transform + Load complete.")
