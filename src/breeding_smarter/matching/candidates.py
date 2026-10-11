"""Candidate sires for a dam on a mating date (P7 task 7.2)."""

from __future__ import annotations

import numpy as np

from breeding_smarter.matching.context import DatasetContext
from breeding_smarter.pedigree.core import IntArray
from breeding_smarter.sim.kennels import haversine_km


def candidate_sires(
    ctx: DatasetContext,
    dam: int,
    day: int,
    max_distance_km: float | None = None,
    include_foreign: bool = True,
) -> IntArray:
    """Registered males of the dam's breed, alive on the mating date, of breeding age
    (species config), without limited registration. `max_distance_km` limits domestic sires by
    the haversine distance between owners; foreign records (AI sires) are kept if
    `include_foreign`."""
    r = ctx.rules
    ped = ctx.ped
    sp = ctx.species
    m = (ped.sex == 1) & (ped.breed == ped.breed[dam]) & ~r.limited
    m &= (r.birth_day <= day) & (day < r.death_day)
    age = (day - r.birth_day) / 365.25
    m &= age >= sp.min_breeding_age_months.male.value / 12.0
    m &= age <= sp.max_breeding_age_years.male.value
    foreign = ctx.is_foreign
    if not include_foreign:
        m &= ~foreign
    idx = np.flatnonzero(m)
    if max_distance_km is not None and idx.size:
        d = haversine_km(
            np.full(idx.size, ctx.lat[dam]),
            np.full(idx.size, ctx.lon[dam]),
            ctx.lat[idx],
            ctx.lon[idx],
        )
        keep = (d <= max_distance_km) | (foreign[idx] & include_foreign)
        idx = idx[keep]
    return idx.astype(np.int64)
