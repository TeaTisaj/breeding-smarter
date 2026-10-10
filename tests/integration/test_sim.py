"""Simulator tests (P3 section 3)."""

import hashlib
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from breeding_smarter.io import configs_dir, read_table
from breeding_smarter.pedigree import Pedigree, max_generations
from breeding_smarter.schema import validate_run
from breeding_smarter.schema.tables import ANIMALS, LITTERS
from breeding_smarter.sim.interfaces import NullGenetics
from breeding_smarter.sim.run import generate, load_setup, run_simulation, seeds
from breeding_smarter.sim.state import SimState

TINY = configs_dir() / "sim" / "tiny.yaml"
DEFAULT = configs_dir() / "sim" / "default.yaml"


def _hashes(run: Path) -> dict[str, str]:
    return {
        str(p.relative_to(run)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(run.rglob("*.parquet"))
        if "cache" not in p.parts
    }


@pytest.fixture(scope="module")
def tiny_run(tmp_path_factory):
    out = tmp_path_factory.mktemp("sim")
    t0 = time.perf_counter()
    run = generate(TINY, out=out, genetics=NullGenetics(), run_id="tiny-a")
    return run, time.perf_counter() - t0


def test_tiny_runs_fast_and_validates(tiny_run):
    run, secs = tiny_run
    assert secs < 5.0
    res = validate_run(run)
    assert res.ok, res.summary()


def test_determinism(tiny_run, tmp_path):
    run, _ = tiny_run
    again = generate(TINY, out=tmp_path, genetics=NullGenetics(), run_id="tiny-b")
    assert _hashes(run) == _hashes(again)
    other = generate(TINY, seed=7, out=tmp_path, genetics=NullGenetics(), run_id="tiny-c")
    assert _hashes(run) != _hashes(other)


def test_determinism_across_processes(tmp_path):
    """Byte-identical output under different PYTHONHASHSEED values (set/dict order)."""
    import os
    import subprocess
    import sys

    code = (
        "from pathlib import Path; from breeding_smarter.sim.run import generate;"
        "from breeding_smarter.sim.interfaces import NullGenetics;"
        f"generate(Path({str(TINY)!r}), out=Path({str(tmp_path)!r}), genetics=NullGenetics(),"
        "run_id='h'+__import__('os').environ['PYTHONHASHSEED'], validate=False)"
    )
    for hs in ("1", "2"):
        env = {**os.environ, "PYTHONHASHSEED": hs}
        subprocess.run([sys.executable, "-c", code], check=True, env=env)
    assert _hashes(tmp_path / "h1") == _hashes(tmp_path / "h2")


def test_topology_and_litter_mates(tiny_run):
    run, _ = tiny_run
    a = pd.read_parquet(run / "registry" / "animals.parquet")
    for col in ("sire_idx", "dam_idx"):
        has = a[a[col].notna()]
        assert (has[col] < has["idx"]).all()
    lit = a[a["litter_id"].notna()].groupby("litter_id")["idx"].agg(["min", "max", "count"])
    assert ((lit["max"] - lit["min"] + 1) == lit["count"]).all()


def test_imports_have_shallow_recorded_pedigrees(tiny_run):
    run, _ = tiny_run
    a = pd.read_parquet(run / "registry" / "animals.parquet")
    state, _ = SimState.load(run / "state")
    setup = load_setup(TINY)
    depth = setup.breeds[0].market.import_pedigree_depth.value
    ped = Pedigree.from_registry(a)
    mg = max_generations(ped)
    gids = np.flatnonzero(state.animals.registered)
    reg_year = state.animals.reg_year[gids]
    imports = np.flatnonzero(a["import_flag"].to_numpy())
    assert imports.size > 0
    for i in imports:
        if mg[i] <= depth:
            continue
        # deeper records only through ancestors registered before this import arrived
        anc = np.flatnonzero(ped.ancestors_mask(np.array([i])))
        assert (reg_year[anc] < reg_year[i]).any()


def test_close_matings_below_leak_rate(tiny_run):
    """Close-relative matings after avoidance stay near (1 - avoidance) x the base rate.

    Base rate = share of close pairs among first-choice sires; a resampled pair can be close
    again, so the expected final rate is base * ((1 - p) + p * base) per retry chain.
    """
    run, _ = tiny_run
    state, _ = SimState.load(run / "state")
    p = load_setup(TINY).breeds[0].market.close_mating_avoidance.value
    c = state.meta["close_SYN_L"]
    base = c["close_initial"] / c["pairs"]
    final = c["close_final"] / c["pairs"]
    assert c["pairs"] > 50
    assert final <= base * ((1 - p) + p * base) * 1.5 + 2 / c["pairs"], (base, final)


def test_save_load_continues_identically(tmp_path):
    setup = load_setup(TINY)
    full, _ = run_simulation(setup, 3, NullGenetics(), until=1995)
    part, rng = run_simulation(setup, 3, NullGenetics(), until=1990)
    part.save(tmp_path / "st", rng)
    loaded, rng2 = SimState.load(tmp_path / "st")
    cont, _ = run_simulation(setup, 3, NullGenetics(), until=1995, state=loaded, rng=rng2)
    assert cont.n == full.n
    for k in full.animals.spec:
        np.testing.assert_array_equal(cont.animals[k], full.animals[k], err_msg=k)
    for k in full.litters.spec:
        np.testing.assert_array_equal(cont.litters[k], full.litters[k], err_msg=k)


def test_seeds_are_independent_streams():
    s = seeds(1)
    assert s["sim"].random() != s["writer"].random()


@pytest.fixture(scope="module")
def scaled_run(tmp_path_factory):
    out = tmp_path_factory.mktemp("scaled")
    return generate(DEFAULT, scale=0.1, out=out, genetics=NullGenetics(), run_id="default-0.1")


@pytest.mark.slow
def test_scaled_default_validates(scaled_run):
    res = validate_run(scaled_run)
    assert res.ok, res.summary()


@pytest.fixture(scope="module")
def full_run(tmp_path_factory):
    out = tmp_path_factory.mktemp("full")
    return generate(DEFAULT, out=out, genetics=NullGenetics(), run_id="default-full")


@pytest.mark.slow
def test_registrations_follow_target(full_run):
    """Registry-era registrations within 10% of the target curve (full-scale run).

    Compared over 5-year blocks for SYN_L and SYN_M and 10-year blocks for SYN_S, whose
    40 to 90 registrations a year make 5-year sums too noisy (litter clustering) for a 10%
    criterion.
    """
    setup = load_setup(DEFAULT)
    a = read_table(full_run / "registry" / "animals.parquet", ANIMALS)
    dom = a[(a["studbook"] != "FOREIGN") & ~a["import_flag"]]
    counts = dom.groupby([dom["breed_id"], dom["birth_date"].dt.year]).size()
    years = range(1985, 2025)
    for b in setup.breeds:
        block = 10 if b.breed_id == "SYN_S" else 5
        target = np.array([b.population.registrations_per_year.at(y) for y in years])
        sim = np.array([counts.get((b.breed_id, y), 0) for y in years])
        t_b = target.reshape(-1, block).sum(1)
        s_b = sim.reshape(-1, block).sum(1)
        rel = np.abs(s_b - t_b) / t_b
        assert (rel < 0.10).all(), (b.breed_id, list(zip(t_b, s_b, strict=True)))


@pytest.mark.slow
def test_litter_size_close_to_config(full_run):
    setup = load_setup(DEFAULT)
    lit = read_table(full_run / "registry" / "litters.parquet", LITTERS)
    for b in setup.breeds:
        m = lit.loc[lit["breed_id"] == b.breed_id, "n_born"].mean()
        assert abs(m - b.reproduction.litter_size_mean.value) < 0.3, (b.breed_id, m)


@pytest.mark.slow
def test_full_default_run_validates(full_run):
    res = validate_run(full_run)
    assert res.ok, res.summary()
