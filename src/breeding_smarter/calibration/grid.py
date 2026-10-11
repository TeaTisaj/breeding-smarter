"""Calibration grid (P5 task 5.5): run parameter combinations per breed and rank them.

Never edits configs: prints and writes a ranked table; the chosen values are applied to the
breed YAML by hand with a note pointing to `reports/validation/calibration_grid.csv`.
"""

from __future__ import annotations

import itertools
import math
import shutil
import tempfile
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from breeding_smarter.calibration.data import RunData
from breeding_smarter.calibration.targets import TargetsConfig, evaluate
from breeding_smarter.config.models import BreedConfig
from breeding_smarter.config.sourced import SourcedSeries
from breeding_smarter.sim.genetics import DogGenetics
from breeding_smarter.sim.interfaces import SimSetup
from breeding_smarter.sim.run import generate, load_setup


def set_param(breed: BreedConfig, name: str, value: Any) -> BreedConfig:
    """Return a copy of the breed config with one dotted parameter replaced.

    `market.popular_sire_alpha` takes a list of `(year, value)` points; other parameters a
    scalar that replaces the `value` of the Sourced field.
    """
    section, field = name.split(".")
    sec = getattr(breed, section)
    old = getattr(sec, field)
    note = "calibration grid candidate"
    if isinstance(old, SourcedSeries):
        new = SourcedSeries(points=[tuple(p) for p in value], assumption=True, note=note)
    else:
        new = old.model_copy(update={"value": value, "assumption": True, "note": note})
    return breed.model_copy(update={section: sec.model_copy(update={field: new})})


def combos(grid: dict[str, list[Any]]) -> list[dict[str, Any]]:
    keys = list(grid)
    return [dict(zip(keys, vals, strict=True)) for vals in itertools.product(*grid.values())]


def score(rows: list[Any], breed: str, kinds: Mapping[str, str]) -> tuple[int, float]:
    """(failed hard checks, summed normalised distance to soft and hard ranges)."""
    n_fail, dist = 0, 0.0
    for r in rows:
        if r.breed != breed or r.status not in ("PASS", "WARN", "FAIL"):
            continue
        if r.status == "FAIL":
            n_fail += 1
        if r.status in ("FAIL", "WARN") and r.target.startswith("["):
            lo, hi = (float(x) for x in r.target.strip("[]").split(","))
            v = float(r.value)
            width = max(hi - lo, 1e-9)
            dist += (lo - v) / width if v < lo else (v - hi) / width
        elif r.status in ("FAIL", "WARN"):
            dist += 1.0
    return n_fail, dist


def run_grid(
    config: Path,
    grid_path: Path,
    targets: TargetsConfig,
    breeds: list[str] | None = None,
    seeds: tuple[int, ...] = (1, 2),
    out_csv: Path | None = None,
) -> pd.DataFrame:
    spec = yaml.safe_load(grid_path.read_text())
    base = load_setup(config)
    rows = []
    for bname, bspec in spec["breeds"].items():
        bid = next(b.breed_id for b in base.breeds if b.breed_id == bname)
        if breeds and bid not in breeds:
            continue
        idx = [b.breed_id for b in base.breeds].index(bid)
        scale = bspec.get("scale", 1.0)
        for combo in combos(bspec["grid"]):
            breed_cfg = base.breeds[idx]
            for k, v in combo.items():
                breed_cfg = set_param(breed_cfg, k, v)
            sim = base.sim.model_copy(update={"scale": scale, "breeds": [base.sim.breeds[idx]]})
            setup = SimSetup(sim=sim, species=base.species, breeds=(breed_cfg,))
            for seed in seeds:
                tmp = Path(tempfile.mkdtemp(prefix="bsm-grid-"))
                try:
                    genetics = DogGenetics.from_setup(setup)
                    run = generate(
                        config,
                        seed=seed,
                        scale=scale,
                        out=tmp,
                        genetics=genetics,
                        run_id="grid",
                        validate=False,
                        setup=setup,
                    )
                    rd = RunData.load(run)
                    trows, _ = evaluate(rd, targets)
                    kinds = {t.id: t.kind for t in targets.targets}
                    n_fail, dist = score(trows, bid, kinds)
                    vals = {
                        f"{r.id}.{r.component}": r.value
                        for r in trows
                        if r.breed == bid and r.status != "REPORT"
                    }
                finally:
                    shutil.rmtree(tmp, ignore_errors=True)
                rows.append(
                    {
                        "breed": bid,
                        "seed": seed,
                        **{k: str(v) for k, v in combo.items()},
                        "n_hard_fail": n_fail,
                        "distance": round(dist, 4),
                        **vals,
                    }
                )
    df = pd.DataFrame(rows)
    keys = [c for c in df.columns if c.startswith("market.") or c.startswith("population.")]
    agg = (
        df.groupby(["breed", *keys], dropna=False)
        .agg(n_hard_fail=("n_hard_fail", "mean"), distance=("distance", "mean"))
        .reset_index()
        .sort_values(["breed", "n_hard_fail", "distance"])
    )
    if out_csv is not None:
        out_csv.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out_csv.with_name(out_csv.stem + "_runs.csv"), index=False)
        agg.to_csv(out_csv, index=False)
    return agg


def best(agg: pd.DataFrame) -> dict[str, dict[str, Any]]:
    out = {}
    for b, g in agg.groupby("breed"):
        row = g.iloc[0]
        out[str(b)] = {
            k: row[k]
            for k in g.columns
            if k not in ("breed",) and not (isinstance(row[k], float) and math.isnan(row[k]))
        }
    return out
