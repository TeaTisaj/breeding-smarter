"""Truth-side kinship for the oracle arm and realised coancestry (P12 task 12.7).

`TrueKinship` keeps F and D of the **true** pedigree of the experiment breed (simulator parents,
including unregistered animals) and extends them every year with `inbreeding_extend`, the same
way `ObservedRegistry` does for the recorded pedigree. The simulator's gids are in birth order
and each breed's pedigree is closed, so appending new gids keeps the order topological.
"""

from __future__ import annotations

import numpy as np

from breeding_smarter.experiments.metrics import expected_heterozygosity
from breeding_smarter.pedigree import Pedigree, inbreeding_extend
from breeding_smarter.pedigree.core import FloatArray, IntArray
from breeding_smarter.pedigree.kinship import kinship_matrix
from breeding_smarter.sim.state import SimState


class TrueKinship:
    """Incremental true pedigree (F, D) of one breed; kinship among any of its animals."""

    def __init__(self, state: SimState, breed: int):
        self.breed = breed
        self.gid = np.zeros(0, np.int64)
        self.local: dict[int, int] = {}
        self.F = np.zeros(0)
        self.D = np.zeros(0)
        self.ped: Pedigree | None = None
        self.update(state)

    @property
    def n(self) -> int:
        return int(self.gid.size)

    def update(self, state: SimState) -> int:
        """Append animals of the breed created since the last call; returns how many."""
        a = state.animals
        last = int(self.gid[-1]) if self.n else -1
        new = np.flatnonzero(a.breed[last + 1 :] == self.breed) + last + 1
        if new.size == 0 and self.ped is not None:
            return 0
        start = self.n
        for k, gid in enumerate(new):
            self.local[int(gid)] = start + k
        self.gid = np.r_[self.gid, new]
        g = self.gid

        def loc(par: IntArray) -> IntArray:
            return np.array([self.local.get(int(p), -1) for p in par], dtype=np.int64)

        sire = np.r_[self.ped.sire, loc(a.sire[new])] if self.ped is not None else loc(a.sire[g])
        dam = np.r_[self.ped.dam, loc(a.dam[new])] if self.ped is not None else loc(a.dam[g])
        self.ped = Pedigree.from_arrays(sire, dam, a.sex[g], birth_year=a.birth_year[g])
        self.F, self.D = inbreeding_extend(self.ped, self.F, self.D, start)
        return int(new.size)

    def kinship(self, gids: IntArray) -> FloatArray:
        """Dense true-pedigree kinship among `gids` (all of the breed)."""
        assert self.ped is not None
        idx = np.array([self.local[int(g)] for g in gids], dtype=np.int64)
        return kinship_matrix(self.ped, self.D, idx)


def realised_coancestry(neutral: np.ndarray) -> float:
    """Mean over neutral loci of `sum_a p_a^2` (= 1 - expected heterozygosity)."""
    return 1.0 - expected_heterozygosity(neutral)
