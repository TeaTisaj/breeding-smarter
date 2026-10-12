"""Kennel club desk (B3): known-answer tests for assessment, outcome and workflow."""

import re

import numpy as np
import pytest

from breeding_smarter import desk
from breeding_smarter.desk import AppStatus, DeskError, Outcome, SeasonQuota
from breeding_smarter.io import RunPaths, configs_dir, update_manifest
from breeding_smarter.matching.candidates import candidate_sires
from breeding_smarter.matching.context import DatasetContext
from breeding_smarter.matching.examples import eligible_dams
from breeding_smarter.rules import day_number, evaluate_candidates, load_profile
from breeding_smarter.rules.engine import OK
from breeding_smarter.sim.run import generate, load_setup, make_genetics, snapshot_configs
from tests.fixtures.pedigrees import tables_from_arrays, write_tables

TINY = configs_dir() / "sim" / "tiny.yaml"
# test_matching's fixture: FIRST_COUSINS plus 9 = unrelated male founder, 10 = half-brother of
# the dam 7 (common sire 3)
SIRE = [-1, -1, -1, -1, 0, 0, 4, 3, 6, -1, 3]
DAM = [-1, -1, -1, -1, 1, 1, 2, 5, 7, -1, 2]
SEX = ["M", "F", "F", "M", "M", "F", "M", "F", "M", "M", "M"]
DAM_I, HALF_BROTHER = 7, 10
FX_DATE = "2012-06-01"
DATE = "2026-11-01"


@pytest.fixture(scope="module")
def fx_ctx(tmp_path_factory):
    run = write_tables(
        tables_from_arrays(SIRE, DAM, SEX, breed="SYN_L"), tmp_path_factory.mktemp("d") / "fx"
    )
    snapshot_configs(load_setup(TINY), TINY, run / "config_snapshot")
    update_manifest(run / "manifest.json", scale=0.02)
    return DatasetContext.from_run(RunPaths(run), "fixture")


@pytest.fixture(scope="module")
def tiny(tmp_path_factory):
    """Tiny run and a clean pair: a dam (2 to 6 years) and a sire passing every rule."""
    run = generate(
        TINY, out=tmp_path_factory.mktemp("t"), genetics=make_genetics("dog", TINY), run_id="tiny"
    )
    ctx = DatasetContext.from_run(RunPaths(run), "tiny")
    day = day_number(DATE)
    prof = load_profile("hr_full")
    for d in eligible_dams(ctx, None, day):
        cand = candidate_sires(ctx, int(d), day)
        if cand.size == 0:
            continue
        ok = cand[evaluate_candidates(ctx.rules, prof, int(d), cand, day).status == OK]
        if ok.size:
            return ctx, int(d), int(ok[0])
    raise AssertionError("no clean pair in the tiny run")


def _app(dam, sire, date=DATE, app_id="APP-0001"):
    return desk.new_application(app_id, dam, sire, date, "Synthetic breeder")


def _ready_for_approval(app, a):
    desk.confirm_stud_owner(app)
    app.manual_done |= {m.key for m in a.manual}


def test_half_siblings_blocked_by_eu_rule(fx_ctx):
    a = desk.assess(fx_ctx, _app(DAM_I, HALF_BROTHER, FX_DATE), "hr_full", None)
    assert a.outcome == Outcome.BLOCKED
    assert "eu_close_relatives" in [c.rule_id for c in a.failed_hard]
    eu = next(c for c in a.checks if c.rule_id == "eu_close_relatives")
    assert eu.symbol == "✗" and "half siblings" in eu.message and eu.source == "eurlex-2026-1818"
    assert any(r.startswith("eu_close_relatives (source eurlex-2026-1818)") for r in a.reasons)
    assert not desk.can_submit(a)
    sentences = desk.explain(a)
    assert "eu_close_relatives" in sentences[0] and "half siblings" in sentences[1]
    ok, why = desk.can_approve(_app(DAM_I, HALF_BROTHER, FX_DATE), a)
    assert not ok and "hard rule" in why


def test_clean_pair_ready(tiny):
    ctx, dam, sire = tiny
    a = desk.assess(ctx, _app(dam, sire), "hr_full", SeasonQuota.from_plan([sire], [2]))
    assert a.outcome == Outcome.READY and a.reasons == []
    assert (a.quota_left, a.quota_total) == (2, 2)
    assert [m.key for m in a.manual] == [m.key for m in desk.STANDARD_MANUAL]
    assert desk.can_submit(a)
    s = desk.explain(a)
    assert 3 <= len(s) <= 5
    assert s[0] == "Mating allowed by all automatic checks."
    assert any("2 of 2 litter(s) left" in x for x in s)


