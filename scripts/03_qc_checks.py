"""
03_qc_checks.py

Run quality checks on interim/processed datasets and write QC outputs to `outputs/` (tables/figures).
"""

from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INTERIM_DIR = PROJECT_ROOT / "data" / "interim"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_TABLES_DIR = PROJECT_ROOT / "outputs" / "tables"
OUTPUT_FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"


def main() -> None:
    for d in (INTERIM_DIR, PROCESSED_DIR, OUTPUT_TABLES_DIR, OUTPUT_FIGURES_DIR):
        d.mkdir(parents=True, exist_ok=True)

    # TODO: implement QC checks and save results
    print("QC output directories ready:")
    print(f"- TABLES:  {OUTPUT_TABLES_DIR}")
    print(f"- FIGURES: {OUTPUT_FIGURES_DIR}")


if __name__ == "__main__":
    main()


