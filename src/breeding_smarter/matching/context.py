"""`DatasetContext`: everything the recommender needs for one dataset, built once (P7 task 7.1).

Engine outputs (F, D, EqG) are cached on disk in the run's `cache/` folder (keyed by run id and
engine version); per-breed reference mean kinship is one Colleau pass and is cached in memory.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
from numpy.typing import NDArray

from breeding_smarter.config.loader import load_loci, load_species
from breeding_smarter.config.models import LociConfig, SpeciesConfig
from breeding_smarter.io.cache import pedigree_cache
from breeding_smarter.io.datasets import resolve_dataset
from breeding_smarter.io.parquet import read_table
from breeding_smarter.io.paths import RunPaths
from breeding_smarter.pedigree import ENGINE_VERSION, Pedigree, mean_kinship
from breeding_smarter.pedigree.core import FloatArray, IntArray
from breeding_smarter.rules.context import ALIVE, RuleContext, day_number
from breeding_smarter.schema.tables import (
    ANIMALS,
    BREEDS,
    DNA_TESTS,
    EBV,
    HEALTH_TESTS,
    KENNELS,
    LITTERS,
)

DAYS_PER_YEAR = 365.25


@dataclass(frozen=True)
class BreedReference:
    """Reference population of a breed on a reference date (living, breeding age)."""

    breed: str
    ref_day: int
    mk: FloatArray  # mean kinship of every registry animal to the reference (nan outside breed)
    mean_mk: float
    sd_mk: float
    n_ref: int
    mean_litter_f: float  # mean F of litters born in the 5 years before the reference date
    allele_freq: FloatArray  # per observed locus, from tested animals born in the last 10 years


@dataclass
class DatasetContext:
    """Registry data plus engine outputs; never reads truth tables."""

    tag: str
    run: RunPaths
    animals: pd.DataFrame
    ped: Pedigree
    F: FloatArray
    D: FloatArray
    eqg: FloatArray
    rules: RuleContext
    species: SpeciesConfig
    loci_cfg: LociConfig
    penetrance: FloatArray  # per observed locus
    geno: NDArray[np.int8]  # [n, loci] known (tested or inferred) risk alleles, -1 unknown
    inferred: NDArray[np.bool_]  # [n, loci] hereditary-clear inference
    ebv_index: FloatArray  # nan if missing
    ebv_accuracy: FloatArray
    lat: FloatArray
    lon: FloatArray
    breed_sub: dict[str, tuple[Pedigree, IntArray]]  # sub-pedigree and old-to-new map
    foreign: NDArray[np.bool_] | None = None  # foreign pedigree records (else from animals)
    extra_offspring: FloatArray | None = None  # planned offspring this year (experiments)
    _refs: dict[tuple[str, int], BreedReference] = field(default_factory=dict, repr=False)

    @property
    def n(self) -> int:
        return self.ped.n

    @property
    def loci(self) -> tuple[str, ...]:
        return self.rules.loci

    def idx_of(self, reg_no: str) -> int:
        hits = np.flatnonzero(self.rules.reg_no == reg_no)
        if hits.size == 0:
            raise KeyError(f"unknown reg_no {reg_no!r}")
        return int(hits[0])

    def breed_of(self, i: int) -> str:
        return self.ped.breed_codes[int(self.ped.breed[i])]

    @property
    def is_foreign(self) -> NDArray[np.bool_]:
        """Foreign pedigree records (studbook FOREIGN, e.g. foreign AI sires); cached."""
        if self.foreign is not None:
            return self.foreign
        v = self.__dict__.get("_is_foreign")
        if v is None:
            v = np.asarray(self.animals["studbook"].to_numpy() == "FOREIGN")
            self.__dict__["_is_foreign"] = v
        return v

    @property
    def cache_key(self) -> str:
        return f"{self.tag}:{self.run.run_id}:engine{ENGINE_VERSION}"

    # ------------------------------------------------------------------ build
    @classmethod
    def load(cls, tag: str = "v1") -> DatasetContext:
        rp = resolve_dataset(tag)
        return cls.from_run(rp, tag)

    @classmethod
    def from_run(cls, rp: RunPaths, tag: str | None = None) -> DatasetContext:
        animals = read_table(rp.table(ANIMALS), ANIMALS)
        litters = read_table(rp.table(LITTERS), LITTERS)
        health = read_table(rp.table(HEALTH_TESTS), HEALTH_TESTS)
        dna = read_table(rp.table(DNA_TESTS), DNA_TESTS)
        breeds = read_table(rp.table(BREEDS), BREEDS)
        ebv = read_table(rp.table(EBV), EBV)
        kennels = read_table(rp.table(KENNELS), KENNELS)
        snap = rp.config_snapshot
        loci_files = sorted((snap / "loci").glob("*.yaml")) if (snap / "loci").is_dir() else []
        loci_cfg = load_loci(loci_files[0].stem, base=snap) if loci_files else load_loci()
        sp_files = sorted((snap / "species").glob("*.yaml"))
        species = load_species(sp_files[0].stem, base=snap) if sp_files else load_species()
        F, D, eqg = pedigree_cache(rp, "registry")
        ped = Pedigree.from_registry(animals)
        rules = RuleContext.from_tables(animals, litters, health, dna, breeds, F=F, D=D, ped=ped)
        pen_of = {x.id: x.penetrance.value for x in loci_cfg.loci}
        penetrance = np.array([pen_of.get(lc, 1.0) for lc in rules.loci])
        geno, inferred = infer_hereditary_clear(rules.dna, ped)
        ebv_index = np.full(ped.n, np.nan)
        ebv_acc = np.zeros(ped.n)
        latest = ebv.sort_values("evaluation_date").groupby("idx").tail(1)
        ebv_index[latest["idx"].to_numpy(np.int64)] = latest["ebv_index"].to_numpy()
        ebv_acc[latest["idx"].to_numpy(np.int64)] = latest["accuracy"].to_numpy()
        k = kennels.set_index("kennel_id")
        owner = animals["owner_id"].to_numpy(np.int64)
        lat = k["lat"].reindex(owner).to_numpy(dtype=float)
        lon = k["lon"].reindex(owner).to_numpy(dtype=float)
        subs = {b: ped.prune(ped.breed_mask(b)) for b in ped.breed_codes}
        return cls(
            tag=tag or rp.run_id,
            run=rp,
            animals=animals,
            ped=ped,
            F=F,
            D=D,
            eqg=eqg,
            rules=rules,
            species=species,
            loci_cfg=loci_cfg,
            penetrance=penetrance,
            geno=geno,
            inferred=inferred,
            ebv_index=ebv_index,
            ebv_accuracy=ebv_acc,
            lat=lat,
            lon=lon,
            breed_sub=subs,
        )

    # ------------------------------------------------------------------ references
    def reference(
        self, breed: str, ref_date: str | int, af_window_years: int = 10
    ) -> BreedReference:
        """Reference population on Jan 1 of the reference date's year (cached per year)."""
        day = ref_date if isinstance(ref_date, int) else day_number(ref_date)
        year = int(np.datetime64(day, "D").astype("datetime64[Y]").astype(np.int64)) + 1970
        key = (breed, year)
        if key in self._refs:
            return self._refs[key]
        jan1 = day_number(f"{year}-01-01")
        sub, old_to_new = self.breed_sub[breed]
        kept = np.flatnonzero(old_to_new >= 0)
        r = self.rules
        alive = (r.birth_day[kept] <= jan1) & (jan1 < r.death_day[kept])
        age_y = (jan1 - r.birth_day[kept]) / DAYS_PER_YEAR
        sp = self.species
        min_age = (
            np.where(
                sub.sex == 1,
                sp.min_breeding_age_months.male.value,
                sp.min_breeding_age_months.female.value,
            )
            / 12.0
        )
        max_age = np.where(
            sub.sex == 1,
            sp.max_breeding_age_years.male.value,
            sp.max_breeding_age_years.female.value,
        )
        in_breed = sub.breed == sub.breed_codes.index(breed)
        ref = alive & in_breed & (age_y >= min_age) & (age_y <= max_age)
        if not ref.any():
            raise ValueError(f"no reference animals for {breed} on {year}-01-01")
        mk_sub = mean_kinship(sub, self.D[kept], ref)
        mk = np.full(self.n, np.nan)
        mk[kept] = mk_sub
        bcode = self.ped.breed_codes.index(breed)
        born = r.birth_day
        win = (self.ped.breed == bcode) & (born >= jan1 - int(af_window_years * DAYS_PER_YEAR))
        win &= born < jan1
        tested = self.rules.dna[win]
        af = np.array(
            [
                float(tested[tested[:, j] >= 0, j].mean() / 2)
                if (tested[:, j] >= 0).any()
                else _overall_freq(self.rules.dna[self.ped.breed == bcode][:, j])
                for j in range(len(self.loci))
            ]
        )
        out = BreedReference(
            breed=breed,
            ref_day=jan1,
            mk=mk,
            mean_mk=float(mk_sub[ref].mean()),
            sd_mk=float(mk_sub[ref].std()) or 1e-9,
            n_ref=int(ref.sum()),
            mean_litter_f=r.breed_mean_litter_f(bcode, jan1),
            allele_freq=af,
        )
        self._refs[key] = out
        return out

    def alive_on(self, idx: IntArray, day: int) -> NDArray[np.bool_]:
        r = self.rules
        return np.asarray((r.birth_day[idx] <= day) & (day < r.death_day[idx]))

    def age_years(self, idx: IntArray | int, day: int) -> FloatArray:
        return np.asarray((day - self.rules.birth_day[idx]) / DAYS_PER_YEAR, dtype=float)

    @property
    def is_dead_marker(self) -> int:
        return ALIVE


def _overall_freq(col: NDArray[np.int8]) -> float:
    t = col[col >= 0]
    return float(t.mean() / 2) if t.size else 0.0


def infer_hereditary_clear(
    dna: NDArray[np.int8], ped: Pedigree
) -> tuple[NDArray[np.int8], NDArray[np.bool_]]:
    """Hereditary clear (one generation): an untested animal whose sire and dam are both
    tested clear is clear; flagged as inferred."""
    if dna.shape[1] == 0:
        return dna.copy(), np.zeros(dna.shape, bool)
    s, d = ped.sire, ped.dam
    both = (s >= 0) & (d >= 0)
    ps = np.where(both[:, None], dna[np.maximum(s, 0)], -1)
    pd_ = np.where(both[:, None], dna[np.maximum(d, 0)], -1)
    inferred = (dna < 0) & (ps == 0) & (pd_ == 0)
    geno = dna.copy()
    geno[inferred] = 0
    return geno, inferred


def load_context(tag: str = "v1") -> DatasetContext:
    return DatasetContext.load(tag)


def context_from_path(path: Path) -> DatasetContext:
    return DatasetContext.from_run(RunPaths(Path(path)))