@pytest.mark.parametrize(("case", "text"), [
    ("not_planned", "no club quota this season"),
    ("quota_zero", "no club quota this season"),
    ("used_up", "used all 1 litter(s)"),
])  # fmt: skip
def test_sire_without_quota_needs_review(tiny, case, text):
    ctx, dam, sire = tiny
    if case == "not_planned":
        q = SeasonQuota.from_plan(np.zeros(0, np.int64), np.zeros(0, np.int64))
    else:
        q = SeasonQuota.from_plan([sire], [0 if case == "quota_zero" else 1])
    if case == "used_up":
        q.ledger.book(sire)  # another approved mating took the last litter
    a = desk.assess(ctx, _app(dam, sire), "hr_full", q)
    assert a.outcome == Outcome.NEEDS_REVIEW
    assert a.quota_left == 0 and any(text in r for r in a.reasons)
    assert desk.can_submit(a)
    quota_check = next(c for c in a.checks if c.rule_id == desk.QUOTA_RULE)
    assert quota_check.symbol == "⚠"


def test_approval_books_quota_once(tiny):
    ctx, dam, sire = tiny
    q = SeasonQuota.from_plan([sire], [2])
    app = _app(dam, sire)
    a = desk.assess(ctx, app, "hr_full", q)
    with pytest.raises(DeskError, match="stud owner"):
        desk.approve(app, a, q)
    desk.confirm_stud_owner(app)
    assert app.status == AppStatus.STUD_OWNER_CONFIRMED and app.stud_owner_confirmed
    with pytest.raises(DeskError, match="Manual checks"):
        desk.approve(app, a, q)
    app.manual_done |= {m.key for m in a.manual}
    desk.approve(app, a, q, note="ok")
    assert app.status == AppStatus.APPROVED and app.booked
    assert q.remaining(sire) == 1
    desk.approve(app, a, q)  # approving the same application again books nothing
    assert q.remaining(sire) == 1
    again = desk.assess(ctx, app, "hr_full", q)  # its own booking is not counted against it
    assert again.outcome == Outcome.READY and again.quota_left == 2
    with pytest.raises(DeskError, match="already approved"):
        desk.reject(app)


def test_rejection_books_nothing(tiny):
    ctx, dam, sire = tiny
    q = SeasonQuota.from_plan([sire], [1])
    app = _app(dam, sire)
    a = desk.assess(ctx, app, "hr_full", q)
    _ready_for_approval(app, a)
    desk.reject(app, "not this season")
    assert app.status == AppStatus.REJECTED and q.remaining(sire) == 1 and not app.booked
    with pytest.raises(DeskError):
        desk.approve(app, a, q)


def test_over_quota_only_as_noted_exception(tiny):
    ctx, dam, sire = tiny
    q = SeasonQuota.from_plan([sire], [0])
    app = _app(dam, sire)
    a = desk.assess(ctx, app, "hr_full", q)
    _ready_for_approval(app, a)
    with pytest.raises(DeskError, match="club exception"):
        desk.approve(app, a, q, exception=True)  # no note
    desk.approve(app, a, q, note="breed club board decision", exception=True)
    assert app.status == AppStatus.APPROVED and app.quota_exception and not app.booked
    assert q.remaining(sire) == 0


def test_explanation_uses_only_card_numbers(tiny, fx_ctx):
    ctx, dam, sire = tiny
    cases = [
        desk.assess(ctx, _app(dam, sire), "hr_full", SeasonQuota.from_plan([sire], [3])),
        desk.assess(ctx, _app(dam, sire), "hr_full", SeasonQuota.from_plan([sire], [0])),
        desk.assess(fx_ctx, _app(DAM_I, HALF_BROTHER, FX_DATE), "hr_full", None),
    ]
    for a in cases:
        c = a.card
        known = " ".join(
            [
                c.model_dump_json(),
                f"{100 * c.predicted_coi:.1f} {100 * c.breed_mean_litter_coi:.1f}",
                f"{a.quota_left} {a.quota_total} {len(a.reasons)} {len(a.failed_hard) - 1}",
            ]
        )
        sentences = desk.explain(a)
        assert 2 <= len(sentences) <= 5
        for n in re.findall(r"\d+(?:\.\d+)?", " ".join(sentences)):
            assert n in known, (n, sentences)


def test_vet_certificate_for_older_dam_sends_to_review(fx_ctx):
    # fixture dam 5 (born 2003-03-01) is 9.3 years old on 2012-06-01; sire 9 is unrelated
    a = desk.assess(fx_ctx, _app(5, 9, FX_DATE), "eu_platform_guide", None)
    assert a.dam_age_years > desk.VET_CERTIFICATE_DAM_AGE_YEARS
    assert "vet_certificate" in [m.key for m in a.manual if m.conditional]
    assert a.outcome == Outcome.NEEDS_REVIEW
    assert any("Veterinary certificate" in r for r in a.reasons)


