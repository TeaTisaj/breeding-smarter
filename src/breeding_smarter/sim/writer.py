"""Convert a SimState to registry and truth tables (P3 task 3.8)."""

from __future__ import annotations

from typing import Protocol

import numpy as np
import pandas as pd

from breeding_smarter.schema.tables import (
    ANIMALS,
    ANIMALS_TRUTH,
    BREEDS,
    DNA_TESTS,
    EBV,
    GENOTYPES_TRUTH,
    HEALTH_TESTS,
    KENNELS,
    LITTERS,
)
from breeding_smarter.sim.interfaces import SimSetup
from breeding_smarter.sim.kennels import COUNTRY_BBOX
from breeding_smarter.sim.names import call_names
from breeding_smarter.sim.state import DEATH_CAUSES, METHODS, SimState

MICROCHIP_PREFIX = "999"  # ISO 11784 test-transponder code (icar-999)


class TableContributor(Protocol):
    """Genetics models add health, DNA, EBV and truth columns through this hook."""

    def contribute_tables(
        self, state: SimState, setup: SimSetup, tables: dict[str, pd.DataFrame], idx_of: np.ndarray
    ) -> None: ...


def _dates(year: np.ndarray, doy: np.ndarray) -> np.ndarray:
    base = (np.asarray(year, np.int64) - 1970).astype("datetime64[Y]").astype("datetime64[D]")
    return base + (np.asarray(doy, np.int64) - 1).astype("timedelta64[D]")


def _nullable(arr: np.ndarray, mask: np.ndarray) -> pd.api.extensions.ExtensionArray:
    out = pd.array(np.where(mask, arr, 0).astype(np.int64), dtype="Int64")
    out[~np.asarray(mask, dtype=bool)] = pd.NA
    return out


def _empty(spec_cols: list[str]) -> pd.DataFrame:
    return pd.DataFrame({c: pd.Series([], dtype=object) for c in spec_cols})


def _seq_per_group(groups: np.ndarray) -> np.ndarray:
    """1-based running number within each group, in array order."""
    order = np.argsort(groups, kind="stable")
    g = groups[order]
    starts = np.r_[0, np.flatnonzero(g[1:] != g[:-1]) + 1]
    run = np.arange(g.size) - np.repeat(starts, np.diff(np.r_[starts, g.size]))
    out = np.empty(g.size, np.int64)
    out[order] = run + 1
    return out


