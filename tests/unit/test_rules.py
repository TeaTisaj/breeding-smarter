"""Rule engine tests (P6 section 5)."""

import time

import numpy as np
import pandas as pd
import pytest
import yaml

from breeding_smarter.rules import (
    RuleConfigError,
    RuleContext,
    Severity,
    Status,
    day_number,
    evaluate_candidates,
    evaluate_pair,
    load_profile,
)
from breeding_smarter.rules.loader import rules_dir
from breeding_smarter.rules.models import Profile, RuleSpec
from breeding_smarter.rules.types import RULE_TYPES, check_one
from tests.fixtures.pedigrees import (
    FIRST_COUSINS,
    FULL_SIBS,
    HALF_SIBS,
    PARENT_OFFSPRING,
    UNRELATED,
    tables_from_arrays,
)
from tests.fixtures.random_ped import realistic_pedigree

DATE = "2030-06-01"


def ctx_of(fx, local=False, **edits):
    t = fx.tables()
    t["registry/breeds"]["is_local_breed"] = local
    for name, fn in edits.items():
        t[name] = fn(t[name])
    return RuleContext.from_tables(
        t["registry/animals"],
        t["registry/litters"],
        t["registry/health_tests"],
        t["registry/dna_tests"],
        t["registry/breeds"],
    )


def rule(type_, severity="HARD", **params):
    return RuleSpec(
        id=f"t_{type_}",
        type=type_,
        params=params,
        severity=severity,
        source="fci-strategies",
        verified=True,
        profile="test",
    )


def one(r, ctx, dam, sire, date=DATE, method=None):
    return check_one(r, ctx, dam, sire, day_number(date), method)


BAN = ["PARENT_OFFSPRING", "FULL_SIBLINGS", "HALF_SIBLINGS", "GRANDPARENT_GRANDCHILD"]


@pytest.mark.parametrize(
    ("fx", "dam", "sire", "word"),
    [
        (PARENT_OFFSPRING, 2, 0, "parent and offspring"),
        (FULL_SIBS, 3, 2, "full siblings"),
        (HALF_SIBS, 4, 3, "half siblings"),
        (FIRST_COUSINS, 7, 0, "grandparent"),  # A is a grandparent of I
    ],
)
def test_relationship_ban_each_relationship(fx, dam, sire, word):
    ok, _, _, msg = one(rule("relationship_ban", relationships=BAN), ctx_of(fx), dam, sire)
    assert not ok and word in msg
    assert "SYN-HR-" in msg or word == "grandparent"


def test_first_cousins_pass_relationship_ban():
    ok, _, _, msg = one(rule("relationship_ban", relationships=BAN), ctx_of(FIRST_COUSINS), 7, 6)
    assert ok, msg


def test_ages_and_breed_alive_registration():
    ctx = ctx_of(UNRELATED)  # 0 M, 1 F born 2000-03-01
    assert one(rule("min_age", sex="F", months=18), ctx, 1, 0, "2001-09-05")[0]
    assert not one(rule("min_age", sex="F", months=18), ctx, 1, 0, "2001-08-01")[0]
    assert not one(rule("max_age", sex="F", years=8), ctx, 1, 0, "2008-04-01")[0]
    assert one(rule("max_age", sex="F", years=8), ctx, 1, 0, "2008-02-01")[0]
    assert one(rule("min_age", sex="M", months=12), ctx, 1, 0, "2001-04-01")[0]
    assert one(rule("same_breed"), ctx, 1, 0)[0]
    assert one(rule("alive_at_mating"), ctx, 1, 0)[0]
    assert not one(rule("alive_at_mating"), ctx, 1, 0, "1999-01-01")[0]
    dead = ctx_of(
        UNRELATED,
        **{
            "registry/animals": lambda a: a.assign(
                death_date=pd.to_datetime(["2005-01-01", None, None])
            )
        },
    )
    assert not one(rule("alive_at_mating"), dead, 1, 0, "2006-01-01")[0]
    exempt = rule("alive_at_mating", frozen_semen_exempt=True)
    assert one(exempt, dead, 1, 0, "2006-01-01", method="ai_frozen")[0]
    limited = ctx_of(
        UNRELATED,
        **{"registry/animals": lambda a: a.assign(registration_type=["limited", "full", "full"])},
    )
    assert not one(rule("registration_type", disallowed=["limited"]), limited, 1, 0)[0]
    assert one(rule("registration_type", disallowed=["limited"]), ctx, 1, 0)[0]


