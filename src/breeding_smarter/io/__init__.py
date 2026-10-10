"""Parquet IO, run paths, manifests and DuckDB views."""

from breeding_smarter.io.duck import duckdb_connect
from breeding_smarter.io.manifest import read_manifest, update_manifest, write_manifest
from breeding_smarter.io.parquet import SchemaError, read_table, write_table
from breeding_smarter.io.paths import RunPaths, configs_dir, data_dir, make_run_id, repo_root

__all__ = [
    "RunPaths",
    "SchemaError",
    "configs_dir",
    "data_dir",
    "duckdb_connect",
    "make_run_id",
    "read_manifest",
    "read_table",
    "repo_root",
    "update_manifest",
    "write_manifest",
    "write_table",
]
