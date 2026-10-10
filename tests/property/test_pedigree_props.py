"""Property tests: the engine against the dense oracle on random pedigrees (P2 section 3)."""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from breeding_smarter.pedigree import (
    A_times,
    contributions,
    equivalent_generations,
    inbreeding,
    inbreeding_extend,
    inbreeding_py,
    kinship_matrix,
    kinship_to_all,
    mean_kinship,
    pair_kinship,
    pair_kinship_decomposed,
)
from breeding_smarter.pedigree.reference import (
    equivalent_generations_brute,
    relationship_matrix_dense,
)
from tests.fixtures.random_ped import random_pedigree

SETTINGS = settings(max_examples=200, deadline=None, suppress_health_check=[HealthCheck.too_slow])
peds = st.builds(
    random_pedigree,
    n=st.integers(1, 150),
    p_unknown=st.floats(0.0, 0.3),
    seed=st.integers(0, 2**32 - 1),
)


@SETTINGS
@given(peds)
def test_F_equals_dense_diagonal(ped):
    A = relationship_matrix_dense(ped)
    F, _ = inbreeding(ped)
    np.testing.assert_allclose(F, np.diag(A) - 1, atol=1e-12)


@SETTINGS
@given(peds, st.integers(0, 2**32 - 1))
def test_A_times_equals_dense(ped, seed):
    A = relationship_matrix_dense(ped)
    _, D = inbreeding(ped)
    x = np.random.default_rng(seed).normal(size=ped.n)
    np.testing.assert_allclose(A_times(ped, D, x), A @ x, atol=1e-10)
    X = np.random.default_rng(seed + 1).normal(size=(ped.n, 3))
    np.testing.assert_allclose(A_times(ped, D, X), A @ X, atol=1e-10)


@SETTINGS
@given(peds, st.data())
def test_pair_kinship_and_decomposition(ped, data):
    A = relationship_matrix_dense(ped)
    F, D = inbreeding(ped)
    for _ in range(5):
        a = data.draw(st.integers(0, ped.n - 1))
        b = data.draw(st.integers(0, ped.n - 1))
        f = pair_kinship(ped, F, D, a, b)
        assert f == pytest.approx(A[a, b] / 2, abs=1e-12)
        assert sum(pair_kinship_decomposed(ped, F, D, a, b).values()) == pytest.approx(
            A[a, b] / 2, abs=1e-12
        )
        np.testing.assert_allclose(kinship_to_all(ped, D, a), A[a] / 2, atol=1e-12)


@SETTINGS
@given(peds)
def test_shortcut_on_and_off_identical(ped):
    np.testing.assert_array_equal(inbreeding(ped, shortcut=True)[0], inbreeding(ped, False)[0])


@SETTINGS
@given(peds, st.data())
def test_pruning_invariance(ped, data):
    F, D = inbreeding(ped)
    keep = np.array(data.draw(st.lists(st.integers(0, ped.n - 1), min_size=1, max_size=10)))
    sub, old_to_new = ped.prune(keep)
    kept = old_to_new >= 0
    assert kept[keep].all()
    F2, D2 = inbreeding(sub)
    np.testing.assert_allclose(F2, F[kept], atol=1e-12)
    np.testing.assert_allclose(D2, D[kept], atol=1e-12)
    A = relationship_matrix_dense(ped)
    K = kinship_matrix(ped, D, np.unique(keep))
    np.testing.assert_allclose(K, A[np.ix_(np.unique(keep), np.unique(keep))] / 2, atol=1e-12)


@SETTINGS
@given(peds, st.data())
def test_founder_contributions_sum_to_one(ped, data):
    ph, old_to_new = ped.with_phantom_parents()
    ph.validate()
    assert ((ph.sire >= 0) == (ph.dam >= 0)).all()
    k = data.draw(st.integers(1, ped.n))
    ref = np.zeros(ph.n, bool)
    ref[old_to_new[ped.n - k :]] = True
    u = contributions(ph, ref)
    founders = (ph.sire < 0) & (ph.dam < 0)
    assert (u >= 0).all()
    assert u[founders].sum() == pytest.approx(1.0, abs=1e-9)
    # phantoms do not change F of the real animals
    np.testing.assert_allclose(inbreeding(ph)[0][old_to_new], inbreeding(ped)[0], atol=1e-12)


@settings(max_examples=200, deadline=None)
@given(
    st.builds(
        random_pedigree,
        n=st.integers(1, 40),
        p_unknown=st.floats(0.0, 0.3),
        seed=st.integers(0, 2**32 - 1),
        window=st.just(6),
    )
)
def test_eqg_equals_brute_force(ped):
    e = equivalent_generations(ped)
    for i in range(ped.n):
        assert e[i] == pytest.approx(equivalent_generations_brute(ped, i), abs=1e-12)


@SETTINGS
@given(peds, st.data())
def test_mean_kinship_equals_dense(ped, data):
    A = relationship_matrix_dense(ped)
    _, D = inbreeding(ped)
    ref = np.array(data.draw(st.lists(st.booleans(), min_size=ped.n, max_size=ped.n)))
    if not ref.any():
        ref[-1] = True
    mk = mean_kinship(ped, D, ref)
    np.testing.assert_allclose(mk, (A[:, ref] / 2).mean(axis=1), atol=1e-12)


@SETTINGS
@given(peds)
def test_numba_equals_python(ped):
    F1, D1 = inbreeding(ped)
    F2, D2 = inbreeding_py(ped)
    np.testing.assert_allclose(F1, F2, atol=1e-12)
    np.testing.assert_allclose(D1, D2, atol=1e-12)


@SETTINGS
@given(peds, st.lists(st.integers(0, 150), min_size=1, max_size=4))
def test_inbreeding_extend_in_chunks(ped, cuts):
    F, D = inbreeding(ped)
    Fx, Dx = np.zeros(0), np.zeros(0)
    start = 0
    for c in sorted({min(c, ped.n) for c in cuts} | {ped.n}):
        if c < start:
            continue
        sub, _ = ped.subset_arrays(np.arange(ped.n) < c)
        Fx, Dx = inbreeding_extend(sub, Fx, Dx, start)
        start = c
    np.testing.assert_allclose(Fx, F, atol=1e-12)
    np.testing.assert_allclose(Dx, D, atol=1e-12)
