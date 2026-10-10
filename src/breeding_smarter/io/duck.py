"""DuckDB views over a run folder."""

from __future__ import annotations

from pathlib import Path

import duckdb

from breeding_smarter.schema.tables import ALL_TABLES


def view_name(table_name: str) -> str:
    """`registry/animals` -> `registry_animals`."""
    return table_name.replace("/", "_")


def duckdb_connect(run_dir: Path, database: str = ":memory:") -> duckdb.DuckDBPyConnection:
    """Connect and register every existing Parquet table of the run as a view."""
    con = duckdb.connect(database)
    for spec in ALL_TABLES:
        path = run_dir / spec.filename
        if path.exists():
            p = str(path).replace("'", "''")
            con.execute(f"CREATE VIEW {view_name(spec.name)} AS SELECT * FROM read_parquet('{p}')")
    return con
