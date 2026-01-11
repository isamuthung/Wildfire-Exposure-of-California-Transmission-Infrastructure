import os
import threading
import time
from pathlib import Path

import geopandas as gpd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


def get_engine():
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "wildfire_grid")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")

    if not db_user or not db_password:
        raise ValueError("Missing DB_USER or DB_PASSWORD in environment (.env).")

    url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    return create_engine(url)


def _start_heartbeat(stop_event: threading.Event, interval_sec: int = 20):
    """
    Prints periodic updates so you know the script is still running.
    """
    start = time.time()
    while not stop_event.is_set():
        elapsed = int(time.time() - start)
        print(f"...still running ({elapsed}s elapsed)")
        stop_event.wait(interval_sec)


def split_sql_statements(sql: str):
    """
    Simple SQL splitter for our controlled SQL file.
    Assumptions:
      - no semicolons inside string literals
      - no procedural blocks requiring semicolons inside DO $$ ... $$ (we don't use those here)
    """
    parts = sql.split(";")
    stmts = []
    for p in parts:
        s = p.strip()
        if not s:
            continue
        # skip pure-line comments blocks
        if all(line.strip().startswith("--") or line.strip() == "" for line in s.splitlines()):
            continue
        stmts.append(s)
    return stmts


def run_sql_file(engine, sql_path: Path, heartbeat_sec: int = 20):
    sql = sql_path.read_text(encoding="utf-8")
    stmts = split_sql_statements(sql)

    if not stmts:
        raise ValueError(f"No executable SQL statements found in {sql_path}")

    print(f"SQL statements to execute: {len(stmts)}")
    stop_event = threading.Event()
    hb_thread = threading.Thread(target=_start_heartbeat, args=(stop_event, heartbeat_sec), daemon=True)

    with engine.begin() as conn:
        hb_thread.start()
        try:
            for i, stmt in enumerate(stmts, start=1):
                preview = " ".join(stmt.split())[:120]
                print(f"[{i}/{len(stmts)}] Executing: {preview} ...")
                conn.execute(text(stmt))
        finally:
            stop_event.set()
            hb_thread.join(timeout=1)

    print("SQL execution complete.")


def export_table(engine, table: str, out_path: Path, geom_col: str = "geom"):
    query = f"SELECT * FROM {table};"
    gdf = gpd.read_postgis(query, engine, geom_col=geom_col)

    if gdf.empty:
        raise ValueError(f"Export table {table} returned 0 rows.")

    # Ensure WGS84
    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")
    else:
        gdf = gdf.to_crs("EPSG:4326")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(out_path, driver="GeoJSON")
    print(f"Wrote {out_path}  (rows={len(gdf):,})")


def main():
    repo_root = Path.cwd()
    if repo_root.name == "scripts":
        repo_root = repo_root.parent

    load_dotenv(repo_root / ".env")

    sql_path = repo_root / "sql" / "queries" / "05_create_map_layers.sql"
    if not sql_path.exists():
        raise FileNotFoundError(f"Missing SQL file: {sql_path}")

    export_dir = repo_root / "map" / "export"
    export_dir.mkdir(parents=True, exist_ok=True)

    engine = get_engine()

    print("Running SQL to create map layers...")
    run_sql_file(engine, sql_path, heartbeat_sec=20)

    layers = {
        "map_tx_lines_all": export_dir / "tx_lines_all.geojson",
        "map_tx_segments_vh": export_dir / "tx_segments_vh.geojson",
        "map_tx_segments_joint": export_dir / "tx_segments_joint.geojson",
        # optional polygon backdrops:
        "map_polygons_vh": export_dir / "polygons_vh.geojson",
        "map_polygons_fire_union": export_dir / "polygons_fire_union.geojson",
    }

    print("Exporting GeoJSON layers...")
    for table, path in layers.items():
        print(f"Export: {table} -> {path.name}")
        export_table(engine, table, path)

    print("Done.")


if __name__ == "__main__":
    main()
