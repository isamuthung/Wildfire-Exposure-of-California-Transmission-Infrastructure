#!/usr/bin/env python3
"""
00_check_env.py

Environment + dependency checks for reproducible runs.
- Validates .env variables
- Validates DB connectivity
- Validates PostGIS availability
- Checks presence of required directories
- Optionally checks external tools (docker, tippecanoe, jupyter)

Exit code:
  0 = OK
  1 = Missing configuration or dependency
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


REQUIRED_ENV_VARS = [
    "DB_USER",
    "DB_PASSWORD",
    "DB_NAME",
]

OPTIONAL_ENV_DEFAULTS = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
}

REQUIRED_DIRS = [
    "data/raw",
    "outputs/tables",
    "outputs/figures",
    "scripts",
    "sql",
]

OPTIONAL_TOOLS = {
    "docker": "Docker (required to run local tileserver + optional DB containers)",
    "tippecanoe": "Tippecanoe (required to build vector tiles)",
    "jupyter": "Jupyter (required if scripts execute notebooks)",
}


def repo_root() -> Path:
    cwd = Path.cwd()
    # Allow running from repo root OR from scripts/
    if cwd.name == "scripts":
        return cwd.parent
    return cwd


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


def warn(msg: str) -> None:
    print(f"[WARN] {msg}")


def ok(msg: str) -> None:
    print(f"[OK] {msg}")


def check_env(root: Path) -> None:
    env_path = root / ".env"
    if not env_path.exists():
        fail(f"Missing .env file at {env_path}")

    load_dotenv(env_path)

    for k, v in OPTIONAL_ENV_DEFAULTS.items():
        os.environ.setdefault(k, v)

    missing = [k for k in REQUIRED_ENV_VARS if not os.getenv(k)]
    if missing:
        fail(f"Missing required env vars in .env: {missing}")

    ok("Loaded .env and found required DB_* variables.")


def check_dirs(root: Path) -> None:
    for d in REQUIRED_DIRS:
        p = root / d
        if not p.exists():
            warn(f"Missing directory: {p} (creating it)")
            p.mkdir(parents=True, exist_ok=True)
    ok("Required directory structure is present.")


def get_engine() -> object:
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")

    url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    return create_engine(url)


def check_db() -> None:
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("SELECT 1;"))
    ok("Connected to Postgres successfully.")


def check_postgis() -> None:
    engine = get_engine()
    with engine.begin() as conn:
        # Check extension availability + basic function
        ext = conn.execute(
            text("SELECT extname FROM pg_extension WHERE extname='postgis';")
        ).fetchone()
        if not ext:
            warn("PostGIS extension not found in this database. Attempting to create it...")
            try:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
            except Exception as e:
                fail(f"Could not create PostGIS extension. Error: {e}")

        # Verify geometry type exists
        conn.execute(text("SELECT ST_AsText(ST_Point(0,0));"))
    ok("PostGIS is available and functional.")


def check_tools() -> None:
    for tool, desc in OPTIONAL_TOOLS.items():
        if shutil.which(tool) is None:
            warn(f"Tool not found: {tool}. ({desc})")
        else:
            ok(f"Tool found: {tool}")


def main() -> None:
    root = repo_root()
    print(f"Repo root: {root}")

    check_env(root)
    check_dirs(root)
    check_db()
    check_postgis()
    check_tools()

    print("\nAll checks completed.")
    print("Next suggested step: python scripts/01_verify_data_paths.py")
    sys.exit(0)


if __name__ == "__main__":
    main()