def test_litter_rules():
    # in REPEATED-like FULL_SIBS fixture, dam 1 whelped litter (2, 3) on 2003-03-01
    ctx = ctx_of(FULL_SIBS)
    r = rule("min_interval_between_litters", months=10)
    assert not one(r, ctx, 1, 0, "2003-10-01")[0]
    assert one(r, ctx, 1, 0, "2004-03-01")[0]
    r = rule("max_litters_in_window", max=1, window_months=24)
    assert not one(r, ctx, 1, 0, "2004-03-01")[0]  # previous litter + this one = 2 > 1
    assert one(r, ctx, 1, 0, "2006-03-01")[0]
    r = rule("max_lifetime_litters", sex="M", max=2)
    assert one(r, ctx, 1, 0)[0]  # sire 0: 1 previous litter + 1 = 2
    r = rule("max_lifetime_litters", sex="M", max=1)
    assert not one(r, ctx, 1, 0)[0]


def _three_litters(caesarean):
    """Dam 1 of UNRELATED whelps on 2003-03-01, 2004-03-01 and 2005-03-01 (sire 0)."""

    def fn(litters):
        whelp = pd.to_datetime(["2003-03-01", "2004-03-01", "2005-03-01"])
        base = litters.iloc[[0, 0, 0]].reset_index(drop=True)
        return base.assign(
            litter_id=[0, 1, 2],
            whelp_date=whelp,
            mating_date=whelp - pd.Timedelta(days=63),
            caesarean=caesarean,
        )

    return fn


def test_max_caesareans_known_answers():
    """N = 2: 0 and 1 previous caesareans pass, 2 fail; a later caesarean does not count."""
    ctx = ctx_of(UNRELATED, **{"registry/litters": _three_litters([True, False, True])})
    r = rule("max_caesareans", n=2)
    ok, val, _, msg = one(r, ctx, 1, 0, "2003-01-01")
    assert ok and val == 0 and "0 previous caesarean" in msg
    ok, val, _, _ = one(r, ctx, 1, 0, "2004-06-01")
    assert ok and val == 1
    ok, val, _, _ = one(r, ctx, 1, 0, "2005-02-01")  # 2005 caesarean is after the mating
    assert ok and val == 1
    ok, val, _, msg = one(r, ctx, 1, 0, "2005-06-01")
    assert not ok and val == 2 and "bar further breeding" in msg
    assert one(rule("max_caesareans", n=3), ctx, 1, 0, "2005-06-01")[0]


def test_max_caesareans_without_caesarean_data_passes():
    ctx = ctx_of(
        UNRELATED,
        **{
            "registry/litters": lambda L: _three_litters([True, True, True])(L).drop(
                columns="caesarean"
            )
        },
    )
    ok, val, _, _ = one(rule("max_caesareans", n=2), ctx, 1, 0, "2005-06-01")
    assert ok and val == 0


def test_max_caesareans_needs_n():
    assert "max_caesareans" in RULE_TYPES
    with pytest.raises(RuleConfigError):
        RULE_TYPES["max_caesareans"].validate_params(rule("max_caesareans"))


def _with_health(grades):
    def fn(_):
        return pd.DataFrame(
            {
                "test_id": np.arange(len(grades)),
                "idx": list(grades),
                "test_type": "HD",
                "scheme": "FCI",
                "result": list(grades.values()),
                "test_date": pd.Timestamp("2002-01-01"),
                "age_months": 14,
                "official": True,
            }
        )

    return {"registry/health_tests": fn}


