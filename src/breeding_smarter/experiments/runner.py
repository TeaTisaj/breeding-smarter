"""Run experiments from the end state of dataset v1 (P8 tasks 8.2, 8.3, 8.6).

Each (breed, strategy, adoption, replicate) continues the saved v1 simulator state for the
configured number of generations with only that breed active. Replicate r uses child seed r of
the experiment seed for every strategy (common random numbers as far as possible; strategies
still diverge once their choices differ). Every finished part is written to its own Parquet
file; a rerun skips finished parts.
"""

from __future__ import annotations

import logging
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml
from pydantic import Field

from breeding_smarter.config.loader import load_config
from breeding_smarter.config.sourced import Sourced, Strict
from breeding_smarter.experiments.metrics import living_he, year_metrics
from breeding_smarter.experiments.observed import ObservedRegistry
from breeding_smarter.experiments.strategies import StrategyParams, make_strategy
from breeding_smarter.io.datasets import resolve_dataset
from breeding_smarter.io.paths import repo_root
from breeding_smarter.matching.config import load_scoring
from breeding_smarter.sim.demography import eligible
from breeding_smarter.sim.genetics import DogGenetics
from breeding_smarter.sim.interfaces import SimSetup
from breeding_smarter.sim.reproduction import simulate_year
from breeding_smarter.sim.run import load_run_setup
from breeding_smarter.sim.state import DOMESTIC, SimState

log = logging.getLogger(__name__)


class BreedRun(Strict):
    replicates: int
    extra_strategies: list[str] = Field(default_factory=list)  # run for this breed only


class ExperimentConfig(Strict):
    id: str
    description: str
    seed: int
    dataset: str = "v1"
    generations: int
    breeds: dict[str, BreedRun]
    strategies: list[str]
    adoption: list[float] = Field(default_factory=lambda: [1.0])
    profile: str = "exp_pairing"
    scoring: str = "default"
    coordination: str = "default"
    coi_cap: Sourced[float]
    s3_top_probs: Sourced[list[float]]
    s4_lambda: Sourced[float]
    ebv_every_years: Sourced[int]
    registration_rate: Sourced[float]


def load_experiment(path: Path) -> ExperimentConfig:
    return load_config(path, ExperimentConfig)


@dataclass(frozen=True)
class Part:
    breed: str
    strategy: str
    adoption: float
    replicate: int

    @property
    def name(self) -> str:
        return f"{self.breed}_{self.strategy}_a{self.adoption:g}_r{self.replicate:02d}"


def experiment_dir(exp_id: str) -> Path:
    return repo_root() / "data" / "experiments" / exp_id


def report_dir(exp_id: str) -> Path:
    return repo_root() / "reports" / "experiments" / exp_id


def parts_of(cfg: ExperimentConfig) -> list[Part]:
    out = []
    for breed, br in cfg.breeds.items():
        for sid in [*cfg.strategies, *br.extra_strategies]:
            adoptions = cfg.adoption if sid == "S3" or sid.startswith("S3q") else [1.0]
            for ad in adoptions:
                for r in range(br.replicates):
                    out.append(Part(breed, sid, ad, r))
    return out


def experiment_setup(run_root: Path, breed: int, registration_rate: float) -> SimSetup:
    """The v1 setup with every live-born puppy registered for the experiment breed."""
    setup = load_run_setup(run_root)
    b = setup.breeds[breed]
    rep = b.reproduction.model_copy(
        update={
            "registration_rate": b.reproduction.registration_rate.model_copy(
                update={"value": registration_rate, "note": "experiments: all live-born registered"}
            )
        }
    )
    breeds = list(setup.breeds)
    breeds[breed] = b.model_copy(update={"reproduction": rep})
    return SimSetup(sim=setup.sim, species=setup.species, breeds=tuple(breeds))


def replicate_rng(seed: int, n_replicates: int, replicate: int) -> np.random.Generator:
    child = np.random.SeedSequence(seed).spawn(n_replicates)[replicate]
    return np.random.Generator(np.random.PCG64(child))


def hard_rule_strategy(sid: str) -> bool:
    """Strategies that promise never to allocate a pair failing a HARD rule."""
    return sid in ("S2", "S3", "S4", "S3hc", "S3xc") or sid.startswith(("CC-", "S3q"))


