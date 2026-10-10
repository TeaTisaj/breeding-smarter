"""Genetics tests (P4 section 2)."""

import numpy as np
import pandas as pd
import pytest
from scipy.stats import chisquare

from breeding_smarter.config.loader import load_genetics, load_loci
from breeding_smarter.evaluation.blup import henderson_ainv
from breeding_smarter.io import configs_dir, read_table
from breeding_smarter.pedigree import inbreeding
from breeding_smarter.pedigree.reference import relationship_matrix_dense
from breeding_smarter.schema.tables import ANIMALS_TRUTH, DNA_TESTS, EBV, GENOTYPES_TRUTH
from breeding_smarter.sim.genetics import DogGenetics
from breeding_smarter.sim.run import generate, load_setup, make_genetics
from breeding_smarter.sim.state import SimState
from tests.fixtures.random_ped import random_pedigree

TINY = configs_dir() / "sim" / "tiny.yaml"
DEFAULT = configs_dir() / "sim" / "default.yaml"


def _model_with_parents(n_founders=2):
    setup = load_setup(TINY)
    g = DogGenetics(setup, load_genetics(), load_loci())
    st = SimState(breed_ids=["SYN_L"])
    gids = st.add_animals(
        n_founders, breed=0, sex=np.array([1, 0] * (n_founders // 2)), death_year=3000
    )
    g.init_founders(st, gids, np.random.default_rng(0))
    return setup, g, st, gids


def _offspring(g, st, sire, dam, n, rng):
    kids = st.add_animals(
        n, breed=0, sex=rng.integers(0, 2, n), death_year=3000, sire=sire, dam=dam
    )
    g.make_offspring(st, np.full(n, sire), np.full(n, dam), kids, rng)
    return kids


@pytest.mark.slow
def test_gene_drop_full_sib_offspring_f():
    """Offspring of full sibs from unrelated founders: mean realised IBD near 0.25."""
    _, g, st, (s, d) = _model_with_parents()
    rng = np.random.default_rng(1)
    sibs = _offspring(g, st, s, d, 400, rng)
    sons = sibs[st.animals.sex[sibs] == 1]
    daughters = sibs[st.animals.sex[sibs] == 0]
    f = []
    for k in range(2000):
        kid = _offspring(
            g, st, int(sons[k % sons.size]), int(daughters[k % daughters.size]), 1, rng
        )
        f.append(st.animals.f_true[kid[0]])
    f = np.array(f)
    se = f.std(ddof=1) / np.sqrt(f.size)
    assert abs(f.mean() - 0.25) < 3 * se + 1e-9, (f.mean(), se)


@pytest.mark.slow
def test_mendelian_carrier_by_carrier_121():
    _setup, g, st, (s, d) = _model_with_parents()
    g.geno[[s, d], :] = 1
    kids = _offspring(g, st, int(s), int(d), 10_000, np.random.default_rng(2))
    for k in range(g.K):
        counts = np.bincount(g.geno[kids, k], minlength=3)
        p = chisquare(counts, f_exp=np.array([0.25, 0.5, 0.25]) * counts.sum()).pvalue
        assert p > 0.001, (k, counts)


@pytest.mark.slow
def test_allele_frequency_no_systematic_drift():
    """Random mating preserves the expected allele frequency (mean drift near 0)."""
    setup, g, _st, _ = _model_with_parents(2)
    rng = np.random.default_rng(3)
    drifts = []
    for _ in range(50):
        st2 = SimState(breed_ids=["SYN_L"])
        g2 = DogGenetics(setup, g.cfg, g.loci)
        n0 = 40
        gids = st2.add_animals(
            n0, breed=0, sex=np.r_[np.ones(20), np.zeros(20)].astype(np.int8), death_year=3000
        )
        g2.init_founders(st2, gids, rng)
        p0 = g2.geno[gids, 1].mean() / 2
        parents = gids
        for _gen in range(5):
            males = parents[st2.animals.sex[parents] == 1]
            females = parents[st2.animals.sex[parents] == 0]
            sires = rng.choice(males, n0)
            dams = rng.choice(females, n0)
            kids = st2.add_animals(
                n0,
                breed=0,
                sex=np.r_[np.ones(20), np.zeros(20)].astype(np.int8),
                death_year=3000,
                sire=sires,
                dam=dams,
            )
            g2.make_offspring(st2, sires, dams, kids, rng)
            parents = kids
        drifts.append(g2.geno[parents, 1].mean() / 2 - p0)
    d = np.array(drifts)
    assert abs(d.mean()) < 3 * d.std(ddof=1) / np.sqrt(d.size)


def test_hd_base_variance_and_regression():
    setup, g, _st, _ = _model_with_parents(2)
    rng = np.random.default_rng(4)
    st2 = SimState(breed_ids=["SYN_L"])
    n = 20_000
    gids = st2.add_animals(n, breed=0, sex=(np.arange(n) % 2).astype(np.int8), death_year=3000)
    g2 = DogGenetics(setup, g.cfg, g.loci)
    g2.init_founders(st2, gids, rng)
    liab = g2.tbv[gids] + rng.normal(0, np.sqrt(1 - g2.h2), n)
    assert 0.9 <= liab.var() <= 1.1
    sires = gids[::2][:5000]
    dams = gids[1::2][:5000]
    kids = st2.add_animals(
        5000, breed=0, sex=np.zeros(5000, np.int8), death_year=3000, sire=sires, dam=dams
    )
    g2.make_offspring(st2, sires, dams, kids, rng)
    mid = 0.5 * (g2.tbv[sires] + g2.tbv[dams])
    slope = np.polyfit(mid, g2.tbv[kids], 1)[0]
    assert 0.95 <= slope <= 1.05


@pytest.mark.parametrize("seed", range(20))
def test_henderson_ainv_equals_inverse(seed):
    ped = random_pedigree(int(np.random.default_rng(seed).integers(2, 80)), 0.2, seed)
    _, D = inbreeding(ped)
    A = relationship_matrix_dense(ped)
    np.testing.assert_allclose(
        henderson_ainv(ped.sire, ped.dam, D).toarray(), np.linalg.inv(A), atol=1e-8
    )


def test_neutral_alleles_dropped_for_dead():
    setup = load_setup(TINY)
    from breeding_smarter.sim.run import run_simulation

    g = make_genetics("dog", TINY)
    st, _ = run_simulation(setup, 1, g, until=1975)
    holders = np.flatnonzero(g.row_of[: g.n] >= 0)
    alive_next = np.flatnonzero(st.animals.death_year > 1975)
    np.testing.assert_array_equal(holders, alive_next)
    assert g.n_rows == alive_next.size


@pytest.fixture(scope="module")
def genetics_run(tmp_path_factory):
    out = tmp_path_factory.mktemp("gen")
    return generate(
        DEFAULT, out=out, genetics=make_genetics("dog", DEFAULT, 0.05), run_id="d005", scale=0.05
    )


def test_dna_results_equal_truth_and_novel_x_hidden(genetics_run):
    dna = read_table(genetics_run / DNA_TESTS.filename, DNA_TESTS)
    assert len(dna) > 0
    assert "NOVEL_X" not in set(dna["locus_id"])
    truth = read_table(genetics_run / ANIMALS_TRUTH.filename, ANIMALS_TRUTH)
    geno = read_table(genetics_run / GENOTYPES_TRUTH.filename, GENOTYPES_TRUTH)
    gid_of = truth.dropna(subset=["idx"]).set_index("idx")["gid"]
    dna["gid"] = dna["idx"].map(gid_of)
    m = dna.merge(geno, on=["gid", "locus_id"])
    names = np.array(["clear", "carrier", "affected"])
    assert (names[m["n_risk_alleles"]] == m["genotype"]).all()
    for p in genetics_run.rglob("registry/*.parquet"):
        assert b"NOVEL_X" not in p.read_bytes()


def test_blup_beats_phenotype(genetics_run):
    """corr(EBV, TBV) > corr(-grade score, TBV) among screened animals with >= 5 screened
    progeny (P4 test)."""
    from breeding_smarter.io import read_table as rt
    from breeding_smarter.schema.tables import ANIMALS, HEALTH_TESTS

    a = rt(genetics_run / ANIMALS.filename, ANIMALS)
    h = rt(genetics_run / HEALTH_TESTS.filename, HEALTH_TESTS)
    e = rt(genetics_run / EBV.filename, EBV)
    t = rt(genetics_run / ANIMALS_TRUTH.filename, ANIMALS_TRUTH)
    score = h.set_index("idx")["result"].map({"A": 1, "B": 2, "C": 3, "D": 4, "E": 5})
    screened = set(score.index)
    kids = a[a["idx"].isin(screened)]
    n_prog = pd.concat([kids["sire_idx"], kids["dam_idx"]]).dropna().astype(int).value_counts()
    sel = [i for i in screened if n_prog.get(i, 0) >= 5]
    assert len(sel) >= 10
    tbv = t.dropna(subset=["idx"]).set_index("idx")["tbv_hd"]
    ebv = e.set_index("idx")["ebv_index"]
    c_ebv = np.corrcoef(ebv.loc[sel], -tbv.loc[sel])[0, 1]
    c_phe = np.corrcoef(-score.loc[sel], -tbv.loc[sel])[0, 1]
    assert c_ebv > c_phe, (c_ebv, c_phe)