def test_health_grade_exclusion():
    r = rule("health_grade_exclusion", test_type="HD", exclude=["E"], missing="warn")
    ctx = ctx_of(UNRELATED, **_with_health({0: "E", 1: "A"}))
    ok, _, _, msg = one(r, ctx, 1, 0)
    assert not ok and "E" in msg
    ctx = ctx_of(UNRELATED, **_with_health({0: "B", 1: "A"}))
    assert one(r, ctx, 1, 0)[0]
    ctx = ctx_of(UNRELATED, **_with_health({1: "A"}))
    ok, _, warn, _ = one(r, ctx, 1, 0)
    assert ok and warn
    block = rule("health_grade_exclusion", test_type="HD", exclude=["E"], missing="block")
    assert not one(block, ctx, 1, 0)[0]


def _with_dna(rows):
    def fn(_):
        return pd.DataFrame(
            [
                {
                    "idx": i,
                    "locus_id": lc,
                    "genotype": g,
                    "test_date": pd.Timestamp("2002-01-01"),
                    "lab": "x",
                }
                for i, lc, g in rows
            ]
        )

    return {"registry/dna_tests": fn}


def test_dna_rules():
    carrier = rule("carrier_pairing", loci="all_tested")
    affected = rule("affected_exclusion", loci="all_tested")
    ctx = ctx_of(
        UNRELATED, **_with_dna([(0, "L1", "carrier"), (1, "L1", "carrier"), (1, "L2", "affected")])
    )
    ok, n, _, msg = one(carrier, ctx, 1, 0)
    assert not ok and n == 1 and "L1" in msg
    assert not one(affected, ctx, 1, 0)[0]
    ctx = ctx_of(UNRELATED, **_with_dna([(0, "L1", "clear"), (1, "L1", "carrier")]))
    assert one(carrier, ctx, 1, 0)[0]
    assert one(affected, ctx, 1, 0)[0]


def test_offspring_coi_threshold():
    r = rule("offspring_coi_threshold", severity="SOFT", threshold=0.065)
    ok, f, _, msg = one(r, ctx_of(FULL_SIBS), 3, 2)
    assert not ok and f == pytest.approx(0.25) and "25.0%" in msg
    assert one(r, ctx_of(UNRELATED), 1, 0)[0]


def test_sire_quota():
    ctx = ctx_of(FULL_SIBS)
    # window to 2004-01-01: registrations 2 (pups 2, 3); sire 0 has 2 offspring plus the
    # expected registered litter (mean of the litters of 2 and 1 pups = 1.5) = 3.5
    r = rule("sire_quota", share=0.05, window_years=5)
    ok, value, _, _ = one(r, ctx, 1, 0, "2004-01-01")
    assert not ok and value == pytest.approx(3.5)
    r = rule("sire_quota", share=5.0, window_years=5)
    assert one(r, ctx, 1, 0, "2004-01-01")[0]


def test_derogation_local_breed():
    p = load_profile("eu_2026_1818")
    r = p.rule("eu_close_relatives").model_copy(update={"derogation_granted": True})
    prof = Profile(name="x", title="x", rules=(r,), members=("x",))
    local = ctx_of(FULL_SIBS, local=True)
    non_local = ctx_of(FULL_SIBS, local=False)
    assert evaluate_pair(local, prof, 2, 3, DATE).status == Status.PERMITTED_WITH_WARNINGS
    assert evaluate_pair(non_local, prof, 2, 3, DATE).status == Status.NOT_PERMITTED
    not_granted = Profile(
        name="x", title="x", rules=(p.rule("eu_close_relatives"),), members=("x",)
    )
    assert evaluate_pair(local, not_granted, 2, 3, DATE).status == Status.NOT_PERMITTED


