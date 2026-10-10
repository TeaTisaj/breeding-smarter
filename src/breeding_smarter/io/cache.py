"""Cached engine outputs (F, D, EqG) per run, keyed by run id and engine version."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from breeding_smarter.io.parquet import read_table
from breeding_smarter.io.paths import RunPaths, data_dir
from breeding_smarter.schema.tables import ANIMALS, ANIMALS_TRUTH


def resolve_run(run: str | Path) -> RunPaths:
    """A run given as a folder path or as a run id under the data directory."""
    p = Path(run)
    if p.is_dir():
        return RunPaths(p.resolve())
    rp = RunPaths(data_dir() / str(run))
    if not rp.root.is_dir():
        raise FileNotFoundError(f"run not found: {run} (looked in {rp.root})")
    return rp


def load_registry_animals(run: RunPaths) -> pd.DataFrame:
    return read_table(run.table(ANIMALS), ANIMALS)


def load_truth_animals(run: RunPaths) -> pd.DataFrame:
    return read_table(run.table(ANIMALS_TRUTH), ANIMALS_TRUTH)


def pedigree_cache(
    run: RunPaths, kind: str = "registry"
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """F, D and EqG of the registry (or `truth`) pedigree, computed once and cached."""
    from breeding_smarter.pedigree import (
        ENGINE_VERSION,
        Pedigree,
        equivalent_generations,
        inbreeding,
    )

    path = run.cache / f"pedigree_F_D_{kind}.parquet"
    meta_path = path.with_suffix(".json")
    key = {"run_id": run.run_id, "engine_version": ENGINE_VERSION, "kind": kind}
    if path.exists() and meta_path.exists() and json.loads(meta_path.read_text()) == key:
        t = pq.read_table(path)
        return (
            t.column("F").to_numpy(),
            t.column("D").to_numpy(),
            t.column("eqg").to_numpy(),
        )
    if kind == "registry":
        ped = Pedigree.from_registry(load_registry_animals(run))
    else:
        ped = Pedigree.from_truth(load_truth_animals(run))
    F, D = inbreeding(ped)
    eqg = equivalent_generations(ped)
    run.cache.mkdir(parents=True, exist_ok=True)
    table = pa.table({"id": ped.ids, "F": F, "D": D, "eqg": eqg})
    pq.write_table(table, path, compression="zstd")
    meta_path.write_text(json.dumps(key))
    return F, D, eqg
