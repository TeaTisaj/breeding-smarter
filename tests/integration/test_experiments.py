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


# ---------------------------------------------------------------- P12 coordination

P12_IDS = [
    "CC-none-rand",
    "CC-none-mc1",
    "CC-mkx-rand",
    "CC-mkx-mc1",
    "CC-cap-rand",
    "CC-cap-mc1",
    "CC-ocs-rand",
    "CC-ocs-mc1",
    "CC-ocs-mc1-oracle",
    "CC-gain050-mc1",
    "S3q",
    "S3q-c075",
    "S3q-gain010-c075",
    "S3q-gain010-hc",
    "S3q-gain010-c050-oracle",
    "S3q-cap",
    "S3q-mkx",
    "S3q-t1",
    "S3-u5",
    "S3q-gain010-c050f",
]


@pytest.mark.parametrize("sid", P12_IDS)
def test_p12_strategy_contract(tiny, sid):
    """Valid sires, no HARD-rule pair, quotas never exceeded beyond logged overflow."""
    _, cfg = tiny
    df = run_part(cfg, Part("SYN_L", sid, 1.0, 0), debug=True)
    metrics = set(df["metric"])
    assert {"M12_realised_coancestry", "M13_generation_interval", "M14_top5_sire_share"} <= metrics
    if (
        "ocs" in sid
        or "gain" in sid
        or (sid.startswith("S3q") and "-cap" not in sid and "-mkx" not in sid)
    ):
        assert "D2_achieved_C" in metrics
    if "gain" in sid:
        assert {"D1_budget", "D8_C_now"} <= metrics


def test_s3q_carrier_limit_is_planned(tiny):
    """The carrier limit reaches the planner and holds whenever it is not relaxed."""
    _, cfg = tiny
    df = run_part(cfg, Part("SYN_L", "S3q-c050", 1.0, 0), debug=True)
    planned = df[df["metric"] == "D11_carrier_planned"]["value"]
    relaxed = df[df["metric"] == "D10_carrier_relaxed"]["value"]
    assert planned.size > 0 and relaxed.size == planned.size


def test_s3q_free_only_carrier_partial_adoption_contract(tiny):
    """E11: the adopter-only carrier bound runs with non-adopters' fixed litters."""
    _, cfg = tiny
    df = run_part(cfg, Part("SYN_L", "S3q-gain010-c050f", 0.5, 0), debug=True)
    assert (df["metric"] == "D11_carrier_planned").any()


def test_s3q_partial_adoption_contract(tiny):
    _, cfg = tiny
    run_part(cfg, Part("SYN_L", "S3q", 0.5, 0), debug=True)


@pytest.mark.parametrize("sid", ["CC-ocs-mc1", "S3q", "S3q-gain010-c075"])
def test_p12_determinism(tiny, sid):
    _, cfg = tiny
    a = run_part(cfg, Part("SYN_L", sid, 1.0, 1)).drop(columns="seconds")
    b = run_part(cfg, Part("SYN_L", sid, 1.0, 1)).drop(columns="seconds")
    a = a[a["metric"] != "D5_solver_seconds"].reset_index(drop=True)
    b = b[b["metric"] != "D5_solver_seconds"].reset_index(drop=True)
    pd.testing.assert_frame_equal(a, b)


def test_true_kinship_incremental_equals_rebuild(tiny):
    from breeding_smarter.experiments.truth_kinship import TrueKinship

    run, _ = tiny
    state, _ = SimState.load(prepared_state(str(run), "SYN_L"))
    setup = experiment_setup(run, 0, 1.0)
    g = DogGenetics.from_setup(setup)
    g.load_arrays(state.extra)
    tk = TrueKinship(state, 0)
    rng = np.random.default_rng(3)
    for y in range(state.year + 1, state.year + 4):
        simulate_year(state, setup, y, g, MarketStrategy(), rng, active_breeds={0})
        assert tk.update(state) > 0
    full = TrueKinship(state, 0)
    np.testing.assert_array_equal(tk.gid, full.gid)
    np.testing.assert_allclose(tk.F, full.F, atol=1e-12)
    np.testing.assert_allclose(tk.D, full.D, atol=1e-12)
    # true-pedigree F of the newest animals equals the engine on the full true pedigree
    kids = tk.gid[-5:]
    K = tk.kinship(kids)
    np.testing.assert_allclose(np.diag(K), 0.5 * (1 + tk.F[-5:]), atol=1e-12)


