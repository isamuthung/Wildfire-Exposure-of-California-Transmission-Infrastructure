CREATE INDEX IF NOT EXISTS idx_hazard_fhsz_geom
ON hazard_fhsz
USING GIST (geom);

CREATE INDEX IF NOT EXISTS idx_fire_perimeters_geom
ON fire_perimeters
USING GIST (geom);

CREATE INDEX IF NOT EXISTS idx_transmission_lines_geom
ON transmission_lines
USING GIST (geom);

CREATE INDEX IF NOT EXISTS idx_fire_perimeters_year
ON fire_perimeters (fire_year);
