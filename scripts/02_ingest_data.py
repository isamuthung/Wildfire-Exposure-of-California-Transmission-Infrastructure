"""
02_ingest_data.py

Ingest raw data from `data/raw/`, perform cleaning/standardization, and write to `data/interim/`
and/or `data/processed/`.
"""

from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
INTERIM_DIR = PROJECT_ROOT / "data" / "interim"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def main() -> None:
    for d in (RAW_DIR, INTERIM_DIR, PROCESSED_DIR):
        d.mkdir(parents=True, exist_ok=True)

    # TODO: implement ingestion/transforms
    print("Directories ready:")
    print(f"- RAW:       {RAW_DIR}")
    print(f"- INTERIM:   {INTERIM_DIR}")
    print(f"- PROCESSED: {PROCESSED_DIR}")


if __name__ == "__main__":
    main()


