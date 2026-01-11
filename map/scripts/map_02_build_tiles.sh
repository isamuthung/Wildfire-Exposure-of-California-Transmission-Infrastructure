#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EXPORT_DIR="$REPO_ROOT/map/export"
TILES_DIR="$REPO_ROOT/map/tiles"

mkdir -p "$TILES_DIR"

# Requires tippecanoe installed:
#   macOS: brew install tippecanoe
#   ubuntu: apt install tippecanoe  (or build from source)

echo "Building MBTiles..."

tippecanoe -o "$TILES_DIR/tx.mbtiles" \
  -l tx_lines_all \
  --drop-densest-as-needed \
  --extend-zooms-if-still-dropping \
  --force \
  "$EXPORT_DIR/tx_lines_all.geojson"

tippecanoe -o "$TILES_DIR/exposure.mbtiles" \
  -l tx_segments_vh \
  --drop-densest-as-needed \
  --extend-zooms-if-still-dropping \
  --force \
  "$EXPORT_DIR/tx_segments_vh.geojson"

tippecanoe -o "$TILES_DIR/joint.mbtiles" \
  -l tx_segments_joint \
  --drop-densest-as-needed \
  --extend-zooms-if-still-dropping \
  --force \
  "$EXPORT_DIR/tx_segments_joint.geojson"

if [ -f "$EXPORT_DIR/polygons_vh.geojson" ]; then
  tippecanoe -o "$TILES_DIR/polygons.mbtiles" \
    -l polygons_vh \
    --drop-densest-as-needed \
    --extend-zooms-if-still-dropping \
    --force \
    "$EXPORT_DIR/polygons_vh.geojson"
fi

echo "MBTiles written to: $TILES_DIR"
ls -lh "$TILES_DIR"
