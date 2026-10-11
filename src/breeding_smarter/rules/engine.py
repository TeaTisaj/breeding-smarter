"""Evaluate rule profiles for one pair or one dam vs many candidate sires (P6 task 6.4)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import numpy as np
from numpy.typing import NDArray
from pydantic import BaseModel

from breeding_smarter.pedigree.core import IntArray
from breeding_smarter.rules.context import RuleContext, day_number
from breeding_smarter.rules.models import Profile, RuleSpec, Severity, Status
from breeding_smarter.rules.types import RULE_TYPES, Batch

HARD_FAIL, SOFT_FAIL, OK = 2, 1, 0


class RuleResult(BaseModel):
    rule_id: str
    profile: str
    severity: Severity
    passed: bool
    warning: bool
    message: str
    value: float | None
    threshold: float | None
    source: str
    verified: bool
    article: str | None
    note: str | None = None


class ComplianceResult(BaseModel):
    status: Status
    sire: int
    dam: int
    mating_date: str
    profile: str
    results: list[RuleResult]

    @property
    def failed_hard(self) -> list[RuleResult]:
        return [r for r in self.results if not r.passed and r.severity == Severity.HARD]

    @property
    def warnings(self) -> list[RuleResult]:
        return [
            r for r in self.results if (not r.passed and r.severity == Severity.SOFT) or r.warning
        ]


def effective_severity(
    rule: RuleSpec, ctx: RuleContext, dam: int, derogation_granted: bool | None = None
) -> Severity:
    """HARD rules with a local-breed derogation become SOFT for local breeds when granted."""
    granted = rule.derogation_granted if derogation_granted is None else derogation_granted
    breed_local = bool(ctx.is_local_breed[int(ctx.ped.breed[dam])])
    if (
        rule.derogation == "local_breed"
        and breed_local
        and granted
        and rule.severity == Severity.HARD
    ):
        return Severity.SOFT
    return rule.severity


@dataclass
class CandidateEvaluation:
    """Rule outcomes for one dam vs many sires; `status` codes 0 ok, 1 warnings, 2 excluded."""

    ctx: RuleContext
    profile: Profile
    dam: int
    sires: IntArray
    day: int
    batches: dict[str, Batch]
    severities: dict[str, Severity]
    status: NDArray[np.int8]

    def failed(self, k: int, severity: Severity) -> list[str]:
        out = []
        for rule in self.profile.rules:
            b, sev = self.batches[rule.id], self.severities[rule.id]
            if sev != severity:
                continue
            if not b.passed[k] or (severity == Severity.SOFT and b.warn[k]):
                out.append(rule.id)
        return out

    def messages(self, k: int, rule_ids: list[str]) -> list[str]:
        sire = int(self.sires[k])
        return [
            RULE_TYPES[r.type].message(r, self.ctx, self.dam, sire, self.batches[r.id], k)
            for r in self.profile.rules
            if r.id in rule_ids
        ]

    def result(self, k: int) -> ComplianceResult:
        sire = int(self.sires[k])
        rows = []
        for r in self.profile.rules:
            b = self.batches[r.id]
            rows.append(
                RuleResult(
                    rule_id=r.id,
                    profile=r.profile,
                    severity=self.severities[r.id],
                    passed=bool(b.passed[k]),
                    warning=bool(b.warn[k]),
                    message=RULE_TYPES[r.type].message(r, self.ctx, self.dam, sire, b, k),
                    value=None if np.isnan(b.value[k]) else float(b.value[k]),
                    threshold=None if np.isnan(b.threshold) else float(b.threshold),
                    source=r.source,
                    verified=r.verified,
                    article=r.article,
                    note=r.note,
                )
            )
        code = int(self.status[k])
        st = (
            Status.NOT_PERMITTED
            if code == HARD_FAIL
            else Status.PERMITTED_WITH_WARNINGS
            if code == SOFT_FAIL
            else Status.PERMITTED
        )
        d = np.datetime64(self.day, "D")
        return ComplianceResult(
            status=st,
            sire=sire,
            dam=self.dam,
            mating_date=str(d),
            profile=self.profile.name,
            results=rows,
        )


def evaluate_candidates(
    ctx: RuleContext,
    profile: Profile,
    dam: int,
    sires: IntArray,
    mating_date: date | str | int,
    method: str | None = None,
    derogation_granted: bool | None = None,
) -> CandidateEvaluation:
    """Every rule of the profile for dam vs each sire (vectorised over sires)."""
    day = mating_date if isinstance(mating_date, int) else day_number(mating_date)
    sires = np.asarray(sires, dtype=np.int64)
    hard = np.zeros(sires.size, bool)
    soft = np.zeros(sires.size, bool)
    batches, sevs = {}, {}
    for rule in profile.rules:
        b = RULE_TYPES[rule.type].check_many(rule, ctx, dam, sires, day, method)
        sev = effective_severity(rule, ctx, dam, derogation_granted)
        batches[rule.id], sevs[rule.id] = b, sev
        if sev == Severity.HARD:
            hard |= ~b.passed
            soft |= b.warn
        elif sev == Severity.SOFT:
            soft |= ~b.passed | b.warn
    status = np.where(hard, HARD_FAIL, np.where(soft, SOFT_FAIL, OK)).astype(np.int8)
    return CandidateEvaluation(ctx, profile, dam, sires, day, batches, sevs, status)


def evaluate_pair(
    ctx: RuleContext,
    profile: Profile,
    sire: int,
    dam: int,
    mating_date: date | str | int,
    method: str | None = None,
    derogation_granted: bool | None = None,
) -> ComplianceResult:
    ev = evaluate_candidates(
        ctx, profile, dam, np.array([sire]), mating_date, method, derogation_granted
    )
    return ev.result(0)