def test_certificate_is_marked_prototype(tiny):
    ctx, dam, sire = tiny
    q = SeasonQuota.from_plan([sire], [1])
    app = _app(dam, sire)
    a = desk.assess(ctx, app, "hr_full", q)
    with pytest.raises(DeskError):
        desk.certificate_html(app, a, "2026-11-02")
    _ready_for_approval(app, a)
    desk.approve(app, a, q)
    page = desk.certificate_html(app, desk.assess(ctx, app, "hr_full", q), "2026-11-02")
    assert page.count(desk.PROTOTYPE_NOTE) == 2
    assert "Mating certificate (prototype)" in page and "One litter booked" in page
    assert a.card.dam_label.split(" (")[0] in page
    assert "<script" not in page.lower()


def test_example_applications_show_each_outcome(tiny):
    from breeding_smarter.coordination.club import club_plan

    ctx, dam, _ = tiny
    breed = ctx.breed_of(dam)
    cp = club_plan(ctx, breed, DATE)
    q = SeasonQuota.from_plan(cp.plan.sires, cp.plan.quotas)
    apps = desk.example_applications(ctx, q, breed, DATE)
    expected = {
        "Synthetic breeder 1": Outcome.BLOCKED,
        "Synthetic breeder 2": Outcome.READY,
        "Synthetic breeder 3": Outcome.NEEDS_REVIEW,
    }
    assert len(apps) == 3
    assert len({a.dam for a in apps}) == 3
    for app in apps:
        a = desk.assess(ctx, app, "hr_full", q)
        assert a.outcome == expected[app.applicant], (app, a.reasons)
        assert app.status == AppStatus.SUBMITTED
    blocked = desk.assess(ctx, apps[0], "hr_full", q)
    assert [c.rule_id for c in blocked.failed_hard] == ["eu_close_relatives"]


def test_next_app_id():
    apps = [_app(0, 1, app_id="APP-0001"), _app(0, 1, app_id="APP-0007")]
    assert desk.next_app_id(apps) == "APP-0008"
    assert desk.next_app_id([]) == "APP-0001"


# ---------------------------------------------------------------- season overview (phase 3)


@pytest.fixture
def season(tiny, fx_ctx):
    """Four applications with known states: approved and booked, waiting without quota,
    rejected, and blocked by the EU close-relative ban (fixture pedigree)."""
    ctx, dam, sire = tiny
    q = SeasonQuota.from_plan([sire], [2])
    approved = _app(dam, sire, app_id="APP-0001")
    a1 = desk.assess(ctx, approved, "hr_full", q)
    _ready_for_approval(approved, a1)
    desk.approve(approved, a1, q)
    waiting = _app(dam, sire, app_id="APP-0002")
    full = SeasonQuota.from_plan([sire], [0])
    rejected = _app(dam, sire, app_id="APP-0003")
    desk.reject(rejected, "duplicate")
    blocked = _app(DAM_I, HALF_BROTHER, FX_DATE, app_id="APP-0004")
    apps = [approved, waiting, rejected, blocked]
    assessed = {
        "APP-0001": desk.assess(ctx, approved, "hr_full", q),
        "APP-0002": desk.assess(ctx, waiting, "hr_full", full),
        "APP-0003": desk.assess(ctx, rejected, "hr_full", q),
        "APP-0004": desk.assess(fx_ctx, blocked, "hr_full", None),
    }
    return ctx, q, apps, assessed


def test_season_summary_known_counts(season):
    _, _, apps, assessed = season
    s = desk.season_summary(apps, assessed)
    assert (s.applications, s.approved, s.rejected, s.blocked, s.waiting) == (4, 1, 1, 1, 1)
    assert s.blocked_by_rule == {"eu_close_relatives": 1}
    assert s.eu_bans == 1
    assert s.without_quota == 1  # APP-0002's sire has no club quota left


def test_quota_usage_counts_bookings(season, tiny):
    ctx, q, _, _ = season
    _, _, sire = tiny
    u = desk.quota_usage(ctx, q)
    assert list(u.columns) == ["sire", "quota", "booked", "left"]
    row = u.iloc[0]
    assert row["sire"] == ctx.rules.label(sire)
    assert (row["quota"], row["booked"], row["left"]) == (2, 1, 1)


def test_compliance_report_rows_rules_and_sources(season):
    ctx, _, apps, assessed = season
    df = desk.compliance_report(ctx, apps, assessed)
    assert list(df["application"]) == ["APP-0001", "APP-0002", "APP-0003", "APP-0004"]
    assert list(df["outcome"]) == ["READY", "NEEDS_REVIEW", "READY", "BLOCKED"]
    assert list(df["status"]) == ["APPROVED", "SUBMITTED", "REJECTED", "SUBMITTED"]
    assert df.loc[3, "failed_hard_rules"] == "eu_close_relatives (eurlex-2026-1818)"
    assert "eu_close_relatives [eurlex-2026-1818; unverified]" in df.loc[3, "checks"]
    assert df.loc[0, "quota_booked"] and not df.loc[2, "quota_booked"]
    assert (df["data"].str.startswith("synthetic")).all()
    csv = df.to_csv(index=False)
    assert csv.count("\n") == 5  # header and four rows
