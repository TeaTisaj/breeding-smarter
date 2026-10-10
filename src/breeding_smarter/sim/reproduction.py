"""One simulated year: dams, sires (strategy), litters, puppies, imports (P3 task 3.6)."""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np

from breeding_smarter.sim.demography import eligible, sample_death, whelp_window
from breeding_smarter.sim.interfaces import GeneticsModel, MatingStrategy, SimSetup, YearContext
from breeding_smarter.sim.kennels import pick_kennels
from breeding_smarter.sim.market import MarketStrategy
from breeding_smarter.sim.registry import (
    found_registry,
    register_with_ancestors,
    run_imports,
    split_population,
)
from breeding_smarter.sim.state import DOMESTIC, FOREIGN, METHODS, SimState

log = logging.getLogger(__name__)
OFFSPRING_WINDOW_YEARS = 5
MIN_LITTER_MEAN = 0.3
PRE_REGISTRY_RAMP_GENERATIONS = 2  # assumption, see target_litters
MIN_SIRES = 3  # recruit males if fewer eligible sires than this (assumption)


@dataclass
class Plan:
    breed: int
    subpop: int
    dams: np.ndarray
    sires: np.ndarray


def stochastic_round(x: float, rng: np.random.Generator) -> int:
    f = np.floor(x)
    return int(f) + int(rng.random() < x - f)


def split_year(setup: SimSetup, breed: int) -> int:
    """Split year, moved to the first simulated year if the configured one is earlier."""
    return max(setup.breeds[breed].population.split_year.value, setup.sim.start_year)


def split_done(setup: SimSetup, breed: int, year: int) -> bool:
    return year > split_year(setup, breed)


def target_litters(setup: SimSetup, breed: int, subpop: int, year: int) -> float:
    """Expected litters so that registrations (registry era) or live births (hidden) hit target.

    Registry era, domestic: `regs(year) * scale / (litter_mean (1 - loss) registration_rate)`.
    Hidden domestic: burn-in size = `burn_in_size_fraction * regs(registry_start)`, ramping
    linearly up to the full `regs(registry_start)` over the `PRE_REGISTRY_RAMP_GENERATIONS`
    generation intervals before the registry is founded (assumption: the breed grows before a
    registry is founded, so enough dams exist in 1980).
    Foreign: `size_factor * regs(registry_start)` live births per year.
    """
    sim = setup.sim
    cfg = setup.breeds[breed]
    rep = cfg.reproduction
    regs = cfg.population.registrations_per_year
    per_litter = rep.litter_size_mean.value * (1 - rep.perinatal_loss_rate.value)
    base = regs.at(sim.registry_start_year) * sim.scale
    if subpop == FOREIGN:
        return sim.foreign.size_factor.value * base / per_litter
    if year >= sim.registry_start_year:
        return regs.at(year) * sim.scale / (per_litter * rep.registration_rate.value)
    frac = cfg.population.burn_in_size_fraction.value
    ramp = PRE_REGISTRY_RAMP_GENERATIONS * sim.generation_interval_years.value
    w = np.clip((year - (sim.registry_start_year - ramp)) / ramp, 0.0, 1.0)
    return (frac + (1.0 - frac) * w) * base / per_litter


def recruit(
    state: SimState,
    setup: SimSetup,
    breed: int,
    subpop: int,
    year: int,
    sex: int,
    n: int,
    genetics: GeneticsModel,
    rng: np.random.Generator,
) -> np.ndarray:
    """Demand-driven recruitment: when breeding candidates are short, breeders acquire `n`
    eligible non-candidate animals (uniformly at random). Counted in `state.meta`."""
    pool = eligible(state, setup, breed, subpop, year, sex, genetics, candidates=False)
    if pool.size == 0 or n <= 0:
        return np.zeros(0, np.int64)
    pick = np.sort(rng.choice(pool, size=min(n, pool.size), replace=False))
    a = state.animals
    a.is_candidate[pick] = True
    a.kennel[pick] = pick_kennels(state, breed, subpop, pick.size, rng)
    key = f"recruited_{setup.breeds[breed].breed_id}_{'F' if sex == 0 else 'M'}"
    state.meta[key] = state.meta.get(key, 0) + int(pick.size)
    return pick