def test_realised_coancestry_is_one_minus_he():
    from breeding_smarter.experiments.metrics import expected_heterozygosity
    from breeding_smarter.experiments.truth_kinship import realised_coancestry

    alleles = np.random.default_rng(0).integers(0, 4, (30, 7, 2)).astype(np.uint16)
    assert realised_coancestry(alleles) == pytest.approx(1 - expected_heterozygosity(alleles))
    same = np.zeros((5, 3, 2), np.uint16)
    assert realised_coancestry(same) == pytest.approx(1.0)


@pytest.fixture(scope="module")
def season(tiny):
    """A registry context one year into the experiment, with that year's candidates."""
    from breeding_smarter.sim.demography import eligible
    from breeding_smarter.sim.state import DOMESTIC

    run, _ = tiny
    state, g, setup, obs = _continue(run, 1)
    year = state.year + 1
    ctx = obs.context(state, year)
    dams = obs.idx(eligible(state, setup, 0, DOMESTIC, year, 0, g))[:12]
    sires = obs.idx(eligible(state, setup, 0, DOMESTIC, year, 1, g))
    return ctx, obs, year, dams[dams >= 0], sires[sires >= 0]


@pytest.mark.parametrize("control", ["none", "mkx", "cap", "ocs", "ocs_gain"])
@pytest.mark.parametrize("mating", ["random", "mc1"])
def test_plan_season_valid(season, control, mating):
    from breeding_smarter.coordination.config import load_coordination
    from breeding_smarter.coordination.planner import pair_inputs, plan_season
    from breeding_smarter.rules import day_number

    ctx, obs, year, dams, sires = season
    day = day_number(f"{year}-07-01")
    cfg = load_coordination()
    plan = plan_season(ctx, obs.breed_id, day, dams, sires, cfg, control, mating)
    a = plan.assignment
    assert a.size == dams.size and (a >= 0).all()
    assert set(a.tolist()) <= set(sires.tolist())
    forb, _ = pair_inputs(ctx, sires, dams, day, "exp_pairing")
    pos = {int(s): k for k, s in enumerate(sires)}
    assert not any(forb[k, pos[int(s)]] for k, s in enumerate(a))
    if plan.quotas is not None:
        counts = np.array([np.sum(a == s) for s in sires])
        assert np.maximum(counts - plan.quotas, 0).sum() <= plan.diagnostics.get("overflow", 0)
    again = plan_season(ctx, obs.breed_id, day, dams, sires, cfg, control, mating)
    np.testing.assert_array_equal(plan.assignment, again.assignment)


def test_none_mc1_is_per_dam_least_cost(season):
    from breeding_smarter.coordination.config import load_coordination
    from breeding_smarter.coordination.planner import pair_inputs, plan_season
    from breeding_smarter.pedigree.kinship import kinship_matrix
    from breeding_smarter.rules import day_number

    ctx, obs, year, dams, sires = season
    day = day_number(f"{year}-07-01")
    cfg = load_coordination()
    plan = plan_season(ctx, obs.breed_id, day, dams, sires, cfg, "none", "mc1")
    K = kinship_matrix(ctx.ped, ctx.D, np.r_[sires, dams])[sires.size :, : sires.size]
    forb, p_any = pair_inputs(ctx, sires, dams, day, "exp_pairing")
    cost = np.where(forb, np.inf, K + cfg.health_weight_in_allocation.value * p_any)
    np.testing.assert_array_equal(plan.assignment, sires[np.argmin(cost, axis=1)])


def test_mkx_quotas_for_breeder_choice(season):
    """E11 `S3q-mkx`: with mating `none`, sires above the candidates' mean MK get quota 0 and
    the others can take every dam."""
    from breeding_smarter.coordination.config import load_coordination
    from breeding_smarter.coordination.planner import plan_season
    from breeding_smarter.rules import day_number

    ctx, obs, year, dams, sires = season
    day = day_number(f"{year}-07-01")
    plan = plan_season(ctx, obs.breed_id, day, dams, sires, load_coordination(), "mkx", "none")
    mk = ctx.reference(obs.breed_id, day).mk[sires]
    assert plan.quotas is not None
    np.testing.assert_array_equal(plan.quotas, np.where(mk > np.nanmean(mk), 0, dams.size))
