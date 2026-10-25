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
| CC-<control>-<mating>[-oracle] | P12 coordinated sire use: contribution control none, mkx,
       cap, ocs or gainNNN (OCS under dF = NNN / 10^4 per generation) x mate allocation rand or
       mc1; `-oracle` plans on true-pedigree kinship (`coordination.planner`) |
| S3q | P12 product mode: OCS quotas for the season, shared booking ledger, each adopting dam
       picks among the top 3 of `rank_fast` restricted to sires with quota left; non-adopters
       follow S2 first and their sires enter OCS as fixed contributions |
| S3q-gainNNN, S3q[-gainNNN]-cBBB | E8: S3q with quotas from gain OCS (dF = NNN / 10^4) and/or a
       carrier limit (planned risk-allele transmission <= BBB / 100 x candidate mean per locus) |
| S3q...-hc, S3q...-oracle | E9/E10: carrier x carrier pairs HARD-blocked; true kinship |
| S3q-cap, S3q-mkx | E11: the recommender inside MK-scaled caps or MK exclusion instead of OCS |
| S3q...-cBBBf | E11: carrier limit on the adopters' own litters only |
| S3-t1, S3-u5, S3q...-t1, S3q...-u5 | E11: breeders take the top sire, or one of the top 5 |

Candidate sires are the simulator's eligible domestic males plus eligible foreign males that
already have a registry record (a breeder can only evaluate dogs with a record). The market
part of S1/S2 also uses unregistered foreign AI sires, as in the history.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field, replace
from typing import Any, NamedTuple

import numpy as np
from scipy.optimize import linear_sum_assignment

from breeding_smarter.coordination.config import CoordinationConfig, load_coordination
from breeding_smarter.coordination.ledger import BookingLedger
from breeding_smarter.coordination.planner import Kin, SeasonPlan, plan_season, recorded_kinship
from breeding_smarter.experiments.observed import ObservedRegistry
from breeding_smarter.experiments.truth_kinship import TrueKinship
from breeding_smarter.matching.config import ScoringConfig
from breeding_smarter.matching.context import DatasetContext
from breeding_smarter.matching.recommend import rank_fast
from breeding_smarter.pedigree.core import IntArray
from breeding_smarter.rules import day_number, evaluate_candidates, load_profile
from breeding_smarter.rules.engine import HARD_FAIL
from breeding_smarter.sim.interfaces import YearContext
from breeding_smarter.sim.market import MarketStrategy, sample_rows
from breeding_smarter.sim.state import DOMESTIC

HARD_COST = 1e6
FREEDOM = {"t1": (1.0,), "u5": (0.2,) * 5}  # E11 breeder freedom (assumptions, plan 16 §3)


@dataclass
class StrategyParams:
    profile: str = "exp_pairing"
    coi_cap: float = 0.065
    top_probs: tuple[float, ...] = (0.5, 0.3, 0.2)
    adoption: float = 1.0
    s4_lambda: float = 1.0
    fci_share: float = 0.05
    coordination: str = "default"


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


class CoordinatedBase:
    """Shared P12 plumbing: candidates, last year's matings, kinship source, diagnostics."""

    oracle: bool = False
    truth: TrueKinship | None = None
    last_plan: SeasonPlan | None = None
    obs: ObservedRegistry | None
    ctx: DatasetContext | None

    def coordination(self) -> CoordinationConfig:
        cfg = self.__dict__.get("_coord")
        if cfg is None:
            cfg = load_coordination(self.params.coordination)  # type: ignore[attr-defined]
            self.__dict__["_coord"] = cfg
        return cfg

    def kin(self, yc: YearContext) -> Kin:
        assert self.obs is not None and self.ctx is not None
        if not self.oracle:
            return recorded_kinship(self.ctx)
        if self.truth is None:
            self.truth = TrueKinship(yc.state, yc.breed)
        else:
            self.truth.update(yc.state)
        truth, obs = self.truth, self.obs

        def kin(idx: IntArray) -> np.ndarray:
            return truth.kinship(obs.gid[np.asarray(idx, np.int64)])

        return kin

    def prev_matings(self, yc: YearContext) -> tuple[IntArray, IntArray]:
        """Registry idx of (sire, dam) of last year's recorded domestic matings."""
        assert self.obs is not None
        L = yc.state.litters
        sel = np.flatnonzero(
            (L.mating_year == yc.year - 1)
            & (L.breed == yc.breed)
            & (L.subpop == DOMESTIC)
            & L.registered
        )
        return self.obs.idx(L.sire[sel]), self.obs.idx(L.dam[sel])


