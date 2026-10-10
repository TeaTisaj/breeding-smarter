"""Breeder kennels with synthetic coordinates (P3 task 3.3)."""

from __future__ import annotations

import numpy as np

from breeding_smarter.sim.names import kennel_names
from breeding_smarter.sim.state import DOMESTIC, FOREIGN, SimState

# Approximate bounding boxes (lat_min, lat_max, lon_min, lon_max). Approximate, POC only.
COUNTRY_BBOX: dict[str, tuple[float, float, float, float]] = {
    "HR": (42.4, 46.6, 13.5, 19.4),
    "SI": (45.4, 46.9, 13.4, 16.6),
    "AT": (46.4, 49.0, 9.5, 17.2),
    "HU": (45.7, 48.6, 16.1, 22.9),
    "IT": (37.0, 46.5, 7.0, 18.5),
    "DE": (47.3, 55.0, 5.9, 15.0),
    "RS": (42.2, 46.2, 18.8, 23.0),
    "CZ": (48.6, 51.1, 12.1, 18.9),
    "PL": (49.0, 54.8, 14.1, 24.1),
    "SE": (55.3, 69.1, 11.0, 24.2),
    "FI": (59.8, 70.1, 20.5, 31.6),
    "NL": (50.7, 53.6, 3.3, 7.2),
}
DOMESTIC_COUNTRY = "HR"
REGS_PER_KENNEL = 15  # assumption from P3 task 3.3: registrations_2026 / 15, at least 5
MIN_KENNELS = 5
PARETO_SHAPE = 1.5  # few large kennels, many small (assumption)


def haversine_km(lat1: np.ndarray, lon1: np.ndarray, lat2: np.ndarray, lon2: np.ndarray):
    r = 6371.0
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dphi = p2 - p1
    dl = np.radians(lon2) - np.radians(lon1)
    a = np.sin(dphi / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * r * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def _points(country: str, n: int, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    lat0, lat1, lon0, lon1 = COUNTRY_BBOX[country]
    return rng.uniform(lat0, lat1, n), rng.uniform(lon0, lon1, n)


def create_kennels(
    state: SimState,
    breed: int,
    n_domestic: int,
    n_foreign: int,
    foreign_countries: list[str],
    rng: np.random.Generator,
) -> None:
    """Domestic (Croatia) and foreign breeder kennels for one breed, Pareto activity weights."""
    n_domestic = max(MIN_KENNELS, n_domestic)
    n_foreign = max(MIN_KENNELS, n_foreign)
    countries = [DOMESTIC_COUNTRY] * n_domestic + [
        foreign_countries[int(i)] for i in rng.integers(0, len(foreign_countries), n_foreign)
    ]
    lat = np.empty(len(countries))
    lon = np.empty(len(countries))
    for c in sorted(set(countries)):  # sorted: set order depends on PYTHONHASHSEED
        m = np.array([x == c for x in countries])
        lat[m], lon[m] = _points(c, int(m.sum()), rng)
    activity = rng.pareto(PARETO_SHAPE, len(countries)) + 0.05
    subpop = np.array([DOMESTIC] * n_domestic + [FOREIGN] * n_foreign, dtype=np.int8)
    names = kennel_names(len(countries), countries, rng)
    taken = set(state.kennel_names)
    for i, nm in enumerate(names):
        while nm in taken:
            nm = nm + "a"
        names[i] = nm
        taken.add(nm)
    state.kennels.add(
        len(countries),
        breed=breed,
        subpop=subpop,
        country=np.array([state.country_code(c) for c in countries]),
        lat=lat,
        lon=lon,
        activity=activity,
    )
    state.kennel_names.extend(names)


def pick_kennels(
    state: SimState, breed: int, subpop: int, n: int, rng: np.random.Generator
) -> np.ndarray:
    """`n` breeder kennels of a breed and subpopulation, weighted by activity."""
    k = state.kennels
    ids = np.flatnonzero((k.breed == breed) & (k.subpop == subpop))
    w = k.activity[ids]
    return ids[rng.choice(ids.size, size=n, p=w / w.sum())] if n else np.zeros(0, np.int64)
