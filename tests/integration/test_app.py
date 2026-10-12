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


# ---------------------------------------------------------------- Kennel club desk (B4)

DESK = APP / "pages" / "8_Kennel_club_desk.py"


def _desk(bundle_path, monkeypatch):
    from streamlit.testing.v1 import AppTest

    monkeypatch.setenv("BSM_BUNDLE_PATH", str(bundle_path))
    at = AppTest.from_file(str(DESK), default_timeout=300)
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    return at


def _queue(at):
    return next(d.value for d in at.dataframe if "application" in d.value.columns)


def test_desk_starts_with_one_example_per_outcome(bundle_path, monkeypatch):
    at = _desk(bundle_path, monkeypatch)
    apps = at.session_state["desk_apps"]
    assert [a.applicant for a in apps] == [f"Synthetic breeder {k}" for k in (1, 2, 3)]
    q = _queue(at)
    assert list(q["automatic checks"]) == ["Blocked", "Allowed", "Needs club review"]
    assert set(q["status"]) == {"SUBMITTED"}
    assert any("Prototype on synthetic data" in c.value for c in at.caption)


def test_desk_half_brother_is_blocked_and_cannot_be_submitted(bundle_path, monkeypatch):
    at = _desk(bundle_path, monkeypatch)
    at.button(key="desk_demo_blocked").click().run()
    assert not at.exception, [e.value for e in at.exception]
    assert any("Blocked: eu_close_relatives (eu_2026_1818)" in e.value for e in at.error)
    assert at.button(key="desk_submit").disabled


def test_desk_submit_confirm_approve_books_quota(bundle_path, monkeypatch):
    from breeding_smarter.desk import AppStatus

    at = _desk(bundle_path, monkeypatch)
    clean = at.session_state["desk_apps"][1]  # the READY example: its dam has quota sires
    at.session_state["desk_dam"] = Bundle(bundle_path).context().rules.reg_no[clean.dam]
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    n_before = len(at.session_state["desk_apps"])
    assert not at.button(key="desk_submit").disabled
    at.button(key="desk_submit").click().run()
    assert not at.exception, [e.value for e in at.exception]
    apps = at.session_state["desk_apps"]
    assert len(apps) == n_before + 1
    new = apps[-1]
    assert new.status == AppStatus.SUBMITTED and new.app_id == "APP-0004"
    # the tab opens this application: it waits for the stud owner, who signs it right there
    assert at.selectbox(key="desk_view").value == "APP-0004"
    panel = [i.value for i in at.info if "APP-0004" in i.value]
    assert panel and "Waiting for the stud owner's signature" in panel[0]
    assert at.button(key="desk_confirm").label == "Stud owner confirms APP-0004"
    # the same mating cannot be submitted twice
    at.selectbox(key="desk_view").set_value("New application").run()
    assert at.button(key="desk_submit").disabled
    assert any("already submitted as APP-0004" in c.value for c in at.caption)
    at.selectbox(key="desk_view").set_value("APP-0004").run()
    at.button(key="desk_confirm").click().run()
    assert new.status == AppStatus.STUD_OWNER_CONFIRMED and new.stud_owner_confirmed
    done = [s.value for s in at.success if "APP-0004" in s.value]
    assert done and "Stud owner confirmed" in done[0] and "breeding officer" in done[0]
    at.selectbox(key="desk_pick").set_value(new.app_id).run()
    assert at.button(key="desk_approve").disabled  # manual checks still open
    for cb in at.checkbox:
        if cb.key and cb.key.startswith(f"desk_m_{new.app_id}_"):
            cb.check()
    at.run()
    quota = at.session_state["desk_quotas"]
    breed = next(b for b, q in quota.items() if q.of(new.sire) > 0)
    left = quota[breed].remaining(new.sire)
    at.button(key="desk_approve").click().run()
    assert not at.exception, [e.value for e in at.exception]
    assert new.status == AppStatus.APPROVED and new.booked
    assert quota[breed].remaining(new.sire) == left - 1
    assert clean.status == AppStatus.SUBMITTED  # the example is untouched
    assert any("mating certificate" in s.value for s in at.success)


def _metrics(at):
    return {m.label: m.value for m in at.metric}


def _expected_summary(at, bundle_path):
    from breeding_smarter import desk

    ctx = Bundle(bundle_path).context()
    quotas = at.session_state["desk_quotas"]
    apps = at.session_state["desk_apps"]
    assessed = {a.app_id: desk.assess(ctx, a, "hr_full", quotas[ctx.breed_of(a.dam)]) for a in apps}
    return desk.season_summary(apps, assessed)


def test_desk_season_overview_matches_session_state(bundle_path, monkeypatch):
    at = _desk(bundle_path, monkeypatch)
    for step in ("initial", "after rejecting APP-0003"):
        if step != "initial":
            at.selectbox(key="desk_pick").set_value("APP-0003").run()
            at.button(key="desk_reject").click().run()
            assert not at.exception, [e.value for e in at.exception]
        s = _expected_summary(at, bundle_path)
        m = _metrics(at)
        assert m["Applications"] == str(s.applications), step
        assert m["Approved"] == str(s.approved), step
        assert m["Blocked"] == str(s.blocked), step
        assert m["Waiting"] == str(s.waiting), step
        assert m["Rejected"] == str(s.rejected), step
        assert m["Blocked by EU 2026/1818 rules"] == str(s.eu_bans), step
        assert m["Waiting with no club quota left"] == str(s.without_quota), step
    assert (s.rejected, s.blocked, s.eu_bans) == (1, 1, 1)
    blocked = next(d.value for d in at.dataframe if "rule" in d.value.columns)
    assert list(blocked["rule"]) == ["eu_close_relatives"]


def test_desk_stud_owner_confirms_an_example_application(bundle_path, monkeypatch):
    from breeding_smarter.desk import AppStatus

    at = _desk(bundle_path, monkeypatch)
    ex = at.session_state["desk_apps"][1]  # the clean example waiting for the stud owner
    at.selectbox(key="desk_view").set_value(ex.app_id).run()
    assert not at.exception, [e.value for e in at.exception]
    assert at.button(key="desk_confirm").label == f"Stud owner confirms {ex.app_id}"
    at.button(key="desk_confirm").click().run()
    assert ex.status == AppStatus.STUD_OWNER_CONFIRMED
    assert any(ex.app_id in s.value and "Stud owner confirmed" in s.value for s in at.success)
    assert not [b for b in at.button if b.key == "desk_confirm"]  # signed: no button any more
    at.selectbox(key="desk_pick").set_value(ex.app_id).run()
    assert any(m.value.endswith("Stud owner confirmed") for m in at.markdown)


def test_desk_blocked_application_needs_no_stud_owner_signature(bundle_path, monkeypatch):
    at = _desk(bundle_path, monkeypatch)
    blocked = at.session_state["desk_apps"][0]  # the half-brother example
    at.selectbox(key="desk_view").set_value(blocked.app_id).run()
    assert not at.exception, [e.value for e in at.exception]
    assert not [b for b in at.button if b.key == "desk_confirm"]
    assert any(
        blocked.app_id in e.value and "no stud owner signature is needed" in e.value
        for e in at.error
    )
