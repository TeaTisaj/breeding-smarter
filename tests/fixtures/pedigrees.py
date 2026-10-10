"""Small hand-built pedigrees in registry format with known inbreeding (used by P2 onwards).

Notation: animals are listed in birth order (idx). `sire`/`dam` use -1 for unknown.
Expected values (Wright 1922; kinship f_ab = A_ab / 2, F of offspring of a x b = f_ab):

- unrelated: A x B unrelated founders -> F = 0.
- full_sibs: C, D full sibs (children of A x B). f(C, D) = 1/4 [f(A,A) + f(A,B) + f(B,A)
  + f(B,B)] = 1/4 (1/2 + 0 + 0 + 1/2) = 1/4 -> F(E) = 0.25.
- half_sibs: C (A x B) and E (A x D) share only A: f = 1/4 f(A,A) = 1/8 -> F = 0.125.
- parent_offspring: A x C where C = A x B: f(A, C) = 1/2 [f(A,A) + f(A,B)] = 1/4 -> F = 0.25.
- first_cousins: H = C x E, I = G x D, C and D full sibs. f(H, I) = 1/4 f(C, D) = 1/16
  -> F = 0.0625.
- repeated_full_sib: F_t = 1/4 (1 + 2 F_{t-1} + F_{t-2}): 0.25, 0.375, 0.5.
- inbred_ancestor: half sibs through sire S with F_S = 0.25 -> F = (1/2)^3 (1 + F_S) = 0.15625.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from breeding_smarter.io import write_manifest, write_table
from breeding_smarter.schema.tables import (
    ANIMALS,
    ANIMALS_TRUTH,
    BREEDS,
    DNA_TESTS,
    EBV,
    GENOTYPES_TRUTH,
    HEALTH_TESTS,
    KENNELS,
    LITTERS,
)

BREED = "SYN_M"
BASE_DATE = date(2000, 3, 1)
PARENT_GAP_DAYS = 3 * 365


@dataclass
class FixturePedigree:
    name: str
    sire: list[int]
    dam: list[int]
    sex: list[str]
    expected_F: dict[int, float]
    expected_kinship: dict[tuple[int, int], float] = field(default_factory=dict)
    description: str = ""

    @property
    def n(self) -> int:
        return len(self.sire)

    def arrays(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        sex = np.array([1 if s == "M" else 0 for s in self.sex], dtype=np.int8)
        return np.array(self.sire, np.int64), np.array(self.dam, np.int64), sex

    def tables(self, breed: str = BREED) -> dict[str, pd.DataFrame]:
        return tables_from_arrays(self.sire, self.dam, self.sex, breed=breed)

    def write_run(self, root: Path, breed: str = BREED) -> Path:
        run_dir = root / f"fixture-{self.name}"
        write_tables(self.tables(breed), run_dir, seed=0, config_name=f"fixture-{self.name}")
        return run_dir


def birth_dates(sire: list[int], dam: list[int]) -> list[date]:
    """Monotone birth dates with every parent at least three years older than its offspring."""
    out: list[date] = []
    for i in range(len(sire)):
        d = out[-1] if out else BASE_DATE
        for p in (sire[i], dam[i]):
            if p >= 0:
                d = max(d, out[p] + timedelta(days=PARENT_GAP_DAYS))
        out.append(d)
    return out


def tables_from_arrays(
    sire: list[int] | np.ndarray,
    dam: list[int] | np.ndarray,
    sex: list[str] | np.ndarray,
    breed: str = BREED,
) -> dict[str, pd.DataFrame]:
    """Every registry and truth table for a pedigree given as parent arrays (-1 unknown)."""
    sire = [int(x) for x in sire]
    dam = [int(x) for x in dam]
    sex = [str(x) for x in sex]
    n = len(sire)
    births = birth_dates(sire, dam)
    litter_of: dict[tuple[int, int, date], int] = {}
    litter_id: list[int | None] = []
    for i in range(n):
        if sire[i] >= 0 and dam[i] >= 0:
            key = (sire[i], dam[i], births[i])
            litter_of.setdefault(key, len(litter_of))
            litter_id.append(litter_of[key])
        else:
            litter_id.append(None)
    to_na = lambda xs: pd.array([x if x is not None and x >= 0 else None for x in xs], "Int64")  # noqa: E731
    animals = pd.DataFrame(
        {
            "idx": np.arange(n, dtype=np.int64),
            "reg_no": [f"SYN-HR-{b.year}-{i:06d}" for i, b in enumerate(births)],
            "name": [f"Fixture Dog {i}" for i in range(n)],
            "species": "dog",
            "breed_id": breed,
            "sex": sex,
            "birth_date": pd.to_datetime(births),
            "sire_idx": to_na(sire),
            "dam_idx": to_na(dam),
            "litter_id": to_na(litter_id),
            "breeder_id": pd.array([1] * n, "Int32"),
            "owner_id": np.ones(n, dtype=np.int32),
            "country_of_birth": "HR",
            "studbook": [
                "HR" if s >= 0 and d >= 0 else "HUR" for s, d in zip(sire, dam, strict=True)
            ],
            "import_flag": False,
            "original_reg_no": None,
            "microchip": [f"999{i:012d}" for i in range(n)],
            "coat_colour": "red",
            "registration_type": "full",
            "death_date": pd.Series([pd.NaT] * n, dtype="datetime64[ns]"),
            "death_cause": None,
            "titles_count": np.zeros(n, dtype=np.int16),
        }
    )
    lrows = []
    for (s, d, b), lid in litter_of.items():
        k = sum(1 for x in litter_id if x == lid)
        lrows.append(
            {
                "litter_id": lid,
                "breed_id": breed,
                "sire_idx": s,
                "dam_idx": d,
                "mating_date": pd.Timestamp(b - timedelta(days=63)),
                "whelp_date": pd.Timestamp(b),
                "n_born": k,
                "n_born_alive": k,
                "n_registered": k,
                "mating_method": "natural",
                "caesarean": False,
                "breeder_id": 1,
            }
        )
    litters = pd.DataFrame(lrows, columns=LITTERS.columns)
    if not lrows:
        litters = litters.astype({"litter_id": "int64", "sire_idx": "int64", "dam_idx": "int64"})
    breeds = pd.DataFrame(
        [
            {
                "breed_id": breed,
                "display_name": "Synthetic Breed M",
                "species": "dog",
                "size_class": "medium",
                "studbook": "HR",
                "is_local_breed": False,
                "archetype_description": "Fixture breed.",
            }
        ]
    )
    kennels = pd.DataFrame(
        [
            {
                "kennel_id": 1,
                "name": "Fixture Kennel",
                "kind": "breeder",
                "country": "HR",
                "lat": 45.8,
                "lon": 16.0,
                "registered_year": 1999,
            }
        ]
    )
    truth = pd.DataFrame(
        {
            "gid": np.arange(n, dtype=np.int64),
            "idx": pd.array(range(n), "Int64"),
            "breed_id": breed,
            "sex": sex,
            "birth_year": np.array([b.year for b in births], dtype=np.int16),
            "true_sire_gid": to_na(sire),
            "true_dam_gid": to_na(dam),
            "is_hidden": False,
            "f_true_ibd": 0.0,
            "f_true_pedigree": 0.0,
            "tbv_hd": 0.0,
            "hd_liability": np.nan,
            "attractiveness": 0.0,
            "fertility": 1.0,
        }
    )
    empty = lambda spec: pd.DataFrame({c: pd.Series([], dtype=object) for c in spec.columns})  # noqa: E731
    return {
        BREEDS.name: breeds,
        KENNELS.name: kennels,
        ANIMALS.name: animals,
        LITTERS.name: litters,
        HEALTH_TESTS.name: empty(HEALTH_TESTS),
        DNA_TESTS.name: empty(DNA_TESTS),
        EBV.name: empty(EBV),
        ANIMALS_TRUTH.name: truth,
        GENOTYPES_TRUTH.name: empty(GENOTYPES_TRUTH),
    }


def write_tables(
    tables: dict[str, pd.DataFrame], run_dir: Path, seed: int = 0, config_name: str = "fixture"
) -> Path:
    from breeding_smarter.schema.tables import TABLES

    for name, df in tables.items():
        write_table(df, TABLES[name], run_dir / TABLES[name].filename)
    write_manifest(
        run_dir / "manifest.json",
        run_id=run_dir.name,
        config_name=config_name,
        seed=seed,
        row_counts={k: len(v) for k, v in tables.items()},
    )
    return run_dir


UNRELATED = FixturePedigree(
    "unrelated",
    [-1, -1, 0],
    [-1, -1, 1],
    ["M", "F", "M"],
    {0: 0, 1: 0, 2: 0},
    {(0, 0): 0.5, (0, 1): 0.0, (0, 2): 0.25},
)
FULL_SIBS = FixturePedigree(
    "full_sibs",
    [-1, -1, 0, 0, 2],
    [-1, -1, 1, 1, 3],
    ["M", "F", "M", "F", "M"],
    {2: 0, 3: 0, 4: 0.25},
    {(2, 3): 0.25, (0, 2): 0.25},
)
HALF_SIBS = FixturePedigree(
    "half_sibs",
    [-1, -1, -1, 0, 0, 3],
    [-1, -1, -1, 1, 2, 4],
    ["M", "F", "F", "M", "F", "M"],
    {3: 0, 4: 0, 5: 0.125},
    {(3, 4): 0.125},
)
PARENT_OFFSPRING = FixturePedigree(
    "parent_offspring",
    [-1, -1, 0, 0],
    [-1, -1, 1, 2],
    ["M", "F", "F", "M"],
    {2: 0, 3: 0.25},
    {(0, 2): 0.25},
)
FIRST_COUSINS = FixturePedigree(
    "first_cousins",
    [-1, -1, -1, -1, 0, 0, 4, 3, 6],
    [-1, -1, -1, -1, 1, 1, 2, 5, 7],
    ["M", "F", "F", "M", "M", "F", "M", "F", "M"],
    {6: 0, 7: 0, 8: 0.0625},
    {(6, 7): 0.0625},
)
REPEATED_FULL_SIB = FixturePedigree(
    "repeated_full_sib",
    [-1, -1, 0, 0, 2, 2, 4, 4, 6],
    [-1, -1, 1, 1, 3, 3, 5, 5, 7],
    ["M", "F", "M", "F", "M", "F", "M", "F", "M"],
    {2: 0, 3: 0, 4: 0.25, 5: 0.25, 6: 0.375, 7: 0.375, 8: 0.5},
)
INBRED_ANCESTOR = FixturePedigree(
    "inbred_ancestor",
    [-1, -1, 0, 0, 2, -1, -1, 4, 4, 7],
    [-1, -1, 1, 1, 3, -1, -1, 5, 6, 8],
    ["M", "F", "M", "F", "M", "F", "F", "M", "F", "M"],
    {4: 0.25, 7: 0, 8: 0, 9: 0.15625},
    {(4, 4): 0.625, (7, 8): 0.15625},
)

ALL_FIXTURES: tuple[FixturePedigree, ...] = (
    UNRELATED,
    FULL_SIBS,
    HALF_SIBS,
    PARENT_OFFSPRING,
    FIRST_COUSINS,
    REPEATED_FULL_SIB,
    INBRED_ANCESTOR,
)
