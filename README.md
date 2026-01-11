# Wildfire-Exposure-of-California-Transmission-Infrastructure

# Wildfire Exposure of California Transmission Infrastructure

Wildfires have become a persistent and structurally significant feature of California’s landscape, shaped not only by extreme events but by repeated exposure across the same regions year after year. Rather than occurring as isolated disasters, wildfire hazard increasingly recurs within defined geographic corridors that intersect critical infrastructure systems not designed for sustained fire pressure. Electric transmission infrastructure is particularly exposed: long, linear assets traverse mountainous and forested terrain, repeatedly intersecting areas of elevated wildfire hazard over time.

Public discussion of wildfire and the grid often centers on individual fire events, outages, or catastrophic seasons. Less attention is given to understanding where wildfire exposure consistently accumulates along the transmission network and which portions of the system face sustained spatial pressure rather than episodic interaction. This project grew out of a desire to use data analytics to better understand that gap using only publicly available information.

This repository implements a **screening-level spatial exposure analysis** of California’s high-voltage electric transmission infrastructure. Using publicly released wildfire hazard maps and historical fire perimeter data, the analysis quantifies where transmission geometry overlaps modeled wildfire hazard, where it intersects observed historical fires, and where these exposures co-occur. The goal is not to predict fires, assess grid reliability, or estimate damages, but to organize fragmented public datasets into a clear, defensible spatial framework that highlights where exposure persistently accumulates and where deeper technical or policy analysis may be most warranted.

---

## Scope & Design

This project is intentionally **descriptive and retrospective**, rather than predictive. It measures spatial overlap between transmission infrastructure and wildfire-related datasets, and treats that overlap strictly as **exposure**, not risk, vulnerability, or likelihood of failure.

Several design principles guide the analysis:

- **Exposure ≠ risk ≠ failure**  
  Spatial overlap indicates co-location, not probability, causality, or operational outcome.

- **Public data only**  
  The analysis uses no confidential system maps, asset-condition data, mitigation information, or reliability metrics.

- **Scope discipline over completeness**  
  Where public data cannot support defensible inference, questions are explicitly left unanswered rather than filled with assumptions.

Within these constraints, the analysis focuses on identifying where wildfire hazard and historical fire occurrence repeatedly intersect transmission infrastructure, how concentrated that exposure is, and whether joint exposure is diffuse or localized across the network. The project does not attempt to estimate ignition probability, fire spread, vegetation conditions, protection systems, outage likelihood, or economic consequences.

---

## Data Sources

All analysis relies exclusively on publicly available, authoritative datasets published by state and federal agencies:

1. **CAL FIRE Fire Hazard Severity Zones (FHSZ)**  
   Statewide hazard classification maps (LRA + SRA) representing modeled wildfire hazard based on fire behavior, fuels, and environmental conditions. These are treated as institutional hazard designations, not outcome-based risk estimates.

2. **CAL FIRE Fire and Resource Assessment Program (FRAP) Fire Perimeters**  
   Historical fire perimeter polygons used to identify where fires have occurred historically. These indicate occurrence, not infrastructure damage or operational impact.

3. **High-Voltage Transmission Line Geometry (Federal / HIFLD sources)**  
   Publicly released transmission line geometries representing ≥115 kV infrastructure. Coverage is incomplete by design and treated as indicative rather than exhaustive.

No attempt is made to infer missing assets, reconstruct confidential system maps, or substitute assumptions for undisclosed infrastructure.

---

## Repository Structure
```
├─ README.md
├─ requirements.txt
├─ .env # local PostGIS credentials (not committed)
├─ .gitignore
│
├─ data/
│ ├─ raw/
│ │ ├─ fhsz/ # CAL FIRE Fire Hazard Severity Zones
│ │ ├─ fire_perimeters/ # CAL FIRE FRAP historical fire perimeters
│ │ └─ transmission/ # Public transmission line shapefiles
│ ├─ interim/
│ └─ processed/
│
├─ notebooks/
│ ├─ 01_ingest_fhsz.ipynb
│ ├─ 02_ingest_fire_perimeters.ipynb
│ ├─ 03_ingest_transmission_lines.ipynb
│ ├─ 04_transmission_fhsz_exposure.ipynb
│ ├─ 05_transmission_fire_exposure.ipynb
│ ├─ 06_joint_exposure.ipynb
│ ├─ 07_results_synthesis.ipynb
│ └─ 08_vector_tile_mapping.ipynb
│
├─ outputs/
│ ├─ tables/
│ ├─ figures/
│ └─ tiles/ # GeoJSON → MBTiles → MapLibre HTML
│
└─ scripts/ # future reproducibility utilities
```

---

## Notebooks

The notebooks are designed to be run **in order** and together form a transparent, database-centered analytics pipeline. Computationally expensive spatial operations are performed once and cached, allowing downstream notebooks to reuse results without re-running geometry intersections.

### 01_ingest_fhsz.ipynb  
Ingests CAL FIRE Fire Hazard Severity Zone datasets (LRA + SRA), standardizes hazard classifications, and writes authoritative hazard tables to PostGIS.

### 02_ingest_fire_perimeters.ipynb  
Ingests CAL FIRE FRAP historical fire perimeters, extracts fire-year attributes, and writes standardized perimeter geometry to PostGIS.

### 03_ingest_transmission_lines.ipynb  
Ingests public transmission line geometries, filters to ≥115 kV, computes accurate line lengths using EPSG:3310, and writes an authoritative `transmission_lines` table with a permanent primary key to support stable joins throughout the analysis.

### 04_transmission_fhsz_exposure.ipynb  
Computes per-line overlap between transmission geometry and wildfire hazard zones. Results are cached in a table that stores overlap length by hazard class.

### 05_transmission_fire_exposure.ipynb  
Computes per-line overlap between transmission geometry and historical fire perimeters within the selected year window. Optional temporal aggregation enables coarse recurrence analysis without repeated geometry computation.

### 06_joint_exposure.ipynb  
Combines cached exposure tables to identify **joint exposure**, defined as transmission segments intersecting both Very High wildfire hazard and historical fire perimeters. This notebook performs no heavy spatial operations.

### 07_results_synthesis.ipynb  
Reads only cached exposure tables and summary outputs to generate report-ready tables and figures. No PostGIS geometry computation occurs in this notebook.

### 08_vector_tile_mapping.ipynb  
Exports California-clipped GeoJSON layers, builds MBTiles using Tippecanoe, serves tiles locally via Docker, and generates an interactive MapLibre map with a contextual basemap. This notebook is intentionally isolated due to runtime and visualization complexity.

---

## Key Results (High-Level)

At a statewide screening level:

- A small share of California’s ≥115 kV transmission network intersects **Very High** wildfire hazard zones.
- An even smaller share intersects historical fire perimeters from 1990–2024.
- **Joint exposure**—where Very High hazard zones and historical fire occurrence overlap the same transmission segments—is highly concentrated within a limited subset of corridors rather than being uniformly distributed across the network.

These results indicate that wildfire exposure of the transmission system is not diffuse, but instead accumulates persistently in specific geographic areas.

---

## Limitations

This project measures **geometric overlap only**. It does not estimate ignition probability, fire spread, asset condition, protection systems, vegetation management practices, outage likelihood, or economic impacts. Public wildfire and infrastructure datasets are coarse abstractions of complex physical systems, and transmission geometry coverage is incomplete by design.

Results are intended to support **prioritization and scoping**, not operational decision-making.

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