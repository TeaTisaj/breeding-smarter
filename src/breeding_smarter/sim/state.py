"""Simulator state: struct of growable numpy arrays, serialisable for P8 continuation."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

DOMESTIC, FOREIGN = 0, 1
METHODS = ("natural", "ai_fresh", "ai_chilled", "ai_frozen")
DEATH_CAUSES = ("age", "disease", "accident", "unknown")

# name -> (dtype, fill value)
ANIMAL_COLUMNS: dict[str, tuple[str, float | int | bool]] = {
    "breed": ("int16", -1),
    "subpop": ("int8", 0),
    "sex": ("int8", 0),  # 1 male, 0 female
    "birth_year": ("int16", 0),
    "birth_doy": ("int16", 1),  # 1..365
    "sire": ("int64", -1),
    "dam": ("int64", -1),
    "death_year": ("int16", 0),
    "death_doy": ("int16", 1),
    "death_cause": ("int8", 0),
    "kennel": ("int32", -1),  # breeder kennel holding a breeding candidate, -1 private
    "birth_kennel": ("int32", -1),
    "is_candidate": ("bool", False),
    "attractiveness": ("float64", 0.0),
    "fertility": ("float64", 1.0),
    "litters_count": ("int16", 0),
    "last_whelp_t": ("float64", -1e9),  # fractional year of last whelping
    "offspring_count": ("int32", 0),
    "registered": ("bool", False),
    "reg_parents_known": ("bool", True),
    "foreign_stub": ("bool", False),
    "import_flag": ("bool", False),
    "import_year": ("int16", -1),
    "reg_year": ("int16", -1),  # year the animal entered the registry
    "litter": ("int64", -1),
    "country": ("int16", 0),
    "f_true": ("float64", 0.0),  # realised IBD, filled by the genetics model
}

LITTER_COLUMNS: dict[str, tuple[str, float | int | bool]] = {
    "breed": ("int16", -1),
    "subpop": ("int8", 0),
    "sire": ("int64", -1),
    "dam": ("int64", -1),
    "mating_year": ("int16", 0),
    "mating_doy": ("int16", 1),
    "whelp_year": ("int16", 0),
    "whelp_doy": ("int16", 1),
    "n_born": ("int16", 0),
    "n_born_alive": ("int16", 0),
    "n_animals": ("int16", 0),  # puppies that became animals (registered or hidden-alive)
    "method": ("int8", 0),
    "caesarean": ("bool", False),
    "breeder": ("int32", -1),
    "registered": ("bool", False),
}

KENNEL_COLUMNS: dict[str, tuple[str, float | int | bool]] = {
    "breed": ("int16", -1),
    "subpop": ("int8", 0),
    "country": ("int16", 0),
    "lat": ("float64", 0.0),
    "lon": ("float64", 0.0),
    "activity": ("float64", 1.0),
}


class Columns:
    """Named numpy columns sharing one length, with capacity doubling."""

    def __init__(self, spec: dict[str, tuple[str, float | int | bool]], capacity: int = 1024):
        self.spec = spec
        self.n = 0
        self.data = {k: np.full(capacity, fill, dtype=dt) for k, (dt, fill) in spec.items()}

    def __getattr__(self, name: str) -> np.ndarray:
        data = self.__dict__.get("data")
        if data is not None and name in data:
            return data[name][: self.n]
        raise AttributeError(name)

    def __getitem__(self, name: str) -> np.ndarray:
        return self.data[name][: self.n]

    def _ensure(self, extra: int) -> None:
        cap = next(iter(self.data.values())).shape[0] if self.data else 0
        need = self.n + extra
        if need <= cap:
            return
        new_cap = max(need, 2 * cap, 16)
        for k, (dt, fill) in self.spec.items():
            arr = np.full(new_cap, fill, dtype=dt)
            arr[: self.n] = self.data[k][: self.n]
            self.data[k] = arr

    def add(self, count: int, **values: Any) -> np.ndarray:
        """Append `count` rows (unspecified columns get the fill value); returns their ids."""
        unknown = set(values) - set(self.spec)
        if unknown:
            raise KeyError(f"unknown columns {unknown}")
        self._ensure(count)
        ids = np.arange(self.n, self.n + count, dtype=np.int64)
        for k, v in values.items():
            self.data[k][self.n : self.n + count] = v
        self.n += count
        return ids

    def to_npz_dict(self, prefix: str) -> dict[str, np.ndarray]:
        return {f"{prefix}{k}": v[: self.n].copy() for k, v in self.data.items()}

    @classmethod
    def from_npz(
        cls, spec: dict[str, tuple[str, float | int | bool]], arrays: Any, prefix: str
    ) -> Columns:
        cols = cls(spec, capacity=16)
        first = arrays[f"{prefix}{next(iter(spec))}"]
        n = int(first.shape[0])
        cols._ensure(n)
        for k in spec:
            cols.data[k][:n] = arrays[f"{prefix}{k}"]
        cols.n = n
        return cols


@dataclass
class SimState:
    """All simulator state. Animals are indexed by `gid` (global birth order)."""

    animals: Columns = field(default_factory=lambda: Columns(ANIMAL_COLUMNS))
    litters: Columns = field(default_factory=lambda: Columns(LITTER_COLUMNS))
    kennels: Columns = field(default_factory=lambda: Columns(KENNEL_COLUMNS, 64))
    kennel_names: list[str] = field(default_factory=list)
    breed_ids: list[str] = field(default_factory=list)
    countries: list[str] = field(default_factory=list)
    year: int = 0  # last completed year
    warnings: list[str] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)
    extra: dict[str, np.ndarray] = field(default_factory=dict)  # genetics arrays etc.

    @property
    def n(self) -> int:
        return self.animals.n

    def add_animals(self, count: int, **fields: Any) -> np.ndarray:
        return self.animals.add(count, **fields)

    def alive_mask(self, year: int) -> np.ndarray:
        a = self.animals
        return (a.birth_year <= year) & (a.death_year > year)

    def age(self, year: float) -> np.ndarray:
        """Age in fractional years at time `year` (fractional year, Jan 1 = integer)."""
        a = self.animals
        return year - (a.birth_year + (a.birth_doy - 1) / 365.0)

    def country_code(self, iso: str) -> int:
        if iso not in self.countries:
            self.countries.append(iso)
        return self.countries.index(iso)

    def save(self, path: Path, rng: np.random.Generator | None = None) -> Path:
        """Save to `path/` as `state.npz` plus `state.json` (metadata and RNG state)."""
        path.mkdir(parents=True, exist_ok=True)
        arrays: dict[str, np.ndarray] = {}
        arrays.update(self.animals.to_npz_dict("a_"))
        arrays.update(self.litters.to_npz_dict("l_"))
        arrays.update(self.kennels.to_npz_dict("k_"))
        arrays.update({f"x_{k}": v for k, v in self.extra.items()})
        np.savez_compressed(path / "state.npz", **arrays)  # type: ignore[arg-type]
        meta = {
            "year": self.year,
            "kennel_names": self.kennel_names,
            "breed_ids": self.breed_ids,
            "countries": self.countries,
            "warnings": self.warnings,
            "meta": self.meta,
            "rng_state": rng.bit_generator.state if rng is not None else None,
        }
        (path / "state.json").write_text(json.dumps(meta, default=_json_default))
        return path

    @classmethod
    def load(cls, path: Path) -> tuple[SimState, np.random.Generator | None]:
        """Inverse of `save`; returns the state and the restored RNG (if one was saved)."""
        meta = json.loads((path / "state.json").read_text())
        with np.load(path / "state.npz") as z:
            state = cls(
                animals=Columns.from_npz(ANIMAL_COLUMNS, z, "a_"),
                litters=Columns.from_npz(LITTER_COLUMNS, z, "l_"),
                kennels=Columns.from_npz(KENNEL_COLUMNS, z, "k_"),
                kennel_names=meta["kennel_names"],
                breed_ids=meta["breed_ids"],
                countries=meta["countries"],
                year=meta["year"],
                warnings=meta["warnings"],
                meta=meta["meta"],
                extra={k[2:]: z[k].copy() for k in z.files if k.startswith("x_")},
            )
        rng = None
        if meta.get("rng_state") is not None:
            rng = np.random.Generator(np.random.PCG64())
            rng.bit_generator.state = meta["rng_state"]
        return state, rng


def _json_default(o: Any) -> Any:
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(type(o))
