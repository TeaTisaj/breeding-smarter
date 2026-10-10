"""Lifespan, death causes, breeding eligibility and whelping windows (P3 task 3.4)."""

from __future__ import annotations

import numpy as np

from breeding_smarter.config.models import SpeciesConfig
from breeding_smarter.sim.interfaces import GeneticsModel, SimSetup
from breeding_smarter.sim.state import DEATH_CAUSES, SimState

# Upper bound of gestation: a whelping at time t implies a mating no earlier than t - 70 days.
GESTATION_MAX_Y = 70 / 365.0
YEAR_END = 364 / 365.0


def sample_death(
    birth_year: np.ndarray, birth_doy: np.ndarray, species: SpeciesConfig, rng: np.random.Generator
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Weibull lifespan from birth; returns (death_year, death_doy, death_cause code)."""
    w = species.lifespan_weibull
    n = birth_year.shape[0]
    life = w.scale_years * rng.weibull(w.shape, n)
    t = birth_year + (birth_doy - 1) / 365.0 + life
    year = np.floor(t).astype(np.int64)
    doy = np.clip((t - year) * 365.0 + 1, 1, 365).astype(np.int64)
    same = year == birth_year
    doy = np.where(same, np.maximum(doy, birth_doy), doy)
    shares = species.death_cause_shares.value
    probs = np.array([shares.get(c, 0.0) for c in DEATH_CAUSES])
    cause = rng.choice(len(DEATH_CAUSES), size=n, p=probs / probs.sum())
    return year, doy, np.asarray(cause, dtype=np.int64)


def whelp_window(
    state: SimState, setup: SimSetup, gids: np.ndarray, year: int, sex: int
) -> tuple[np.ndarray, np.ndarray]:
    """Earliest and latest whelping time (fractional years) in `year` for each animal.

    A whelping at time t implies a mating in [t - 70 days, t]. The earliest t keeps the
    parent at or above its minimum breeding age and (dams) the minimum interval since the last
    whelping at any possible mating date; the latest keeps the parent at or below its maximum
    breeding age at mating. Empty windows have `lo > hi`.
    """
    a = state.animals
    sp = setup.species
    key = "F" if sex == 0 else "M"
    birth_t = a.birth_year[gids] + (a.birth_doy[gids] - 1) / 365.0
    lo = np.maximum(year, birth_t + sp.min_breeding_age_months.for_sex(key) / 12 + GESTATION_MAX_Y)
    hi = np.minimum(year + YEAR_END, birth_t + sp.max_breeding_age_years.for_sex(key))
    if sex == 0:
        gap = np.array([b.reproduction.min_months_between_litters.value for b in setup.breeds])
        g = gap[a.breed[gids]] / 12.0
        lo = np.maximum(lo, a.last_whelp_t[gids] + g + GESTATION_MAX_Y)
    return lo, hi


def eligible(
    state: SimState,
    setup: SimSetup,
    breed: int,
    subpop: int,
    year: int,
    sex: int,
    genetics: GeneticsModel,
    candidates: bool = True,
) -> np.ndarray:
    """Gids able to breed in `year`: alive all year, breeding candidate (or, with
    `candidates=False`, non-candidates for recruitment), non-empty whelping window, litter limit
    (dams) and health eligibility from the genetics model."""
    a = state.animals
    base = (a.breed == breed) & (a.subpop == subpop) & (a.sex == sex)
    base &= a.is_candidate if candidates else ~a.is_candidate
    base &= (a.birth_year < year) & (a.death_year > year)
    idx = np.flatnonzero(base)
    if idx.size == 0:
        return idx
    lo, hi = whelp_window(state, setup, idx, year, sex)
    ok = lo <= hi
    if sex == 0:
        ok &= a.litters_count[idx] < setup.breeds[breed].reproduction.max_litters_per_dam.value
    idx = idx[ok]
    if idx.size:
        idx = idx[genetics.is_eligible(state, idx, year)]
    return idx