def offspring_window(state: SimState, year: int) -> np.ndarray:
    """Offspring (animals) per gid from litters whelped in the 5 years before `year`."""
    lit = state.litters
    m = (lit.whelp_year >= year - OFFSPRING_WINDOW_YEARS) & (lit.whelp_year < year)
    return np.bincount(lit.sire[m], weights=lit.n_animals[m], minlength=state.n).astype(float)


def plan_year(
    state: SimState,
    setup: SimSetup,
    year: int,
    genetics: GeneticsModel,
    strategy: MatingStrategy,
    rng: np.random.Generator,
    active_breeds: set[int] | None = None,
    market: MatingStrategy | None = None,
) -> list[Plan]:
    """Choose dams and sires for every active breed and subpopulation."""
    market = market or MarketStrategy()
    off5 = offspring_window(state, year)
    plans: list[Plan] = []
    for b in range(len(setup.breeds)):
        if active_breeds is not None and b not in active_breeds:
            continue
        cfg = setup.breeds[b]
        if year == split_year(setup, b):
            share = setup.sim.foreign.size_factor.value / (
                setup.sim.foreign.size_factor.value + cfg.population.burn_in_size_fraction.value
            )
            split_population(state, setup, b, year, share, rng)
        subpops = [DOMESTIC, FOREIGN] if split_done(setup, b, year) else [DOMESTIC]
        for sp in subpops:
            n_target = stochastic_round(target_litters(setup, b, sp, year), rng)
            dams_el = eligible(state, setup, b, sp, year, 0, genetics)
            sires_el = eligible(state, setup, b, sp, year, 1, genetics)
            if dams_el.size < n_target:
                dams_el = np.union1d(
                    dams_el,
                    recruit(state, setup, b, sp, year, 0, n_target - dams_el.size, genetics, rng),
                )
            if sires_el.size < MIN_SIRES and dams_el.size:
                sires_el = np.union1d(
                    sires_el,
                    recruit(state, setup, b, sp, year, 1, MIN_SIRES - sires_el.size, genetics, rng),
                )
            if n_target == 0 or dams_el.size == 0:
                dams = np.zeros(0, np.int64)
                if n_target > 0:
                    state.warnings.append(f"{year} {cfg.breed_id} subpop {sp}: no eligible dams")
            elif dams_el.size < n_target:
                msg = (
                    f"{year} {cfg.breed_id} subpop {sp}: {dams_el.size} eligible dams < {n_target}"
                )
                state.warnings.append(msg)
                log.debug(msg)
                dams = dams_el
            else:
                a = state.animals
                k = a.kennel[dams_el]
                w = a.fertility[dams_el] * np.where(k >= 0, state.kennels.activity[k], 1.0)
                dams = np.sort(rng.choice(dams_el, size=n_target, replace=False, p=w / w.sum()))
            foreign = np.zeros(0, np.int64)
            if (
                sp == DOMESTIC
                and year >= setup.sim.registry_start_year
                and split_done(setup, b, year)
            ):
                foreign = eligible(state, setup, b, FOREIGN, year, 1, genetics)
            ctx = YearContext(state, setup, year, b, sp, off5, genetics, foreign)
            strat = strategy if sp == DOMESTIC else market
            sires = strat.plan_matings(dams, sires_el, ctx, rng) if dams.size else dams
            keep = sires >= 0
            plans.append(Plan(b, sp, dams[keep], sires[keep]))
    return plans


