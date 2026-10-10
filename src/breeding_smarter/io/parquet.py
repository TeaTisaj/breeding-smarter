"""Parquet read/write that enforces a TableSpec (cast or fail, never silently coerce)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from breeding_smarter.schema.tables import TableSpec

ROW_GROUP_SIZE = 128 * 1024
COMPRESSION = "zstd"

_NULLABLE_INT = {
    pa.int8(): pd.Int8Dtype(),
    pa.int16(): pd.Int16Dtype(),
    pa.int32(): pd.Int32Dtype(),
    pa.int64(): pd.Int64Dtype(),
}


class SchemaError(ValueError):
    """A DataFrame or file does not match its TableSpec."""


def _to_arrow_column(series: pd.Series, field: pa.Field) -> pa.Array:
    if pa.types.is_date32(field.type) and pd.api.types.is_datetime64_any_dtype(series.dtype):
        values = series.to_numpy(dtype="datetime64[D]")
        mask = np.isnat(values)
        return pa.array(values, type=pa.date32(), mask=mask)
    try:
        return pa.array(series, type=field.type, from_pandas=True)
    except (pa.ArrowInvalid, pa.ArrowTypeError) as exc:
        raise SchemaError(f"column {field.name!r}: cannot convert to {field.type}: {exc}") from exc


def to_arrow(df: pd.DataFrame, spec: TableSpec) -> pa.Table:
    """Convert `df` to an Arrow table with exactly the spec's schema.

    Columns must match the spec (same names; order is taken from the spec). Not-null fields
    must have no nulls. Conversions that lose information raise `SchemaError`.
    """
    expected = spec.columns
    missing = [c for c in expected if c not in df.columns]
    extra = [c for c in df.columns if c not in expected]
    if missing or extra:
        raise SchemaError(f"{spec.name}: missing columns {missing}, unexpected columns {extra}")
    arrays = []
    for f in spec.schema:
        arr = _to_arrow_column(df[f.name], f)
        if not f.nullable and arr.null_count:
            raise SchemaError(f"{spec.name}.{f.name}: {arr.null_count} nulls in a not-null field")
        arrays.append(arr)
    return pa.Table.from_arrays(arrays, schema=spec.schema)


def write_table(df: pd.DataFrame, spec: TableSpec, path: Path) -> Path:
    """Write `df` as Parquet (zstd, 128k-row groups) after enforcing the spec."""
    table = to_arrow(df, spec)
    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(
        table,
        path,
        compression=COMPRESSION,
        row_group_size=ROW_GROUP_SIZE,
        write_statistics=True,
    )
    return path


def check_file_schema(path: Path, spec: TableSpec) -> list[str]:
    """Differences between a Parquet file's schema and the spec (empty list if equal)."""
    actual = pq.read_schema(path).remove_metadata()
    problems: list[str] = []
    if actual.names != spec.schema.names:
        problems.append(f"column names {actual.names} != {spec.schema.names}")
        return problems
    for a, e in zip(actual, spec.schema, strict=True):
        if a.type != e.type:
            problems.append(f"{e.name}: type {a.type} != {e.type}")
        if a.nullable != e.nullable:
            problems.append(f"{e.name}: nullable {a.nullable} != {e.nullable}")
    return problems


def from_arrow(table: pa.Table, spec: TableSpec) -> pd.DataFrame:
    """Arrow to pandas: nullable ints become pandas nullable dtypes, dates become datetime64."""
    df = table.to_pandas(
        types_mapper=lambda t: _NULLABLE_INT.get(t), date_as_object=False, ignore_metadata=True
    )
    for f in spec.schema:
        if pa.types.is_integer(f.type) and not f.nullable:
            df[f.name] = df[f.name].astype(f.type.to_pandas_dtype())
    return df


def read_table(path: Path, spec: TableSpec, columns: list[str] | None = None) -> pd.DataFrame:
    """Read a Parquet file and check it against the spec (fails on any schema difference)."""
    problems = check_file_schema(path, spec)
    if problems:
        raise SchemaError(f"{path}: schema does not match {spec.name}: {problems}")
    table = pq.read_table(path, columns=columns)
    if columns is not None:
        sub = TableSpec(spec.name, spec.description, tuple(spec.field(c) for c in columns), ())
        return from_arrow(table, sub)
    return from_arrow(table, spec)
