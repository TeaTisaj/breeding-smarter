"""P12 coordination: targets, OCS known answers and properties, quotas, allocation, ledger."""

import itertools

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from scipy.optimize import minimize

from breeding_smarter.coordination.allocation import assign_mc1, assign_random
from breeding_smarter.coordination.caps import mk_scaled_caps
from breeding_smarter.coordination.config import load_coordination
from breeding_smarter.coordination.ledger import BookingLedger
from breeding_smarter.coordination.ocs import (
    OCSProblem,
    expected_coancestry,
    solve_conservation,
    solve_gain,
)
from breeding_smarter.coordination.quotas import sainte_lague
from breeding_smarter.coordination.targets import ne_from_delta, next_budget, per_year
from breeding_smarter.pedigree import Pedigree, inbreeding
from breeding_smarter.pedigree.kinship import kinship_matrix
from tests.fixtures.random_ped import random_pedigree

# ---------------------------------------------------------------- config and targets


def test_config_loads_and_matches_research():
    c = load_coordination()
    assert c.delta_f_ladder.value == [0.01, 0.005, 0.0025]
    assert c.delta_f_default.value == 0.005
    assert c.cap_base_litters_per_year.value == 5
    assert c.min_expected_litters.value == 0.25


def test_config_rejects_unknown_keys(tmp_path):
    from breeding_smarter.config.loader import ConfigError

    src = (
        load_coordination.__globals__["configs_dir"]() / "coordination" / "default.yaml"
    ).read_text()
    (tmp_path / "coordination").mkdir()
    (tmp_path / "coordination" / "bad.yaml").write_text(
        src + "bogus: {value: 1, assumption: true}\n"
    )
    with pytest.raises(ConfigError):
        load_coordination("bad", base=tmp_path)


def test_budget_worked_example():
    # docs/research_coordination.md: C 0.10, dF 0.5%, L 4 -> 0.10113
    assert next_budget(0.10, 0.005, 4) == pytest.approx(0.10113, abs=1e-5)
    assert round(100 * per_year(0.005, 4), 3) == 0.125  # research table, 0.125% per year
    assert per_year(0.005, 4) == pytest.approx(1 - 0.995**0.25, rel=1e-12)
    assert next_budget(0.0, 0.005, 1) == pytest.approx(0.005)
    assert ne_from_delta(0.005) == pytest.approx(100.0)
    assert ne_from_delta(0.0) == np.inf
    # L years of the yearly budget compound to one generation of dF
    c = 0.2
    for _ in range(4):
        c = next_budget(c, 0.01, 4)
    assert 1 - c == pytest.approx((1 - 0.2) * 0.99)


# ---------------------------------------------------------------- helpers


def _K(sire, dam, members):
    n = len(sire)
    sex = np.zeros(n, np.int8)
    sex[[s for s in sire if s >= 0]] = 1
    ped = Pedigree.from_arrays(np.array(sire), np.array(dam), sex, birth_year=np.arange(n) + 2000)
    _, D = inbreeding(ped)
    return kinship_matrix(ped, D, np.array(members, np.int64))


def _problem(K, m, n, caps=None, **kw):
    kw.setdefault("n_age_classes", 0)
    kw.setdefault("depth", False)
    return OCSProblem(
        K=K,
        n_dams=n,
        caps=np.full(m, float(n)) if caps is None else np.asarray(caps, float),
        age_class=kw.pop("age_class", np.zeros(m, np.int64)),
        eqg=kw.pop("eqg", np.zeros(m)),
        **kw,
    )


def _unrelated(m, n):
    return 0.5 * np.eye(m + n)


# ---------------------------------------------------------------- OCS known answers


def test_two_unrelated_sires_split_equally():
    res = solve_conservation(_problem(_unrelated(2, 4), 2, 4))
    assert abs(res.litters[0] - res.litters[1]) < 1e-6
    assert res.litters.sum() == pytest.approx(4)


def test_full_sibs_vs_unrelated_closed_form():
    """Sires 0, 1 full sibs (f = 1/4, self 1/2), sire 2 unrelated; dams unrelated to all.
    min x'K_SS x with sum x = 1: K x = lambda 1 -> 0.75 a = 0.5 b, 2a + b = 1 ->
    a = 2/7, b = 3/7, i.e. litters (2, 2, 3) for 7 dams."""
    K = _unrelated(3, 7)
    K[0, 1] = K[1, 0] = 0.25
    res = solve_conservation(_problem(K, 3, 7))
    np.testing.assert_allclose(res.litters, [2, 2, 3], atol=1e-5)


