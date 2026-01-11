#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "1) Exporting map layers from PostGIS..."
python "$REPO_ROOT/scripts/05_export_map_layers.py"

echo "2) Building vector tiles..."
bash "$REPO_ROOT/scripts/06_build_vector_tiles.sh"

echo "3) Starting tileserver (http://localhost:8080)..."
cd "$REPO_ROOT/map"
docker compose up