def make_litters(
    state: SimState,
    setup: SimSetup,
    year: int,
    plans: list[Plan],
    genetics: GeneticsModel,
    rng: np.random.Generator,
) -> np.ndarray:
    """Create litters and puppies; puppies get consecutive gids in whelping order."""
    if not plans:
        return np.zeros(0, np.int64)
    dams = np.concatenate([p.dams for p in plans]).astype(np.int64)
    sires = np.concatenate([p.sires for p in plans]).astype(np.int64)
    breed = np.concatenate([np.full(p.dams.size, p.breed) for p in plans]).astype(np.int64)
    subpop = np.concatenate([np.full(p.dams.size, p.subpop) for p in plans]).astype(np.int8)
    n = dams.size
    if n == 0:
        return np.zeros(0, np.int64)
    a, sp_cfg = state.animals, setup.species
    lo_d, hi_d = whelp_window(state, setup, dams, year, 0)
    lo_s, hi_s = whelp_window(state, setup, sires, year, 1)
    lo, hi = np.maximum(lo_d, lo_s), np.minimum(hi_d, hi_s)
    ok = lo <= hi
    dams, sires, breed, subpop, lo, hi = (x[ok] for x in (dams, sires, breed, subpop, lo, hi))
    n = dams.size
    if n == 0:
        return np.zeros(0, np.int64)
    t_whelp = lo + rng.random(n) * (hi - lo)
    # (doy - 1) / 365 >= t_whelp - year, so the window lower bound holds after rounding
    whelp_doy = np.clip(np.ceil((t_whelp - year) * 365.0) + 1, 1, 365).astype(np.int64)
    order = np.argsort(whelp_doy, kind="stable")
    dams, sires, breed, subpop, whelp_doy = (
        x[order] for x in (dams, sires, breed, subpop, whelp_doy)
    )
    reps = [b.reproduction for b in setup.breeds]
    mean = np.array([r.litter_size_mean.value for r in reps])[breed]
    disp = np.array([r.litter_size_dispersion.value for r in reps])[breed]
    loss = np.array([r.perinatal_loss_rate.value for r in reps])[breed]
    reg_rate = np.array([r.registration_rate.value for r in reps])[breed]
    caes = np.array([r.caesarean_rate.value for r in reps])[breed]
    slope = sp_cfg.inbreeding_litter_slope.value
    # The configured mean is the mean litter of the mated, non-inbred dams: normalise the
    # dams' fertility by its mean within each breed and subpopulation this year (dams are
    # chosen with fertility weights, so raw fertility would inflate litters).
    fert = a.fertility[dams]
    grp = breed * 2 + subpop
    grp_mean = np.bincount(grp, weights=fert) / np.maximum(np.bincount(grp), 1)
    rel_fert = fert / grp_mean[grp]
    mu = np.maximum(MIN_LITTER_MEAN, mean * rel_fert * (1.0 - slope * a.f_true[dams]))
    n_born = np.maximum(1, rng.negative_binomial(disp, disp / (disp + mu)))
    n_alive = rng.binomial(n_born, 1.0 - loss)
    registry_dom = (year >= setup.sim.registry_start_year) & (subpop == DOMESTIC)
    n_reg = rng.binomial(n_alive, reg_rate)
    n_animals = np.where(registry_dom, n_reg, n_alive)
    gest = np.clip(
        np.rint(rng.normal(sp_cfg.gestation_days.value, sp_cfg.gestation_sd_days.value, n)), 56, 70
    ).astype(np.int64)
    whelp = np.datetime64(f"{year}-01-01") + (whelp_doy - 1).astype("timedelta64[D]")
    mating = whelp - gest.astype("timedelta64[D]")
    m_year = mating.astype("datetime64[Y]").astype(np.int64) + 1970
    m_doy = (mating - mating.astype("datetime64[Y]").astype("datetime64[D]")).astype(np.int64) + 1
    ai = (a.subpop[sires] == FOREIGN) & (subpop == DOMESTIC)
    frozen = np.array([b.market.ai_frozen_share.value for b in setup.breeds])[breed]
    method = np.where(
        ai, np.where(rng.random(n) < frozen, METHODS.index("ai_frozen"), 2), 0
    ).astype(np.int8)
    registered_litter = registry_dom & (n_animals > 0)
    lit_ids = state.litters.add(
        n,
        breed=breed,
        subpop=subpop,
        sire=sires,
        dam=dams,
        mating_year=m_year,
        mating_doy=m_doy,
        whelp_year=year,
        whelp_doy=whelp_doy,
        n_born=n_born,
        n_born_alive=n_alive,
        n_animals=n_animals,
        method=method,
        caesarean=rng.random(n) < caes,
        breeder=a.kennel[dams],
        registered=registered_litter,
    )
    np.add.at(a.data["litters_count"], dams, 1)
    a.data["last_whelp_t"][dams] = year + (whelp_doy - 1) / 365.0
    np.add.at(a.data["offspring_count"], dams, n_animals)
    np.add.at(a.data["offspring_count"], sires, n_animals)
    gids = _add_puppies(
        state,
        setup,
        year,
        lit_ids,
        dams,
        sires,
        breed,
        subpop,
        whelp_doy,
        n_animals,
        registry_dom,
        genetics,
        rng,
    )
    depth = np.array([b.market.import_pedigree_depth.value for b in setup.breeds])[breed]
    for k in np.flatnonzero(registered_litter & ai):
        if not a.registered[sires[k]]:
            register_with_ancestors(state, int(sires[k]), int(depth[k]), year, root_is_stub=True)
    return gids


