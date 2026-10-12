"""Kennel club desk: mating applications checked before the mating (prototype, synthetic data).

A breeder applies for a mating, the stud owner confirms, and the breeding officer approves or
rejects. The automatic checks are the pair's score card (`score_pair`: every rule of the
profile with its source) and the sire's club quota for the season (the club planner's quotas
in a `BookingLedger`). What the registry cannot know goes on a manual checklist for the
officer. Pure functions, no I/O.

Outcome of the automatic checks:
- BLOCKED: a HARD rule fails.
- NEEDS_REVIEW: no HARD failure, but a SOFT rule warns, the sire has no club quota left, or a
  conditional manual check applies (veterinary certificate for an older dam).
- READY: everything automatic passed. The standard manual checks (breeding examinations, show
  grades, original health results) are always listed and still wait for the officer, but they
  do not change the outcome.

Application status: SUBMITTED -> STUD_OWNER_CONFIRMED -> APPROVED or REJECTED. Approval books
one litter of the sire's quota, exactly once; rejection books nothing.
"""

from __future__ import annotations

import html
import math
from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from enum import StrEnum

import numpy as np
import pandas as pd

from breeding_smarter.coordination.ledger import BookingLedger
from breeding_smarter.matching.candidates import candidate_sires
from breeding_smarter.matching.context import DatasetContext
from breeding_smarter.matching.examples import eligible_dams
from breeding_smarter.matching.explain import ScoreCard
from breeding_smarter.matching.recommend import rank_fast, score_pair
from breeding_smarter.pedigree.core import IntArray
from breeding_smarter.rules import day_number, evaluate_candidates, load_profile
from breeding_smarter.rules.engine import OK
from breeding_smarter.rules.models import Severity

PROTOTYPE_NOTE = "Prototype on synthetic data. Not an official kennel club form."
# assumption (desk spec B3, no source): a dam older than this needs a veterinary certificate
VET_CERTIFICATE_DAM_AGE_YEARS = 7.0
EU_CLOSE_RELATIVES = "eu_close_relatives"
EU_PROFILE = "eu_2026_1818"


class DeskError(ValueError):
    """An action that the application's state does not allow."""


class AppStatus(StrEnum):
    SUBMITTED = "SUBMITTED"
    STUD_OWNER_CONFIRMED = "STUD_OWNER_CONFIRMED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class Outcome(StrEnum):
    READY = "READY"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    BLOCKED = "BLOCKED"


OUTCOME_LABEL = {
    Outcome.READY: "Allowed",
    Outcome.NEEDS_REVIEW: "Needs club review",
    Outcome.BLOCKED: "Blocked",
}


@dataclass
class MatingApplication:
    app_id: str
    dam: int  # registry idx
    sire: int  # registry idx
    mating_date: str  # ISO date of the planned mating
    applicant: str  # synthetic name
    status: AppStatus = AppStatus.SUBMITTED
    stud_owner_confirmed: bool = False
    officer_decision: str | None = None  # "approved" or "rejected"
    note: str = ""
    manual_done: set[str] = field(default_factory=set)
    booked: bool = False  # approval booked one litter of the sire's club quota
    quota_exception: bool = False  # approved over quota as a club exception (nothing booked)


@dataclass
class SeasonQuota:
    """The season's club quotas (litters per sire) and the shared booking ledger."""

    ledger: BookingLedger
    total: dict[int, int]

    @classmethod
    def from_plan(cls, sires: IntArray, quotas: IntArray) -> SeasonQuota:
        sires = np.asarray(sires, np.int64)
        quotas = np.maximum(np.asarray(quotas, np.int64), 0)
        total = {int(s): int(q) for s, q in zip(sires, quotas, strict=True)}
        return cls(BookingLedger(sires, quotas), total)

    def remaining(self, sire: int) -> int:
        return self.ledger.remaining(sire)

    def of(self, sire: int) -> int:
        return self.total.get(int(sire), 0)


