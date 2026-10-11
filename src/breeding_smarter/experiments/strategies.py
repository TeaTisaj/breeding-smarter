"""Breeding strategies for the experiments (P8 task 8.1). All see observed data only.

| id | behaviour |
|----|-----------|
| S0 | random among eligible males of the breed |
| S1 | status-quo market (P3/P4 `MarketStrategy`) |
| S2 | market, but HARD-rule failures of `exp_pairing` removed and pairs above the COI cap
       avoided (a regulated market with a COI check) |
| S3 | recommender: each adopting dam picks among the top 3 of `rank_fast` (P7) with
       probabilities 0.5/0.3/0.2; non-adopters follow S2 |
| S4 | coordinated planner: all dams of the year assigned jointly, cost F_off + lambda MK_off,
       sire capacity from the FCI 5% rule, HARD-rule pairs cost 1e6 |

Candidate sires are the simulator's eligible domestic males plus eligible foreign males that
already have a registry record (a breeder can only evaluate dogs with a record). The market
part of S1/S2 also uses unregistered foreign AI sires, as in the history.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from scipy.optimize import linear_sum_assignment

from breeding_smarter.experiments.observed import ObservedRegistry
from breeding_smarter.matching.config import ScoringConfig
from breeding_smarter.matching.context import DatasetContext
from breeding_smarter.matching.recommend import rank_fast
from breeding_smarter.pedigree.core import IntArray
from breeding_smarter.rules import day_number, evaluate_candidates, load_profile
from breeding_smarter.rules.engine import HARD_FAIL
from breeding_smarter.sim.interfaces import YearContext
from breeding_smarter.sim.market import MarketStrategy, sample_rows

HARD_COST = 1e6


@dataclass
class StrategyParams:
    profile: str = "exp_pairing"
    coi_cap: float = 0.065
    top_probs: tuple[float, ...] = (0.5, 0.3, 0.2)
    adoption: float = 1.0
    s4_lambda: float = 1.0
    fci_share: float = 0.05


@dataclass
class ObservedStrategy:
    """Base: holds the registry view; the runner sets `obs` and `ctx` every year."""

    params: StrategyParams
    scoring: ScoringConfig
    obs: ObservedRegistry | None = None
    ctx: DatasetContext | None = None
    stats: dict[str, Any] = field(default_factory=dict)

    def candidates(self, sires: IntArray, yc: YearContext) -> tuple[IntArray, IntArray]:
        """(gids, registry idx) of candidate sires: eligible domestic + registered foreign."""
        assert self.obs is not None
        foreign = np.array([g for g in yc.foreign_sires if self.obs.has(int(g))], dtype=np.int64)
        gids = np.r_[np.asarray(sires, np.int64), foreign]
        return gids, self.obs.idx(gids)

    def day(self, year: int) -> int:
        return day_number(f"{year}-07-01")


class RandomStrategy:
    name = "S0"

    def plan_matings(self, dams, sires, ctx, rng):
        if len(sires) == 0:
            return np.full(len(dams), -1, np.int64)
        return np.asarray(sires)[rng.integers(0, len(sires), len(dams))].astype(np.int64)


class CompliantMarket(ObservedStrategy):
    """S2: market weights restricted to pairs that pass HARD rules and the COI cap."""

    name = "S2"

    def allowed(self, dam_idx: int, sire_idx: IntArray, day: int) -> np.ndarray:
        assert self.ctx is not None
        prof = load_profile(self.params.profile)
        ok = np.zeros(sire_idx.size, bool)
        known = sire_idx >= 0
        ev = evaluate_candidates(self.ctx.rules, prof, dam_idx, sire_idx[known], day)
        f = self.ctx.rules.kinship_row(dam_idx)[sire_idx[known]]
        ok[known] = (ev.status != HARD_FAIL) & (f <= self.params.coi_cap)
        ok[~known] = True  # no record: no recorded relationship
        return ok

    def plan_matings(self, dams, sires, ctx, rng):
        assert self.obs is not None
        dams = np.asarray(dams, np.int64)
        sires = np.asarray(sires, np.int64)
        out = MarketStrategy().plan_matings(dams, sires, ctx, rng)  # foreign AI as in market
        dom = np.isin(out, sires) | (out < 0)
        if sires.size == 0:
            return out
        market = MarketStrategy()
        W = market.sire_weights(dams[dom], sires, ctx)
        day = self.day(ctx.year)
        s_idx = self.obs.idx(sires)
        d_idx = self.obs.idx(dams[dom])
        relaxed = 0
        for k, di in enumerate(d_idx):
            ok = self.allowed(int(di), s_idx, day) if di >= 0 else np.ones(sires.size, bool)
            if not ok.any():  # nothing passes the cap: fall back to HARD-rule pass only
                relaxed += 1
                ok = self._hard_only(int(di), s_idx, day)
            W[k, ~ok] = 0.0
        j = sample_rows(W, rng)
        out[dom] = np.where(j >= 0, sires[np.maximum(j, 0)], -1)
        self.stats["s2_relaxed"] = self.stats.get("s2_relaxed", 0) + relaxed
        return out

    def _hard_only(self, dam_idx: int, sire_idx: IntArray, day: int) -> np.ndarray:
        assert self.ctx is not None
        ev = evaluate_candidates(
            self.ctx.rules, load_profile(self.params.profile), dam_idx, sire_idx, day
        )
        return np.asarray(ev.status != HARD_FAIL)


class Recommender(CompliantMarket):
    """S3: adopting dams pick among the top 3 of `rank_fast`; others follow S2."""

    name = "S3"

    def plan_matings(self, dams, sires, ctx, rng):
        assert self.obs is not None and self.ctx is not None
        dams = np.asarray(dams, np.int64)
        out = np.full(dams.size, -1, np.int64)
        adopt = rng.random(dams.size) < self.params.adoption
        if (~adopt).any():
            out[~adopt] = super().plan_matings(dams[~adopt], sires, ctx, rng)
        cand_gid, cand_idx = self.candidates(sires, ctx)
        keep = cand_idx >= 0
        cand_gid, cand_idx = cand_gid[keep], cand_idx[keep]
        gid_of = dict(zip(cand_idx.tolist(), cand_gid.tolist(), strict=True))
        self.ctx.extra_offspring = np.zeros(self.obs.n)
        exp_litter = float(self.ctx.rules.expected_litter_registered[0])
        day = self.day(ctx.year)
        probs = np.array(self.params.top_probs)
        for k in np.flatnonzero(adopt):
            di = int(self.obs.idx_of.get(int(dams[k]), -1))
            if di < 0 or cand_idx.size == 0:
                continue
            ranked, _ = rank_fast(
                self.ctx, di, day, self.params.profile, self.scoring, candidates=cand_idx
            )
            if ranked.size == 0:
                continue
            top = ranked[: probs.size]
            p = probs[: top.size] / probs[: top.size].sum()
            choice = int(top[rng.choice(top.size, p=p)])
            out[k] = gid_of[choice]
            self.ctx.extra_offspring[choice] += exp_litter
        self.ctx.extra_offspring = None
        return out


class CoordinatedPlanner(ObservedStrategy):
    """S4: joint assignment of all dams of the year (Hungarian algorithm on replicated sires)."""

    name = "S4"

    def plan_matings(self, dams, sires, ctx, rng):
        assert self.obs is not None and self.ctx is not None
        dams = np.asarray(dams, np.int64)
        out = np.full(dams.size, -1, np.int64)
        cand_gid, cand_idx = self.candidates(sires, ctx)
        keep = cand_idx >= 0
        cand_gid, cand_idx = cand_gid[keep], cand_idx[keep]
        d_idx = self.obs.idx(dams)
        if cand_idx.size == 0 or dams.size == 0:
            return out
        day = self.day(ctx.year)
        ref = self.ctx.reference(self.obs.breed_id, day)
        prof = load_profile(self.params.profile)
        cost = np.full((dams.size, cand_idx.size), HARD_COST)
        for k, di in enumerate(d_idx):
            if di < 0:
                continue
            f = self.ctx.rules.kinship_row(int(di))[cand_idx]
            mk = 0.5 * (ref.mk[cand_idx] + ref.mk[int(di)])
            ev = evaluate_candidates(self.ctx.rules, prof, int(di), cand_idx, day)
            cost[k] = np.where(ev.status == HARD_FAIL, HARD_COST, f + self.params.s4_lambda * mk)
        since = day - int(365.25 * 5)
        regs = float(self.ctx.rules.breed_births.count_before(np.array([0]), day, since)[0])
        exp_litter = max(1.0, float(self.ctx.rules.expected_litter_registered[0]))
        cap = max(1, round(self.params.fci_share * regs / 5.0 / exp_litter))
        cols = np.repeat(np.arange(cand_idx.size), cap)
        rows, j = linear_sum_assignment(cost[:, cols])
        ok = cost[rows, cols[j]] < HARD_COST
        out[rows[ok]] = cand_gid[cols[j][ok]]
        self.stats["s4_capacity"] = cap
        return out


def make_strategy(sid: str, params: StrategyParams, scoring: ScoringConfig) -> Any:
    if sid == "S0":
        return RandomStrategy()
    if sid == "S1":
        return MarketStrategy()
    if sid == "S2":
        return CompliantMarket(params, scoring)
    if sid == "S3":
        return Recommender(params, scoring)
    if sid == "S4":
        return CoordinatedPlanner(params, scoring)
    raise ValueError(f"unknown strategy {sid}")
