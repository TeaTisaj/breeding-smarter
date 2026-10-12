"""Demo app smoke tests on a bundle built from the tiny run (P9 section 5)."""

import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from breeding_smarter.bundle import Bundle, export_bundle
from breeding_smarter.io import configs_dir
from breeding_smarter.sim.run import generate, make_genetics

APP = Path(__file__).parents[2] / "app"
PAGES = ["Home.py", *[f"pages/{p.name}" for p in sorted((APP / "pages").glob("*.py"))]]
TINY = configs_dir() / "sim" / "tiny.yaml"


@pytest.fixture(scope="module")
def bundle_path(tmp_path_factory):
    out = tmp_path_factory.mktemp("bundle")
    run = generate(TINY, out=out, genetics=make_genetics("dog", TINY), run_id="tiny-app")
    b = export_bundle(str(run), [], out / "bundle")
    ctx = Bundle(b).context()
    a = ctx.animals
    alive_f = np.flatnonzero(
        (a["sex"] == "F").to_numpy()
        & a["death_date"].isna().to_numpy()
        & (a["birth_date"].dt.year.between(2021, 2024)).to_numpy()
    )
    dam = a.iloc[int(alive_f[-1])]
    (b / "demo.yaml").write_text(
        yaml.safe_dump(
            {
                "dataset": "tiny",
                "mating_date": "2026-11-01",
                "profile": "hr_full",
                "dams": [
                    {
                        "reg_no": dam["reg_no"],
                        "name": dam["name"],
                        "breed": dam["breed_id"],
                        "story": "fixture dam",
                    }
                ],
            }
        )
    )
    return b


def test_bundle_loads_into_context(bundle_path):
    ctx = Bundle(bundle_path).context()
    assert ctx.n > 0 and ctx.F.shape == (ctx.n,)
    assert (bundle_path / "truth_small.parquet").exists()
    assert Bundle(bundle_path).manifest["note"] == "All animals are synthetic."


@pytest.mark.parametrize("page", PAGES)
def test_page_runs(bundle_path, monkeypatch, page):
    from streamlit.testing.v1 import AppTest

    monkeypatch.setenv("BSM_BUNDLE_PATH", str(bundle_path))
    at = AppTest.from_file(str(APP / page), default_timeout=180)
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert any("Synthetic data" in w.value for w in at.warning), "banner missing"


def test_mate_finder_returns_a_table(bundle_path, monkeypatch):
    from streamlit.testing.v1 import AppTest

    monkeypatch.setenv("BSM_BUNDLE_PATH", str(bundle_path))
    at = AppTest.from_file(str(APP / "pages" / "3_Mate_finder.py"), default_timeout=180)
    at.run()
    assert not at.exception
    tables = [d.value for d in at.dataframe]
    assert tables and len(tables[0]) > 0
    assert "tier" in tables[0].columns


def test_glossary_covers_every_tooltip():
    import sys

    sys.path.insert(0, str(APP))
    from glossary import GLOSSARY

    used = set()
    for f in APP.rglob("*.py"):
        text = f.read_text(encoding="utf-8")
        used |= set(re.findall(r'tip\("([^"]+)"\)', text))
        used |= set(re.findall(r'kpi\([^)]*,\s*"([^"]+)"\)', text))
    missing = used - set(GLOSSARY)
    assert not missing, missing
    for term in ("COI", "kinship", "mean kinship", "Ne", "EBV", "EqG", "carrier", "tier"):
        assert term in GLOSSARY


def test_mate_finder_respects_club_quotas(bundle_path, monkeypatch):
    from streamlit.testing.v1 import AppTest

    monkeypatch.setenv("BSM_BUNDLE_PATH", str(bundle_path))
    at = AppTest.from_file(str(APP / "pages" / "3_Mate_finder.py"), default_timeout=180)
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert at.toggle[0].value is True, "club quotas must be on by default"
    default = at.dataframe[0].value
    assert "quota left" in default.columns
    assert (default["quota left"] > 0).all()
    at.toggle[0].set_value(False).run()
    assert not at.exception, [e.value for e in at.exception]
    n_all = len(at.dataframe[0].value)
    assert "quota left" not in at.dataframe[0].value.columns
    at.toggle[0].set_value(True).run()
    assert not at.exception, [e.value for e in at.exception]
    table = at.dataframe[0].value
    assert "quota left" in table.columns
    assert (table["quota left"] > 0).all()
    assert len(table) <= n_all
    pd.testing.assert_frame_equal(table, default)


@pytest.mark.parametrize(
    ("mode", "budget"), [("OCS", "lowest possible"), ("OCS", "0.5%"), ("cap", "lowest possible")]
)
def test_club_planner_modes(bundle_path, monkeypatch, mode, budget):
    from streamlit.testing.v1 import AppTest

    monkeypatch.setenv("BSM_BUNDLE_PATH", str(bundle_path))
    at = AppTest.from_file(str(APP / "pages" / "7_Club_planner.py"), default_timeout=180)
    at.run()
    at.radio[0].set_value(mode)
    at.select_slider[0].set_value(budget)
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    sires = at.dataframe[0].value
    assert {"sire", "MK", "cap", "quota"} <= set(sires.columns)
    matings = at.dataframe[1].value
    assert (sires["quota"].clip(lower=0).sum() >= (matings["sire"] != "").sum()) or mode == "cap"