def test_hr_full_composition():
    p = load_profile("hr_full")
    ids = [r.id for r in p.rules]
    assert len(ids) == len(set(ids))
    expected = {
        "base_same_breed",
        "base_alive",
        "eu_close_relatives",
        "eu_dam_min_age",
        "eu_dam_litter_frequency",
        "fci_registration_type",
        "fci_sire_quota",
        "hks_hd_exclusion",
        "hks_dam_min_age",
        "hks_dam_max_age",
        "hks_max_caesareans",
        "hks_one_litter_12m",
        "guide_coi_6_5",
        "guide_coi_breed_mean",
        "dna_carrier_pairing",
        "dna_affected_parent",
    }
    assert set(ids) == expected
    for name in ("uk_full", "nl_full", "kc_uk", "rvb_nl"):
        assert load_profile(name).rules


def test_kennel_club_desk_rules_and_unchanged_existing_rules():
    """B2: new HKS rules are HARD, sourced and unverified; earlier rules unchanged; no EU
    caesarean rule until it is confirmed in the Official Journal text."""
    sources = set(yaml.safe_load((rules_dir().parent / "sources.yaml").read_text())["sources"])
    hks = {r.id: r for r in load_profile("hks_hr").rules}
    eu = {r.id: r for r in load_profile("eu_2026_1818").rules}
    new = {
        "hks_max_caesareans": (hks, "max_caesareans", {"n": 2}),
        "hks_one_litter_12m": (hks, "max_litters_in_window", {"max": 1, "window_months": 12}),
    }
    for rid, (prof, type_, params) in new.items():
        r = prof[rid]
        assert (r.type, r.params, r.severity) == (type_, params, Severity.HARD), rid
        assert r.verified is False and r.source in sources, rid
    assert "calendar year" in (hks["hks_one_litter_12m"].note or "")
    old = {
        "hks_hd_exclusion": ("health_grade_exclusion", {"test_type": "HD", "exclude": ["E"],
                                                        "missing": "allow"}, True),
        "hks_dam_min_age": ("min_age", {"sex": "F", "months": 15}, False),
        "hks_dam_max_age": ("max_age", {"sex": "F", "years": 8}, False),
        "eu_close_relatives": ("relationship_ban", {"relationships": BAN}, False),
        "eu_dam_min_age": ("min_age", {"sex": "F", "months": 18}, False),
        "eu_dam_litter_frequency": ("max_litters_in_window", {"max": 3, "window_months": 24},
                                    False),
    }  # fmt: skip
    rules = {**hks, **eu}
    for rid, (type_, params, verified) in old.items():
        r = rules[rid]
        assert (r.type, r.params, r.severity, r.verified) == (
            type_, params, Severity.HARD, verified
        ), rid  # fmt: skip
    assert set(hks) == {
        "hks_hd_exclusion",
        "hks_dam_min_age",
        "hks_dam_max_age",
        "hks_max_caesareans",
        "hks_one_litter_12m",
    }
    assert set(eu) == {"eu_close_relatives", "eu_dam_min_age", "eu_dam_litter_frequency"}
    for name in ("eu_2026_1818", "hr_full", "nl_full"):
        caes = [r.id for r in load_profile(name).rules if r.type == "max_caesareans"]
        assert all(r.startswith("hks_") for r in caes), (name, caes)


def test_status_aggregation():
    hard = rule("offspring_coi_threshold", severity="HARD", threshold=0.065)
    soft = hard.model_copy(update={"id": "soft", "severity": Severity.SOFT})
    info = hard.model_copy(update={"id": "info", "severity": Severity.INFO})
    ctx = ctx_of(FULL_SIBS)
    mk = lambda *rs: Profile(name="x", title="x", rules=rs, members=("x",))  # noqa: E731
    assert evaluate_pair(ctx, mk(hard), 2, 3, DATE).status == Status.NOT_PERMITTED
    assert evaluate_pair(ctx, mk(soft), 2, 3, DATE).status == Status.PERMITTED_WITH_WARNINGS
    assert evaluate_pair(ctx, mk(info), 2, 3, DATE).status == Status.PERMITTED
    assert evaluate_pair(ctx, mk(soft, hard), 2, 3, DATE).status == Status.NOT_PERMITTED


def _write(tmp, name, doc):
    (tmp / f"{name}.yaml").write_text(yaml.safe_dump(doc))


