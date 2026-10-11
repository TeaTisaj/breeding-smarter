"""Rule type implementations (P6 task 6.3), vectorised over candidate sires.

Every type implements `check_many(rule, ctx, dam, sires, day, method)` returning a `Batch`
(passed, warn, value, threshold per sire) and `message(...)` for one result. `check_one` is a
thin wrapper used in tests.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar

import numpy as np
from numpy.typing import NDArray

from breeding_smarter.pedigree.core import FloatArray, IntArray
from breeding_smarter.pedigree.relationships import Relationship, close_relative_flags
from breeding_smarter.rules.context import GRADES, RuleContext
from breeding_smarter.rules.models import RuleSpec

DAYS_PER_MONTH = 365.25 / 12
BoolArray = NDArray[np.bool_]

REL_TEXT = {
    "PARENT_OFFSPRING": "parent and offspring",
    "FULL_SIBLINGS": "full siblings",
    "HALF_SIBLINGS": "half siblings",
    "GRANDPARENT_GRANDCHILD": "grandparent and grandchild",
}


@dataclass
class Batch:
    passed: BoolArray
    value: FloatArray
    threshold: float
    warn: BoolArray  # soft warning regardless of the rule's severity (e.g. missing data)
    detail: list[str] | None = None  # optional per-sire detail text

    @classmethod
    def of(cls, passed: Any, value: Any, threshold: float = np.nan, warn: Any = None) -> Batch:
        p = np.asarray(passed, dtype=bool)
        v = np.broadcast_to(np.asarray(value, dtype=float), p.shape).copy()
        w = np.zeros(p.shape, bool) if warn is None else np.asarray(warn, dtype=bool)
        return cls(p, v, threshold, w)


class RuleType:
    name: ClassVar[str]
    required: ClassVar[tuple[str, ...]] = ()

    @classmethod
    def validate_params(cls, rule: RuleSpec) -> None:
        from breeding_smarter.rules.loader import RuleConfigError

        missing = [p for p in cls.required if p not in rule.params]
        if missing:
            raise RuleConfigError(f"rule {rule.id} ({rule.type}): missing params {missing}")

    def check_many(
        self,
        rule: RuleSpec,
        ctx: RuleContext,
        dam: int,
        sires: IntArray,
        day: int,
        method: str | None = None,
    ) -> Batch:
        raise NotImplementedError

    def message(
        self, rule: RuleSpec, ctx: RuleContext, dam: int, sire: int, b: Batch, k: int
    ) -> str:
        raise NotImplementedError


class SameBreed(RuleType):
    name = "same_breed"

    def check_many(
        self,
        rule: RuleSpec,
        ctx: RuleContext,
        dam: int,
        sires: IntArray,
        day: int,
        method: str | None = None,
    ) -> Batch:
        return Batch.of(ctx.ped.breed[sires] == ctx.ped.breed[dam], 0.0)

    def message(
        self, rule: RuleSpec, ctx: RuleContext, dam: int, sire: int, b: Batch, k: int
    ) -> str:
        bc = ctx.ped.breed_codes
        if b.passed[k]:
            return "Sire and dam are of the same breed."
        return f"Different breeds ({bc[ctx.ped.breed[sire]]} x {bc[ctx.ped.breed[dam]]})."


class AliveAtMating(RuleType):
    name = "alive_at_mating"

    def check_many(
        self,
        rule: RuleSpec,
        ctx: RuleContext,
        dam: int,
        sires: IntArray,
        day: int,
        method: str | None = None,
    ) -> Batch:
        exempt = rule.params.get("frozen_semen_exempt", False) and method == "ai_frozen"
        dam_ok = ctx.birth_day[dam] <= day < ctx.death_day[dam]
        sire_alive = (ctx.birth_day[sires] <= day) & (day < ctx.death_day[sires])
        sire_ok = sire_alive | (exempt & (ctx.birth_day[sires] <= day))
        return Batch.of(sire_ok & dam_ok, 0.0)

    def message(
        self, rule: RuleSpec, ctx: RuleContext, dam: int, sire: int, b: Batch, k: int
    ) -> str:
        if b.passed[k]:
            return "Both parents alive on the mating date."
        return "A parent is not alive (or not yet born) on the mating date."


class RegistrationType(RuleType):
    name = "registration_type"
    required = ("disallowed",)

    def check_many(
        self,
        rule: RuleSpec,
        ctx: RuleContext,
        dam: int,
        sires: IntArray,
        day: int,
        method: str | None = None,
    ) -> Batch:
        assert rule.params["disallowed"] == ["limited"]
        bad = ctx.limited[sires] | ctx.limited[dam]
        return Batch.of(~bad, bad.astype(float))

    def message(
        self, rule: RuleSpec, ctx: RuleContext, dam: int, sire: int, b: Batch, k: int
    ) -> str:
        if b.passed[k]:
            return "Both parents have full registration."
        who = "dam" if ctx.limited[dam] else "sire"
        return f"The {who} has limited registration (offspring cannot be registered)."


def _linking(ctx: RuleContext, dam: int, sire: int, rel: str) -> str:
    """Name the linking ancestor(s) of a relationship by name and reg_no."""
    S, Dm = ctx.ped.sire, ctx.ped.dam
    if rel == "PARENT_OFFSPRING":
        return ctx.label(sire) + (" is the dam's sire" if S[dam] == sire else " is the dam's son")
    if rel in ("FULL_SIBLINGS", "HALF_SIBLINGS"):
        common = [int(p) for p, q in ((S[dam], S[sire]), (Dm[dam], Dm[sire])) if p >= 0 and p == q]
        return "common parent(s): " + ", ".join(ctx.label(c) for c in common)
    if rel == "GRANDPARENT_GRANDCHILD":
        return ctx.label(sire) + " is a grandparent of the dam, or the dam of the sire"
    return ""


class RelationshipBan(RuleType):
    name = "relationship_ban"
    required = ("relationships",)

    def check_many(
        self,
        rule: RuleSpec,
        ctx: RuleContext,
        dam: int,
        sires: IntArray,
        day: int,
        method: str | None = None,
    ) -> Batch:
        flags = close_relative_flags(ctx.ped, dam, sires)
        banned = np.zeros(sires.size, bool)
        for r in rule.params["relationships"]:
            banned |= flags[Relationship(r)]
        return Batch.of(~banned, banned.astype(float))

    def message(
        self, rule: RuleSpec, ctx: RuleContext, dam: int, sire: int, b: Batch, k: int
    ) -> str:
        if b.passed[k]:
            return "No banned close relationship."
        flags = close_relative_flags(ctx.ped, dam, np.array([sire]))
        hits = [r for r in rule.params["relationships"] if flags[Relationship(r)][0]]
        text = "; ".join(f"{REL_TEXT[h]} ({_linking(ctx, dam, sire, h)})" for h in hits)
        return f"Banned relationship: {text}."


def _age_months(ctx: RuleContext, idx: IntArray | int, day: int) -> FloatArray:
    return np.asarray((day - ctx.birth_day[idx]) / DAYS_PER_MONTH, dtype=float)


class MinAge(RuleType):
    name = "min_age"
    required = ("sex",)

    def _limit(self, rule: RuleSpec) -> float:
        p = rule.params
        return float(p["months"]) if "months" in p else 12.0 * float(p["years"])

    def check_many(
        self,
        rule: RuleSpec,
        ctx: RuleContext,
        dam: int,
        sires: IntArray,
        day: int,
        method: str | None = None,
    ) -> Batch:
        lim = self._limit(rule)
        if rule.params["sex"] == "F":
            age = np.full(sires.size, _age_months(ctx, dam, day))
        else:
            age = _age_months(ctx, sires, day)
        return Batch.of(age >= lim, age, lim)

    def message(
        self, rule: RuleSpec, ctx: RuleContext, dam: int, sire: int, b: Batch, k: int
    ) -> str:
        who = "Dam" if rule.params["sex"] == "F" else "Sire"
        op = ">=" if b.passed[k] else "<"
        return f"{who} age {b.value[k]:.1f} months {op} minimum {b.threshold:g} months."


class MaxAge(MinAge):
    name = "max_age"

    def check_many(
        self,
        rule: RuleSpec,
        ctx: RuleContext,
        dam: int,
        sires: IntArray,
        day: int,
        method: str | None = None,
    ) -> Batch:
        b = super().check_many(rule, ctx, dam, sires, day, method)
        return Batch.of(b.value <= b.threshold, b.value, b.threshold)

    def message(
        self, rule: RuleSpec, ctx: RuleContext, dam: int, sire: int, b: Batch, k: int
    ) -> str:
        who = "Dam" if rule.params["sex"] == "F" else "Sire"
        op = "<=" if b.passed[k] else ">"
        return f"{who} age {b.value[k]:.1f} months {op} maximum {b.threshold:g} months."


class MinIntervalBetweenLitters(RuleType):
    name = "min_interval_between_litters"
    required = ("months",)

    def check_many(
        self,
        rule: RuleSpec,
        ctx: RuleContext,
        dam: int,
        sires: IntArray,
        day: int,
        method: str | None = None,
    ) -> Batch:
        last = ctx.dam_litters.last_before(dam, day)
        gap = np.inf if last is None else (day - last) / DAYS_PER_MONTH
        lim = float(rule.params["months"])
        return Batch.of(np.full(sires.size, gap >= lim), gap, lim)

    def message(
        self, rule: RuleSpec, ctx: RuleContext, dam: int, sire: int, b: Batch, k: int
    ) -> str:
        if np.isinf(b.value[k]):
            return "No previous litter."
        op = ">=" if b.passed[k] else "<"
        return f"{b.value[k]:.1f} months since the dam's last litter {op} {b.threshold:g}."


class MaxLittersInWindow(RuleType):
    name = "max_litters_in_window"
    required = ("max", "window_months")

    def check_many(
        self,
        rule: RuleSpec,
        ctx: RuleContext,
        dam: int,
        sires: IntArray,
        day: int,
        method: str | None = None,
    ) -> Batch:
        since = day - int(rule.params["window_months"] * DAYS_PER_MONTH)
        n = int(ctx.dam_litters.count_before(np.array([dam]), day, since)[0]) + 1
        mx = float(rule.params["max"])
        return Batch.of(np.full(sires.size, n <= mx), n, mx)

    def message(
        self, rule: RuleSpec, ctx: RuleContext, dam: int, sire: int, b: Batch, k: int
    ) -> str:
        w = rule.params["window_months"]
        op = "<=" if b.passed[k] else ">"
        return f"{b.value[k]:.0f} litters in {w} months including this one {op} {b.threshold:g}."


class MaxLifetimeLitters(RuleType):
    name = "max_lifetime_litters"
    required = ("max", "sex")

    def check_many(
        self,
        rule: RuleSpec,
        ctx: RuleContext,
        dam: int,
        sires: IntArray,
        day: int,
        method: str | None = None,
    ) -> Batch:
        mx = float(rule.params["max"])
        if rule.params["sex"] == "F":
            n = np.full(sires.size, ctx.dam_litters.count_before(np.array([dam]), day)[0] + 1)
        else:
            n = ctx.sire_litters.count_before(sires, day) + 1
        return Batch.of(n <= mx, n, mx)

    def message(
        self, rule: RuleSpec, ctx: RuleContext, dam: int, sire: int, b: Batch, k: int
    ) -> str:
        who = "dam" if rule.params["sex"] == "F" else "sire"
        op = "<=" if b.passed[k] else ">"
        return (
            f"Lifetime litters of the {who} including this one: "
            f"{b.value[k]:.0f} {op} {b.threshold:g}."
        )


class HealthGradeExclusion(RuleType):
    name = "health_grade_exclusion"
    required = ("test_type", "exclude")

    def check_many(
        self,
        rule: RuleSpec,
        ctx: RuleContext,
        dam: int,
        sires: IntArray,
        day: int,
        method: str | None = None,
    ) -> Batch:
        assert rule.params["test_type"] == "HD"
        excl = np.array([GRADES.index(g) for g in rule.params["exclude"]])
        gs, gd = ctx.hd_grade[sires], ctx.hd_grade[dam]
        bad = np.isin(gs, excl) | np.isin(gd, excl)
        missing = (gs < 0) | (gd < 0)
        mode = rule.params.get("missing", "allow")
        passed = ~bad & ~(missing & (mode == "block"))
        warn = missing & (mode == "warn") & ~bad
        return Batch.of(passed, np.maximum(gs, gd), float(excl.min()), warn)

    def message(
        self, rule: RuleSpec, ctx: RuleContext, dam: int, sire: int, b: Batch, k: int
    ) -> str:
        def g(i: int) -> str:
            return GRADES[ctx.hd_grade[i]] if ctx.hd_grade[i] >= 0 else "none"

        txt = f"HD: sire {g(sire)}, dam {g(dam)}"
        if not b.passed[k]:
            return txt + f"; grades {rule.params['exclude']} exclude from breeding."
        return txt + ("; missing result." if b.warn[k] else ".")


class AffectedExclusion(RuleType):
    name = "affected_exclusion"

    def check_many(
        self,
        rule: RuleSpec,
        ctx: RuleContext,
        dam: int,
        sires: IntArray,
        day: int,
        method: str | None = None,
    ) -> Batch:
        if not ctx.loci:
            return Batch.of(np.ones(sires.size, bool), 0.0)
        aff = (ctx.dna[sires] == 2).any(axis=1) | bool((ctx.dna[dam] == 2).any())
        return Batch.of(~aff, aff.astype(float))

    def message(
        self, rule: RuleSpec, ctx: RuleContext, dam: int, sire: int, b: Batch, k: int
    ) -> str:
        if b.passed[k]:
            return "No parent known affected at a tested locus."
        loci = [lc for j, lc in enumerate(ctx.loci) if 2 in (ctx.dna[sire, j], ctx.dna[dam, j])]
        return f"A parent is known affected at {', '.join(loci)}."


class CarrierPairing(RuleType):
    name = "carrier_pairing"

    def check_many(
        self,
        rule: RuleSpec,
        ctx: RuleContext,
        dam: int,
        sires: IntArray,
        day: int,
        method: str | None = None,
    ) -> Batch:
        if not ctx.loci:
            return Batch.of(np.ones(sires.size, bool), 0.0)
        both = (ctx.dna[sires] >= 1) & (ctx.dna[dam][None, :] >= 1)
        n = both.sum(axis=1)
        return Batch.of(n == 0, n)

    def message(
        self, rule: RuleSpec, ctx: RuleContext, dam: int, sire: int, b: Batch, k: int
    ) -> str:
        if b.passed[k]:
            return "No known carrier x carrier combination."
        loci = [
            lc for j, lc in enumerate(ctx.loci) if ctx.dna[sire, j] >= 1 and ctx.dna[dam, j] >= 1
        ]
        return (
            f"Both parents known carriers (or affected) at {', '.join(loci)}: "
            "25% or more affected puppies expected."
        )


class OffspringCoiThreshold(RuleType):
    name = "offspring_coi_threshold"

    @classmethod
    def validate_params(cls, rule: RuleSpec) -> None:
        from breeding_smarter.rules.loader import RuleConfigError

        if ("threshold" in rule.params) == bool(rule.params.get("relative_to_breed_mean")):
            raise RuleConfigError(f"rule {rule.id}: give threshold or relative_to_breed_mean")

    def check_many(
        self,
        rule: RuleSpec,
        ctx: RuleContext,
        dam: int,
        sires: IntArray,
        day: int,
        method: str | None = None,
    ) -> Batch:
        f = ctx.kinship_row(dam)[sires]
        if rule.params.get("relative_to_breed_mean"):
            th = ctx.breed_mean_litter_f(int(ctx.ped.breed[dam]), day)
        else:
            th = float(rule.params["threshold"])
        return Batch.of(f <= th if not np.isnan(th) else np.ones(sires.size, bool), f, th)

    def message(
        self, rule: RuleSpec, ctx: RuleContext, dam: int, sire: int, b: Batch, k: int
    ) -> str:
        ref = (
            "breed average of recent litters"
            if rule.params.get("relative_to_breed_mean")
            else "threshold"
        )
        op = "<=" if b.passed[k] else ">"
        return (
            f"Predicted COI of the litter {100 * b.value[k]:.1f}% {op} {ref} "
            f"{100 * b.threshold:.1f}%."
        )


class SireQuota(RuleType):
    name = "sire_quota"
    required = ("share", "window_years")

    def check_many(
        self,
        rule: RuleSpec,
        ctx: RuleContext,
        dam: int,
        sires: IntArray,
        day: int,
        method: str | None = None,
    ) -> Batch:
        since = day - int(365.25 * rule.params["window_years"])
        b = int(ctx.ped.breed[dam])
        off = ctx.sire_offspring.count_before(sires, day, since).astype(float)
        off += ctx.expected_litter_registered[b]
        regs = float(ctx.breed_births.count_before(np.array([b]), day, since)[0])
        cap = rule.params["share"] * regs
        return Batch.of(off <= cap, off, cap)

    def message(
        self, rule: RuleSpec, ctx: RuleContext, dam: int, sire: int, b: Batch, k: int
    ) -> str:
        op = "<=" if b.passed[k] else ">"
        share = 100 * rule.params["share"]
        return (
            f"Sire offspring in {rule.params['window_years']} years incl. this litter "
            f"{b.value[k]:.0f} {op} {share:g}% of breed registrations ({b.threshold:.0f})."
        )


RULE_TYPES: dict[str, RuleType] = {
    t.name: t()
    for t in (
        SameBreed,
        AliveAtMating,
        RegistrationType,
        RelationshipBan,
        MinAge,
        MaxAge,
        MinIntervalBetweenLitters,
        MaxLittersInWindow,
        MaxLifetimeLitters,
        HealthGradeExclusion,
        AffectedExclusion,
        CarrierPairing,
        OffspringCoiThreshold,
        SireQuota,
    )
}


def check_one(
    rule: RuleSpec, ctx: RuleContext, dam: int, sire: int, day: int, method: str | None = None
) -> tuple[bool, float, bool, str]:
    """(passed, value, warn, message) for one pair."""
    t = RULE_TYPES[rule.type]
    b = t.check_many(rule, ctx, dam, np.array([sire], np.int64), day, method)
    return (
        bool(b.passed[0]),
        float(b.value[0]),
        bool(b.warn[0]),
        t.message(rule, ctx, dam, sire, b, 0),
    )
