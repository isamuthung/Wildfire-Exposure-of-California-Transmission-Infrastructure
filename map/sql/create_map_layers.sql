BEGIN;

-- Drop tables (CASCADE removes dependent indexes/views)
DROP TABLE IF EXISTS map_tx_lines_all CASCADE;
DROP TABLE IF EXISTS map_tx_segments_vh CASCADE;
DROP TABLE IF EXISTS map_tx_segments_joint CASCADE;
DROP TABLE IF EXISTS map_polygons_vh CASCADE;
DROP TABLE IF EXISTS map_polygons_fire_union CASCADE;

-- Drop orphaned composite types (Postgres creates a row type for each table)
DROP TYPE IF EXISTS map_tx_lines_all CASCADE;
DROP TYPE IF EXISTS map_tx_segments_vh CASCADE;
DROP TYPE IF EXISTS map_tx_segments_joint CASCADE;
DROP TYPE IF EXISTS map_polygons_vh CASCADE;
DROP TYPE IF EXISTS map_polygons_fire_union CASCADE;

-- -------------------------------------------------------------------
-- 1) Base lines (all)
-- -------------------------------------------------------------------
CREATE TABLE map_tx_lines_all AS
SELECT
  t.line_id,
  t.owner,
  t.voltage_kv,
  ST_Transform(t.geom, 4326) AS geom
FROM tx_lines_3310 t;

ALTER TABLE map_tx_lines_all ADD PRIMARY KEY (line_id);
CREATE INDEX IF NOT EXISTS idx_map_tx_lines_all_geom_gist ON map_tx_lines_all USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_map_tx_lines_all_voltage ON map_tx_lines_all (voltage_kv);
CREATE INDEX IF NOT EXISTS idx_map_tx_lines_all_owner ON map_tx_lines_all (owner);
ANALYZE map_tx_lines_all;

-- -------------------------------------------------------------------
-- 2) Very High FHSZ segments (clipped line segments)
-- -------------------------------------------------------------------
CREATE TABLE map_tx_segments_vh AS
WITH vh_union AS (
  SELECT ST_UnaryUnion(ST_Collect(geom)) AS geom
  FROM hazard_fhsz_3310
  WHERE hazard_class = 'Very High'
),
vh_clip AS (
  SELECT
    t.line_id,
    t.owner,
    t.voltage_kv,
    ST_Intersection(t.geom, v.geom) AS inter_geom
  FROM tx_lines_3310 t
  CROSS JOIN vh_union v
  WHERE ST_Intersects(t.geom, v.geom)
),
vh_lines AS (
  SELECT
    line_id,
    owner,
    voltage_kv,
    ST_CollectionExtract(inter_geom, 2) AS geom
  FROM vh_clip
  WHERE inter_geom IS NOT NULL
    AND NOT ST_IsEmpty(inter_geom)
)
SELECT
  line_id,
  owner,
  voltage_kv,
  'Very High'::text AS hazard_class,
  (ST_Length(geom) / 1000.0) AS seg_km,
  ST_Transform(geom, 4326) AS geom
FROM vh_lines
WHERE geom IS NOT NULL
  AND NOT ST_IsEmpty(geom);

CREATE INDEX IF NOT EXISTS idx_map_tx_segments_vh_geom_gist ON map_tx_segments_vh USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_map_tx_segments_vh_line ON map_tx_segments_vh (line_id);
ANALYZE map_tx_segments_vh;

-- -------------------------------------------------------------------
-- 3) Joint exposure segments (Very High ∩ Historical fire union)
-- -------------------------------------------------------------------
CREATE TABLE map_tx_segments_joint AS
WITH fire AS (
  SELECT geom FROM fire_union_3310
),
joint_clip AS (
  SELECT
    v.line_id,
    v.owner,
    v.voltage_kv,
    ST_Intersection(ST_Transform(v.geom, 3310), f.geom) AS inter_geom
  FROM map_tx_segments_vh v
  CROSS JOIN fire f
  WHERE ST_Intersects(ST_Transform(v.geom, 3310), f.geom)
),
joint_lines AS (
  SELECT
    line_id,
    owner,
    voltage_kv,
    ST_CollectionExtract(inter_geom, 2) AS geom
  FROM joint_clip
  WHERE inter_geom IS NOT NULL
    AND NOT ST_IsEmpty(inter_geom)
)
SELECT
  line_id,
  owner,
  voltage_kv,
  (ST_Length(geom) / 1000.0) AS seg_km,
  ST_Transform(geom, 4326) AS geom
FROM joint_lines
WHERE geom IS NOT NULL
  AND NOT ST_IsEmpty(geom);

CREATE INDEX IF NOT EXISTS idx_map_tx_segments_joint_geom_gist ON map_tx_segments_joint USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_map_tx_segments_joint_line ON map_tx_segments_joint (line_id);
ANALYZE map_tx_segments_joint;

-- -------------------------------------------------------------------
-- 4) Optional polygon backdrops
-- -------------------------------------------------------------------
CREATE TABLE map_polygons_vh AS
WITH vh_union AS (
  SELECT ST_UnaryUnion(ST_Collect(geom)) AS geom
  FROM hazard_fhsz_3310
  WHERE hazard_class = 'Very High'
),
vh_simplified AS (
  SELECT ST_SimplifyPreserveTopology(geom, 250) AS geom
  FROM vh_union
)
SELECT
  'Very High'::text AS hazard_class,
  ST_Transform(geom, 4326) AS geom
FROM vh_simplified;

CREATE INDEX IF NOT EXISTS idx_map_polygons_vh_geom_gist ON map_polygons_vh USING GIST (geom);
ANALYZE map_polygons_vh;

CREATE TABLE map_polygons_fire_union AS
WITH f AS (
  SELECT geom FROM fire_union_3310
),
f_simplified AS (
  SELECT ST_SimplifyPreserveTopology(geom, 250) AS geom
  FROM f
)
SELECT
  'Fire union'::text AS name,
  ST_Transform(geom, 4326) AS geom
FROM f_simplified;

CREATE INDEX IF NOT EXISTS idx_map_polygons_fire_union_geom_gist ON map_polygons_fire_union USING GIST (geom);
ANALYZE map_polygons_fire_union;

COMMIT;
