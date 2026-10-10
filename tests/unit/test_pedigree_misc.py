import math

import numpy as np
import pytest

from breeding_smarter.pedigree import (
    Pedigree,
    Relationship,
    complete_generations,
    equivalent_generations,
    inbreeding,
    max_generations,
    nearest_common_ancestor,
    population_report,
    relationship,
)
from breeding_smarter.pedigree.population import (
    founder_stats,
    gene_diversity,
    generation_interval,
    gini,
    ne_census,
    ne_individual_delta_f,
    sire_usage,
    top_share,
)
from breeding_smarter.pedigree.reference import relationship_matrix_dense
from breeding_smarter.pedigree.relationships import (
    close_relative_flags,
    generations_to_nearest_common_ancestor,
)
from tests.fixtures.pedigrees import FIRST_COUSINS, HALF_SIBS, REPEATED_FULL_SIB
from tests.fixtures.random_ped import random_pedigree

R = Relationship


def ped_of(fx):
    return Pedigree.from_arrays(*fx.arrays())


def test_relationships_first_cousins_fixture():
    ped = ped_of(FIRST_COUSINS)
    # 0 A, 1 B, 2 E, 3 G, 4 C=AxB, 5 D=AxB, 6 H=CxE, 7 I=GxD, 8 X=HxI
    assert relationship(ped, 4, 5) == {R.FULL_SIBLINGS}
    assert relationship(ped, 0, 4) == {R.PARENT_OFFSPRING}
    assert relationship(ped, 0, 6) == {R.GRANDPARENT_GRANDCHILD}
    assert relationship(ped, 6, 7) == {R.NONE_DETECTED}  # first cousins: not a banned degree
    assert relationship(ped, 5, 6) == {R.AUNT_UNCLE_NIECE_NEPHEW}
    assert relationship(ped, 3, 3) == {R.SELF}
    assert nearest_common_ancestor(ped, 6, 7) == (0, 2, 2)
    assert generations_to_nearest_common_ancestor(ped, 6, 7) == 4
    assert nearest_common_ancestor(ped, 0, 1) is None


def test_relationships_half_sibs():
    ped = ped_of(HALF_SIBS)
    assert relationship(ped, 3, 4) == {R.HALF_SIBLINGS}


def test_close_relative_flags_match_relationship():
    ped = random_pedigree(300, 0.1, seed=3, window=8)
    females = np.flatnonzero(ped.sex == 0)
    males = np.flatnonzero(ped.sex == 1)
    for dam in females[-20:]:
        flags = close_relative_flags(ped, int(dam), males)
        for k, s in enumerate(males):
            rel = relationship(ped, int(dam), int(s))
            for r, arr in flags.items():
                assert arr[k] == (r in rel), (dam, s, r)


def test_completeness_and_offspring_index():
    ped = ped_of(REPEATED_FULL_SIB)
    assert list(max_generations(ped)) == [0, 0, 1, 1, 2, 2, 3, 3, 4]
    assert list(complete_generations(ped)) == [0, 0, 1, 1, 2, 2, 3, 3, 4]
    e = equivalent_generations(ped)
    assert e[2] == pytest.approx(1.0) and e[4] == pytest.approx(2.0)
    ptr, ch = ped.offspring_index()
    assert list(ch[ptr[2] : ptr[3]]) == [4, 5]
    assert list(ch[ptr[8] : ptr[9]]) == []
    one_known = Pedigree.from_arrays([-1, -1], [-1, 0], [0, 1])
    assert list(complete_generations(one_known)) == [0, 0]
    assert list(max_generations(one_known)) == [0, 1]


def test_deep_loops_sire_across_generations():
    """One sire mated to his daughters, granddaughters, ... (deep loops)."""
    sire = [-1, -1]
    dam = [-1, -1]
    sex = [1, 0]
    last_f = 1
    for _ in range(12):
        sire.append(0)
        dam.append(last_f)
        sex.append(0)
        last_f = len(sire) - 1
    ped = Pedigree.from_arrays(sire, dam, sex)
    F = inbreeding(ped)[0]
    A = relationship_matrix_dense(ped)
    np.testing.assert_allclose(F, np.diag(A) - 1, atol=1e-12)
    assert F[-1] > 0.45  # approaches 0.5 with repeated backcrossing


