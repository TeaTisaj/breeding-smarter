"""Known-answer tests for the pedigree engine (P2 task 2.2).

Expected values are derived in `tests/fixtures/pedigrees.py` (module docstring):
F(offspring of a x b) = f_ab; f_aa = (1 + F_a) / 2; f(parent, offspring) = 1/4 and
f(full sibs) = 1/4 for non-inbred unrelated parents; f(half sibs) = 1/8.
"""

import numpy as np
import pytest

from breeding_smarter.pedigree import (
    Pedigree,
    PedigreeError,
    inbreeding,
    inbreeding_py,
    pair_kinship,
    pair_kinship_decomposed,
)
from breeding_smarter.pedigree.reference import relationship_matrix_dense
from tests.fixtures.pedigrees import (
    ALL_FIXTURES,
    FULL_SIBS,
    HALF_SIBS,
    INBRED_ANCESTOR,
    PARENT_OFFSPRING,
    REPEATED_FULL_SIB,
    UNRELATED,
)


def ped_of(fx):
    sire, dam, sex = fx.arrays()
    return Pedigree.from_arrays(sire, dam, sex)


@pytest.mark.parametrize("fx", ALL_FIXTURES, ids=lambda f: f.name)
@pytest.mark.parametrize("impl", ["numba", "python", "dense"])
def test_expected_F(fx, impl):
    ped = ped_of(fx)
    if impl == "numba":
        F = inbreeding(ped)[0]
    elif impl == "python":
        F = inbreeding_py(ped)[0]
    else:
        F = np.diag(relationship_matrix_dense(ped)) - 1
    for i, expected in fx.expected_F.items():
        assert F[i] == pytest.approx(expected, abs=1e-12), (fx.name, i)


@pytest.mark.parametrize("fx", ALL_FIXTURES, ids=lambda f: f.name)
def test_expected_kinship(fx):
    ped = ped_of(fx)
    F, D = inbreeding(ped)
    for (a, b), expected in fx.expected_kinship.items():
        assert pair_kinship(ped, F, D, a, b) == pytest.approx(expected, abs=1e-12)
        dec = pair_kinship_decomposed(ped, F, D, a, b)
        assert sum(dec.values()) == pytest.approx(expected, abs=1e-12)


def test_kinship_identities():
    ped = ped_of(UNRELATED)
    F, D = inbreeding(ped)
    assert pair_kinship(ped, F, D, 0, 0) == pytest.approx(0.5)  # non-inbred founder
    assert pair_kinship(ped, F, D, 0, 2) == pytest.approx(0.25)  # parent-offspring
    ped = ped_of(INBRED_ANCESTOR)
    F, D = inbreeding(ped)
    assert F[4] == pytest.approx(0.25)
    assert pair_kinship(ped, F, D, 4, 4) == pytest.approx(0.625)  # (1 + 0.25) / 2
    ped = ped_of(FULL_SIBS)
    F, D = inbreeding(ped)
    assert pair_kinship(ped, F, D, 2, 3) == pytest.approx(0.25)
    ped = ped_of(HALF_SIBS)
    F, D = inbreeding(ped)
    assert pair_kinship(ped, F, D, 3, 4) == pytest.approx(0.125)


def test_repeated_full_sib_recurrence():
    """F_t = 1/4 (1 + 2 F_{t-1} + F_{t-2})."""
    F = inbreeding(ped_of(REPEATED_FULL_SIB))[0]
    gens = [0.0, 0.0, F[4], F[6], F[8]]
    for t in range(2, 5):
        assert gens[t] == pytest.approx(0.25 * (1 + 2 * gens[t - 1] + gens[t - 2]))
    assert list(F[[4, 6, 8]]) == pytest.approx([0.25, 0.375, 0.5])


def test_decomposition_names_the_common_ancestor():
    ped = ped_of(PARENT_OFFSPRING)
    F, D = inbreeding(ped)
    dec = pair_kinship_decomposed(ped, F, D, 0, 2)
    assert set(dec) == {0}  # all of f(A, C) traces to A
    assert dec[0] == pytest.approx(0.25)


def test_D_convention():
    """D_i = 0.5 - 0.25 (F_s + F_d) with F[-1] = -1: 1 (no parents), 0.75 (one), 0.5 (two)."""
    ped = Pedigree.from_arrays(
        np.array([-1, -1, 0, 0]), np.array([-1, -1, 1, -1]), np.array([1, 0, 1, 0])
    )
    _, D = inbreeding(ped)
    assert list(D) == pytest.approx([1.0, 1.0, 0.5, 0.75])


def test_edge_cases():
    empty = Pedigree.from_arrays(np.array([], int), np.array([], int), np.array([], int))
    F, D = inbreeding(empty)
    assert len(F) == 0 and len(D) == 0
    one = Pedigree.from_arrays(np.array([-1]), np.array([-1]), np.array([1]))
    assert list(inbreeding(one)[0]) == [0.0]
    only_dam = Pedigree.from_arrays(np.array([-1, -1]), np.array([-1, 0]), np.array([0, 1]))
    assert list(inbreeding(only_dam)[0]) == [0.0, 0.0]


def test_validate_rejects_bad_pedigrees():
    with pytest.raises(PedigreeError, match="topological"):
        Pedigree.from_arrays(np.array([1, -1]), np.array([-1, -1]), np.array([1, 1]))
    with pytest.raises(PedigreeError, match="sex"):
        Pedigree.from_arrays(np.array([-1, 0]), np.array([-1, -1]), np.array([0, 1]))
    with pytest.raises(PedigreeError, match="sex"):
        Pedigree.from_arrays(np.array([-1, -1]), np.array([-1, 0]), np.array([1, 1]))


def test_from_registry_and_truth(tmp_path):
    tables = REPEATED_FULL_SIB.tables()
    ped = Pedigree.from_registry(tables["registry/animals"])
    assert list(inbreeding(ped)[0][[4, 6, 8]]) == pytest.approx([0.25, 0.375, 0.5])
    assert ped.breed_codes == ("SYN_M",)
    tped = Pedigree.from_truth(tables["truth/animals_truth"])
    assert np.array_equal(tped.sire, ped.sire) and np.array_equal(tped.dam, ped.dam)
