# Wildfire-Exposure-of-California-Transmission-Infrastructure
Screening-Level Spatial Analysis

This repository implements a **screening-level spatial exposure analysis** of publicly available (and incomplete by design) California **≥115 kV** transmission line geometries against:

- **CAL FIRE Fire Hazard Severity Zones (FHSZ)** (modeled hazard classifications)
- **CAL FIRE FRAP historical fire perimeters** (observed occurrence polygons)

The core outputs quantify (in kilometers) where transmission geometry overlaps:

- **FHSZ hazard classes**
- **historical fire perimeters**
- **joint exposure** (segments intersecting both **Very High** FHSZ and the historical fire footprint)

The goal is not to predict fires, assess grid reliability, or estimate damages. Instead, the project organizes fragmented public datasets into a clear, reproducible spatial framework that highlights where exposure persistently accumulates and where deeper engineering, planning, or policy analysis may be most warranted.

## Scope & Design

This project is intentionally descriptive and retrospective, rather than predictive. All spatial overlap is treated strictly as exposure, not risk, vulnerability, or likelihood of failure.

Core design principles:
* Exposure ≠ risk ≠ failure: Spatial overlap indicates co-location only. It does not imply causality, probability, or operational outcome.
* Public data only: No confidential system maps, asset-condition data, mitigation measures, or reliability metrics are used.
* Scope discipline over completeness: Where public data cannot support defensible inference, questions are left unanswered rather than filled with assumptions.

Within these constraints, the analysis focuses on identifying where wildfire hazard and historical fire occurrence repeatedly intersect transmission infrastructure, how concentrated that exposure is, and whether joint exposure is diffuse or localized across the system.

The project does not attempt to estimate ignition probability, fire spread, vegetation conditions, protection systems, outage likelihood, or economic consequences.

## Data Sources

All analysis relies exclusively on publicly available, authoritative datasets published by state and federal agencies:

* CAL FIRE Fire Hazard Severity Zones (FHSZ)
Statewide hazard classification maps (LRA + SRA) representing modeled wildfire hazard based on fire behavior, fuels, and environmental conditions. These are treated as institutional hazard designations, not probabilistic risk estimates.

* CAL FIRE Fire and Resource Assessment Program (FRAP) Fire Perimeters
Historical fire perimeter polygons indicating where fires have occurred. These indicate occurrence, not infrastructure damage or operational impact.

* High-Voltage Transmission Line Geometry (Federal / HIFLD sources)
Publicly released geometries representing ≥115 kV transmission infrastructure. Coverage is incomplete by design and treated as indicative rather than exhaustive.

No attempt is made to infer missing assets, reconstruct confidential system maps, or replace undisclosed infrastructure with assumptions.

## Repository Structure
```
Wildfire-Exposure-of-California-Transmission-Infrastructure/
|--- .gitignore
|--- LICENSE
|--- README.md
|--- requirements.txt
|--- data/
|    |--- .gitkeep
|--- docs/
|    |--- index.html
|    |--- tiles/
|         |--- exposure.pmtiles
|         |--- joint.pmtiles
|         |--- tx.pmtiles
|--- map/
|    |--- config.json
|    |--- docker-compose.yml
|    |--- sql/
|    |    |--- create_map_layers.sql
|    |--- scripts/
|    |    |--- map_01_export_layers.py
|    |    |--- map_02_build_tiles.sh
|    |    |--- map_03_serve_local.sh
|    |--- web/
|         |--- index.html
|--- notebooks/
|    |--- 01_ingest_fire_hazard_severity_zones.ipynb
|    |--- 02_ingest_fire_perimeters.ipynb
|    |--- 03_ingest_transmission_lines.ipynb
|    |--- 04_compute_transmission_and_fhsz_exposure.ipynb
|    |--- 05_compute_transmission_and_historical_fire_exposure.ipynb
|    |--- 06_compute_joint_exposure.ipynb
|    |--- 07_results_synthesis.ipynb
|--- outputs/
|    |--- figures/
|    |    |--- fig_exposure_funnel.png
|    |    |--- fig_fhsz_overlap_by_class.png
|    |    |--- fig_joint_exposure_pareto.png
|    |--- tables/
|         |--- report_exec_summary.csv
|         |--- report_overlap_by_hazard_class.csv
|         |--- report_top25_joint_exposure_lines.csv
|         |--- tx_joint_exposure_by_line.csv
|         |--- tx_joint_exposure_summary.csv
|         |--- tx_joint_exposure_top25_lines.csv
|         |--- tx_length_by_fhsz_class.csv
|         |--- tx_overlap_any_fire_by_line.csv
|         |--- tx_overlap_any_fire_total.csv
|         |--- tx_overlap_fhsz_by_line.csv
```