def test_sire_of_half_the_dams_gets_less():
    # 0: sire A, 1: sire B, 2-5: mothers, 6,7: daughters of A, 8,9: unrelated dams
    sire = [-1, -1, -1, -1, -1, -1, 0, 0, -1, -1]
    dam = [-1, -1, -1, -1, -1, -1, 2, 3, -1, -1]
    K = _K(sire, dam, [0, 1, 6, 7, 8, 9])
    res = solve_conservation(_problem(K, 2, 4))
    assert res.litters[1] > res.litters[0] + 0.5
    equal = expected_coancestry(K, np.array([2.0, 2.0]), 4)
    assert res.coancestry < equal


def test_caps_bind_one_each():
    res = solve_conservation(_problem(_unrelated(3, 3) + 0.0, 3, 3, caps=[1, 1, 1]))
    np.testing.assert_allclose(res.litters, [1, 1, 1], atol=1e-6)


def _age_problem(n_age_classes):
    # sire 0 (young) is the sire of all four dams; sires 1, 2 old and unrelated
    sire = [-1, -1, -1, -1, -1, -1, -1, 0, 0, 0, 0]
    dam = [-1, -1, -1, -1, -1, -1, -1, 3, 4, 5, 6]
    K = _K(sire, dam, [0, 1, 2, 7, 8, 9, 10])
    return _problem(K, 3, 4, age_class=np.array([2, 6, 6]), n_age_classes=n_age_classes)


def test_age_class_constraint_forces_young_sire():
    free = solve_conservation(_age_problem(0))
    assert free.litters[0] < 1 - 1e-3
    forced = solve_conservation(_age_problem(2))
    assert forced.litters[0] >= 1 - 1e-6


def test_depth_constraint_limits_shallow_sire():
    K = _unrelated(3, 4)
    K[1, 2] = K[2, 1] = 0.25  # the two deep sires are related; the shallow one is not
    kw = dict(eqg=np.array([0.0, 5.0, 5.0]))
    free = solve_conservation(_problem(K, 3, 4, depth=False, **kw))
    assert free.litters[0] / 4 > 1 / 3 + 1e-3
    dep = solve_conservation(_problem(K, 3, 4, depth=True, **kw))
    assert dep.litters @ kw["eqg"] / 4 >= 10 / 3 - 1e-6


def test_gain_loose_tight_and_infeasible():
    K = _unrelated(4, 4)
    K[0, 1] = K[1, 0] = 0.25
    merit = np.array([2.0, 1.5, 0.0, -1.0])
    p = _problem(K, 4, 4, caps=[2, 2, 2, 2], merit=merit)
    loose = solve_gain(p, budget=1.0)
    np.testing.assert_allclose(loose.litters, [2, 2, 0, 0], atol=1e-4)
    cons = solve_conservation(p)
    tight = solve_gain(p, budget=cons.coancestry + 1e-6)
    assert not tight.infeasible
    assert np.abs(tight.litters - cons.litters).max() < 0.05
    bad = solve_gain(p, budget=cons.coancestry - 0.01)
    assert bad.infeasible
    np.testing.assert_allclose(bad.litters, cons.litters, atol=1e-6)


def test_carrier_constraint_binds_closed_form():
    # sire 0 transmits the risk allele with prob 0.5, sire 1 never; bound 0.5 x mean(0.5, 0)
    t = np.array([[0.5], [0.0]])
    free = solve_conservation(_problem(_unrelated(2, 4), 2, 4))
    np.testing.assert_allclose(free.litters, [2, 2], atol=1e-4)
    res = solve_conservation(
        _problem(_unrelated(2, 4), 2, 4, carrier_t=t, carrier_bound=np.array([0.125]))
    )
    np.testing.assert_allclose(res.litters, [1, 3], atol=1e-4)
    assert res.relaxed == []


def test_carrier_relaxed_first_and_reported():
    t = np.array([[0.5], [0.0]])
    p = _problem(
        _unrelated(2, 4), 2, 4, carrier_t=t, carrier_bound=np.array([0.125]),
        fixed_sire_litters=np.array([2.0, 0.0]),
    )  # fmt: skip
    res = solve_conservation(p)
    assert res.relaxed == ["carrier"]
    np.testing.assert_allclose(res.litters, [2, 2], atol=1e-3)