@dataclass(frozen=True)
class Check:
    """One automatic check: a rule of the profile (from the score card) or the club quota."""

    rule_id: str
    severity: str
    passed: bool
    warning: bool
    message: str
    source: str
    verified: bool
    profile: str = ""  # the rule profile that defines the rule (e.g. eu_2026_1818)

    @property
    def symbol(self) -> str:
        if self.passed and not self.warning:
            return "✓"
        if not self.passed and self.severity == Severity.HARD:
            return "✗"
        if not self.passed and self.severity == Severity.INFO:
            return "ℹ"
        return "⚠"


@dataclass(frozen=True)
class ManualCheck:
    key: str
    text: str
    conditional: bool = False  # True: applies to this pair only and sends it to review


STANDARD_MANUAL = (
    ManualCheck("exam_dam", "Valid breeding examination of the dam"),
    ManualCheck("exam_sire", "Valid breeding examination of the sire"),
    ManualCheck("show_grade", "Show grade (good or very good) for both dogs"),
    ManualCheck("health_originals", "Original health certificates match the registry results"),
)
VET_CERTIFICATE = ManualCheck(
    "vet_certificate",
    f"Veterinary certificate for a dam older than {VET_CERTIFICATE_DAM_AGE_YEARS:g} years",
    conditional=True,
)
QUOTA_RULE = "club_quota"
QUOTA_SOURCE = "club planner (this season)"


@dataclass
class Assessment:
    app_id: str
    outcome: Outcome
    checks: list[Check]  # every rule of the profile, then the club quota (if known)
    manual: list[ManualCheck]
    reasons: list[str]  # why BLOCKED or NEEDS_REVIEW, each naming its rule or check
    quota_left: int | None  # club litters left for the sire before this application
    quota_total: int | None
    dam_age_years: float
    card: ScoreCard

    @property
    def failed_hard(self) -> list[Check]:
        return [c for c in self.checks if not c.passed and c.severity == Severity.HARD]

    @property
    def warnings(self) -> list[Check]:
        return [
            c
            for c in self.checks
            if c.rule_id != QUOTA_RULE
            and ((not c.passed and c.severity == Severity.SOFT) or c.warning)
        ]


def manual_checks(dam_age_years: float) -> list[ManualCheck]:
    out = list(STANDARD_MANUAL)
    if dam_age_years > VET_CERTIFICATE_DAM_AGE_YEARS:
        out.append(VET_CERTIFICATE)
    return out


def assess(
    ctx: DatasetContext,
    application: MatingApplication,
    profile: str = "hr_full",
    quota: SeasonQuota | None = None,
) -> Assessment:
    """Automatic checks, manual checklist and outcome for one application."""
    card = score_pair(ctx, application.sire, application.dam, application.mating_date, profile)
    checks = [
        Check(
            rule_id=str(r["rule_id"]),
            severity=str(r["severity"]),
            passed=bool(r["passed"]),
            warning=bool(r["warning"]),
            message=str(r["message"]),
            source=str(r["source"]),
            verified=bool(r["verified"]),
            profile=str(r.get("profile", "")),
        )
        for r in card.rules
    ]
    left = total = None
    if quota is not None:
        total = quota.of(application.sire)
        left = quota.remaining(application.sire) + (1 if application.booked else 0)
        checks.append(
            Check(
                rule_id=QUOTA_RULE,
                severity=Severity.SOFT,
                passed=left > 0,
                warning=False,
                message=_quota_sentence(left, total),
                source=QUOTA_SOURCE,
                verified=True,
            )
        )
    day = day_number(application.mating_date)
    age = float(ctx.age_years(application.dam, day))
    manual = manual_checks(age)
    hard = [c for c in checks if not c.passed and c.severity == Severity.HARD]
    reasons = [f"{c.rule_id} (source {c.source}): {c.message}" for c in hard]
    if hard:
        outcome = Outcome.BLOCKED
    else:
        for c in checks:
            soft = (not c.passed and c.severity == Severity.SOFT) or c.warning
            if soft and c.rule_id != QUOTA_RULE:
                reasons.append(f"{c.rule_id} (source {c.source}): {c.message}")
        if left is not None and left <= 0:
            reasons.append(_quota_sentence(left, total or 0))
        reasons += [m.text for m in manual if m.conditional]
        outcome = Outcome.NEEDS_REVIEW if reasons else Outcome.READY
    return Assessment(
        app_id=application.app_id,
        outcome=outcome,
        checks=checks,
        manual=manual,
        reasons=reasons,
        quota_left=left,
        quota_total=total,
        dam_age_years=age,
        card=card,
    )


