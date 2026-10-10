"""Run a simulation and write a run folder (P3 task 3.9)."""

from __future__ import annotations

import logging
import shutil
import time
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

from breeding_smarter.config.loader import config_hash, load_breed, load_sim, load_species
from breeding_smarter.config.models import SimConfig
from breeding_smarter.io.manifest import write_manifest
from breeding_smarter.io.parquet import write_table
from breeding_smarter.io.paths import RunPaths, configs_dir, data_dir, make_run_id
from breeding_smarter.schema.tables import TABLES
from breeding_smarter.sim.demography import sample_death
from breeding_smarter.sim.interfaces import GeneticsModel, MatingStrategy, NullGenetics, SimSetup
from breeding_smarter.sim.kennels import REGS_PER_KENNEL, create_kennels, pick_kennels
from breeding_smarter.sim.market import MarketStrategy
from breeding_smarter.sim.reproduction import simulate_year
from breeding_smarter.sim.state import DOMESTIC, SimState
from breeding_smarter.sim.writer import to_tables

log = logging.getLogger(__name__)
FOUNDER_AGE_YEARS = (1, 6)  # base founders are born 1 to 6 years before the start (assumption)


def load_setup(config_path: Path, scale: float | None = None) -> SimSetup:
    sim = load_sim(config_path)
    if scale is not None:
        sim = sim.model_copy(update={"scale": scale})
    return SimSetup(
        sim=sim,
        species=load_species(sim.species),
        breeds=tuple(load_breed(b) for b in sim.breeds),
    )


def seeds(seed: int) -> dict[str, np.random.Generator]:
    """Child generators from one master seed (SeedSequence.spawn)."""
    sim_ss, writer_ss, extra_ss = np.random.SeedSequence(seed).spawn(3)
    return {
        "sim": np.random.Generator(np.random.PCG64(sim_ss)),
        "writer": np.random.Generator(np.random.PCG64(writer_ss)),
        "extra": np.random.Generator(np.random.PCG64(extra_ss)),
    }


def init_state(setup: SimSetup, genetics: GeneticsModel, rng: np.random.Generator) -> SimState:
    """Kennels and unrelated base founders (true F = 0) for every breed."""
    sim = setup.sim
    state = SimState(breed_ids=[b.breed_id for b in setup.breeds])
    state.country_code("HR")
    start = sim.start_year
    for b, cfg in enumerate(setup.breeds):
        regs = cfg.population.registrations_per_year
        n_dom = round(regs.at(sim.end_year) * sim.scale / REGS_PER_KENNEL)
        n_for = round(
            sim.foreign.size_factor.value
            * regs.at(sim.registry_start_year)
            * sim.scale
            / REGS_PER_KENNEL
        )
        create_kennels(state, b, n_dom, n_for, sim.foreign.countries, rng)
        n = max(
            sim.registry.min_founders.value,
            round(cfg.population.founders_base_generation.value * sim.scale),
        )
        lo, hi = FOUNDER_AGE_YEARS
        by = start - rng.integers(lo, hi + 1, n)
        doy = rng.integers(1, 366, n)
        d_year, d_doy, d_cause = sample_death(by, doy, setup.species, rng)
        # founders must survive into the first simulated year
        d_year = np.maximum(d_year, start + 1)
        sex = (rng.random(n) < setup.species.sex_ratio_male.value).astype(np.int8)
        gids = state.add_animals(
            n,
            breed=b,
            subpop=DOMESTIC,
            sex=sex,
            birth_year=by,
            birth_doy=doy,
            death_year=d_year,
            death_doy=d_doy,
            death_cause=d_cause,
            kennel=pick_kennels(state, b, DOMESTIC, n, rng),
            is_candidate=True,
            attractiveness=rng.normal(0, setup.species.attractiveness_sd.value, n),
            fertility=rng.lognormal(0.0, setup.species.fertility_log_sd.value, n),
        )
        state.animals.data["birth_kennel"][gids] = state.animals.kennel[gids]
        genetics.init_founders(state, gids, rng)
    state.year = start - 1
    state.meta["start_year"] = start
    return state


def run_simulation(
    setup: SimSetup,
    seed: int,
    genetics: GeneticsModel | None = None,
    strategy: MatingStrategy | None = None,
    until: int | None = None,
    state: SimState | None = None,
    rng: np.random.Generator | None = None,
    active_breeds: set[int] | None = None,
    progress: Callable[[int], None] | None = None,
) -> tuple[SimState, np.random.Generator]:
    """Advance from a fresh state (or `state`) to year `until` (default: config end year)."""
    genetics = genetics or NullGenetics()
    strategy = strategy or MarketStrategy()
    if state is None:
        rng = seeds(seed)["sim"]
        state = init_state(setup, genetics, rng)
    elif rng is None:
        raise ValueError("continuing a state needs its RNG")
    end = until if until is not None else setup.sim.end_year
    for year in range(state.year + 1, end + 1):
        simulate_year(state, setup, year, genetics, strategy, rng, active_breeds)
        if progress is not None:
            progress(year)
    return state, rng


