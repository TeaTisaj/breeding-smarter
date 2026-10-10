# ADR-001: Parquet files plus DuckDB, not Postgres, for the POC

Status: accepted (2026-10-10)

## Context
The proof of concept must be built in two weeks, published as an open dataset and run on a laptop at the congress.

## Decision
Store every table as Parquet (zstd) in a run folder; query with DuckDB views and pandas. No database server.

## Consequences
- Zero infrastructure: clone, generate, analyse.
- Datasets are trivially publishable (Zenodo, Hugging Face).
- No concurrent writes, auth or multi-tenancy; Postgres plus Django come after the conference when real users exist.