def _pct(x: float) -> str:
    return f"{100 * x:.1f}%"


def _quota_sentence(left: int, total: int) -> str:
    if total <= 0:
        return "The sire has no club quota this season."
    if left <= 0:
        return f"The sire has used all {total} litter(s) of this season's club quota."
    return f"The sire has {left} of {total} litter(s) left in this season's club quota."


def _dna_sentence(card: ScoreCard) -> str | None:
    if not card.health:
        return None
    known, unknown, carriers = [], [], []
    for h in card.health:
        if "unknown" in (h.sire_status, h.dam_status):
            unknown.append(h.locus)
            continue
        known.append(h.locus)
        for who, st in (("sire", h.sire_status), ("dam", h.dam_status)):
            if st.startswith(("carrier", "affected")):
                carriers.append(f"{who} {st.split(' ')[0]} at {h.locus}")
    parts = []
    if carriers:
        parts.append("Known DNA findings: " + ", ".join(carriers))
    elif known:
        parts.append(
            f"Both dogs have a known DNA status at {', '.join(known)}; neither is a carrier"
        )
    if unknown:
        parts.append(f"status unknown for at least one dog at {', '.join(unknown)}")
    text = "; ".join(parts)
    return text[0].upper() + text[1:] + "."


def explain(assessment: Assessment) -> list[str]:
    """3 to 5 sentences built from templates and the numbers on the card (no free text)."""
    a, card = assessment, assessment.card
    out: list[str] = []
    if a.outcome == Outcome.BLOCKED:
        first = a.failed_hard[0]
        more = len(a.failed_hard) - 1
        extra = f" ({more} more hard rule(s) also fail)" if more else ""
        out.append(f"Mating blocked by {first.rule_id} (source {first.source}){extra}.")
        out.append(first.message)
    elif a.outcome == Outcome.NEEDS_REVIEW:
        out.append(
            f"No hard rule fails, but the club needs to review {len(a.reasons)} point(s) "
            "before approval."
        )
    else:
        out.append("Mating allowed by all automatic checks.")
    mean = card.breed_mean_litter_coi
    coi = card.predicted_coi
    if mean is None or math.isnan(mean):
        out.append(f"Predicted inbreeding {_pct(coi)}; no breed average is available.")
    else:
        rel = "below" if coi < mean else "above" if coi > mean else "equal to"
        out.append(f"Predicted inbreeding {_pct(coi)}, {rel} the breed average of {_pct(mean)}.")
    dna = _dna_sentence(card)
    if dna:
        out.append(dna)
    if a.quota_left is not None and a.quota_total is not None:
        out.append(_quota_sentence(a.quota_left, a.quota_total))
    if card.depth_warning and len(out) < 5:
        out.append(card.depth_warning)
    return out[:5]


# ---------------------------------------------------------------- workflow


def new_application(
    app_id: str, dam: int, sire: int, mating_date: str, applicant: str
) -> MatingApplication:
    return MatingApplication(app_id, int(dam), int(sire), mating_date, applicant)


def next_app_id(applications: Iterable[MatingApplication]) -> str:
    n = max((int(a.app_id.split("-")[-1]) for a in applications), default=0)
    return f"APP-{n + 1:04d}"


def can_submit(assessment: Assessment) -> bool:
    return assessment.outcome != Outcome.BLOCKED


