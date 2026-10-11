"""Rank candidate sires for a dam and build score cards (P7 task 7.6, 7.6b)."""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache

import numpy as np

from breeding_smarter.matching.candidates import candidate_sires
from breeding_smarter.matching.components import Components, compute_components
from breeding_smarter.matching.config import ScoringConfig, load_scoring
from breeding_smarter.matching.context import BreedReference, DatasetContext
from breeding_smarter.matching.explain import ScoreCard, build_card
from breeding_smarter.pedigree.core import FloatArray, IntArray
from breeding_smarter.rules import Profile, day_number, evaluate_candidates, load_profile
from breeding_smarter.rules.engine import HARD_FAIL, SOFT_FAIL, CandidateEvaluation
from breeding_smarter.rules.models import Severity


@lru_cache(maxsize=32)
def _profile(name: str) -> Profile:
    return load_profile(name)


@lru_cache(maxsize=4)
def _default_scoring() -> ScoringConfig:
    return load_scoring()


def _resolve(
    profile: str | Profile, scoring: ScoringConfig | None
) -> tuple[Profile, ScoringConfig]:
    p = _profile(profile) if isinstance(profile, str) else profile
    return p, scoring or _default_scoring()


@dataclass
class Ranked:
    sire: int
    score: float
    tier: str
    status: int  # 0 ok, 1 warnings
    warnings: list[str]


@dataclass
class Recommendation:
    dam: int
    mating_date: str
    profile: str
    ranked: list[Ranked]
    excluded: list[tuple[int, list[str]]]
    n_candidates: int
    n_excluded: int
    n_with_warnings: int
    reference: BreedReference
    _cards: dict[int, ScoreCard] = field(default_factory=dict, repr=False)
    _builder: object = None

    def card(self, sire: int) -> ScoreCard:
        """Score card of a ranked or excluded sire (built lazily)."""
        if sire not in self._cards:
            self._cards[sire] = self._builder(sire)  # type: ignore[operator]
        return self._cards[sire]


def _score(
    comp: Components, ev: CandidateEvaluation, scoring: ScoringConfig
) -> tuple[FloatArray, list[str]]:
    total = comp.total(scoring)
    tiers = [scoring.tier(float(s)) for s in total]
    cap = scoring.soft_warning_caps_tier_at.value
    cap_rank = scoring.tier_rank(cap)
    for k, st in enumerate(ev.status):
        if st == SOFT_FAIL and scoring.tier_rank(tiers[k]) < cap_rank:
            tiers[k] = cap
    return total, tiers


def _evaluate(
    ctx: DatasetContext,
    dam: int,
    day: int,
    profile: Profile,
    scoring: ScoringConfig,
    max_distance_km: float | None,
    include_foreign: bool = True,
) -> tuple[IntArray, Components, CandidateEvaluation, BreedReference]:
    sires = candidate_sires(ctx, dam, day, max_distance_km, include_foreign)
    ref = ctx.reference(ctx.breed_of(dam), day, scoring.allele_frequency_window_years.value)
    ev = evaluate_candidates(ctx.rules, profile, dam, sires, day)
    comp = compute_components(ctx, dam, sires, day, ref, scoring)
    return sires, comp, ev, ref


def rank_fast(
    ctx: DatasetContext,
    dam_idx: int,
    mating_date: str | int,
    profile: str | Profile = "hr_full",
    scoring: ScoringConfig | None = None,
    max_distance_km: float | None = None,
) -> tuple[IntArray, FloatArray]:
    """Same components and rules as `recommend_sires`, without cards or messages.

    Returns permitted sires sorted by score (descending, ties by index) and their scores.
    """
    prof, sc = _resolve(profile, scoring)
    day = mating_date if isinstance(mating_date, int) else day_number(mating_date)
    sires, comp, ev, _ = _evaluate(ctx, dam_idx, day, prof, sc, max_distance_km)
    total = comp.total(sc)
    ok = ev.status != HARD_FAIL
    s, t = sires[ok], total[ok]
    order = np.lexsort((s, -t))
    return s[order], t[order]


def recommend_sires(
    ctx: DatasetContext,
    dam_idx: int,
    mating_date: str,
    profile: str | Profile = "hr_full",
    scoring: ScoringConfig | None = None,
    top_k: int = 20,
    max_distance_km: float | None = None,
) -> Recommendation:
    """Rank all permitted candidate sires; excluded ones are listed with their reasons."""
    prof, sc = _resolve(profile, scoring)
    day = day_number(mating_date)
    sires, comp, ev, ref = _evaluate(ctx, dam_idx, day, prof, sc, max_distance_km)
    total, tiers = _score(comp, ev, sc)
    ok = ev.status != HARD_FAIL
    order = np.lexsort((sires, -total))
    ranked, excluded = [], []
    pos_of = {int(s): k for k, s in enumerate(sires)}
    for k in order:
        s = int(sires[k])
        if ok[k]:
            warn = ev.messages(int(k), ev.failed(int(k), Severity.SOFT))
            ranked.append(Ranked(s, float(total[k]), tiers[k], int(ev.status[k]), warn))
        else:
            excluded.append((s, ev.messages(int(k), ev.failed(int(k), Severity.HARD))))

    def builder(sire: int) -> ScoreCard:
        k = pos_of[sire]
        return build_card(
            ctx, dam_idx, k, comp, ref, sc, float(total[k]), tiers[k], ev.result(k), mating_date
        )

    rec = Recommendation(
        dam=dam_idx,
        mating_date=mating_date,
        profile=prof.name,
        ranked=ranked,
        excluded=excluded,
        n_candidates=int(sires.size),
        n_excluded=len(excluded),
        n_with_warnings=int((ev.status == SOFT_FAIL).sum()),
        reference=ref,
        _builder=builder,
    )
    for r in ranked[:top_k]:
        rec.card(r.sire)
    return rec


def score_pair(
    ctx: DatasetContext,
    sire_idx: int,
    dam_idx: int,
    mating_date: str,
    profile: str | Profile = "hr_full",
    scoring: ScoringConfig | None = None,
) -> ScoreCard:
    """Score card for any pair (the sire need not pass the candidate filter)."""
    prof, sc = _resolve(profile, scoring)
    day = day_number(mating_date)
    ref = ctx.reference(ctx.breed_of(dam_idx), day, sc.allele_frequency_window_years.value)
    sires = np.array([sire_idx], np.int64)
    ev = evaluate_candidates(ctx.rules, prof, dam_idx, sires, day)
    comp = compute_components(ctx, dam_idx, sires, day, ref, sc)
    total, tiers = _score(comp, ev, sc)
    return build_card(
        ctx, dam_idx, 0, comp, ref, sc, float(total[0]), tiers[0], ev.result(0), mating_date
    )