class ContractChecker:
    """Debug wrapper: every sire is eligible (domestic eligible or eligible foreign) or -1, of
    the dam's breed, (for S2 to S4 and P12 strategies) no pair fails a HARD rule of the
    profile, and (P12) no sire gets more litters than its quota beyond the logged overflow."""

    def __init__(self, inner: Any, hard_rules: bool, profile: str):
        self.inner = inner
        self.name = getattr(inner, "name", "?")
        self.hard_rules = hard_rules
        self.profile = profile
        self.checked = 0

    def __getattr__(self, item: str) -> Any:
        return getattr(self.inner, item)

    def __setattr__(self, key: str, value: Any) -> None:
        if key in ("obs", "ctx") and "inner" in self.__dict__:
            setattr(self.inner, key, value)
        else:
            super().__setattr__(key, value)

    def plan_matings(self, dams, sires, ctx, rng):
        from breeding_smarter.rules import evaluate_pair, load_profile

        out = self.inner.plan_matings(dams, sires, ctx, rng)
        a = ctx.state.animals
        allowed = set(np.asarray(sires).tolist()) | set(np.asarray(ctx.foreign_sires).tolist())
        for d, s in zip(dams, out, strict=True):
            if s < 0:
                continue
            assert int(s) in allowed, f"sire {s} not eligible"
            assert a.breed[s] == a.breed[d], "sire of another breed"
            if self.hard_rules and self.inner.obs.has(int(s)):
                obs = self.inner.obs
                res = evaluate_pair(
                    self.inner.ctx.rules,
                    load_profile(self.profile),
                    obs.idx_of[int(s)],
                    obs.idx_of[int(d)],
                    f"{ctx.year}-07-01",
                )
                assert not res.failed_hard, f"HARD rule violated: {res.failed_hard}"
            self.checked += 1
        plan = getattr(self.inner, "last_plan", None)
        if plan is not None and plan.quotas is not None:
            obs = self.inner.obs
            used = obs.idx(np.asarray(out)[np.asarray(out) >= 0])
            pos = {int(s): k for k, s in enumerate(plan.sires)}
            counts = np.zeros(plan.sires.size, np.int64)
            for s in used:
                if int(s) in pos:
                    counts[pos[int(s)]] += 1
            fixed = int(plan.diagnostics.get("n_dams", 0)) - int(
                plan.diagnostics.get("adopters", plan.diagnostics.get("n_dams", 0))
            )
            excess = int(np.maximum(counts - plan.quotas, 0).sum())
            assert excess <= int(plan.diagnostics.get("overflow", 0)) + fixed, "quota exceeded"
        return out


def run_part(
    cfg: ExperimentConfig, part: Part, out_dir: Path | None = None, debug: bool = False
) -> pd.DataFrame:
    """Simulate one (breed, strategy, adoption, replicate) and return long-format metrics."""
    t0 = time.perf_counter()
    rp = resolve_dataset(cfg.dataset)
    state, _ = SimState.load(prepared_state(cfg.dataset, part.breed))
    bidx = state.breed_ids.index(part.breed)
    setup = experiment_setup(rp.root, bidx, cfg.registration_rate.value)
    genetics = DogGenetics.from_setup(setup)
    genetics.load_arrays(state.extra)
    genetics.exclude_known_carriers = part.strategy == "S3xc"
    state.meta["litter_reference_frozen"] = True
    rng = replicate_rng(cfg.seed, cfg.breeds[part.breed].replicates, part.replicate)
    params = StrategyParams(
        profile=cfg.profile,
        coi_cap=cfg.coi_cap.value,
        top_probs=tuple(cfg.s3_top_probs.value),
        adoption=part.adoption,
        s4_lambda=cfg.s4_lambda.value,
        coordination=cfg.coordination,
    )
    strategy = make_strategy(part.strategy, params, load_scoring(cfg.scoring))
    if debug:
        hard = hard_rule_strategy(part.strategy)
        profile = strategy.params.profile if hasattr(strategy, "params") else cfg.profile
        strategy = ContractChecker(strategy, hard, profile)
    start = state.year
    obs = ObservedRegistry(state, genetics, setup, bidx)
    h2 = genetics.h2
    obs.evaluate_ebv(state, start, h2)
    he0 = living_he(state, genetics, bidx, start)
    gi = setup.sim.generation_interval_years.value
    end = start + round(cfg.generations * gi)
    rows: list[dict[str, Any]] = []
    for year in range(start + 1, end + 1):
        ctx = obs.context(state, year)
        if hasattr(strategy, "obs"):
            strategy.obs, strategy.ctx = obs, ctx
        elig = {
            "dams": int(eligible(state, setup, bidx, DOMESTIC, year, 0, genetics).size),
            "sires": int(eligible(state, setup, bidx, DOMESTIC, year, 1, genetics).size),
        }
        simulate_year(state, setup, year, genetics, strategy, rng, active_breeds={bidx})
        obs.update(state, year)
        if (year - start) % cfg.ebv_every_years.value == 0:
            obs.evaluate_ebv(state, year, h2)
        ctx_end = obs.context(state, year + 1)
        m = year_metrics(state, genetics, obs, ctx_end, bidx, year, elig, he0)
        m.update(plan_diagnostics(strategy))
        for k, v in m.items():
            rows.append({"metric": k, "value": v, "year": year})
    df = pd.DataFrame(rows)
    df.insert(0, "experiment", cfg.id)
    df.insert(1, "breed", part.breed)
    df.insert(2, "strategy", part.strategy)
    df.insert(3, "adoption", part.adoption)
    df.insert(4, "replicate", part.replicate)
    df["generation"] = (df["year"] - start) / gi
    df["seconds"] = time.perf_counter() - t0
    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)
        df.to_parquet(out_dir / f"{part.name}.parquet", index=False)
    log.info("%s done in %.1f s", part.name, time.perf_counter() - t0)
    return df


