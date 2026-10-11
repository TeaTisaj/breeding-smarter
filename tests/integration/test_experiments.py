"""Experiment tests on the tiny run (P8 section 6)."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from breeding_smarter.experiments.observed import ObservedRegistry
from breeding_smarter.experiments.runner import (
    Part,
    experiment_setup,
    load_experiment,
    prepared_state,
    run_part,
)
from breeding_smarter.experiments.strategies import StrategyParams, make_strategy
from breeding_smarter.experiments.summary import ne_from_series, t_interval
from breeding_smarter.io import configs_dir
from breeding_smarter.matching import load_scoring
from breeding_smarter.pedigree import inbreeding
from breeding_smarter.sim.genetics import DogGenetics
from breeding_smarter.sim.market import MarketStrategy
from breeding_smarter.sim.reproduction import simulate_year
from breeding_smarter.sim.run import generate, make_genetics
from breeding_smarter.sim.state import SimState

TINY = configs_dir() / "sim" / "tiny.yaml"


@pytest.fixture(scope="module")
def tiny(tmp_path_factory):
    out = tmp_path_factory.mktemp("xp")
    run = generate(TINY, out=out, genetics=make_genetics("dog", TINY), run_id="tiny-xp")
    doc = yaml.safe_load((configs_dir() / "experiments" / "headline.yaml").read_text())
    doc.update(id="T_tiny", dataset=str(run), generations=1, breeds={"SYN_L": {"replicates": 2}})
    cfg_path = out / "tiny_exp.yaml"
    cfg_path.write_text(yaml.safe_dump(doc))
    return run, load_experiment(cfg_path)


@pytest.mark.parametrize("sid", ["S0", "S1", "S2", "S3", "S4", "S3hc", "S3xc"])
def test_strategy_contract(tiny, sid):
    _, cfg = tiny
    df = run_part(cfg, Part("SYN_L", sid, 1.0, 0), debug=True)
    assert (df["metric"] == "M2_realised_ibd").any()
    assert df["value"].notna().any()


def test_determinism(tiny):
    _, cfg = tiny
    a = run_part(cfg, Part("SYN_L", "S3", 1.0, 1)).drop(columns="seconds")
    b = run_part(cfg, Part("SYN_L", "S3", 1.0, 1)).drop(columns="seconds")
    pd.testing.assert_frame_equal(a, b)


def _continue(run: Path, years: int):
    state, _ = SimState.load(prepared_state(str(run), "SYN_L"))
    setup = experiment_setup(run, 0, 1.0)
    g = DogGenetics.from_setup(setup)
    g.load_arrays(state.extra)
    obs = ObservedRegistry(state, g, setup, 0)
    rng = np.random.default_rng(5)
    for y in range(state.year + 1, state.year + 1 + years):
        simulate_year(state, setup, y, g, MarketStrategy(), rng, active_breeds={0})
        obs.update(state, y)
    return state, g, setup, obs


def test_incremental_context_equals_rebuild(tiny):
    run, _ = tiny
    state, _g, _setup, obs = _continue(run, 4)
    ped = obs.pedigree(state)
    F, D = inbreeding(ped)
    np.testing.assert_allclose(obs.F, F, atol=1e-12)
    np.testing.assert_allclose(obs.D, D, atol=1e-12)
    a = state.animals
    assert obs.n == int((a.registered & (a.breed == 0)).sum())
    year = state.year + 1
    ctx = obs.context(state, year)
    from breeding_smarter.pedigree import mean_kinship

    ref = ctx.reference("SYN_L", f"{year}-01-01")
    alive = (ctx.rules.birth_day <= ref.ref_day) & (ref.ref_day < ctx.rules.death_day)
    assert ref.n_ref <= int(alive.sum())
    mask = np.isfinite(ref.mk)
    sub_ref = np.zeros(obs.n, bool)
    # recompute MK from scratch with the same reference animals
    sp = ctx.species
    age = (ref.ref_day - ctx.rules.birth_day) / 365.25
    lo = (
        np.where(
            ped.sex == 1,
            sp.min_breeding_age_months.male.value,
            sp.min_breeding_age_months.female.value,
        )
        / 12
    )
    hi = np.where(
        ped.sex == 1, sp.max_breeding_age_years.male.value, sp.max_breeding_age_years.female.value
    )
    sub_ref = alive & (age >= lo) & (age <= hi)
    np.testing.assert_allclose(ref.mk[mask], mean_kinship(ped, D, sub_ref)[mask], atol=1e-12)
    # litter counts match the simulator
    L = state.litters
    n_lit = int((L.registered & (L.breed == 0)).sum())
    assert len(obs.lit_ids) == n_lit


def test_s4_respects_capacity(tiny):
    run, _ = tiny
    state, g, setup, obs = _continue(run, 1)
    params = StrategyParams()
    s4 = make_strategy("S4", params, load_scoring())
    year = state.year + 1
    s4.obs, s4.ctx = obs, obs.context(state, year)
    counted: dict[int, int] = {}
    orig = s4.plan_matings

    def wrapped(dams, sires, ctx, rng):
        out = orig(dams, sires, ctx, rng)
        for s in out[out >= 0]:
            counted[int(s)] = counted.get(int(s), 0) + 1
        return out

    s4.plan_matings = wrapped
    simulate_year(state, setup, year, g, s4, np.random.default_rng(1), active_breeds={0})
    assert counted, "no matings planned"
    assert max(counted.values()) <= s4.stats["s4_capacity"]


def test_summary_statistics():
    m, _lo, hi = t_interval(np.array([1.0, 2.0, 3.0]))
    assert m == 2.0
    assert hi - m == pytest.approx(4.302652729911275 / np.sqrt(3))
    gens = np.arange(0, 11, dtype=float)
    dF = 0.02
    f = 1 - (1 - dF) ** gens
    est, ne = ne_from_series(gens, f)
    assert est == pytest.approx(dF)
    assert ne == pytest.approx(25.0)
