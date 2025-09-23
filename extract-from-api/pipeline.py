"""
Pipeline runner to execute: extract → transform
"""

from extract_plants import extract
from transform_plants import transform

if __name__ == "__main__":
    extract()
    transform()
    print("[PIPELINE] Extract + Transform complete.")