Notes:
- `data/` is a placeholder for **large raw inputs** (not committed).
- `outputs/` and `docs/tiles/` contain **pre-built artifacts** produced by the notebooks / map pipeline.
- There is an extra file `notebooks/05_compute_transmission_and_historical_fire_exposure.ipynb.ipynb` (a duplicate notebook).

## Notebooks

The notebooks are designed to be run in order and together form a transparent, database-centered analytics pipeline. Computationally expensive spatial intersections are executed in **PostGIS** and cached for reuse.

`01_ingest_fire_hazard_severity_zones.ipynb`

Ingests CAL FIRE Fire Hazard Severity Zone data (LRA + SRA), standardizes classifications, and writes authoritative hazard tables to PostGIS.

`02_ingest_fire_perimeters.ipynb`

Ingests CAL FIRE FRAP historical fire perimeters, extracts temporal attributes, and stores standardized geometries in PostGIS.

`03_ingest_transmission_lines.ipynb`

Ingests public transmission line geometries, filters to ≥115 kV, computes accurate line lengths in EPSG:3310, and assigns permanent primary keys for stable joins.

`04_compute_transmission_and_fhsz_exposure.ipynb`

Computes per-line overlap between transmission geometry and wildfire hazard zones. Results are cached by hazard class to avoid repeated geometry computation.

`05_compute_transmission_and_historical_fire_exposure.ipynb`

Computes per-line overlap between transmission geometry and historical fire perimeters within the selected analysis window.

`06_compute_joint_exposure.ipynb`

Combines cached exposure tables to identify joint exposure, defined as transmission segments intersecting both Very High hazard zones and historical fire perimeters. No heavy spatial computation occurs here.

`07_results_synthesis.ipynb`

Generates report-ready tables and figures using cached exposure results only.

---

## Interactive Map

The repo includes an interactive web map for visual inspection and communication (layer toggles + hover attributes).

Two viewing modes are included:

- **Static site (recommended for sharing)**: `docs/index.html` uses **PMTiles** from `docs/tiles/` (intended for GitHub Pages or any static host).
- **Local tileserver (development)**: `map/web/index.html` is configured to read vector tiles served by **TileServer-GL** (`map/docker-compose.yml`) from MBTiles under `map/tiles/`.

If you are rebuilding map artifacts from PostGIS, the map-specific SQL for generating map-ready tables lives at `map/sql/create_map_layers.sql`.
---

## Reproducibility

To reproduce results end-to-end, you need:

- **Python** (install dependencies from `requirements.txt`)
- **A PostGIS database** reachable from your environment
- The raw input datasets (see the ingest notebooks for what/where)

The notebooks read PostGIS connection settings from environment variables (or a `.env` file in the repo root):

- `DB_HOST` (default: `localhost`)
- `DB_PORT` (default: `5432`)
- `DB_NAME` (default: `wildfire_grid`)
- `DB_USER` (required)
- `DB_PASSWORD` (required)

Run the notebooks in order:

```
python -m venv .venv
source .venv/bin/activate        # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
jupyter lab
```

Docker is used only for **local tile serving** in the map workflow; it is not required for the analysis notebooks themselves.

## Closing Note

This project is a focused, public-data analytics exercise. Its contribution is not predictive power, but a reproducible way to see **where wildfire exposure repeatedly co-locates with transmission infrastructure** and where deeper planning/engineering questions may be most warranted.