def save_state(path: Path, state: SimState, rng: np.random.Generator, genetics: GeneticsModel):
    state.extra = dict(genetics.state_arrays())
    return state.save(path, rng)


def snapshot_configs(setup: SimSetup, config_path: Path, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "sim").mkdir(exist_ok=True)
    (dest / "sim" / config_path.name).write_text(Path(config_path).read_text())
    for sub, names in (("species", [setup.sim.species]), ("breeds", setup.sim.breeds)):
        (dest / sub).mkdir(exist_ok=True)
        for nm in names:
            shutil.copy(configs_dir() / sub / f"{nm}.yaml", dest / sub / f"{nm}.yaml")
    shutil.copy(configs_dir() / "sources.yaml", dest / "sources.yaml")
    for sub, name in (("loci", setup.sim.loci), ("genetics", setup.sim.genetics)):
        src = configs_dir() / sub / f"{name}.yaml"
        if src.exists():
            (dest / sub).mkdir(exist_ok=True)
            shutil.copy(src, dest / sub / f"{name}.yaml")


def setup_hash(setup: SimSetup) -> str:
    return config_hash([setup.sim, setup.species, *setup.breeds])


def generate(
    config_path: Path,
    seed: int | None = None,
    scale: float | None = None,
    out: Path | None = None,
    genetics: GeneticsModel | None = None,
    run_id: str | None = None,
    progress: Callable[[int], None] | None = None,
    validate: bool = True,
) -> Path:
    """Simulate, write tables, manifest, config snapshot and end state; validate the run."""
    from breeding_smarter.schema.validate import validate_run

    setup = load_setup(config_path, scale)
    sim: SimConfig = setup.sim
    seed = sim.seed if seed is None else seed
    genetics = genetics or NullGenetics()
    t0 = time.perf_counter()
    started = datetime.now(UTC).isoformat(timespec="seconds")
    state, rng = run_simulation(setup, seed, genetics, progress=progress)
    t_sim = time.perf_counter() - t0
    name = sim.name if scale is None else f"{sim.name}x{scale:g}"
    rid = run_id or make_run_id(name, seed)
    paths = RunPaths((out or data_dir()) / rid)
    if paths.root.exists():
        shutil.rmtree(paths.root)
    tables = to_tables(
        state, setup, seeds(seed)["writer"], sim.end_year, contributor=_contrib(genetics)
    )
    for tname, df in tables.items():
        write_table(df, TABLES[tname], paths.root / TABLES[tname].filename)
    snapshot_configs(setup, config_path, paths.config_snapshot)
    if hasattr(genetics, "post_write"):
        genetics.post_write(paths.root)
    save_state(paths.state, state, rng, genetics)
    wall = time.perf_counter() - t0
    manifest = {
        "run_id": rid,
        "config_name": sim.name,
        "config_path": str(config_path),
        "config_hash": setup_hash(setup),
        "seed": seed,
        "scale": sim.scale,
        "started_at": started,
        "simulation_seconds": round(t_sim, 2),
        "generator_wall_seconds": round(wall, 2),
        "row_counts": {k: len(v) for k, v in tables.items()},
        "n_warnings": len(state.warnings),
        "warnings": state.warnings[:50],
        "genetics": type(genetics).__name__,
    }
    write_manifest(paths.manifest, **manifest)
    from breeding_smarter.io.manifest import update_manifest

    update_manifest(
        paths.manifest,
        row_counts={name: pq_rows(paths.root / spec.filename) for name, spec in TABLES.items()},
    )
    if validate:
        from breeding_smarter.config.loader import load_loci

        res = validate_run(paths.root, allowed_loci=set(load_loci(sim.loci).ids))
        update_manifest(paths.manifest, validation_ok=res.ok, validation_summary=res.summary())
        if not res.ok:
            log.error("validation failed:\n%s", res.summary())
    return paths.root


def pq_rows(path: Path) -> int:
    import pyarrow.parquet as pq

    return int(pq.ParquetFile(path).metadata.num_rows) if path.exists() else 0


def make_genetics(kind: str, config_path: Path, scale: float | None = None) -> GeneticsModel:
    """`null` (structure only) or `dog` (P4 genetics; falls back to null until P4 exists)."""
    if kind == "null":
        return NullGenetics()
    import importlib

    try:
        mod = importlib.import_module("breeding_smarter.sim.genetics")
    except ImportError:
        return NullGenetics()
    model: GeneticsModel = mod.DogGenetics.from_setup(load_setup(config_path, scale))
    return model


def _contrib(genetics: GeneticsModel) -> Any:
    return genetics if hasattr(genetics, "contribute_tables") else None
