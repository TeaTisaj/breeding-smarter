"""Matching on dataset v1: golden snapshot of the demo dams and performance (P7 section 4).

Skipped when dataset v1 is not on disk (CI has no data). Update the snapshot only on purpose:
`uv run python -m tests.integration.test_matching_v1` and commit it with a reason.
"""

import json
import time
from pathlib import Path

import numpy as np
import pytest

from breeding_smarter.io.datasets import resolve_dataset
from breeding_smarter.matching import DatasetContext, load_context, recommend_sires
from breeding_smarter.matching.examples import load_demo

GOLDEN = Path(__file__).parents[1] / "fixtures" / "golden" / "demo_top10.json"


def _have_v1() -> bool:
    try:
        resolve_dataset("v1")
        return True
    except (FileNotFoundError, KeyError):
        return False


pytestmark = [pytest.mark.integration, pytest.mark.skipif(not _have_v1(), reason="no dataset v1")]


def snapshot(ctx: DatasetContext) -> dict[str, list[list[object]]]:
    demo = load_demo()
    out = {}
    for d in demo["dams"]:
        rec = recommend_sires(
            ctx, ctx.idx_of(d["reg_no"]), demo["mating_date"], demo["profile"], top_k=0
        )
        out[d["reg_no"]] = [
            [str(ctx.rules.reg_no[r.sire]), round(r.score, 4), r.tier] for r in rec.ranked[:10]
        ]
    return out


@pytest.fixture(scope="module")
def ctx():
    return load_context("v1")


def test_golden_top10(ctx):
    assert snapshot(ctx) == json.loads(GOLDEN.read_text())


def test_demo_dams_tell_their_story(ctx):
    demo = load_demo()
    d3 = demo["dams"][2]
    rec = recommend_sires(ctx, ctx.idx_of(d3["reg_no"]), demo["mating_date"], top_k=1)
    assert rec.card(rec.ranked[0].sire).depth_warning
    d2 = demo["dams"][1]
    rec2 = recommend_sires(ctx, ctx.idx_of(d2["reg_no"]), demo["mating_date"], top_k=0)
    ranked = [ctx.rules.reg_no[r.sire] for r in rec2.ranked]
    assert d2["popular_sire"] in ranked and ranked.index(d2["popular_sire"]) > 10


@pytest.mark.slow
def test_recommend_performance():
    t0 = time.perf_counter()
    ctx = load_context("v1")
    a = ctx.animals
    dams = np.flatnonzero(
        (a["breed_id"] == "SYN_L").to_numpy()
        & (a["sex"] == "F").to_numpy()
        & (a["birth_date"].dt.year == 2022).to_numpy()
    )
    t1 = time.perf_counter()
    recommend_sires(ctx, int(dams[0]), "2026-11-01")
    cold = time.perf_counter() - t1
    t2 = time.perf_counter()
    recommend_sires(ctx, int(dams[1]), "2026-11-01")
    warm = time.perf_counter() - t2
    print(f"context load {t1 - t0:.2f} s, cold {cold:.3f} s, warm {warm:.3f} s")
    assert cold < 2.0
    assert warm < 0.3


if __name__ == "__main__":
    GOLDEN.write_text(json.dumps(snapshot(load_context("v1")), indent=1) + "\n")
    print(f"wrote {GOLDEN}")