def test_gini_and_top_share():
    assert gini([1, 1, 1, 1]) == 0.0
    assert top_share([10, 1, 1, 1, 1]) == pytest.approx(10 / 14)
    assert gini([0, 0, 0, 10]) == pytest.approx(0.75)
    assert top_share([]) == 0.0


def test_ne_and_diversity_basics():
    F = np.array([0.0, 0.1, 0.2])
    eqg = np.array([0.5, 3.0, 5.0])
    ne = ne_individual_delta_f(F, eqg, np.ones(3, bool))
    df = np.array([1 - 0.9 ** (1 / 2), 1 - 0.8 ** (1 / 4)])
    assert ne.n_used == 2 and ne.n_excluded == 1
    assert ne.ne == pytest.approx(1 / (2 * df.mean()))
    ped = ped_of(FIRST_COUSINS)
    c = ne_census(ped, np.isin(np.arange(9), [4, 5, 6, 7, 8]))
    # sires {0, 3, 4, 6} = 4; dams {1, 2, 5, 7} = 4 -> 4*4*4/8 = 8
    assert (c.n_sires, c.n_dams, c.ne) == (4, 4, 8.0)
    assert gene_diversity(np.array([0.25, 0.5]), np.array([True, True])) == 0.625


def test_founder_stats_two_founders():
    ped = ped_of(FIRST_COUSINS)
    _, D = inbreeding(ped)
    ref = np.zeros(9, bool)
    ref[8] = True
    fs = founder_stats(ped, ref, D)
    # X = H x I; H = C x E, I = G x D: A, B contribute 1/8 each via C and D; E, G 1/4 each
    contrib = dict(fs.top_founders)
    assert contrib == pytest.approx({2: 0.25, 3: 0.25, 0: 0.25, 1: 0.25})
    assert fs.fe == pytest.approx(4.0)
    assert fs.fg == pytest.approx(1 / (2 * 0.5 * (1 + 0.0625)))
    assert fs.sum_contributions == pytest.approx(1.0)


def test_generation_interval_and_sire_usage():
    ped = random_pedigree(400, 0.05, seed=1)
    ref = ped.birth_year >= 2090
    gi = generation_interval(ped, ref)
    assert gi.n_parent_links > 0 and gi.overall > 0
    su = sire_usage(ped, year=2099, window_years=5)
    assert 0 < su.top_sire_share <= su.top20_share <= 1
    assert su.n_offspring == int(((ped.birth_year > 2094) & (ped.birth_year <= 2099)).sum())
    assert su.n_above_fci >= 1  # 5% of ~20 offspring per year is tiny


def test_population_report_runs():
    ped = random_pedigree(500, 0.1, seed=2)
    ped = Pedigree.from_arrays(ped.sire, ped.dam, ped.sex, ped.birth_year, breed_codes=("SYN_M",))
    F, D = inbreeding(ped)
    rep = population_report(ped, F, D, equivalent_generations(ped), "SYN_M", 2124, 4.5)
    assert rep.n_reference == int(((ped.birth_year > 2119.5) & (ped.birth_year <= 2124)).sum())
    assert 0 < rep.gene_diversity < 1
    assert rep.founders.sum_contributions == pytest.approx(1.0)
    assert math.isfinite(rep.ne_census.ne)


def test_pairwise_close_flags_match_relationship():
    from breeding_smarter.pedigree.relationships import pairwise_close_flags

    ped = random_pedigree(300, 0.1, seed=5, window=8)
    females = np.flatnonzero(ped.sex == 0)[-30:]
    males = np.flatnonzero(ped.sex == 1)
    dd, ss = np.meshgrid(females, males, indexing="ij")
    flags = pairwise_close_flags(ped.sire, ped.dam, dd.ravel(), ss.ravel())
    banned = {R.PARENT_OFFSPRING, R.FULL_SIBLINGS, R.HALF_SIBLINGS, R.GRANDPARENT_GRANDCHILD}
    for f, d, s in zip(flags, dd.ravel(), ss.ravel(), strict=True):
        assert f == bool(relationship(ped, int(d), int(s)) & banned)