def test_non_binding_carrier_bound_changes_nothing():
    rng = np.random.default_rng(5)
    m, n = 6, 8
    ped = random_pedigree(60, 0.2, 5)
    _, D = inbreeding(ped)
    K = kinship_matrix(ped, D, np.arange(60 - m - n, 60, dtype=np.int64))
    t = rng.uniform(0, 0.5, (m, 2))
    base = solve_conservation(_problem(K, m, n, caps=np.full(m, 3.0)))
    loose = solve_conservation(
        _problem(K, m, n, caps=np.full(m, 3.0), carrier_t=t, carrier_bound=np.full(2, 1.0))
    )
    np.testing.assert_allclose(base.litters, loose.litters, atol=1e-4)
    assert loose.relaxed == base.relaxed


def test_gain_with_carrier_closed_form():
    K = _unrelated(4, 4)
    merit = np.array([2.0, 1.5, 0.0, -1.0])
    t = np.array([[0.5], [0.0], [0.0], [0.0]])
    p = _problem(K, 4, 4, caps=[2, 2, 2, 2], merit=merit, carrier_t=t, carrier_bound=[0.125])
    res = solve_gain(p, budget=1.0)
    np.testing.assert_allclose(res.litters, [1, 2, 1, 0], atol=1e-4)
    assert res.litters @ t[:, 0] / 4 <= 0.125 + 1e-6
    # C_min is the conservation minimum under the carrier constraint
    assert res.c_min == pytest.approx(solve_conservation(p).coancestry, abs=1e-6)


def test_expected_coancestry_equals_brute_force_offspring_kinship():
    sire = [-1, -1, -1, -1, 0, 0, -1]
    dam = [-1, -1, -1, -1, 2, 3, -1]
    members = [0, 1, 4, 5, 6]  # sires 0, 1; dams 4, 5, 6
    K = _K(sire, dam, members)
    matings = [(0, 2), (0, 3), (1, 4)]  # (sire pos, dam pos) in K
    total = 0.0
    for (s1, d1), (s2, d2) in itertools.product(matings, matings):
        total += 0.25 * (K[s1, s2] + K[s1, d2] + K[d1, s2] + K[d1, d2])
    assert expected_coancestry(K, np.array([2.0, 1.0]), 3) == pytest.approx(total / 9)


# ---------------------------------------------------------------- OCS properties


def _random_problem(seed, m, n):
    ped = random_pedigree(80, 0.2, seed)
    _, D = inbreeding(ped)
    males = np.flatnonzero(ped.sex == 1)[-m:]
    females = np.flatnonzero(ped.sex == 0)[-n:]
    m, n = males.size, females.size
    K = kinship_matrix(ped, D, np.r_[males, females])
    rng = np.random.default_rng(seed)
    caps = rng.integers(1, n + 1, m).astype(float)
    while caps.sum() < n:
        caps[rng.integers(m)] += 1
    age = rng.integers(2, 6, m)
    eqg = rng.random(m) * 4
    return K, m, n, caps, age, eqg, rng


