"""
04_build_metrics.py

Compute final metrics/aggregations from processed datasets and write final outputs to `outputs/`.
"""

from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_TABLES_DIR = PROJECT_ROOT / "outputs" / "tables"
OUTPUT_FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"


def main() -> None:
    for d in (PROCESSED_DIR, OUTPUT_TABLES_DIR, OUTPUT_FIGURES_DIR):
        d.mkdir(parents=True, exist_ok=True)

    # TODO: implement metric building
    print("Metrics output directories ready:")
    print(f"- PROCESSED: {PROCESSED_DIR}")
    print(f"- TABLES:    {OUTPUT_TABLES_DIR}")
    print(f"- FIGURES:   {OUTPUT_FIGURES_DIR}")


if __name__ == "__main__":
    main()