def to_tables(
    state: SimState,
    setup: SimSetup,
    rng: np.random.Generator,
    end_year: int,
    contributor: TableContributor | None = None,
) -> dict[str, pd.DataFrame]:
    """Registry tables (registered animals, renumbered `idx` in gid order) and truth tables."""
    a, k = state.animals, state.kennels
    reg_cfg = setup.sim.registry
    gids = np.flatnonzero(a.registered)
    m = gids.size
    idx_of = np.full(state.n, -1, np.int64)
    idx_of[gids] = np.arange(m)

    known = a.reg_parents_known[gids]
    sire_g, dam_g = a.sire[gids], a.dam[gids]
    sire_idx = np.where(known & (sire_g >= 0), idx_of[np.maximum(sire_g, 0)], -1)
    dam_idx = np.where(known & (dam_g >= 0), idx_of[np.maximum(dam_g, 0)], -1)

    stub = a.foreign_stub[gids]
    by = a.birth_year[gids].astype(np.int64)
    country = np.array(state.countries, dtype=object)[a.country[gids]]
    seq_dom = _seq_per_group(np.where(stub, -1, by))
    for_key = np.array([f"{c}" for c in country], dtype=object)
    seq_for = _seq_per_group(pd.factorize(for_key)[0])
    reg_no = np.where(
        stub,
        [f"SYN-FOREIGN-{c}-{s:06d}" for c, s in zip(country, seq_for, strict=True)],
        [f"SYN-HR-{y}-{s:06d}" for y, s in zip(by, seq_dom, strict=True)],
    )
    imp = a.import_flag[gids]
    orig = [
        f"SYN-FOREIGN-{c}-I{s:06d}" if i else None
        for c, s, i in zip(country, seq_for, imp, strict=True)
    ]

    # studbook: HR if parents and grandparents are all recorded, else HUR; stubs FOREIGN
    def par(x: np.ndarray, arr: np.ndarray) -> np.ndarray:
        return np.where(x >= 0, arr[np.maximum(x, 0)], -1)

    gp = np.stack(
        [
            par(sire_idx, sire_idx),
            par(sire_idx, dam_idx),
            par(dam_idx, sire_idx),
            par(dam_idx, dam_idx),
        ]
    )
    full3 = (sire_idx >= 0) & (dam_idx >= 0) & (gp >= 0).all(axis=0)
    studbook = np.where(stub, "FOREIGN", np.where(full3, "HR", "HUR"))

    # kennels: breeder kennel ids are row + 1; private owners are appended after them
    n_k = k.n
    bk = a.birth_kennel[gids]
    breeder_id = pd.array(np.where(bk >= 0, bk + 1, 0).astype(np.int32), dtype="Int32")
    breeder_id[bk < 0] = pd.NA
    own_k = a.kennel[gids]
    owner = np.where(own_k >= 0, own_k + 1, -1).astype(np.int64)
    pets = np.flatnonzero(owner < 0)
    pet_country = country[pets]
    owner_rows = []
    next_id = n_k + 1
    per_owner = reg_cfg.dogs_per_private_owner.value
    for c in sorted(set(pet_country)):
        sel = pets[pet_country == c]
        n_own = int(np.ceil(sel.size / per_owner))
        ids = next_id + np.arange(n_own)
        owner[sel] = ids[rng.integers(0, n_own, sel.size)]
        lat0, lat1, lon0, lon1 = COUNTRY_BBOX[c]
        for j, oid in enumerate(ids):
            owner_rows.append(
                {
                    "kennel_id": int(oid),
                    "name": f"Private owner {c}-{j + 1:05d}",
                    "kind": "private_owner",
                    "country": c,
                    "lat": float(rng.uniform(lat0, lat1)),
                    "lon": float(rng.uniform(lon0, lon1)),
                }
            )
        next_id += n_own

    affix = np.array([*state.kennel_names, ""], dtype=object)[np.where(bk >= 0, bk, n_k)]
    calls = np.array(call_names(m, rng), dtype=object)
    names = [f"{c} {af}".strip() for c, af in zip(calls, affix, strict=True)]
    chips = np.unique(rng.integers(0, 10**12, size=int(m * 1.2) + 10))
    while chips.size < m:
        chips = np.unique(np.r_[chips, rng.integers(0, 10**12, size=m)])
    chips = rng.permutation(chips)[:m]
    breed_codes = np.array([b.breed_id for b in setup.breeds], dtype=object)
    breed_of = a.breed[gids]
    colours = [b.coat_colours for b in setup.breeds]
    coat = [colours[b][int(rng.integers(0, len(colours[b])))] for b in breed_of]
    limited = (~a.is_candidate[gids]) & (rng.random(m) < reg_cfg.limited_registration_share.value)
    dead = a.death_year[gids] <= end_year
    titles = rng.poisson(reg_cfg.titles_rate.value * np.exp(a.attractiveness[gids]))
    lit = a.litter[gids]
    lit_ok = (lit >= 0) & state.litters.registered[np.maximum(lit, 0)] & known
    animals = pd.DataFrame(
        {
            "idx": np.arange(m, dtype=np.int64),
            "reg_no": reg_no,
            "name": names,
            "species": setup.species.species,
            "breed_id": breed_codes[breed_of],
            "sex": np.where(a.sex[gids] == 1, "M", "F"),
            "birth_date": _dates(by, a.birth_doy[gids]),
            "sire_idx": _nullable(sire_idx, sire_idx >= 0),
            "dam_idx": _nullable(dam_idx, dam_idx >= 0),
            "litter_id": _nullable(lit, lit_ok),
            "breeder_id": breeder_id,
            "owner_id": owner.astype(np.int32),
            "country_of_birth": country,
            "studbook": studbook,
            "import_flag": imp,
            "original_reg_no": orig,
            "microchip": [f"{MICROCHIP_PREFIX}{c:012d}" for c in chips],
            "coat_colour": coat,
            "registration_type": np.where(limited, "limited", "full"),
            "death_date": pd.Series(
                np.where(
                    dead, _dates(a.death_year[gids], a.death_doy[gids]), np.datetime64("NaT", "D")
                )
            ),
            "death_cause": np.where(
                dead, np.array(DEATH_CAUSES, dtype=object)[a.death_cause[gids]], None
            ),
            "titles_count": titles.astype(np.int16),
        }
    )

    L = state.litters
    lsel = np.flatnonzero(L.registered)
    litters = pd.DataFrame(
        {
            "litter_id": lsel.astype(np.int64),
            "breed_id": breed_codes[L.breed[lsel]],
            "sire_idx": idx_of[L.sire[lsel]],
            "dam_idx": idx_of[L.dam[lsel]],
            "mating_date": _dates(L.mating_year[lsel], L.mating_doy[lsel]),
            "whelp_date": _dates(L.whelp_year[lsel], L.whelp_doy[lsel]),
            "n_born": L.n_born[lsel],
            "n_born_alive": L.n_born_alive[lsel],
            "n_registered": L.n_animals[lsel],
            "mating_method": np.array(METHODS, dtype=object)[L.method[lsel]],
            "caesarean": L.caesarean[lsel],
            "breeder_id": (L.breeder[lsel] + 1).astype(np.int32),
        }
    )

    first_year = pd.Series(by).groupby(bk).min()
    k_reg = np.full(n_k, setup.sim.registry_start_year)
    valid = first_year.index.to_numpy() >= 0
    k_reg[first_year.index.to_numpy()[valid]] = np.maximum(
        first_year.to_numpy()[valid], setup.sim.registry_start_year
    )
    kennels = pd.DataFrame(
        {
            "kennel_id": np.arange(1, n_k + 1, dtype=np.int32),
            "name": state.kennel_names,
            "kind": "breeder",
            "country": np.array(state.countries, dtype=object)[k.country],
            "lat": k.lat,
            "lon": k.lon,
            "registered_year": k_reg.astype(np.int16),
        }
    )
    if owner_rows:
        own = pd.DataFrame(owner_rows)
        first = pd.Series(by).groupby(owner).min()
        own["registered_year"] = own["kennel_id"].map(first).fillna(end_year).astype(np.int16)
        kennels = pd.concat([kennels, own], ignore_index=True)

    breeds = pd.DataFrame(
        [
            {
                "breed_id": b.breed_id,
                "display_name": b.display_name,
                "species": setup.species.species,
                "size_class": b.size_class,
                "studbook": b.studbook,
                "is_local_breed": b.is_local_breed,
                "archetype_description": b.archetype_description,
            }
            for b in setup.breeds
        ]
    )
    n = state.n
    truth = pd.DataFrame(
        {
            "gid": np.arange(n, dtype=np.int64),
            "idx": _nullable(idx_of, idx_of >= 0),
            "breed_id": breed_codes[a.breed],
            "sex": np.where(a.sex == 1, "M", "F"),
            "birth_year": a.birth_year.astype(np.int16),
            "true_sire_gid": _nullable(a.sire, a.sire >= 0),
            "true_dam_gid": _nullable(a.dam, a.dam >= 0),
            "is_hidden": idx_of < 0,
            "f_true_ibd": a.f_true.astype(np.float64),
            "f_true_pedigree": np.zeros(n),
            "tbv_hd": np.zeros(n),
            "hd_liability": np.full(n, np.nan),
            "attractiveness": a.attractiveness.astype(np.float64),
            "fertility": a.fertility.astype(np.float64),
        }
    )
    tables = {
        BREEDS.name: breeds,
        KENNELS.name: kennels,
        ANIMALS.name: animals,
        LITTERS.name: litters,
        HEALTH_TESTS.name: _empty(HEALTH_TESTS.columns),
        DNA_TESTS.name: _empty(DNA_TESTS.columns),
        EBV.name: _empty(EBV.columns),
        ANIMALS_TRUTH.name: truth,
        GENOTYPES_TRUTH.name: _empty(GENOTYPES_TRUTH.columns),
    }
    if contributor is not None:
        contributor.contribute_tables(state, setup, tables, idx_of)
    return tables
