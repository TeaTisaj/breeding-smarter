"""Matching tests (P7 section 4)."""

import numpy as np
import pytest

from breeding_smarter.io import RunPaths, configs_dir, update_manifest
from breeding_smarter.matching import load_scoring, rank_fast, recommend_sires, score_pair
from breeding_smarter.matching.components import inbreeding_subscore, transmission
from breeding_smarter.matching.context import DatasetContext, infer_hereditary_clear
from breeding_smarter.pedigree import Pedigree
from breeding_smarter.sim.run import generate, load_setup, make_genetics, snapshot_configs
from tests.fixtures.pedigrees import tables_from_arrays, write_tables

TINY = configs_dir() / "sim" / "tiny.yaml"
DATE = "2012-06-01"

# FIRST_COUSINS plus 9 = unrelated male founder, 10 = half-brother of the dam (G x E)
SIRE = [-1, -1, -1, -1, 0, 0, 4, 3, 6, -1, 3]
DAM = [-1, -1, -1, -1, 1, 1, 2, 5, 7, -1, 2]
SEX = ["M", "F", "F", "M", "M", "F", "M", "F", "M", "M", "M"]
DAM_I = 7


@pytest.fixture(scope="module")
def fx_ctx(tmp_path_factory):
    run = write_tables(
        tables_from_arrays(SIRE, DAM, SEX, breed="SYN_L"), tmp_path_factory.mktemp("m") / "fx"
    )
    snapshot_configs(load_setup(TINY), TINY, run / "config_snapshot")
    update_manifest(run / "manifest.json", scale=0.02)
    return DatasetContext.from_run(RunPaths(run), "fixture")


def test_subscore_boundaries_and_monotonicity():
    sc = load_scoring()
    f = np.array([0.0, 0.03, 0.0775, 0.125, 0.3])
    s = inbreeding_subscore(f, sc)
    assert s[0] == 1 and s[1] == 1 and s[3] == 0 and s[4] == 0
    assert s[2] == pytest.approx(0.5)
    assert np.all(np.diff(s) <= 0)


def test_health_probabilities():
    q = np.array([0.2])
    t = transmission(np.array([[0], [1], [2], [-1]], np.int8), q)
    assert list(t[:, 0]) == [0.0, 0.5, 1.0, 0.2]
    pen = 0.8
    assert t[0, 0] * t[3, 0] * pen == 0  # clear x anything
    assert t[1, 0] * t[1, 0] * pen == pytest.approx(0.25 * pen)
    assert t[2, 0] * t[1, 0] * pen == pytest.approx(0.5 * pen)


def test_hereditary_clear_inference():
    ped = Pedigree.from_arrays([-1, -1, 0, 0], [-1, -1, 1, 1], [1, 0, 0, 1])
    dna = np.array([[0], [0], [-1], [1]], np.int8)
    geno, inferred = infer_hereditary_clear(dna, ped)
    assert geno[2, 0] == 0 and inferred[2, 0]
    assert geno[3, 0] == 1 and not inferred[3, 0]  # tested result wins
    dna2 = np.array([[1], [0], [-1], [-1]], np.int8)
    geno2, inf2 = infer_hereditary_clear(dna2, ped)
    assert geno2[2, 0] == -1 and not inf2[2, 0]  # a carrier parent: no inference


def test_fixture_ranking(fx_ctx):
    rec = recommend_sires(fx_ctx, DAM_I, DATE)
    excluded = {s for s, _ in rec.excluded}
    assert 10 in excluded  # half-brother: EU close-relative ban
    assert any("half siblings" in m for s, ms in rec.excluded if s == 10 for m in ms)
    assert 8 in excluded  # the dam's own son
    ranked = {r.sire for r in rec.ranked}
    assert {0, 3}.isdisjoint(ranked)  # grandfather and father: over 12 years, not candidates
    only_f = load_scoring().with_weights(
        {"inbreeding": 1, "diversity": 0, "health": 0, "ebv": 0, "sire_use": 0, "depth": 0}
    )
    rec2 = recommend_sires(fx_ctx, DAM_I, DATE, scoring=only_f)
    order = [r.sire for r in rec2.ranked]
    assert order.index(9) < order.index(6)  # unrelated above first cousin


def test_explanation_shares(fx_ctx):
    card = score_pair(fx_ctx, 6, DAM_I, DATE)  # first cousins: F = 1/16 via A and B
    assert card.predicted_coi == pytest.approx(0.0625)
    shares = [a.share for a in card.ancestors]
    assert sum(shares) + card.other_ancestors_share == pytest.approx(1.0, abs=1e-12)
    assert shares == sorted(shares, reverse=True)
    assert {a.idx for a in card.ancestors} == {0, 1}
    assert card.ancestors[0].generations_sire_side == 3
    assert "Why this COI?" in card.to_markdown()
    assert card.to_dict()["sire"] == 6


def test_score_pair_equals_recommendation(fx_ctx):
    rec = recommend_sires(fx_ctx, DAM_I, DATE)
    for r in rec.ranked:
        card = score_pair(fx_ctx, r.sire, DAM_I, DATE)
        assert card.score == pytest.approx(r.score)
        assert card.tier == r.tier


@pytest.fixture(scope="module")
def tiny_ctx(tmp_path_factory):
    run = generate(
        TINY, out=tmp_path_factory.mktemp("t"), genetics=make_genetics("dog", TINY), run_id="tiny"
    )
    return DatasetContext.from_run(RunPaths(run), "tiny")


def test_rank_fast_equals_recommend(tiny_ctx):
    a = tiny_ctx.animals
    dams = np.flatnonzero((a["sex"] == "F").to_numpy() & (a["birth_date"].dt.year >= 2021))
    for d in dams[:5]:
        rec = recommend_sires(tiny_ctx, int(d), "2026-11-01", top_k=0)
        sires, scores = rank_fast(tiny_ctx, int(d), "2026-11-01")
        assert [r.sire for r in rec.ranked] == list(sires)
        np.testing.assert_allclose([r.score for r in rec.ranked], scores)
        assert rec.n_candidates == len(rec.ranked) + rec.n_excluded