def confirm_stud_owner(app: MatingApplication) -> None:
    """The second signature; repeating it changes nothing."""
    if app.status in (AppStatus.APPROVED, AppStatus.REJECTED):
        raise DeskError(f"{app.app_id} is already {app.status.value.lower()}")
    app.stud_owner_confirmed = True
    app.status = AppStatus.STUD_OWNER_CONFIRMED


def can_approve(app: MatingApplication, assessment: Assessment) -> tuple[bool, str]:
    """(allowed, reason if not): stud owner confirmed, manual checks ticked, not blocked."""
    if app.status == AppStatus.REJECTED:
        return False, "The application was rejected."
    if assessment.outcome == Outcome.BLOCKED:
        return False, "A hard rule fails: the mating cannot be approved."
    if not app.stud_owner_confirmed:
        return False, "The stud owner has not confirmed yet."
    missing = [m.text for m in assessment.manual if m.key not in app.manual_done]
    if missing:
        return False, "Manual checks still open: " + "; ".join(missing) + "."
    return True, ""


def approve(
    app: MatingApplication,
    assessment: Assessment,
    quota: SeasonQuota | None,
    note: str = "",
    exception: bool = False,
) -> None:
    """Approve and book one litter of the sire's club quota (once). With no quota left, only an
    explicit club exception with a note is possible; it books nothing."""
    if app.status == AppStatus.APPROVED:
        return
    ok, why = can_approve(app, assessment)
    if not ok:
        raise DeskError(why)
    if quota is not None and quota.remaining(app.sire) <= 0:
        if not (exception and note.strip()):
            raise DeskError(
                "The sire has no club quota left: approve only as a club exception with a note."
            )
        app.quota_exception = True
    elif quota is not None:
        quota.ledger.book(app.sire)
        app.booked = True
    app.status = AppStatus.APPROVED
    app.officer_decision = "approved"
    if note:
        app.note = note


def reject(app: MatingApplication, note: str = "") -> None:
    """Reject; books nothing. An approved application cannot be rejected afterwards."""
    if app.status == AppStatus.APPROVED:
        raise DeskError(f"{app.app_id} is already approved")
    app.status = AppStatus.REJECTED
    app.officer_decision = "rejected"
    if note:
        app.note = note


# ---------------------------------------------------------------- certificate


def certificate_html(app: MatingApplication, assessment: Assessment, issued_on: str) -> str:
    """Mating certificate (prototype) of an approved application as a standalone HTML page."""
    if app.status != AppStatus.APPROVED:
        raise DeskError(f"{app.app_id} is not approved")
    e = html.escape
    card = assessment.card
    rows = "".join(
        f"<tr><td>{e(c.symbol)}</td><td>{e(c.rule_id)}</td><td>{e(c.severity)}</td>"
        f"<td>{e(c.message)}</td><td>{e(c.source)}</td>"
        f"<td>{'yes' if c.verified else 'unverified'}</td></tr>"
        for c in assessment.checks
    )
    manual = "".join(
        f"<li>{e(m.text)}: {'checked' if m.key in app.manual_done else 'open'}</li>"
        for m in assessment.manual
    )
    if app.quota_exception:
        quota = "Approved over the club quota as a club exception (nothing booked)."
    elif app.booked and assessment.quota_total is not None:
        quota = f"One litter booked of the sire's club quota of {assessment.quota_total}."
    else:
        quota = "No club quota recorded."
    note = f"<p>Officer note: {e(app.note)}</p>" if app.note else ""
    banner = f'<p class="proto">{e(PROTOTYPE_NOTE)}</p>'
    return (
        "<!doctype html><html><head><meta charset='utf-8'>"
        f"<title>Mating certificate (prototype) {e(app.app_id)}</title>"
        "<style>body{font-family:sans-serif;max-width:900px;margin:2em auto}"
        ".proto{background:#fff3cd;padding:.5em;border:1px solid #c9a227;font-weight:bold}"
        "table{border-collapse:collapse;width:100%}td,th{border:1px solid #999;padding:4px;"
        "font-size:13px;text-align:left}</style></head><body>"
        f"{banner}<h1>Mating certificate (prototype)</h1>"
        f"<p>Application {e(app.app_id)}, status {e(app.status.value)}, issued {e(issued_on)}.</p>"
        f"<p>Dam: {e(card.dam_label)}<br>Sire: {e(card.sire_label)}<br>Breed: {e(card.breed)}"
        f"<br>Planned mating date: {e(app.mating_date)}<br>Applicant: {e(app.applicant)}</p>"
        f"<p>Automatic checks: {e(OUTCOME_LABEL[assessment.outcome])}. "
        f"Predicted inbreeding {e(_pct(card.predicted_coi))}.</p>"
        "<table><tr><th></th><th>Check</th><th>Severity</th><th>Result</th><th>Source</th>"
        f"<th>Verified</th></tr>{rows}</table>"
        f"<h2>Manual checks</h2><ul>{manual}</ul><p>{e(quota)}</p>{note}"
        f"{banner}</body></html>"
    )