def test_loader_rejects_bad_yaml(tmp_path):
    base = {"severity": "HARD", "source": "kc-coi", "verified": True}
    _write(
        tmp_path,
        "a",
        {"profile": "a", "title": "a", "rules": [{"id": "x", "type": "nope", **base}]},
    )
    with pytest.raises(RuleConfigError, match="unknown rule type"):
        load_profile("a", tmp_path)
    _write(
        tmp_path,
        "b",
        {
            "profile": "b",
            "title": "b",
            "rules": [
                {
                    "id": "x",
                    "type": "relationship_ban",
                    "params": {"relationships": ["COUSINS"]},
                    **base,
                }
            ],
        },
    )
    with pytest.raises(RuleConfigError, match="unknown relationship"):
        load_profile("b", tmp_path)
    _write(
        tmp_path,
        "c",
        {
            "profile": "c",
            "title": "c",
            "rules": [{"id": "x", "type": "same_breed", "severity": "HARD", "verified": True}],
        },
    )
    with pytest.raises(RuleConfigError, match="source"):
        load_profile("c", tmp_path)
    _write(tmp_path, "d", {"profile": "d", "title": "d", "include": ["e"]})
    _write(tmp_path, "e", {"profile": "e", "title": "e", "include": ["d"]})
    with pytest.raises(RuleConfigError, match="cycle"):
        load_profile("d", tmp_path)
    _write(
        tmp_path,
        "f",
        {
            "profile": "f",
            "title": "f",
            "rules": [{"id": "x", "type": "min_age", "params": {}, **base}],
        },
    )
    with pytest.raises(RuleConfigError, match="missing params"):
        load_profile("f", tmp_path)


def test_every_profile_loads():
    for p in rules_dir().glob("*.yaml"):
        load_profile(p.stem)


@pytest.fixture(scope="module")
def big_ctx():
    ped = realistic_pedigree(20_000, seed=3)
    sex = np.where(ped.sex == 1, "M", "F")
    t = tables_from_arrays(ped.sire, ped.dam, sex)
    return RuleContext.from_tables(
        t["registry/animals"],
        t["registry/litters"],
        t["registry/health_tests"],
        t["registry/dna_tests"],
        t["registry/breeds"],
        ped=None,
    )


def test_check_many_equals_check_one(big_ctx):
    rng = np.random.default_rng(0)
    prof = load_profile("hr_full")
    females = np.flatnonzero(big_ctx.ped.sex == 0)
    males = np.flatnonzero(big_ctx.ped.sex == 1)
    day = day_number("2040-01-01")
    for dam in rng.choice(females[-2000:], 5, replace=False):
        sires = rng.choice(males[-3000:], 40, replace=False)
        for r in prof.rules:
            b = RULE_TYPES[r.type].check_many(r, big_ctx, int(dam), sires, day)
            for k, s in enumerate(sires):
                ok, v, w, _ = check_one(r, big_ctx, int(dam), int(s), day)
                assert ok == b.passed[k] and w == b.warn[k], r.id
                assert (np.isnan(v) and np.isnan(b.value[k])) or v == pytest.approx(b.value[k])


def test_evaluate_candidates_performance(big_ctx):
    prof = load_profile("hr_full")
    males = np.flatnonzero(big_ctx.ped.sex == 1)[-2000:]
    dam = int(np.flatnonzero(big_ctx.ped.sex == 0)[-1])
    evaluate_candidates(big_ctx, prof, dam, males, "2040-01-01")  # warm
    t0 = time.perf_counter()
    ev = evaluate_candidates(big_ctx, prof, dam + 0, males, "2040-01-02")
    assert time.perf_counter() - t0 < 0.2
    assert ev.status.shape == males.shape


def test_rule_docs_up_to_date():
    from breeding_smarter.io import repo_root
    from breeding_smarter.rules.docs import render_catalogue, render_verification

    d = repo_root() / "docs"
    assert (d / "rules_catalogue.md").read_text() == render_catalogue(), "run `bsm rules docs`"
    assert (d / "rules_verification.md").read_text() == render_verification()
