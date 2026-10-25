"""One planning round: sire quotas for the season, then mate allocation (P12 task 12.6).

Contribution control (`control`):

| control | sire quotas |
|---|---|
| none | unlimited (every sire may take every dam) |
| mkx | sires with mean kinship (MK) above the candidates' mean are excluded [windig-2013] |
| cap | MK-scaled per-year caps (D9), no optimisation |
| ocs | conservation OCS (min c'Kc) under caps, age and depth constraints, then Sainte-Laguë |
| ocs_gain | max HD EBV under the yearly kinship budget (D5 to D8), then Sainte-Laguë |

Mate allocation (`mating`): `mc1` minimum total pair kinship + w x P(affected puppy)
[sonesson-meuwissen-2000], `random` random within quotas, `none` quotas only (the product mode
S3q lets breeders choose within them). HARD-rule pairs are never allocated. With `mkx` and
`none` (E11 `S3q-mkx`) excluded sires get quota 0 and the others can take every dam.

`carrier_factor` (beta, OCS controls only, E8): per tested locus the season's planned
risk-allele transmission of the sires is at most beta x its mean over the candidate sires;
`carrier_free_only` (E11) applies it to the litters not fixed by non-adopters only.

Dams are registry indices; -1 marks a dam without a registry record (treated as an unrelated,
non-inbred animal with unknown genotypes and no rule checks). Kinship comes from `kin`
(default: recorded pedigree); the oracle arm passes true-pedigree kinship.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from numpy.typing import NDArray

from breeding_smarter.coordination.allocation import FORBIDDEN, assign_mc1, assign_random
from breeding_smarter.coordination.caps import mk_scaled_caps
from breeding_smarter.coordination.config import CoordinationConfig
from breeding_smarter.coordination.ocs import (
    OCSProblem,
    expected_coancestry,
    solve_conservation,
    solve_gain,
)
from breeding_smarter.coordination.quotas import sainte_lague
from breeding_smarter.coordination.targets import estimate_generation_interval, next_budget
from breeding_smarter.matching.components import transmission
from breeding_smarter.matching.context import DatasetContext
from breeding_smarter.pedigree.core import FloatArray, IntArray
from breeding_smarter.pedigree.kinship import kinship_matrix
from breeding_smarter.rules import day_number, evaluate_candidates, load_profile
from breeding_smarter.rules.engine import HARD_FAIL

CONTROLS = ("none", "mkx", "cap", "ocs", "ocs_gain")
MATINGS = ("random", "mc1", "none")
Kin = Callable[[IntArray], FloatArray]


@dataclass
class SeasonPlan:
    sires: IntArray  # candidate sires (registry idx)
    quotas: IntArray | None  # litters per candidate sire for the free dams; None = unlimited
    assignment: IntArray  # registry idx of the sire per dam (-1 = none); fixed dams kept
    diagnostics: dict[str, Any] = field(default_factory=dict)


def recorded_kinship(ctx: DatasetContext) -> Kin:
    def kin(idx: IntArray) -> FloatArray:
        return kinship_matrix(ctx.ped, ctx.D, np.asarray(idx, np.int64))

    return kin


def _kinship_with_unknown(kin: Kin, idx: IntArray) -> FloatArray:
    """Kinship among `idx`; entries with idx -1 are unrelated, non-inbred (self 1/2)."""
    idx = np.asarray(idx, np.int64)
    K = np.zeros((idx.size, idx.size))
    known = np.flatnonzero(idx >= 0)
    if known.size:
        K[np.ix_(known, known)] = kin(idx[known])
    unk = np.flatnonzero(idx < 0)
    K[unk, unk] = 0.5
    return K


def past_coancestry(kin: Kin, sires: IntArray, dams: IntArray) -> float:
    """`c'Kc` of realised matings (pairs with both parents recorded)."""
    ok = (np.asarray(sires) >= 0) & (np.asarray(dams) >= 0)
    s, d = np.asarray(sires)[ok], np.asarray(dams)[ok]
    if s.size == 0:
        return float("nan")
    us, counts = np.unique(s, return_counts=True)
    K = kin(np.r_[us, d])
    return expected_coancestry(K, counts.astype(float), int(d.size))


def pair_inputs(
    ctx: DatasetContext,
    sires: IntArray,
    dams: IntArray,
    day: int,
    profile: str,
) -> tuple[NDArray[np.bool_], FloatArray]:
    """(forbidden, P(any affected puppy)) for dams x sires."""
    breed = ctx.breed_of(int(sires[0])) if sires.size else ""
    ref = ctx.reference(breed, day)
    prof = load_profile(profile)
    forb = np.zeros((dams.size, sires.size), bool)
    for k, d in enumerate(dams):
        if d >= 0:
            forb[k] = evaluate_candidates(ctx.rules, prof, int(d), sires, day).status == HARD_FAIL
    q = ref.allele_freq
    t_s = transmission(ctx.geno[sires], q)
    geno_d = np.where((dams >= 0)[:, None], ctx.geno[np.maximum(dams, 0)], -1).astype(np.int8)
    t_d = transmission(geno_d, q)
    p_aff = t_d[:, None, :] * t_s[None, :, :] * ctx.penetrance[None, None, :]
    p_any = 1.0 - np.prod(1.0 - p_aff, axis=2) if p_aff.shape[2] else np.zeros(forb.shape)
    return forb, p_any


def _merit(ctx: DatasetContext, sires: IntArray) -> FloatArray:
    e = ctx.ebv_index[sires].astype(float)
    if np.isfinite(e).sum() < 2:
        return np.zeros(sires.size)
    z = (e - np.nanmean(e)) / (np.nanstd(e) or 1.0)
    return np.asarray(np.nan_to_num(z, nan=0.0))


def _unlimited(
    cost: FloatArray, allowed: NDArray[np.bool_], mating: str, rng: np.random.Generator
) -> IntArray:
    """Per-dam choice without quotas (sire position per dam, -1 if nothing allowed)."""
    out = np.full(cost.shape[0], -1, np.int64)
    for k in range(cost.shape[0]):
        ok = np.flatnonzero(allowed[k])
        if ok.size == 0:
            continue
        if mating == "mc1":
            out[k] = ok[np.argmin(cost[k, ok])]
        else:
            out[k] = ok[rng.integers(ok.size)]
    return out


def plan_season(
    ctx: DatasetContext,
    breed: str,
    day: int,
    dams: IntArray,
    sires: IntArray,
    cfg: CoordinationConfig,
    control: str,
    mating: str,
    *,
    profile: str = "exp_pairing",
    kin: Kin | None = None,
    delta_f: float | None = None,
    fixed: dict[int, int] | None = None,
    prev_matings: tuple[IntArray, IntArray] | None = None,
    L: float | None = None,
    carrier_factor: float | None = None,
    carrier_free_only: bool = False,
    rng: np.random.Generator | None = None,
) -> SeasonPlan:
    """Quotas and allocation for the season's `dams` (positions in `fixed` are already mated:
    position -> sire registry idx, -1 if the sire has no record)."""
    if control not in CONTROLS or mating not in MATINGS:
        raise ValueError(f"unknown control/mating {control!r}/{mating!r}")
    rng = rng or np.random.default_rng(0)
    kin = kin or recorded_kinship(ctx)
    fixed = fixed or {}
    dams = np.asarray(dams, np.int64)
    sires = np.asarray(sires, np.int64)
    n_d, m = dams.size, sires.size
    diag: dict[str, Any] = {"control": control, "mating": mating, "n_dams": n_d, "n_sires": m}
    assignment = np.full(n_d, -1, np.int64)
    for k_fixed, s in fixed.items():
        assignment[k_fixed] = s
    free = np.array([k for k in range(n_d) if k not in fixed], dtype=np.int64)
    if m == 0 or n_d == 0:
        return SeasonPlan(sires, np.zeros(m, np.int64), assignment, diag)

    # extra parents: sires of fixed matings that are not candidates (recorded only)
    extra = np.array(
        sorted({s for s in fixed.values() if s >= 0 and s not in set(sires.tolist())}),
        dtype=np.int64,
    )
    all_sires = np.r_[sires, extra]
    K = _kinship_with_unknown(kin, np.r_[all_sires, dams])
    M = all_sires.size
    K_pair = K[M:, :m]  # dams x candidate sires
    forb, p_any = pair_inputs(ctx, sires, dams[free], day, profile)
    ref = ctx.reference(breed, day)
    mk = ref.mk[sires]
    mk_ref = float(np.nanmean(mk))
    w_h = cfg.health_weight_in_allocation.value
    cost = np.where(forb, FORBIDDEN, K_pair[free] + w_h * p_any)

    quotas: IntArray | None = None
    allowed = ~forb
    if control == "mkx":
        keep = ~(mk > mk_ref)
        allowed = allowed & keep[None, :]
        diag["n_sires_with_quota"] = int(keep.sum())
        if mating == "none":
            quotas = np.where(keep, free.size, 0).astype(np.int64)
    elif control == "cap":
        caps = mk_scaled_caps(
            mk, mk_ref, cfg.cap_base_litters_per_year.value, cfg.cap_mk_scaling.value
        )
        quotas = caps
        if quotas.sum() < free.size:
            q = sainte_lague(caps.astype(float), free.size, caps, 0.0, np.argsort(mk))
            quotas, diag["relaxed_caps"] = caps + np.maximum(q.quota - caps, 0), q.relaxed
    elif control in ("ocs", "ocs_gain"):
        quotas = _ocs_quotas(
            ctx, cfg, control, sires, all_sires, dams, K, mk, mk_ref, fixed, free, day,
            kin, delta_f, prev_matings, L, diag, carrier_factor, ref.allele_freq,
            carrier_free_only,
        )  # fmt: skip
    if control == "none":
        diag["n_sires_with_quota"] = m
    if quotas is not None:
        diag["n_sires_with_quota"] = int((quotas > 0).sum())

    if mating != "none" and free.size:
        if quotas is None:
            pos = _unlimited(cost, allowed, mating, rng)
        else:
            c = np.where(allowed, cost, FORBIDDEN)
            if mating == "mc1":
                pos = assign_mc1(c, np.zeros_like(c), ~allowed, quotas, 0.0)
            else:
                pos = assign_random(quotas, ~allowed, rng)
            miss = np.flatnonzero(pos < 0)
            if miss.size:  # no allowed seat left: least-cost / random allowed sire (overflow)
                pos[miss] = _unlimited(cost[miss], allowed[miss], mating, rng)
            diag["overflow"] = int(miss.size)
        assignment[free] = np.where(pos >= 0, sires[np.maximum(pos, 0)], -1)
        diag["unassigned"] = int((pos < 0).sum())
    return SeasonPlan(sires, quotas, assignment, diag)


def _ocs_quotas(
    ctx: DatasetContext,
    cfg: CoordinationConfig,
    control: str,
    sires: IntArray,
    all_sires: IntArray,
    dams: IntArray,
    K: FloatArray,
    mk: FloatArray,
    mk_ref: float,
    fixed: dict[int, int],
    free: IntArray,
    day: int,
    kin: Kin,
    delta_f: float | None,
    prev_matings: tuple[IntArray, IntArray] | None,
    L: float | None,
    diag: dict[str, Any],
    carrier_factor: float | None = None,
    allele_freq: FloatArray | None = None,
    carrier_free_only: bool = False,
) -> IntArray:
    m, M, n_d = sires.size, all_sires.size, dams.size
    # dams whose fixed sire has no record leave the problem (their contribution is unknown)
    in_prob = np.array([fixed.get(k, 0) >= 0 for k in range(n_d)])
    dpos = np.flatnonzero(in_prob)
    Kp = K[np.ix_(np.r_[np.arange(M), M + dpos], np.r_[np.arange(M), M + dpos])]
    fixed_l = np.zeros(M)
    pos_of = {int(s): k for k, s in enumerate(all_sires)}
    for s in fixed.values():
        if s >= 0:
            fixed_l[pos_of[int(s)]] += 1
    cap_base = cfg.cap_base_litters_per_year.value
    caps = np.r_[
        mk_scaled_caps(mk, mk_ref, cap_base, cfg.cap_mk_scaling.value).astype(float),
        np.zeros(M - m),
    ]
    if caps.sum() + fixed_l.sum() < dpos.size:  # not enough room: lift caps uniformly
        caps[:m] += np.ceil((dpos.size - caps.sum() - fixed_l.sum()) / m)
        diag["relaxed_caps"] = True
    year = int(np.datetime64(day, "D").astype("datetime64[Y]").astype(np.int64)) + 1970
    jan1 = day_number(f"{year}-01-01")
    age = np.r_[np.floor(ctx.age_years(sires, jan1)).astype(np.int64), np.full(M - m, -1)]
    eqg = np.r_[ctx.eqg[sires], ctx.eqg[all_sires[m:]] if m < M else np.zeros(0)]
    exp_reg = float(ctx.rules.expected_litter_registered[int(ctx.ped.breed[sires[0]])])
    n_new = dpos.size * max(exp_reg, 1.0) if cfg.small_cohort_term.value else 0.0
    carrier_t = carrier_bound = None
    if carrier_factor is not None and allele_freq is not None and ctx.geno.shape[1]:
        t = transmission(ctx.geno[all_sires], allele_freq)
        mean_t = np.nanmean(t[:m], axis=0)
        loci = np.flatnonzero(mean_t > 0)
        if loci.size:
            carrier_t = np.nan_to_num(t[:, loci])
            carrier_bound = carrier_factor * mean_t[loci]
    prob = OCSProblem(
        K=Kp,
        n_dams=int(dpos.size),
        caps=caps,
        age_class=age,
        eqg=eqg,
        merit=np.r_[_merit(ctx, sires), np.zeros(M - m)],
        fixed_sire_litters=fixed_l,
        n_newborn=n_new,
        n_age_classes=cfg.youngest_age_classes_required.value,
        depth=cfg.depth_constraint.value,
        carrier_t=carrier_t,
        carrier_bound=carrier_bound,
        carrier_free_only=carrier_free_only,
    )
    solver = cfg.solver.value
    if control == "ocs":
        res = solve_conservation(prob, solver)
    else:
        dF = cfg.delta_f_default.value if delta_f is None else delta_f
        if L is None:
            L = estimate_generation_interval(
                ctx.ped, year - 1, cfg.generation_interval_window_years.value
            )
        c_now = past_coancestry(kin, *prev_matings) if prev_matings is not None else np.nan
        if not np.isfinite(c_now):
            c_now = solve_conservation(prob, solver).coancestry
        budget = next_budget(c_now, dF, L)
        res = solve_gain(prob, budget, solver)
        diag.update(C_now=c_now, L=L, delta_f=dF, budget=budget, C_min=res.c_min)
    diag.update(
        achieved_C=res.coancestry,
        infeasible=res.infeasible,
        solver_seconds=res.seconds,
        relaxed_constraints=",".join(res.relaxed),
        solver_status=res.status,
    )
    if carrier_t is not None:
        diag["carrier_relaxed"] = float("carrier" in res.relaxed)
        diag["carrier_planned"] = float(np.mean(res.litters @ carrier_t / prob.n_dams))
    free_l = np.maximum(res.litters[:m] - fixed_l[:m], 0.0)
    q = sainte_lague(
        free_l,
        int(free.size),
        np.maximum(caps[:m] - fixed_l[:m], 0).astype(np.int64),
        cfg.min_expected_litters.value,
        np.argsort(mk),
    )
    diag["relaxed_caps"] = int(diag.get("relaxed_caps", 0)) + q.relaxed
    return q.quota