# ---------------------------------------------------------------- demo examples


def _first(ranked: IntArray, ok: set[int]) -> int | None:
    return next((int(s) for s in ranked if int(s) in ok), None)


def example_applications(
    ctx: DatasetContext,
    quota: SeasonQuota,
    breed: str,
    mating_date: str,
    profile: str = "hr_full",
    max_dams: int = 400,
) -> list[MatingApplication]:
    """Three applications for the demo queue, found in the data (empty slots are skipped):
    1. a dam and her half-brother, blocked only by the EU close-relative ban;
    2. a clean pair within the club quota (READY, waiting for the stud owner);
    3. a pair whose sire has no club quota left (NEEDS_REVIEW).
    """
    day = day_number(mating_date)
    prof = load_profile(profile)
    S, D = ctx.ped.sire, ctx.ped.dam
    blocked = clean = no_quota = None
    for d in eligible_dams(ctx, breed, day)[:max_dams]:
        d = int(d)
        if ctx.age_years(d, day) > VET_CERTIFICATE_DAM_AGE_YEARS:
            continue
        cand = candidate_sires(ctx, d, day)
        if cand.size == 0:
            continue
        ev = evaluate_candidates(ctx.rules, prof, d, cand, day)
        if blocked is None:
            half = ((S[cand] == S[d]) & (S[d] >= 0)) ^ ((D[cand] == D[d]) & (D[d] >= 0))
            for k in np.flatnonzero(half):
                if ev.failed(int(k), Severity.HARD) == [EU_CLOSE_RELATIVES]:
                    blocked = (d, int(cand[k]))
                    break
            if blocked is not None and blocked[0] == d:
                continue
        clean_ok = {int(cand[k]) for k in np.flatnonzero(ev.status == OK)}
        if not clean_ok:
            continue
        ranked, _ = rank_fast(ctx, d, day, prof, candidates=np.array(sorted(clean_ok), np.int64))
        if clean is None:
            s = _first(ranked, {x for x in clean_ok if quota.remaining(x) > 0})
            if s is not None:
                clean = (d, s)
                continue
        if no_quota is None:
            s = _first(ranked, {x for x in clean_ok if quota.remaining(x) <= 0})
            if s is not None:
                no_quota = (d, s)
        if blocked is not None and clean is not None and no_quota is not None:
            break
    out: list[MatingApplication] = []
    for slot, pair in enumerate((blocked, clean, no_quota), start=1):
        if pair is not None:
            out.append(
                new_application(
                    f"APP-{slot:04d}", pair[0], pair[1], mating_date, f"Synthetic breeder {slot}"
                )
            )
    return out


# ---------------------------------------------------------------- season overview


@dataclass(frozen=True)
class SeasonSummary:
    """Counts over the season's applications. `approved`, `rejected` and `waiting` split them by
    status (waiting = open and not blocked); `blocked` counts every application whose automatic
    checks give BLOCKED, whatever its status, so it can overlap with `rejected`."""

    applications: int
    approved: int
    rejected: int
    blocked: int
    waiting: int
    blocked_by_rule: dict[str, int]  # HARD rule -> blocked applications it fails
    eu_bans: int  # blocked applications failing a rule of the EU 2026/1818 profile
    without_quota: int  # waiting applications whose sire has no club quota left


