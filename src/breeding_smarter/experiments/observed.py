"""The registry's view of a running simulation, for one breed (P8 task 8.1 `IncrementalContext`).

Strategies may only use what a kennel club records: registered animals and their recorded
parents, litters, HD grades, DNA test results and EBVs from a registry-only BLUP. This class
keeps that view up to date year by year without reloading anything from disk:

- animals are appended in registration order (each year's new registrations sorted by gid,
  which is birth order), so the recorded pedigree stays topologically ordered and F and D are
  extended incrementally with `inbreeding_extend`;
- recorded parent links are fixed at registration (a parent registered later stays unknown);
- deaths are known once they have happened; HD grades and DNA results once they are recorded;
- EBVs are re-estimated every few years (pedigree BLUP on recorded data only).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from numpy.typing import NDArray

from breeding_smarter.evaluation.blup import GRADE_SCORE, evaluate_arrays, to_index
from breeding_smarter.io.paths import RunPaths
from breeding_smarter.matching.context import DatasetContext, infer_hereditary_clear
from breeding_smarter.pedigree import Pedigree, equivalent_generations, inbreeding_extend
from breeding_smarter.pedigree.core import FloatArray, IntArray
from breeding_smarter.rules.context import ALIVE, RuleContext
from breeding_smarter.sim.genetics import DogGenetics
from breeding_smarter.sim.interfaces import SimSetup
from breeding_smarter.sim.state import DOMESTIC, SimState

EPOCH_YEAR = 1970


def days(
    year: NDArray[np.int64] | NDArray[np.int16], doy: NDArray[np.int64] | NDArray[np.int16]
) -> IntArray:
    base = (np.asarray(year, np.int64) - EPOCH_YEAR).astype("datetime64[Y]").astype("datetime64[D]")
    return np.asarray((base + (np.asarray(doy, np.int64) - 1)).astype(np.int64))


def frac_year_to_day(t: FloatArray) -> IntArray:
    year = np.floor(t).astype(np.int64)
    doy = np.clip(np.floor((t - year) * 365.0).astype(np.int64) + 1, 1, 365)
    return days(year, doy)


class ObservedRegistry:
    """Append-only recorded pedigree, litters and observations of one breed."""

    def __init__(self, state: SimState, genetics: DogGenetics, setup: SimSetup, breed: int):
        self.setup = setup
        self.genetics = genetics
        self.breed = breed
        self.breed_id = setup.breeds[breed].breed_id
        self.testable = [j for j, lc in enumerate(genetics.loci.loci) if lc.testable]
        self.loci = tuple(genetics.loci.loci[j].id for j in self.testable)
        self.penetrance = genetics.penetrance[self.testable]
        self.gid = np.zeros(0, np.int64)
        self.sire = np.zeros(0, np.int64)
        self.dam = np.zeros(0, np.int64)
        self.idx_of: dict[int, int] = {}
        self.F = np.zeros(0)
        self.D = np.zeros(0)
        self.lit_ids: list[int] = []
        self.ebv_index = np.zeros(0)
        self.ebv_accuracy = np.zeros(0)
        a = state.animals
        initial = np.flatnonzero(a.registered & (a.breed == breed))
        self._append(state, initial)
        self._append_litters(state, until_year=state.year)

    # ------------------------------------------------------------------ updates
    @property
    def n(self) -> int:
        return int(self.gid.size)

    def has(self, gid: int) -> bool:
        return gid in self.idx_of

    def idx(self, gids: IntArray) -> IntArray:
        return np.array([self.idx_of.get(int(g), -1) for g in gids], dtype=np.int64)

    def _append(self, state: SimState, gids: IntArray) -> None:
        gids = np.sort(np.asarray(gids, np.int64))
        gids = np.array([g for g in gids if int(g) not in self.idx_of], dtype=np.int64)
        if gids.size == 0:
            return
        a = state.animals
        start = self.n
        for k, g in enumerate(gids):
            self.idx_of[int(g)] = start + k
        known = a.reg_parents_known[gids]

        def link(par: IntArray) -> IntArray:
            out = np.array([self.idx_of.get(int(p), -1) if p >= 0 else -1 for p in par])
            return np.where(known, out, -1).astype(np.int64)

        self.gid = np.r_[self.gid, gids]
        self.sire = np.r_[self.sire, link(a.sire[gids])]
        self.dam = np.r_[self.dam, link(a.dam[gids])]
        ped = self.pedigree(state)
        self.F, self.D = inbreeding_extend(ped, self.F, self.D, start)
        self.ebv_index = np.r_[self.ebv_index, np.full(gids.size, np.nan)]
        self.ebv_accuracy = np.r_[self.ebv_accuracy, np.zeros(gids.size)]

    def _append_litters(self, state: SimState, until_year: int, from_year: int = -(10**9)) -> None:
        L = state.litters
        sel = np.flatnonzero(
            L.registered
            & (L.breed == self.breed)
            & (L.whelp_year >= from_year)
            & (L.whelp_year <= until_year)
        )
        seen = set(self.lit_ids)
        self.lit_ids += [int(i) for i in sel if int(i) not in seen]

    def update(self, state: SimState, year: int) -> int:
        """Append the animals and litters registered during `year`; returns how many animals."""
        a = state.animals
        new = np.flatnonzero(a.registered & (a.breed == self.breed) & (a.reg_year == year))
        before = self.n
        self._append(state, new)
        self._append_litters(state, until_year=year, from_year=year)
        return self.n - before

    # ------------------------------------------------------------------ views
    def pedigree(self, state: SimState) -> Pedigree:
        a = state.animals
        return Pedigree(
            sire=self.sire,
            dam=self.dam,
            sex=a.sex[self.gid],
            birth_year=a.birth_year[self.gid],
            breed=np.zeros(self.n, np.int16),
            ids=self.gid,
            breed_codes=(self.breed_id,),
        )

    def observed_grades(self, now: float) -> NDArray[np.int8]:
        g = self.genetics
        grade = g.grade[self.gid].copy()
        grade[~(g.screen_t[self.gid] < now)] = -1
        return grade

    def observed_dna(self, now: float) -> NDArray[np.int8]:
        g = self.genetics
        tested = g.tested[self.gid][:, self.testable] & (g.test_t[self.gid][:, self.testable] < now)
        return np.where(tested, g.geno[self.gid][:, self.testable], -1).astype(np.int8)

    def evaluate_ebv(
        self, state: SimState, year: int, h2: float, group_years: int = 5, sd_window: int = 5
    ) -> None:
        """Registry-only pedigree BLUP on recorded HD grades as of the end of `year`."""
        grades = self.observed_grades(year + 1.0)
        dom = state.animals.subpop[self.gid] == DOMESTIC
        rec = np.flatnonzero((grades >= 0) & dom)
        y = np.array([GRADE_SCORE["ABCDE"[int(k)]] for k in grades[rec]], dtype=float)
        ped = self.pedigree(state)
        res = evaluate_arrays(ped, self.D, rec.astype(np.int64), y, h2, group_years)
        recent = ped.birth_year > year - sd_window
        self.ebv_index = to_index(res.ebv, recent)
        self.ebv_accuracy = res.accuracy

    def context(self, state: SimState, year: int) -> DatasetContext:
        """A `DatasetContext` of the registry as of Jan 1 of `year` (for `rank_fast`)."""
        a = state.animals
        g = self.gid
        ped = self.pedigree(state)
        birth = days(a.birth_year[g], a.birth_doy[g])
        dead = a.death_year[g] < year
        death = np.where(dead, days(a.death_year[g], a.death_doy[g]), ALIVE)
        L = state.litters
        lit = np.array(self.lit_ids, dtype=np.int64)
        lit_dam = self.idx(L.dam[lit])
        lit_sire = self.idx(L.sire[lit])
        ok = (lit_dam >= 0) & (lit_sire >= 0)
        lit = lit[ok]
        lit_dam, lit_sire = lit_dam[ok], lit_sire[ok]
        lit_f = np.array(
            [
                self.F[self.idx_of[int(p)]] if int(p) in self.idx_of else np.nan
                for p in self._first_pups(state, lit)
            ]
        )
        dna = self.observed_dna(float(year))
        rules = RuleContext.from_arrays(
            ped=ped,
            F=self.F,
            D=self.D,
            reg_no=np.array([f"gid-{x}" for x in g], dtype=object),
            name=np.array([f"gid {x}" for x in g], dtype=object),
            birth_day=birth,
            death_day=death,
            limited=np.zeros(self.n, bool),
            is_local_breed=np.array([self.setup.breeds[self.breed].is_local_breed]),
            hd_grade=self.observed_grades(float(year)),
            loci=self.loci,
            dna=dna,
            lit_dam=lit_dam,
            lit_sire=lit_sire,
            lit_whelp=days(L.whelp_year[lit], L.whelp_doy[lit]),
            lit_mating=days(L.mating_year[lit], L.mating_doy[lit]),
            lit_n_registered=L.n_animals[lit].astype(float),
            lit_f=lit_f,
            domestic=~a.foreign_stub[g],
        )
        geno, inferred = infer_hereditary_clear(dna, ped)
        return DatasetContext(
            tag=f"experiment-{self.breed_id}-{year}",
            run=RunPaths(_NOWHERE),
            animals=pd.DataFrame(),
            ped=ped,
            F=self.F,
            D=self.D,
            eqg=equivalent_generations(ped),
            rules=rules,
            species=self.setup.species,
            loci_cfg=self.genetics.loci,
            penetrance=self.penetrance,
            geno=geno,
            inferred=inferred,
            ebv_index=self.ebv_index.copy(),
            ebv_accuracy=self.ebv_accuracy.copy(),
            lat=np.zeros(self.n),
            lon=np.zeros(self.n),
            breed_sub={self.breed_id: (ped, np.arange(self.n, dtype=np.int64))},
            foreign=a.foreign_stub[g].copy(),
        )

    def _first_pups(self, state: SimState, lit: IntArray) -> IntArray:
        """First registered pup (gid) of each litter, -1 if none (vectorised)."""
        a = state.animals
        has = np.flatnonzero(a.litter >= 0)
        ids, first = np.unique(a.litter[has], return_index=True)
        pos = np.searchsorted(ids, lit)
        pos = np.minimum(pos, max(ids.size - 1, 0))
        found = ids.size > 0 and True
        out = (
            np.where(found & (ids[pos] == lit), has[first[pos]], -1)
            if ids.size
            else (np.full(lit.size, -1))
        )
        return np.asarray(out, dtype=np.int64)


_NOWHERE = Path("/nonexistent-experiment-run")
