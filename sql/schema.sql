-- Track data sources
CREATE TABLE IF NOT EXISTS meta_sources (
    source_name TEXT PRIMARY KEY,
    source_url TEXT,
    retrieved_date DATE,
    notes TEXT
);

-- Wildfire hazard zones (CAL FIRE FHSZ)
CREATE TABLE IF NOT EXISTS hazard_fhsz (
    id SERIAL PRIMARY KEY,
    hazard_class TEXT,
    responsibility TEXT,
    geom GEOMETRY(MULTIPOLYGON, 4326)
);

-- Historical wildfire perimeters
CREATE TABLE IF NOT EXISTS fire_perimeters (
    id SERIAL PRIMARY KEY,
    fire_name TEXT,
    fire_year INTEGER,
    source TEXT,
    geom GEOMETRY(MULTIPOLYGON, 4326)
);

-- Transmission lines
CREATE TABLE IF NOT EXISTS transmission_lines (
    id SERIAL PRIMARY KEY,
    name TEXT,
    voltage_kv INTEGER,
    source TEXT,
    geom GEOMETRY(MULTILINESTRING, 4326)
);
