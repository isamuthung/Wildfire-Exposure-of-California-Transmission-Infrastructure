# Wildfire-Exposure-of-California-Transmission-Infrastructure
Screening-Level Spatial Analysis

Wildfires have become a persistent and structurally significant feature of California’s landscape, shaped not only by extreme events but by repeated exposure across the same regions year after year. Rather than occurring as isolated disasters, wildfire hazard increasingly recurs within defined geographic corridors that intersect critical infrastructure systems not designed for sustained fire pressure. Electric transmission infrastructure is particularly exposed. High-voltage transmission lines are long, linear assets that traverse mountainous and forested terrain, often intersecting areas of elevated wildfire hazard repeatedly over time. Public discussion of wildfire and the electric grid frequently centers on individual fire events, outages, or catastrophic seasons. Less attention is paid to where wildfire exposure consistently accumulates across the transmission network and which portions of the system face sustained spatial pressure rather than episodic interaction. This project was developed to help clarify that gap using only publicly available data and defensible spatial analytics.

This repository implements a screening-level spatial exposure analysis of California’s high-voltage electric transmission infrastructure. Using publicly released wildfire hazard maps and historical fire perimeter data, the analysis quantifies:
* where transmission geometry overlaps modeled wildfire hazard
* where it intersects observed historical fire perimeters
* where those two forms of exposure co-occur

The goal is not to predict fires, assess grid reliability, or estimate damages. Instead, the project organizes fragmented public datasets into a clear, reproducible spatial framework that highlights where exposure persistently accumulates and where deeper engineering, planning, or policy analysis may be most warranted.

## Scope & Design

This project is intentionally descriptive and retrospective, rather than predictive. All spatial overlap is treated strictly as exposure, not risk, vulnerability, or likelihood of failure.

Core design principles:
* Exposure ≠ risk ≠ failure: Spatial overlap indicates co-location only. It does not imply causality, probability, or operational outcome.
* Public data only: No confidential system maps, asset-condition data, mitigation measures, or reliability metrics are used.
* Scope discipline over completeness: Where public data cannot support defensible inference, questions are explicitly left unanswered rather than filled with assumptions.

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
|--- .env.example
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
|    |--- export/
|    |    |--- polygons_fire_union.geojson
|    |    |--- polygons_vh.geojson
|    |    |--- tx_lines_all.geojson
|    |    |--- tx_segments_joint.geojson
|    |    |--- tx_segments_vh.geojson
|    |--- tiles/
|    |    |--- exposure.mbtiles
|    |    |--- joint.mbtiles
|    |    |--- tx.mbtiles
|    |--- web/
|         |--- index.html
|--- notebooks/
|    |--- 01_ingest_fire_hazard_severity_zones.ipynb
|    |--- 02_ingest_fire_perimeters.ipynb
|    |--- 03_ingest_transmission_lines.ipynb
|    |--- 04_compute_transmission_and_fhsz_exposure.ipynb
|    |--- 05_compute_transmissio_and_historical_fire_exposure.ipynb
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
|--- scripts/
|    |--- 00_check_env.py
|    |--- 01_validate_inputs.py
|    |--- 02_execute_pipeline.py
|    |--- 03_quality_checks.py
|    |--- 04_build_report_assets.py
|    |--- 05_export_map_layers.py
|    |--- 06_build_vector_tiles.sh
|    |--- 07_run_map_local.sh
|--- sql/
|    |--- indexes.sql
|    |--- schema.sql
|    |--- queries/
|         |--- 05_create_map_layers.sql
```
## Notebooks

The notebooks are designed to be run in order and together form a transparent, database-centered analytics pipeline. Computationally expensive spatial intersections are executed once and cached in PostGIS, ensuring reproducibility and performance.

01_ingest_fhsz.ipynb

Ingests CAL FIRE Fire Hazard Severity Zone data (LRA + SRA), standardizes classifications, and writes authoritative hazard tables to PostGIS.

02_ingest_fire_perimeters.ipynb

Ingests CAL FIRE FRAP historical fire perimeters, extracts temporal attributes, and stores standardized geometries in PostGIS.

03_ingest_transmission_lines.ipynb

Ingests public transmission line geometries, filters to ≥115 kV, computes accurate line lengths in EPSG:3310, and assigns permanent primary keys for stable joins.

04_transmission_fhsz_exposure.ipynb

Computes per-line overlap between transmission geometry and wildfire hazard zones. Results are cached by hazard class to avoid repeated geometry computation.

05_transmission_fire_exposure.ipynb

Computes per-line overlap between transmission geometry and historical fire perimeters within the selected analysis window.

06_joint_exposure.ipynb

Combines cached exposure tables to identify joint exposure, defined as transmission segments intersecting both Very High hazard zones and historical fire perimeters. No heavy spatial computation occurs here.

07_results_synthesis.ipynb

Generates report-ready tables and figures using cached exposure results only.

---

## Interactive Map

The project includes a high-quality interactive web map built with:

* Tippecanoe for vector-tile generation
* TileServer-GL (Dockerized) for local tile serving
* MapLibre GL JS for browser-based rendering

This approach enables:
* smooth rendering of large transmission datasets
* layer toggling (all lines, Very High hazard segments, joint exposure)
* clean cartographic styling comparable to professional GIS platforms

The map is served locally and designed to be embeddable or hosted on static infrastructure if desired.
---

## Reproducibility

All results can be reproduced locally by creating a virtual environment, configuring a local PostGIS database, and running the notebooks in order:

```
python -m venv .venv
source .venv/bin/activate        # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
jupyter lab
```

Docker is used only for local vector-tile generation and visualization. No containers are intended to run persistently, and all services can be stopped safely when the project is closed.

## Closing Note

This project is conceived as a focused data analytics exercise grounded in public information and institutional realism. Its contribution lies not in predictive power, but in clarifying where wildfire exposure persistently intersects California’s transmission infrastructure and where the most consequential questions remain unanswered.
