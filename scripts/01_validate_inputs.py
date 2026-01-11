"""
01_get_data.py

Fetch/download raw data sources and write them to `data/raw/`.
"""

from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    # TODO: implement data download/copy logic
    print(f"Raw data directory ready: {RAW_DIR}")


if __name__ == "__main__":
    main()


