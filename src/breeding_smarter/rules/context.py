"""`RuleContext`: arrays indexed by registry idx, built once per dataset (P6 task 6.2).

No pandas inside rule checks: everything a rule needs is a numpy array here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

import numpy as np
import pandas as pd
from numpy.typing import NDArray

from breeding_smarter.pedigree import Pedigree, inbreeding, kinship_to_all
from breeding_smarter.pedigree.core import FloatArray, IntArray

ALIVE = np.iinfo(np.int64).max
CSR_SHIFT = 1_000_000  # day numbers shifted to be positive (dates after 0710 AD)
CSR_OFFSET = 4_000_000  # > any shifted day number
GRADES = ("A", "B", "C", "D", "E")
GENOTYPES = ("clear", "carrier", "affected")


def day_number(d: date | np.datetime64 | pd.Timestamp | str) -> int:
    """Days since 1970-01-01."""
    return int(np.datetime64(pd.Timestamp(d).date(), "D").astype(np.int64))


def _days(s: pd.Series) -> IntArray:
    v = s.to_numpy(dtype="datetime64[ns]")
    out = v.astype("datetime64[D]").astype(np.int64)
    return np.asarray(np.where(np.isnat(v), ALIVE, out), dtype=np.int64)


@dataclass(frozen=True)
class CSR:
    """Sorted values per key: `values[ptr[k]:ptr[k+1]]`."""

    ptr: IntArray
    values: IntArray
    extra: FloatArray | None = None

    @classmethod
    def build(
        cls, keys: IntArray, values: IntArray, n: int, extra: FloatArray | None = None
    ) -> CSR:
        order = np.lexsort((values, keys))
        k = keys[order]
        ptr = np.zeros(n + 1, np.int64)
        np.cumsum(np.bincount(k, minlength=n), out=ptr[1:])
        return cls(ptr, values[order].astype(np.int64), None if extra is None else extra[order])

    @property
    def _encoded(self) -> IntArray:
        """Globally sorted `key * OFFSET + value` (values are day numbers)."""
        enc = self.__dict__.get("_enc")
        if enc is None:
            n_keys = self.ptr.size - 1
            keys = np.repeat(np.arange(n_keys, dtype=np.int64), np.diff(self.ptr))
            enc = keys * CSR_OFFSET + (self.values + CSR_SHIFT)
            object.__setattr__(self, "_enc", enc)
        return enc

    def count_before(self, keys: IntArray, day: int, since: int | None = None) -> IntArray:
        """Number of values in `[since, day)` (or `< day`) for each key (vectorised)."""
        k = np.asarray(keys, dtype=np.int64) * CSR_OFFSET
        enc = self._encoded
        hi = np.searchsorted(enc, k + day + CSR_SHIFT, side="left")
        lo_v = (since if since is not None else -CSR_SHIFT) + CSR_SHIFT
        lo = np.searchsorted(enc, k + lo_v, side="left")
        return np.asarray(hi - lo, dtype=np.int64)

    def last_before(self, key: int, day: int) -> int | None:
        v = self.values[self.ptr[key] : self.ptr[key + 1]]
        i = int(np.searchsorted(v, day, side="left"))
        return int(v[i - 1]) if i > 0 else None


@dataclass
class RuleContext:
    ped: Pedigree
    F: FloatArray
    D: FloatArray
    reg_no: NDArray[np.object_]
    name: NDArray[np.object_]
    birth_day: IntArray
    death_day: IntArray
    limited: NDArray[np.bool_]
    is_local_breed: NDArray[np.bool_]  # per breed code
    hd_grade: NDArray[np.int8]  # latest official HD grade 0..4, -1 none
    loci: tuple[str, ...]
    dna: NDArray[np.int8]  # [n, loci] risk alleles 0/1/2 from tests, -1 untested
    dam_litters: CSR  # whelp days per dam
    sire_litters: CSR  # mating days per sire
    sire_offspring: CSR  # birth days of registered offspring per sire
    breed_births: CSR  # birth days of registered domestic animals per breed code
    breed_litter_f: CSR  # whelp days per breed with litter F (inbreeding of the pups) in extra
    expected_litter_registered: FloatArray  # per breed code
    _kin_cache: dict[int, FloatArray] = field(default_factory=dict, repr=False)

    @property
    def n(self) -> int:
        return self.ped.n

    def label(self, i: int) -> str:
        return f"{self.name[i]} ({self.reg_no[i]})"

    def kinship_row(self, a: int) -> FloatArray:
        """Kinship of `a` with every animal (one Colleau pass, cached; small LRU)."""
        if a not in self._kin_cache:
            if len(self._kin_cache) > 64:
                self._kin_cache.pop(next(iter(self._kin_cache)))
            self._kin_cache[a] = kinship_to_all(self.ped, self.D, a)
        return self._kin_cache[a]

    def breed_mean_litter_f(self, breed: int, day: int, years: int = 5) -> float:
        """Mean F of litters whelped in the `years` before `day` in the breed."""
        c = self.breed_litter_f
        v = c.values[c.ptr[breed] : c.ptr[breed + 1]]
        e = c.extra
        assert e is not None
        f = e[c.ptr[breed] : c.ptr[breed + 1]]
        lo = np.searchsorted(v, day - int(365.25 * years), side="left")
        hi = np.searchsorted(v, day, side="left")
        return float(f[lo:hi].mean()) if hi > lo else float("nan")

    @classmethod
    def from_tables(
        cls,
        animals: pd.DataFrame,
        litters: pd.DataFrame,
        health: pd.DataFrame,
        dna: pd.DataFrame,
        breeds: pd.DataFrame,
        F: FloatArray | None = None,
        D: FloatArray | None = None,
        ped: Pedigree | None = None,
    ) -> RuleContext:
        ped = ped or Pedigree.from_registry(animals)
        if F is None or D is None:
            F, D = inbreeding(ped)
        n = ped.n
        codes = list(ped.breed_codes)
        local = breeds.set_index("breed_id")["is_local_breed"]
        is_local = np.array([bool(local.get(c, False)) for c in codes])
        hd = health[(health["test_type"] == "HD") & health["official"]].sort_values(
            ["idx", "test_date"], kind="stable"
        )
        hd = hd.groupby("idx").tail(1)
        hd_grade = np.full(n, -1, np.int8)
        hd_grade[hd["idx"].to_numpy(np.int64)] = (
            hd["result"].map({g: i for i, g in enumerate(GRADES)}).to_numpy(np.int8)
        )
        loci = tuple(sorted(dna["locus_id"].unique())) if len(dna) else ()
        geno = np.full((n, len(loci)), -1, np.int8)
        if len(dna):
            col = dna["locus_id"].map({lc: i for i, lc in enumerate(loci)}).to_numpy(np.int64)
            val = dna["genotype"].map({g: i for i, g in enumerate(GENOTYPES)}).to_numpy(np.int8)
            geno[dna["idx"].to_numpy(np.int64), col] = val
        birth = _days(animals["birth_date"])
        whelp = _days(litters["whelp_date"])
        mating = _days(litters["mating_date"])
        dams = litters["dam_idx"].to_numpy(np.int64)
        sires = litters["sire_idx"].to_numpy(np.int64)
        domestic = animals["studbook"].to_numpy() != "FOREIGN"
        # litter F: F of the pups = kinship of the parents; use the first registered pup's F
        first_pup = animals.dropna(subset=["litter_id"]).groupby("litter_id")["idx"].min()
        lf = litters["litter_id"].map(first_pup).to_numpy(dtype=float)
        has_pup = ~np.isnan(lf)
        lit_f = np.where(has_pup, F[np.where(has_pup, lf, 0).astype(np.int64)], np.nan)
        return cls.from_arrays(
            ped=ped,
            F=F,
            D=D,
            reg_no=animals["reg_no"].to_numpy(dtype=object),
            name=animals["name"].to_numpy(dtype=object),
            birth_day=birth,
            death_day=_days(animals["death_date"]),
            limited=animals["registration_type"].to_numpy() == "limited",
            is_local_breed=is_local,
            hd_grade=hd_grade,
            loci=loci,
            dna=geno,
            lit_dam=dams,
            lit_sire=sires,
            lit_whelp=whelp,
            lit_mating=mating,
            lit_n_registered=litters["n_registered"].to_numpy(dtype=float),
            lit_f=lit_f,
            domestic=domestic,
        )

    @classmethod
    def from_arrays(
        cls,
        ped: Pedigree,
        F: FloatArray,
        D: FloatArray,
        reg_no: NDArray[np.object_],
        name: NDArray[np.object_],
        birth_day: IntArray,
        death_day: IntArray,
        limited: NDArray[np.bool_],
        is_local_breed: NDArray[np.bool_],
        hd_grade: NDArray[np.int8],
        loci: tuple[str, ...],
        dna: NDArray[np.int8],
        lit_dam: IntArray,
        lit_sire: IntArray,
        lit_whelp: IntArray,
        lit_mating: IntArray,
        lit_n_registered: FloatArray,
        lit_f: FloatArray,
        domestic: NDArray[np.bool_],
    ) -> RuleContext:
        """Build from per-animal and per-litter arrays (registry idx order); `lit_f` is the
        inbreeding of each litter's pups (nan if unknown)."""
        n = ped.n
        nb = len(ped.breed_codes)
        lit_breed = ped.breed[lit_dam].astype(np.int64)
        exp_size = np.array(
            [
                float(lit_n_registered[lit_breed == b].mean()) if (lit_breed == b).any() else 0.0
                for b in range(nb)
            ]
        )
        has_sire = ped.sire >= 0
        ok = ~np.isnan(lit_f)
        return cls(
            ped=ped,
            F=F,
            D=D,
            reg_no=reg_no,
            name=name,
            birth_day=birth_day,
            death_day=death_day,
            limited=limited,
            is_local_breed=is_local_breed,
            hd_grade=hd_grade,
            loci=loci,
            dna=dna,
            dam_litters=CSR.build(lit_dam, lit_whelp, n),
            sire_litters=CSR.build(lit_sire, lit_mating, n),
            sire_offspring=CSR.build(ped.sire[has_sire], birth_day[has_sire], n),
            breed_births=CSR.build(ped.breed[domestic].astype(np.int64), birth_day[domestic], nb),
            breed_litter_f=CSR.build(lit_breed[ok], lit_whelp[ok], nb, lit_f[ok]),
            expected_litter_registered=exp_size,
        )