def _open(app: MatingApplication) -> bool:
    return app.status in (AppStatus.SUBMITTED, AppStatus.STUD_OWNER_CONFIRMED)


def season_summary(
    applications: Iterable[MatingApplication], assessments: Mapping[str, Assessment]
) -> SeasonSummary:
    apps = list(applications)
    blocked = [a for a in apps if assessments[a.app_id].outcome == Outcome.BLOCKED]
    waiting = [a for a in apps if _open(a) and assessments[a.app_id].outcome != Outcome.BLOCKED]
    by_rule = Counter(c.rule_id for a in blocked for c in assessments[a.app_id].failed_hard)
    eu = sum(
        any(c.profile == EU_PROFILE for c in assessments[a.app_id].failed_hard) for a in blocked
    )
    no_quota = sum((q := assessments[a.app_id].quota_left) is not None and q <= 0 for a in waiting)
    return SeasonSummary(
        applications=len(apps),
        approved=sum(a.status == AppStatus.APPROVED for a in apps),
        rejected=sum(a.status == AppStatus.REJECTED for a in apps),
        blocked=len(blocked),
        waiting=len(waiting),
        blocked_by_rule=dict(sorted(by_rule.items(), key=lambda kv: (-kv[1], kv[0]))),
        eu_bans=int(eu),
        without_quota=int(no_quota),
    )


def quota_usage(ctx: DatasetContext, quota: SeasonQuota) -> pd.DataFrame:
    """Club quota per sire with a quota this season: litters booked and left."""
    rows = [
        {
            "sire": ctx.rules.label(s),
            "quota": q,
            "booked": q - quota.remaining(s),
            "left": quota.remaining(s),
        }
        for s, q in quota.total.items()
        if q > 0
    ]
    df = pd.DataFrame(rows, columns=["sire", "quota", "booked", "left"])
    return df.sort_values(["booked", "quota", "sire"], ascending=[False, False, True]).reset_index(
        drop=True
    )


def compliance_report(
    ctx: DatasetContext,
    applications: Iterable[MatingApplication],
    assessments: Mapping[str, Assessment],
) -> pd.DataFrame:
    """One row per application: outcome, status, every rule with its result and source."""
    r = ctx.rules
    rows = []
    for app in applications:
        a = assessments[app.app_id]
        rows.append(
            {
                "application": app.app_id,
                "data": "synthetic (prototype, not an official kennel club form)",
                "breed": a.card.breed,
                "dam_reg_no": r.reg_no[app.dam],
                "dam_name": r.name[app.dam],
                "sire_reg_no": r.reg_no[app.sire],
                "sire_name": r.name[app.sire],
                "mating_date": app.mating_date,
                "applicant": app.applicant,
                "outcome": a.outcome.value,
                "status": app.status.value,
                "stud_owner_confirmed": app.stud_owner_confirmed,
                "failed_hard_rules": "; ".join(f"{c.rule_id} ({c.source})" for c in a.failed_hard),
                "warnings": "; ".join(f"{c.rule_id} ({c.source})" for c in a.warnings),
                "checks": "; ".join(
                    f"{c.symbol} {c.rule_id} [{c.source}; "
                    f"{'verified' if c.verified else 'unverified'}]"
                    for c in a.checks
                ),
                "predicted_coi": round(a.card.predicted_coi, 4),
                "quota_left_before": a.quota_left,
                "quota_total": a.quota_total,
                "quota_booked": app.booked,
                "quota_exception": app.quota_exception,
                "manual_checks_done": "; ".join(
                    m.key for m in a.manual if m.key in app.manual_done
                ),
                "officer_decision": app.officer_decision or "",
                "note": app.note,
            }
        )
    return pd.DataFrame(rows)
