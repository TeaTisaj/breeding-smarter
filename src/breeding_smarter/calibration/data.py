"""Load a run folder (tables, engine outputs, setup) for calibration metrics."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from breeding_smarter.config.models import BreedConfig
from breeding_smarter.io.cache import pedigree_cache
from breeding_smarter.io.manifest import update_manifest
from breeding_smarter.io.parquet import read_table, write_table
from breeding_smarter.io.paths import RunPaths
from breeding_smarter.pedigree import ENGINE_VERSION, Pedigree
from breeding_smarter.schema.tables import (
    ANIMALS,
    ANIMALS_TRUTH,
    DNA_TESTS,
    EBV,
    GENOTYPES_TRUTH,
    HEALTH_TESTS,
    LITTERS,
)
from breeding_smarter.sim.interfaces import SimSetup
from breeding_smarter.sim.run import load_run_setup


def fill_true_pedigree_f(run: RunPaths) -> np.ndarray:
    """Compute F on the full true pedigree and store it in `truth/animals_truth` (P5 task 5.3).

    Only rewrites the table when the column is still empty (all zeros) or was computed with
    another engine version.
    """
    truth = read_table(run.table(ANIMALS_TRUTH), ANIMALS_TRUTH)
    F, _, _ = pedigree_cache(run, "truth")
    import json

    m = json.loads(run.manifest.read_text())
    if m.get("f_true_pedigree_engine") != ENGINE_VERSION or not np.allclose(
        truth["f_true_pedigree"].to_numpy(), F
    ):
        truth["f_true_pedigree"] = F
        write_table(truth, ANIMALS_TRUTH, run.table(ANIMALS_TRUTH))
        update_manifest(run.manifest, f_true_pedigree_engine=ENGINE_VERSION)
    return F


@dataclass
class RunData:
    """Everything the calibration metrics need, loaded once."""

    run: RunPaths
    setup: SimSetup
    animals: pd.DataFrame
    litters: pd.DataFrame
    health: pd.DataFrame
    dna: pd.DataFrame
    ebv: pd.DataFrame
    truth: pd.DataFrame
    ped: Pedigree
    F: np.ndarray
    D: np.ndarray
    eqg: np.ndarray
    F_true: np.ndarray  # true pedigree F per gid

    @classmethod
    def load(cls, run_dir: Path) -> RunData:
        run = RunPaths(Path(run_dir))
        F_true = fill_true_pedigree_f(run)
        animals = read_table(run.table(ANIMALS), ANIMALS)
        animals["year"] = animals["birth_date"].dt.year
        F, D, eqg = pedigree_cache(run, "registry")
        truth = read_table(run.table(ANIMALS_TRUTH), ANIMALS_TRUTH)
        return cls(
            run=run,
            setup=load_run_setup(run.root),
            animals=animals,
            litters=read_table(run.table(LITTERS), LITTERS),
            health=read_table(run.table(HEALTH_TESTS), HEALTH_TESTS),
            dna=read_table(run.table(DNA_TESTS), DNA_TESTS),
            ebv=read_table(run.table(EBV), EBV),
            truth=truth,
            ped=Pedigree.from_registry(animals),
            F=F,
            D=D,
            eqg=eqg,
            F_true=F_true,
        )

    def genotypes(self) -> pd.DataFrame:
        return read_table(self.run.table(GENOTYPES_TRUTH), GENOTYPES_TRUTH)

    @property
    def breeds(self) -> list[str]:
        return [b.breed_id for b in self.setup.breeds]

    def breed_cfg(self, breed: str) -> BreedConfig:
        return self.setup.breeds[self.breeds.index(breed)]

    @property
    def domestic(self) -> np.ndarray:
        """Registered animals that are not foreign pedigree stubs."""
        return np.asarray(self.animals["studbook"].to_numpy() != "FOREIGN")

    def true_f_of_idx(self) -> np.ndarray:
        """True pedigree F and realised IBD aligned to registry idx: (F_true, f_ibd)."""
        t = self.truth.dropna(subset=["idx"])
        order = t["idx"].astype("int64").to_numpy()
        f_ped = np.empty(len(self.animals))
        f_ibd = np.empty(len(self.animals))
        f_ped[order] = self.F_true[t["gid"].to_numpy()]
        f_ibd[order] = t["f_true_ibd"].to_numpy()
        return np.stack([f_ped, f_ibd])
