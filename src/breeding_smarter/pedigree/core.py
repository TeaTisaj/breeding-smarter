"""The `Pedigree` container (struct of numpy arrays in topological order).

Notation used throughout `breeding_smarter.pedigree`:

- Animals are numbered `0..n-1` in birth order; `sire[i] < i`, `dam[i] < i`, unknown parent `-1`.
- **A** is the numerator relationship matrix; `A[i,i] = 1 + F_i`; kinship `f_ij = A[i,j] / 2`.
- The inbreeding of a (possibly hypothetical) offspring of `a x b` equals `f_ab`.
- `A = L D L'` (equivalently `A = T D T'` with `T = (I - P)^-1`, `P[i,s] = P[i,d] = 0.5`).
- `D_i = 0.5 - 0.25 (F_s + F_d)` with the convention `F[-1] = -1` for unknown parents: `0.5 -
  0.25 (F_s + F_d)` with both parents known, `0.75 - 0.25 F_known` with one, `1` with none.

References: Wright 1922; Meuwissen and Luo 1992; Colleau 2002; Sargolzaei et al. 2005
(`docs/research.md` section 6).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from numpy.typing import NDArray

IntArray = NDArray[np.int64]
FloatArray = NDArray[np.float64]
MALE, FEMALE = 1, 0


class PedigreeError(ValueError):
    """The pedigree violates an invariant (topological order, parent sex, self-parenting)."""


def _as_int64(x: object) -> IntArray:
    return np.ascontiguousarray(np.asarray(x, dtype=np.int64))


@dataclass(frozen=True)
class Pedigree:
    """Parents, sex, birth year and breed of `n` animals in topological (birth) order.

    `sex`: 1 male, 0 female. `ids`: original registry idx or truth gid (-1 for phantoms).
    """

    sire: IntArray
    dam: IntArray
    sex: NDArray[np.int8]
    birth_year: NDArray[np.int16]
    breed: NDArray[np.int16]
    ids: IntArray
    breed_codes: tuple[str, ...] = ()

    def __len__(self) -> int:
        return int(self.sire.shape[0])

    @property
    def n(self) -> int:
        return len(self)

    @classmethod
    def from_arrays(
        cls,
        sire: object,
        dam: object,
        sex: object,
        birth_year: object | None = None,
        breed: object | None = None,
        ids: object | None = None,
        breed_codes: tuple[str, ...] = (),
        validate: bool = True,
    ) -> Pedigree:
        s = _as_int64(sire)
        n = s.shape[0]
        ped = cls(
            sire=s,
            dam=_as_int64(dam),
            sex=np.asarray(sex, dtype=np.int8),
            birth_year=(
                np.zeros(n, np.int16) if birth_year is None else np.asarray(birth_year, np.int16)
            ),
            breed=np.zeros(n, np.int16) if breed is None else np.asarray(breed, np.int16),
            ids=np.arange(n, dtype=np.int64) if ids is None else _as_int64(ids),
            breed_codes=breed_codes,
        )
        if validate:
            ped.validate()
        return ped

    @staticmethod
    def _parents(col: pd.Series) -> IntArray:
        return _as_int64(pd.Series(col, dtype="Int64").fillna(-1).to_numpy(dtype=np.int64))

    @classmethod
    def _encode(cls, df: pd.DataFrame, sire: IntArray, dam: IntArray, years: object) -> Pedigree:
        codes, uniques = pd.factorize(df["breed_id"], sort=True)
        sex = (df["sex"].to_numpy() == "M").astype(np.int8)
        return cls.from_arrays(
            sire,
            dam,
            sex,
            birth_year=years,
            breed=codes.astype(np.int16),
            breed_codes=tuple(str(u) for u in uniques),
        )

    @classmethod
    def from_registry(cls, animals: pd.DataFrame) -> Pedigree:
        """From `registry/animals` (idx must be 0..n-1 in order)."""
        idx = animals["idx"].to_numpy(dtype=np.int64)
        if not np.array_equal(idx, np.arange(len(idx))):
            raise PedigreeError("registry idx must be contiguous 0..n-1 in row order")
        years = pd.to_datetime(animals["birth_date"]).dt.year.to_numpy()
        return cls._encode(
            animals, cls._parents(animals["sire_idx"]), cls._parents(animals["dam_idx"]), years
        )

    @classmethod
    def from_truth(cls, truth: pd.DataFrame) -> Pedigree:
        """From `truth/animals_truth` (gid must be 0..n-1 in order; true parents)."""
        gid = truth["gid"].to_numpy(dtype=np.int64)
        if not np.array_equal(gid, np.arange(len(gid))):
            raise PedigreeError("truth gid must be contiguous 0..n-1 in row order")
        return cls._encode(
            truth,
            cls._parents(truth["true_sire_gid"]),
            cls._parents(truth["true_dam_gid"]),
            truth["birth_year"].to_numpy(),
        )

    def validate(self) -> None:
        """Raise `PedigreeError` on topological order, parent sex or self-parenting errors."""
        n = self.n
        for name, arr in (("sex", self.sex), ("dam", self.dam), ("birth_year", self.birth_year)):
            if arr.shape[0] != n:
                raise PedigreeError(f"{name} has length {arr.shape[0]}, expected {n}")
        i = np.arange(n)
        for name, par, sex in (("sire", self.sire, MALE), ("dam", self.dam, FEMALE)):
            bad = np.flatnonzero((par >= i) | (par < -1))
            if bad.size:
                raise PedigreeError(f"{name} breaks topological order at rows {bad[:5].tolist()}")
            known = par >= 0
            bad = np.flatnonzero(known & (self.sex[np.where(known, par, 0)] != sex))
            if bad.size:
                raise PedigreeError(f"{name} has the wrong sex at rows {bad[:5].tolist()}")

    def subset_arrays(self, keep: NDArray[np.bool_]) -> tuple[Pedigree, IntArray]:
        """Keep exactly the rows in `keep` (must be closed under ancestry) and renumber."""
        old_to_new = np.full(self.n, -1, dtype=np.int64)
        old_to_new[keep] = np.arange(int(keep.sum()), dtype=np.int64)

        def remap(par: IntArray) -> IntArray:
            p = par[keep]
            return np.where(p >= 0, old_to_new[np.maximum(p, 0)], -1)

        ped = Pedigree(
            sire=remap(self.sire),
            dam=remap(self.dam),
            sex=self.sex[keep],
            birth_year=self.birth_year[keep],
            breed=self.breed[keep],
            ids=self.ids[keep],
            breed_codes=self.breed_codes,
        )
        return ped, old_to_new

    def ancestors_mask(self, keep: NDArray[np.bool_] | IntArray) -> NDArray[np.bool_]:
        """Boolean mask of `keep` plus all their ancestors (one backward sweep, O(n))."""
        mark = np.zeros(self.n, dtype=np.bool_)
        mark[keep] = True
        return _mark_ancestors(self.sire, self.dam, mark)

    def prune(self, keep: NDArray[np.bool_] | IntArray) -> tuple[Pedigree, IntArray]:
        """Keep the given animals plus all their ancestors; renumber preserving order.

        Returns the pruned pedigree and the old-to-new index map (-1 for dropped animals).
        F, D and kinships among kept animals are unchanged by pruning.
        """
        return self.subset_arrays(self.ancestors_mask(keep))

    def with_phantom_parents(self) -> tuple[Pedigree, IntArray]:
        """Insert a unique phantom founder for each missing parent of half-known animals.

        Phantoms (ids = -1) are inserted right before their child, which keeps topological
        order. Needed so founder contributions sum to 1. Returns the new pedigree and the
        old-to-new index map.
        """
        half = (self.sire >= 0) != (self.dam >= 0)
        n_new = self.n + int(half.sum())
        shift = np.cumsum(half)  # phantoms inserted up to and including row i
        old_to_new = np.arange(self.n, dtype=np.int64) + shift
        phantom_pos = old_to_new[half] - 1
        sire = np.full(n_new, -1, np.int64)
        dam = np.full(n_new, -1, np.int64)
        known_s = self.sire >= 0
        known_d = self.dam >= 0
        sire[old_to_new] = np.where(known_s, old_to_new[np.maximum(self.sire, 0)], -1)
        dam[old_to_new] = np.where(known_d, old_to_new[np.maximum(self.dam, 0)], -1)
        child_rows = old_to_new[half]
        missing_sire = ~known_s[half]
        sire[child_rows[missing_sire]] = phantom_pos[missing_sire]
        dam[child_rows[~missing_sire]] = phantom_pos[~missing_sire]

        def spread[T: np.generic](arr: NDArray[T], phantom_vals: NDArray[T]) -> NDArray[T]:
            out = np.empty(n_new, dtype=arr.dtype)
            out[old_to_new] = arr
            out[phantom_pos] = phantom_vals
            return out

        ped = Pedigree(
            sire=sire,
            dam=dam,
            sex=spread(self.sex, np.where(missing_sire, MALE, FEMALE).astype(np.int8)),
            birth_year=spread(self.birth_year, self.birth_year[half]),
            breed=spread(self.breed, self.breed[half]),
            ids=spread(self.ids, np.full(int(half.sum()), -1, np.int64)),
            breed_codes=self.breed_codes,
        )
        return ped, old_to_new

    def offspring_index(self) -> tuple[IntArray, IntArray]:
        """CSR arrays: children of animal `i` are `children[ptr[i]:ptr[i+1]]` (sorted)."""
        par = np.concatenate([self.sire, self.dam])
        child = np.concatenate([np.arange(self.n), np.arange(self.n)])
        known = par >= 0
        par, child = par[known], child[known]
        order = np.lexsort((child, par))
        counts = np.bincount(par, minlength=self.n)
        ptr = np.zeros(self.n + 1, dtype=np.int64)
        np.cumsum(counts, out=ptr[1:])
        return ptr, child[order].astype(np.int64)

    def breed_mask(self, breed_id: str) -> NDArray[np.bool_]:
        code = self.breed_codes.index(breed_id)
        return np.asarray(self.breed == code)


def _mark_ancestors(sire: IntArray, dam: IntArray, mark: NDArray[np.bool_]) -> NDArray[np.bool_]:
    from breeding_smarter.pedigree._kernels import mark_ancestors

    return mark_ancestors(sire, dam, mark)
