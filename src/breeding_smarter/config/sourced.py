"""The `Sourced` pattern: every biological or regulatory number carries its provenance.

In YAML a number is written as `{value: ..., source: <key>}` (key from `configs/sources.yaml`)
or `{value: ..., assumption: true, note: "..."}`. A value without either fails at load time.
"""

from __future__ import annotations

from functools import cache
from pathlib import Path
from typing import Any, Self

import numpy as np
import yaml
from pydantic import BaseModel, ConfigDict, model_validator

from breeding_smarter.io.paths import configs_dir


class Strict(BaseModel):
    """Base model: unknown keys fail loudly, instances are immutable."""

    model_config = ConfigDict(extra="forbid", frozen=True)


@cache
def known_sources(path: Path | None = None) -> frozenset[str]:
    """Citation keys from `configs/sources.yaml`."""
    p = path or configs_dir() / "sources.yaml"
    data = yaml.safe_load(p.read_text())
    return frozenset(data["sources"])


@cache
def source_refs(path: Path | None = None) -> dict[str, tuple[str, str | None]]:
    """Source key -> (reference, public `url` or None) from `configs/sources.yaml`."""
    p = path or configs_dir() / "sources.yaml"
    data = yaml.safe_load(p.read_text(encoding="utf-8"))["sources"]
    return {k: (v["ref"], v.get("url")) for k, v in data.items()}


class Provenance(Strict):
    """Mixin fields: `source` (citation key) or `assumption: true`, plus a free-text note."""

    source: str | None = None
    assumption: bool = False
    note: str | None = None

    @model_validator(mode="after")
    def _check_provenance(self) -> Self:
        if self.source is None and not self.assumption:
            raise ValueError("value needs `source: <key>` or `assumption: true`")
        if self.source is not None and self.source not in known_sources():
            raise ValueError(f"unknown source key {self.source!r} (not in configs/sources.yaml)")
        return self


class Sourced[T](Provenance):
    """A value with provenance."""

    value: T


class SourcedSeries(Provenance):
    """A time series given as `(year, value)` points, linearly interpolated, clamped at the ends."""

    points: list[tuple[int, float]]

    @model_validator(mode="after")
    def _sorted(self) -> Self:
        years = [p[0] for p in self.points]
        if not years or years != sorted(years) or len(set(years)) != len(years):
            raise ValueError("points must be non-empty with strictly increasing years")
        return self

    def at(self, year: float) -> float:
        xs = np.array([p[0] for p in self.points], dtype=float)
        ys = np.array([p[1] for p in self.points], dtype=float)
        return float(np.interp(year, xs, ys))


def collect_assumptions(model: BaseModel, prefix: str = "") -> list[tuple[str, Any, str | None]]:
    """All `(path, value, note)` triples marked `assumption: true` inside a config model."""
    out: list[tuple[str, Any, str | None]] = []
    for name in type(model).model_fields:
        val = getattr(model, name)
        path = f"{prefix}.{name}" if prefix else name
        items: list[tuple[str, Any]]
        if isinstance(val, BaseModel):
            items = [(path, val)]
        elif isinstance(val, list | tuple):
            items = [(f"{path}[{i}]", v) for i, v in enumerate(val)]
        elif isinstance(val, dict):
            items = [(f"{path}.{k}", v) for k, v in val.items()]
        else:
            items = []
        for p, v in items:
            if not isinstance(v, BaseModel):
                continue
            if isinstance(v, Provenance) and v.assumption:
                shown = getattr(v, "value", None)
                if shown is None:
                    shown = getattr(v, "points", None)
                if shown is None:
                    shown = v.model_dump(exclude={"source", "assumption", "note"})
                out.append((p, shown, v.note))
            out.extend(collect_assumptions(v, p))
    return out