DIAGNOSTICS = {
    "budget": "D1_budget",
    "achieved_C": "D2_achieved_C",
    "infeasible": "D3_infeasible",
    "n_sires_with_quota": "D4_n_sires_with_quota",
    "solver_seconds": "D5_solver_seconds",
    "relaxed_caps": "D6_relaxed_caps",
    "overflow": "D7_overflow",
    "C_now": "D8_C_now",
    "L": "D9_generation_interval_used",
    "carrier_relaxed": "D10_carrier_relaxed",
    "carrier_planned": "D11_carrier_planned",
}


def plan_diagnostics(strategy: Any) -> dict[str, float]:
    """Per-year planner diagnostics of P12 strategies (empty for others); resets the plan."""
    inner = getattr(strategy, "inner", strategy)
    plan = getattr(inner, "last_plan", None)
    if plan is None:
        return {}
    inner.last_plan = None
    return {
        name: float(plan.diagnostics[key])
        for key, name in DIAGNOSTICS.items()
        if key in plan.diagnostics and plan.diagnostics[key] is not None
    }


def _drop_other_breeds(state: SimState, genetics: DogGenetics, breed: int) -> None:
    """Free the neutral alleles of animals of other breeds (they never breed again)."""
    a = state.animals
    holders = np.flatnonzero(genetics.row_of[: genetics.n] >= 0)
    keep = holders[a.breed[holders] == breed]
    rows = genetics.row_of[keep]
    genetics.neutral = genetics.neutral[rows].copy()
    genetics.row_of[holders] = -1
    genetics.row_of[keep] = np.arange(keep.size)
    genetics.n_rows = keep.size


def prepared_state(dataset: str, breed: str) -> Path:
    """End-of-history state of `dataset` with neutral alleles kept only for `breed` (smaller and
    faster to load in every worker). Built once and cached in the run's cache/ folder."""
    rp = resolve_dataset(dataset)
    path = rp.cache / f"experiment_state_{breed}"
    if (path / "state.npz").exists():
        return path
    state, rng = SimState.load(rp.state)
    bidx = state.breed_ids.index(breed)
    setup = load_run_setup(rp.root)
    genetics = DogGenetics.from_setup(setup)
    genetics.load_arrays(state.extra)
    _drop_other_breeds(state, genetics, bidx)
    state.extra = dict(genetics.state_arrays())
    state.save(path, rng)
    return path


def _worker(args: tuple[Path, Part, Path]) -> str:
    cfg_path, part, out = args
    run_part(load_experiment(cfg_path), part, out)
    return part.name


def run_experiment(
    cfg_path: Path, workers: int = 1, limit: int | None = None, only: list[str] | None = None
) -> Path:
    """Run all unfinished parts (in parallel); returns the parts folder."""
    cfg = load_experiment(cfg_path)
    out = experiment_dir(cfg.id) / "parts"
    out.mkdir(parents=True, exist_ok=True)
    (experiment_dir(cfg.id) / "config.yaml").write_text(
        yaml.safe_dump(cfg.model_dump(mode="json"), sort_keys=False)
    )
    todo = [p for p in parts_of(cfg) if not (out / f"{p.name}.parquet").exists()]
    for breed in {p.breed for p in todo}:
        prepared_state(cfg.dataset, breed)
    if only:
        todo = [p for p in todo if p.strategy in only]
    if limit is not None:
        todo = todo[:limit]
    if workers <= 1:
        for p in todo:
            run_part(cfg, p, out)
    else:
        with ProcessPoolExecutor(max_workers=workers) as ex:
            futs = [ex.submit(_worker, (cfg_path, p, out)) for p in todo]
            for f in as_completed(futs):
                log.info("finished %s", f.result())
    return out


def load_results(exp_id: str) -> pd.DataFrame:
    parts = sorted((experiment_dir(exp_id) / "parts").glob("*.parquet"))
    return pd.concat([pd.read_parquet(p) for p in parts], ignore_index=True)
