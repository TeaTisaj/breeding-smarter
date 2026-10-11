"""Calibration targets: config models and evaluation (target vs simulated)."""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from pydantic import Field

from breeding_smarter.calibration.data import RunData
from breeding_smarter.calibration.metrics import METRICS, MetricResult
from breeding_smarter.config.loader import load_config
from breeding_smarter.config.sourced import Provenance, Strict
from breeding_smarter.io.paths import configs_dir


class Check(Strict):
    component: str
    range: tuple[float, float] | dict[str, tuple[float, float]] | None = None
    equals: bool | None = None
    breeds: list[str] | None = None

    def target_for(self, breed: str) -> str:
        if self.equals is not None:
            return f"= {self.equals}"
        r = self.range[breed] if isinstance(self.range, dict) else self.range
        return "" if r is None else f"[{r[0]:g}, {r[1]:g}]"

    def passes(self, breed: str, value: object) -> bool | None:
        if self.breeds is not None and breed not in self.breeds:
            return None
        if self.equals is not None:
            return bool(value) == self.equals
        r = self.range.get(breed) if isinstance(self.range, dict) else self.range
        if r is None:
            return None
        v = float(value)
        return not math.isnan(v) and r[0] <= v <= r[1]


class Target(Provenance):
    id: str
    description: str
    metric: str
    kind: Literal["hard", "soft", "report"]
    checks: list[Check] = Field(default_factory=list)


class TargetsConfig(Strict):
    targets: list[Target]


def load_targets(path: Path | None = None) -> TargetsConfig:
    cfg = load_config(path or configs_dir() / "calibration" / "targets.yaml", TargetsConfig)
    for t in cfg.targets:
        if t.metric not in METRICS:
            raise ValueError(f"{t.id}: unknown metric {t.metric!r}")
    return cfg


@dataclass
class Row:
    id: str
    description: str
    kind: str
    breed: str
    component: str
    value: object
    target: str
    status: str
    source: str


def _fmt(v: object) -> str:
    if isinstance(v, bool):
        return str(v)
    if isinstance(v, float):
        return "nan" if math.isnan(v) else (f"{v:.4g}" if abs(v) < 1e4 else f"{v:.0f}")
    return str(v)


def evaluate(rd: RunData, cfg: TargetsConfig) -> tuple[list[Row], dict[str, MetricResult]]:
    """All target rows (one per target, breed and component) and the metric results."""
    rows: list[Row] = []
    results: dict[str, MetricResult] = {}
    for t in cfg.targets:
        res = METRICS[t.metric](rd)
        results[t.id] = res
        src = t.source or ("assumption" if t.assumption else "")
        for breed, comps in res.values.items():
            if t.kind == "report" or not t.checks:
                for comp, val in comps.items():
                    rows.append(
                        Row(t.id, t.description, t.kind, breed, comp, _fmt(val), "", "REPORT", src)
                    )
                continue
            for c in t.checks:
                val = comps.get(c.component)
                ok = c.passes(breed, val)
                if ok is None:
                    status = "REPORT"
                elif ok:
                    status = "PASS"
                else:
                    status = "FAIL" if t.kind == "hard" else "WARN"
                rows.append(
                    Row(
                        t.id,
                        t.description,
                        t.kind,
                        breed,
                        c.component,
                        _fmt(val),
                        c.target_for(breed) if ok is not None else "",
                        status,
                        src,
                    )
                )
    return rows, results


def hard_failures(rows: list[Row]) -> list[Row]:
    return [r for r in rows if r.status == "FAIL"]