class Coordinated(CoordinatedBase, ObservedStrategy):
    """CC-* arms: `plan_season` once per year with the year's dams and candidate sires."""

    def __init__(
        self,
        params: StrategyParams,
        scoring: ScoringConfig,
        control: str,
        mating: str,
        oracle: bool = False,
        delta_f: float | None = None,
        name: str = "CC",
    ):
        ObservedStrategy.__init__(self, params, scoring)
        self.control, self.mating, self.oracle, self.delta_f = control, mating, oracle, delta_f
        self.name = name
        self.truth = None
        self.last_plan = None

    def plan_matings(self, dams, sires, ctx, rng):
        assert self.obs is not None and self.ctx is not None
        dams = np.asarray(dams, np.int64)
        out = np.full(dams.size, -1, np.int64)
        cand_gid, cand_idx = self.candidates(sires, ctx)
        keep = cand_idx >= 0
        cand_gid, cand_idx = cand_gid[keep], cand_idx[keep]
        if cand_idx.size == 0 or dams.size == 0:
            return out
        plan = plan_season(
            self.ctx,
            self.obs.breed_id,
            self.day(ctx.year),
            self.obs.idx(dams),
            cand_idx,
            self.coordination(),
            self.control,
            self.mating,
            profile=self.params.profile,
            kin=self.kin(ctx),
            delta_f=self.delta_f,
            prev_matings=self.prev_matings(ctx) if self.control == "ocs_gain" else None,
            rng=rng,
        )
        gid_of = dict(zip(cand_idx.tolist(), cand_gid.tolist(), strict=True))
        out = np.array([gid_of[int(s)] if s >= 0 else -1 for s in plan.assignment], np.int64)
        self.last_plan = plan
        return out


class RecommenderWithQuotas(CoordinatedBase, Recommender):
    """S3q: the recommender inside OCS quotas (shared booking ledger)."""

    name = "S3q"

    def __init__(
        self,
        params: StrategyParams,
        scoring: ScoringConfig,
        control: str = "ocs",
        delta_f: float | None = None,
        carrier_factor: float | None = None,
        name: str = "S3q",
        carrier_free_only: bool = False,
    ):
        Recommender.__init__(self, params, scoring)
        self.control, self.delta_f, self.carrier_factor = control, delta_f, carrier_factor
        self.carrier_free_only = carrier_free_only
        self.name = name
        self.truth = None
        self.last_plan = None

    def plan_matings(self, dams, sires, ctx, rng):
        assert self.obs is not None and self.ctx is not None
        dams = np.asarray(dams, np.int64)
        out = np.full(dams.size, -1, np.int64)
        adopt = rng.random(dams.size) < self.params.adoption
        if (~adopt).any():
            out[~adopt] = CompliantMarket.plan_matings(self, dams[~adopt], sires, ctx, rng)
        cand_gid, cand_idx = self.candidates(sires, ctx)
        keep = cand_idx >= 0
        cand_gid, cand_idx = cand_gid[keep], cand_idx[keep]
        if cand_idx.size == 0 or not adopt.any():
            return out
        # OCS over adopters plus mated non-adopters (their sires are fixed contributions)
        in_plan = adopt | (out >= 0)
        pos = np.flatnonzero(in_plan)
        d_idx = self.obs.idx(dams[pos])
        fixed = {
            k: int(self.obs.idx_of.get(int(out[p]), -1)) for k, p in enumerate(pos) if not adopt[p]
        }
        day = self.day(ctx.year)
        plan = plan_season(
            self.ctx,
            self.obs.breed_id,
            day,
            d_idx,
            cand_idx,
            self.coordination(),
            self.control,
            "none",
            profile=self.params.profile,
            kin=self.kin(ctx),
            delta_f=self.delta_f,
            fixed=fixed,
            prev_matings=self.prev_matings(ctx) if self.control == "ocs_gain" else None,
            carrier_factor=self.carrier_factor,
            carrier_free_only=self.carrier_free_only,
            rng=rng,
        )
        assert plan.quotas is not None
        ledger = BookingLedger(cand_idx, plan.quotas)
        gid_of = dict(zip(cand_idx.tolist(), cand_gid.tolist(), strict=True))
        self.ctx.extra_offspring = np.zeros(self.obs.n)
        exp_litter = float(self.ctx.rules.expected_litter_registered[0])
        probs = np.array(self.params.top_probs)
        overflow = 0
        for k in rng.permutation(np.flatnonzero(adopt)):
            di = int(self.obs.idx_of.get(int(dams[k]), -1))
            if di < 0:
                continue
            avail = ledger.available()
            ranked = np.zeros(0, np.int64)
            if avail.size:
                ranked, _ = rank_fast(
                    self.ctx, di, day, self.params.profile, self.scoring, candidates=avail
                )
            booked = ranked.size > 0
            if not booked:  # nothing allowed with quota left: best allowed sire (overflow)
                ranked, _ = rank_fast(
                    self.ctx, di, day, self.params.profile, self.scoring, candidates=cand_idx
                )
                if ranked.size == 0:
                    continue
                overflow += 1
            top = ranked[: probs.size]
            p = probs[: top.size] / probs[: top.size].sum()
            choice = int(top[rng.choice(top.size, p=p)])
            if booked:
                ledger.book(choice)
            out[k] = gid_of[choice]
            self.ctx.extra_offspring[choice] += exp_litter
        self.ctx.extra_offspring = None
        plan.diagnostics["overflow"] = overflow
        plan.diagnostics["adopters"] = int(adopt.sum())
        self.last_plan = plan
        return out