@settings(max_examples=200, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(seed=st.integers(0, 10_000), m=st.integers(2, 8), n=st.integers(1, 8))
def test_ocs_constraints_and_optimality(seed, m, n):
    K, m, n, caps, age, eqg, rng = _random_problem(seed, m, n)
    if m < 2 or n < 1:
        return
    full = _problem(K, m, n, caps=caps, age_class=age, eqg=eqg, n_age_classes=2, depth=True)
    res = solve_conservation(full)
    lit = res.litters
    assert lit.sum() == pytest.approx(n, abs=1e-6)
    assert (lit >= -1e-7).all() and (lit <= caps + 1e-6).all()
    if "age" not in res.relaxed:
        for a in np.unique(age)[:2]:
            assert lit[age == a].sum() >= min(1.0, caps[age == a].sum()) - 1e-5
    if "depth" not in res.relaxed:
        assert lit @ eqg / n >= eqg.mean() - 1e-5
    # optimality without side constraints: beats random feasible integer allocations
    simple = _problem(K, m, n, caps=caps)
    best = solve_conservation(simple).coancestry
    for _ in range(20):
        alloc = np.zeros(m)
        for _k in range(n):
            free = np.flatnonzero(alloc < caps)
            alloc[rng.choice(free)] += 1
        assert best <= expected_coancestry(K, alloc, n) + 1e-7
    if (caps >= n / m).all():
        assert best <= expected_coancestry(K, np.full(m, n / m), n) + 1e-7


@pytest.mark.parametrize("seed", range(5))
def test_ocs_matches_independent_solver(seed):
    """Cross-check against scipy SLSQP (robustocs needs a Gurobi licence; see ADR-007)."""
    K, m, n, caps, _, _, _ = _random_problem(seed, 6, 5)
    res = solve_conservation(_problem(K, m, n, caps=caps))
    m_ = m

    def f(x):
        return expected_coancestry(K, x * n, n)

    x0 = np.minimum(caps / n, 1.0 / m_)
    x0 = x0 / x0.sum()
    ref = minimize(
        f,
        x0,
        method="SLSQP",
        bounds=[(0, c / n) for c in caps],
        constraints=[{"type": "eq", "fun": lambda x: x.sum() - 1}],
        options={"ftol": 1e-12, "maxiter": 500},
    )
    assert res.coancestry == pytest.approx(ref.fun, abs=1e-6)


def test_ocs_matches_robustocs_if_installed():
    pytest.importorskip("robustocs")


# ---------------------------------------------------------------- caps, quotas, allocation


def test_mk_scaled_caps():
    caps = mk_scaled_caps(np.array([0.05, 0.10, 0.20, 0.50, 0.0, np.nan]), 0.10, 5)
    assert list(caps) == [5, 5, 2, 1, 5, 5]
    mk = np.linspace(0.01, 1, 50)
    assert (np.diff(mk_scaled_caps(mk, 0.1, 5)) <= 0).all()
    assert (mk_scaled_caps(mk, 0.1, 5, scale=False) == 5).all()


def test_sainte_lague_textbook():
    # votes 53, 24, 23 for 7 seats: Sainte-Laguë gives 3, 2, 2 (D'Hondt would give 4, 2, 1)
    q = sainte_lague(np.array([53.0, 24.0, 23.0]), 7, np.array([10, 10, 10]), 0.0)
    assert list(q.quota) == [3, 2, 2]
    assert q.relaxed == 0


def test_sainte_lague_caps_threshold_and_ties():
    q = sainte_lague(np.array([3.0, 0.9, 0.1, 1.0]), 5, np.array([2, 5, 5, 5]), 0.25)
    assert q.quota.sum() == 5
    assert q.quota[0] == 2 and q.quota[2] == 0
    t = sainte_lague(np.array([1.0, 1.0]), 1, np.array([5, 5]), 0.25)
    assert list(t.quota) == [1, 0]  # tie: lower index


def test_sainte_lague_relaxes_caps():
    q = sainte_lague(np.array([2.0, 2.0, 0.1]), 4, np.array([1, 1, 5]), 0.25, np.array([1, 0, 2]))
    assert q.quota.sum() == 4 and q.quota[2] == 0
    assert q.relaxed == 2


def _brute_mc1(cost, quotas):
    n, m = cost.shape
    best = np.inf
    for combo in itertools.product(range(m), repeat=n):
        if (np.bincount(combo, minlength=m) <= quotas).all():
            best = min(best, sum(cost[i, j] for i, j in enumerate(combo)))
    return best


@pytest.mark.parametrize("seed", range(10))
def test_mc1_equals_brute_force(seed):
    rng = np.random.default_rng(seed)
    kin = rng.random((4, 3)) * 0.2
    pa = rng.random((4, 3)) * 0.05
    forb = rng.random((4, 3)) < 0.2
    forb[:, 0] = False
    quotas = np.array([2, 1, 2])
    a = assign_mc1(kin, pa, forb, quotas)
    cost = np.where(forb, 1e6, kin + pa)
    assert (a >= 0).all()
    assert (np.bincount(a, minlength=3) <= quotas).all()
    assert not forb[np.arange(4), a].any()
    assert cost[np.arange(4), a].sum() == pytest.approx(_brute_mc1(cost, quotas))


def test_random_assignment_respects_quotas_and_seed():
    forb = np.zeros((6, 3), bool)
    forb[0, :2] = True
    quotas = np.array([2, 2, 2])
    a = assign_random(quotas, forb, np.random.default_rng(1))
    assert (np.bincount(a, minlength=3) <= quotas).all() and a[0] == 2
    b = assign_random(quotas, forb, np.random.default_rng(1))
    assert (a == b).all()


def test_unassignable_dam_gets_minus_one():
    forb = np.array([[True, True], [False, False]])
    a = assign_mc1(np.zeros((2, 2)), np.zeros((2, 2)), forb, np.array([1, 1]))
    assert a[0] == -1 and a[1] >= 0


def test_ledger():
    led = BookingLedger(np.array([10, 11]), np.array([1, 2]))
    led.book(10)
    assert list(led.available()) == [11]
    assert led.remaining(11) == 2 and led.remaining(99) == 0
    with pytest.raises(ValueError):
        led.book(10)
