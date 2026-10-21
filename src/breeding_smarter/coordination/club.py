"""Club-level planning on a registry dataset (P12 task 12.12): CLI `bsm coordinate`, app page 7.

- Candidate sires: registered males of the breed alive on the date, of breeding age (species
  config), without limited registration (foreign AI records included), as `candidate_sires`,
  that are in breeding use: sired registered offspring in the last 5 years or have an HD
  screening result (most registered males are never bred). At most `MAX_SIRES` are planned (the
  lowest mean kinship first) to keep the solve interactive; an approximation of the club tool
  only, the experiments use the simulator's eligible sires.
- Auto dams: living domestic females of the breed aged 2 to 6 years without limited
  registration and with no litter whelped in the previous 10 months. If there are more than
  the breed's litters of the last 12 months, a seeded random sample of that size is planned
  (one season's worth of matings).
- Last year's matings (gain mode budget): distinct (sire, dam) pairs of registered animals born
  in the 12 months before the date.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from breeding_smarter.coordination.caps import mk_scaled_caps
from breeding_smarter.coordination.config import CoordinationConfig, load_coordination
from breeding_smarter.coordination.planner import SeasonPlan, plan_season
from breeding_smarter.matching.context import DAYS_PER_YEAR, DatasetContext
from breeding_smarter.pedigree.core import IntArray
from breeding_smarter.rules import day_number

AUTO_DAM_AGE = (2.0, 6.0)
AUTO_GAP_MONTHS = 10
ACTIVE_YEARS = 5
MAX_SIRES = 1500


def club_sires(
    ctx: DatasetContext, breed: str, day: int, active: bool = True, max_sires: int = MAX_SIRES
) -> IntArray:
    r, ped, sp = ctx.rules, ctx.ped, ctx.species
    b = ped.breed_codes.index(breed)
    m = (ped.sex == 1) & (ped.breed == b) & ~r.limited
    m &= (r.birth_day <= day) & (day < r.death_day)
    age = (day - r.birth_day) / DAYS_PER_YEAR
    m &= age >= sp.min_breeding_age_months.male.value / 12.0
    m &= age <= sp.max_breeding_age_years.male.value
    idx = np.flatnonzero(m).astype(np.int64)
    if active:
        since = day - int(ACTIVE_YEARS * DAYS_PER_YEAR)
        used = r.sire_offspring.count_before(idx, day, since) > 0
        idx = idx[used | (r.hd_grade[idx] >= 0)]
    if idx.size > max_sires:
        mk = ctx.reference(breed, day).mk[idx]
        idx = np.sort(idx[np.argsort(mk, kind="stable")[:max_sires]])
    return idx


def _litters_between(ctx: DatasetContext, dams: IntArray, lo: int, hi: int) -> IntArray:
    """Litters whelped in [lo, hi) per dam."""
    c = ctx.rules.dam_litters
    out = np.zeros(dams.size, np.int64)
    for k, d in enumerate(dams):
        v = c.values[c.ptr[d] : c.ptr[d + 1]]
        out[k] = int(((v >= lo) & (v < hi)).sum())
    return out


def auto_dams(
    ctx: DatasetContext, breed: str, day: int, rng: np.random.Generator | None = None
) -> IntArray:
    r, ped = ctx.rules, ctx.ped
    b = ped.breed_codes.index(breed)
    f = (ped.sex == 0) & (ped.breed == b) & ~r.limited & ~ctx.is_foreign
    f &= (r.birth_day <= day) & (day < r.death_day)
    age = (day - r.birth_day) / DAYS_PER_YEAR
    f &= (age >= AUTO_DAM_AGE[0]) & (age <= AUTO_DAM_AGE[1])
    cand = np.flatnonzero(f).astype(np.int64)
    gap = int(AUTO_GAP_MONTHS / 12 * DAYS_PER_YEAR)
    cand = cand[_litters_between(ctx, cand, day - gap, day + 1) == 0]
    all_f = np.flatnonzero((ped.sex == 0) & (ped.breed == b)).astype(np.int64)
    season = int(_litters_between(ctx, all_f, day - int(DAYS_PER_YEAR), day).sum())
    if 0 < season < cand.size:
        rng = rng or np.random.default_rng(0)
        cand = np.sort(rng.choice(cand, size=season, replace=False))
    return cand


def last_year_matings(ctx: DatasetContext, breed: str, day: int) -> tuple[IntArray, IntArray]:
    ped, r = ctx.ped, ctx.rules
    b = ped.breed_codes.index(breed)
    m = (ped.breed == b) & (r.birth_day >= day - int(DAYS_PER_YEAR)) & (r.birth_day < day)
    m &= (ped.sire >= 0) & (ped.dam >= 0)
    pairs = np.unique(np.c_[ped.sire[m], ped.dam[m]], axis=0)
    return pairs[:, 0].astype(np.int64), pairs[:, 1].astype(np.int64)


@dataclass
class ClubPlan:
    plan: SeasonPlan
    sires: pd.DataFrame  # one row per candidate sire
    matings: pd.DataFrame  # suggested allocation, one row per dam
    status_quo: pd.Series  # litters per sire in the last 12 months (for comparison)


def club_plan(
    ctx: DatasetContext,
    breed: str,
    date: str,
    dams: IntArray | None = None,
    mode: str = "ocs",
    delta_f: float | None = None,
    cfg: CoordinationConfig | None = None,
    profile: str = "hr_full",
    seed: int = 0,
    carrier_factor: float | None = None,
) -> ClubPlan:
    """Quotas (mode `ocs`, `cap`; `ocs` with `delta_f` = gain under that budget; optional carrier
    limit `carrier_factor`, as in E8/E9) and an MC1 allocation for the season's dams on `date`."""
    cfg = cfg or load_coordination()
    day = day_number(date)
    rng = np.random.default_rng(seed)
    sires = club_sires(ctx, breed, day)
    dams = auto_dams(ctx, breed, day, rng) if dams is None else np.asarray(dams, np.int64)
    control = "ocs_gain" if (mode == "ocs" and delta_f is not None) else mode
    prev = last_year_matings(ctx, breed, day) if control == "ocs_gain" else None
    plan = plan_season(
        ctx, breed, day, dams, sires, cfg, control, "mc1",
        profile=profile, delta_f=delta_f, prev_matings=prev, carrier_factor=carrier_factor,
        rng=rng,
    )  # fmt: skip
    ref = ctx.reference(breed, day)
    mk = ref.mk[sires]
    caps = mk_scaled_caps(
        mk, float(np.nanmean(mk)), cfg.cap_base_litters_per_year.value, cfg.cap_mk_scaling.value
    )
    since = day - int(DAYS_PER_YEAR)
    recent = ctx.rules.sire_litters.count_before(sires, day, since)
    r = ctx.rules
    table = pd.DataFrame(
        {
            "sire": r.reg_no[sires],
            "name": r.name[sires],
            "age": np.round((day - r.birth_day[sires]) / DAYS_PER_YEAR, 1),
            "MK": np.round(mk, 4),
            "EqG": np.round(ctx.eqg[sires], 2),
            "foreign": ctx.is_foreign[sires],
            "cap": caps,
            "quota": plan.quotas if plan.quotas is not None else np.full(sires.size, -1),
            "litters_last_12m": recent,
        }
    ).sort_values(["quota", "MK"], ascending=[False, True])
    a = plan.assignment
    ok = a >= 0
    coi = np.full(dams.size, np.nan)
    for k in np.flatnonzero(ok):
        coi[k] = r.kinship_row(int(dams[k]))[a[k]]
    matings = pd.DataFrame(
        {
            "dam": r.reg_no[dams],
            "dam_name": r.name[dams],
            "sire": np.where(ok, r.reg_no[np.maximum(a, 0)], ""),
            "sire_name": np.where(ok, r.name[np.maximum(a, 0)], ""),
            "predicted_COI": np.round(coi, 4),
        }
    )
    sq = pd.Series(recent, index=r.reg_no[sires], name="litters_last_12m")
    return ClubPlan(plan, table.reset_index(drop=True), matings, sq)