def parse_cc(sid: str) -> tuple[str, str, bool, float | None]:
    """`CC-<control>-<mating>[-oracle]` -> (control, mating, oracle, delta_f)."""
    parts = sid.split("-")
    if len(parts) not in (3, 4) or parts[0] != "CC" or (len(parts) == 4 and parts[3] != "oracle"):
        raise ValueError(f"bad coordinated strategy id {sid!r}")
    control, mating = parts[1], {"rand": "random", "mc1": "mc1"}[parts[2]]
    delta_f = None
    if control.startswith("gain"):
        delta_f = int(control[4:]) / 1e4
        control = "ocs_gain"
    return control, mating, len(parts) == 4, delta_f


class S3qSpec(NamedTuple):
    control: str  # "ocs", "ocs_gain", "cap" or "mkx"
    delta_f: float | None
    carrier_factor: float | None
    hard_carrier: bool = False
    oracle: bool = False
    carrier_free_only: bool = False
    freedom: str | None = None  # key of FREEDOM; None = params.top_probs


def parse_s3q(sid: str) -> S3qSpec:
    """`S3q[-cap|-mkx|-gainNNN][-cBBB[f]][-hc][-oracle][-t1|-u5]` -> S3qSpec.

    `-hc` HARD-blocks carrier x carrier pairs (profile `exp_pairing_hard_carrier`; Marija
    Perkovic's E8 design, branch `feature/e8-hips-quotas`); `-oracle` plans on true-pedigree
    kinship (as `CC-ocs-mc1-oracle`). E11: `-cap`/`-mkx` replace OCS by the CC controls (no
    carrier limit, which needs OCS), `f` bounds only the adopters' litters, `-t1`/`-u5` set
    breeder freedom."""
    m = re.fullmatch(
        r"S3q(?:-(cap|mkx)|-gain(\d{3}))?(?:-c(\d{3})(f)?)?(-hc)?(-oracle)?(?:-(t1|u5))?", sid
    )
    if m is None:
        raise ValueError(f"bad S3q strategy id {sid!r}")
    simple, gain, carrier, free_only, hc, oracle, freedom = m.groups()
    if simple and carrier:
        raise ValueError(f"carrier limit needs OCS quotas: {sid!r}")
    return S3qSpec(
        simple or ("ocs_gain" if gain else "ocs"),
        int(gain) / 1e4 if gain else None,
        int(carrier) / 100 if carrier else None,
        hc is not None,
        oracle is not None,
        free_only is not None,
        freedom,
    )


def make_strategy(sid: str, params: StrategyParams, scoring: ScoringConfig) -> Any:
    if sid == "S0":
        return RandomStrategy()
    if sid == "S1":
        return MarketStrategy()
    if sid == "S2":
        return CompliantMarket(params, scoring)
    if sid == "S3":
        return Recommender(params, scoring)
    if sid.startswith("S3-") and sid[3:] in FREEDOM:  # E11 breeder freedom
        return Recommender(replace(params, top_probs=FREEDOM[sid[3:]]), scoring)
    if sid == "S3hc":  # E3 (b): carrier x carrier HARD-blocked
        return Recommender(replace(params, profile="exp_pairing_hard_carrier"), scoring)
    if sid == "S3xc":  # E3 (c): all known carriers excluded (genetics eligibility, runner)
        return Recommender(params, scoring)
    if sid == "S4":
        return CoordinatedPlanner(params, scoring)
    if sid == "S3q" or sid.startswith("S3q-"):
        spec = parse_s3q(sid)
        if spec.hard_carrier:
            params = replace(params, profile="exp_pairing_hard_carrier")
        if spec.freedom:
            params = replace(params, top_probs=FREEDOM[spec.freedom])
        s3q = RecommenderWithQuotas(
            params, scoring, spec.control, spec.delta_f, spec.carrier_factor, name=sid,
            carrier_free_only=spec.carrier_free_only,
        )  # fmt: skip
        s3q.oracle = spec.oracle
        return s3q
    if sid.startswith("CC-"):
        control, mating, oracle, delta_f = parse_cc(sid)
        return Coordinated(params, scoring, control, mating, oracle, delta_f, name=sid)
    raise ValueError(f"unknown strategy {sid}")
