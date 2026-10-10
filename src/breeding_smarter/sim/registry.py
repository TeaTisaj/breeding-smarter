"""Registry founding, imports and foreign stub pedigrees (P3 task 3.7)."""

from __future__ import annotations

import numpy as np

from breeding_smarter.sim.interfaces import GeneticsModel, SimSetup
from breeding_smarter.sim.kennels import pick_kennels
from breeding_smarter.sim.state import DOMESTIC, FOREIGN, SimState

IMPORT_AGE_YEARS = (1, 4)  # young adults (assumption)


def found_registry(state: SimState, setup: SimSetup, year: int) -> int:
    """Register every domestic animal alive on Jan 1 of `year`.

    Animals of breeding age become founders with unknown parents; younger animals keep links
    to their parents (which are registered too if they are alive). Returns the count.
    """
    a = state.animals
    alive = (a.subpop == DOMESTIC) & (a.birth_year < year) & (a.death_year >= year)
    idx = np.flatnonzero(alive)
    age = year - (a.birth_year[idx] + (a.birth_doy[idx] - 1) / 365.0)
    sp = setup.species.min_breeding_age_months
    min_age = np.where(a.sex[idx] == 0, sp.female.value, sp.male.value) / 12.0
    adult = age >= min_age
    a.registered[idx] = True
    a.reg_year[idx] = year
    a.reg_parents_known[idx[adult]] = False
    return int(idx.size)


def register_with_ancestors(
    state: SimState, root: int, depth: int, year: int, root_is_stub: bool
) -> int:
    """Register `root` and its ancestors up to `depth` generations as pedigree records.

    Ancestors registered here are FOREIGN stubs; animals at generation `depth` get unknown
    parents. Animals already registered keep their record (first registration wins), except
    the root, whose record is refreshed. Returns the number of newly registered animals.
    """
    a = state.animals
    new = 0
    stack = [(int(root), 0)]
    seen: set[int] = set()
    while stack:
        g, lvl = stack.pop()
        if g in seen:
            continue
        seen.add(g)
        if g != root and a.registered[g]:
            continue
        if not a.registered[g]:
            new += 1
            a.reg_year[g] = year
        a.registered[g] = True
        a.foreign_stub[g] = root_is_stub if g == root else True
        a.reg_parents_known[g] = lvl < depth
        if lvl < depth:
            for p in (int(a.sire[g]), int(a.dam[g])):
                if p >= 0:
                    stack.append((p, lvl + 1))
    return new


def import_animals(
    state: SimState,
    setup: SimSetup,
    breed: int,
    year: int,
    n: int,
    genetics: GeneticsModel,
    rng: np.random.Generator,
    sex: int | None = None,
    alive_through: int | None = None,
) -> np.ndarray:
    """Move up to `n` young foreign breeding candidates (optionally of one sex) into domestic
    breeder kennels. In the registry era they are registered with stub pedigrees of
    `import_pedigree_depth` generations and DNA tested on entry (via the genetics model)."""
    a = state.animals
    lo, hi = IMPORT_AGE_YEARS
    mask = (
        (a.breed == breed)
        & (a.subpop == FOREIGN)
        & a.is_candidate
        & (a.birth_year >= year - hi)
        & (a.birth_year <= year - lo)
        & (a.death_year > (alive_through if alive_through is not None else year + 1))
    )
    if sex is not None:
        mask &= a.sex == sex
    pool = np.flatnonzero(mask)
    if n <= 0 or pool.size == 0:
        return np.zeros(0, np.int64)
    gids = np.sort(rng.choice(pool, size=min(n, pool.size), replace=False))
    a.subpop[gids] = DOMESTIC
    a.kennel[gids] = pick_kennels(state, breed, DOMESTIC, gids.size, rng)
    a.import_flag[gids] = True
    a.import_year[gids] = year
    if year >= setup.sim.registry_start_year:
        depth = setup.breeds[breed].market.import_pedigree_depth.value
        for g in gids:
            register_with_ancestors(state, int(g), depth, year, root_is_stub=False)
    genetics.on_import(state, gids, year, rng)
    return gids


def run_imports(
    state: SimState,
    setup: SimSetup,
    breed: int,
    year: int,
    n_new_candidates: int,
    genetics: GeneticsModel,
    rng: np.random.Generator,
) -> np.ndarray:
    """Move `import_rate * n_new_candidates` young foreign candidates into domestic kennels."""
    expected = setup.breeds[breed].market.import_rate.value * n_new_candidates
    n = int(np.floor(expected)) + int(rng.random() < expected - np.floor(expected))
    return import_animals(state, setup, breed, year, n, genetics, rng)


def split_population(
    state: SimState,
    setup: SimSetup,
    breed: int,
    year: int,
    foreign_share: float,
    rng: np.random.Generator,
) -> int:
    """Split the living animals of a breed into domestic and foreign subpopulations."""
    a = state.animals
    living = np.flatnonzero((a.breed == breed) & (a.death_year > year) & (a.birth_year < year))
    move = living[rng.random(living.size) < foreign_share]
    a.subpop[move] = FOREIGN
    cand = move[a.is_candidate[move]]
    a.kennel[cand] = pick_kennels(state, breed, FOREIGN, cand.size, rng)
    a.country[cand] = state.kennels.country[a.kennel[cand]]
    pets = move[~a.is_candidate[move]]
    a.kennel[pets] = -1
    fk = np.flatnonzero((state.kennels.breed == breed) & (state.kennels.subpop == FOREIGN))
    a.country[pets] = state.kennels.country[fk[rng.integers(0, fk.size, pets.size)]]
    return int(move.size)