def _add_puppies(
    state: SimState,
    setup: SimSetup,
    year: int,
    lit_ids: np.ndarray,
    dams: np.ndarray,
    sires: np.ndarray,
    breed: np.ndarray,
    subpop: np.ndarray,
    whelp_doy: np.ndarray,
    n_animals: np.ndarray,
    registry_dom: np.ndarray,
    genetics: GeneticsModel,
    rng: np.random.Generator,
) -> np.ndarray:
    a, sp_cfg = state.animals, setup.species
    total = int(n_animals.sum())
    if total == 0:
        return np.zeros(0, np.int64)
    rep = lambda x: np.repeat(x, n_animals)  # noqa: E731
    c_dam, c_sire, c_breed, c_sub = rep(dams), rep(sires), rep(breed), rep(subpop)
    c_doy, c_lit, c_reg = rep(whelp_doy), rep(lit_ids), rep(registry_dom)
    sex = (rng.random(total) < sp_cfg.sex_ratio_male.value).astype(np.int8)
    sd_a = sp_cfg.attractiveness_sd.value
    attr = 0.5 * (a.attractiveness[c_sire] + a.attractiveness[c_dam]) + rng.normal(
        0, np.sqrt(0.5) * sd_a, total
    )
    fert = rng.lognormal(0.0, sp_cfg.fertility_log_sd.value, total)
    f_share = np.array([b.market.female_candidate_share.value for b in setup.breeds])
    m_share = np.array([b.market.male_candidate_share.value for b in setup.breeds])
    share = np.where(sex == 1, m_share[c_breed], f_share[c_breed])
    cand = rng.random(total) < share
    kennel = np.full(total, -1, np.int32)
    for b in np.unique(c_breed):
        for sp in (DOMESTIC, FOREIGN):
            m = cand & (c_breed == b) & (c_sub == sp)
            if m.any():
                kennel[m] = pick_kennels(state, int(b), sp, int(m.sum()), rng)
    birth_year = np.full(total, year)
    d_year, d_doy, d_cause = sample_death(birth_year, c_doy, sp_cfg, rng)
    country = np.where(
        a.kennel[c_dam] >= 0, state.kennels.country[np.maximum(a.kennel[c_dam], 0)], 0
    )
    gids = state.add_animals(
        total,
        breed=c_breed,
        subpop=c_sub,
        sex=sex,
        birth_year=birth_year,
        birth_doy=c_doy,
        sire=c_sire,
        dam=c_dam,
        death_year=d_year,
        death_doy=d_doy,
        death_cause=d_cause,
        kennel=kennel,
        birth_kennel=a.kennel[c_dam],
        is_candidate=cand,
        attractiveness=attr,
        fertility=fert,
        registered=c_reg,
        reg_year=np.where(c_reg, year, -1),
        litter=c_lit,
        country=country,
    )
    genetics.make_offspring(state, c_sire, c_dam, gids, rng)
    return gids


def simulate_year(
    state: SimState,
    setup: SimSetup,
    year: int,
    genetics: GeneticsModel,
    strategy: MatingStrategy,
    rng: np.random.Generator,
    active_breeds: set[int] | None = None,
) -> None:
    """Advance the state by one year (registry founding, matings, litters, imports)."""
    if year == setup.sim.registry_start_year:
        found_registry(state, setup, year)
    plans = plan_year(state, setup, year, genetics, strategy, rng, active_breeds)
    gids = make_litters(state, setup, year, plans, genetics, rng)
    if year >= setup.sim.registry_start_year:
        a = state.animals
        for b in range(len(setup.breeds)):
            if active_breeds is not None and b not in active_breeds:
                continue
            if not split_done(setup, b, year):
                continue
            new_cand = int(
                (a.is_candidate[gids] & (a.breed[gids] == b) & (a.subpop[gids] == DOMESTIC)).sum()
            )
            run_imports(state, setup, b, year, new_cand, genetics, rng)
    genetics.on_year_end(state, year, rng)
    state.year = year
