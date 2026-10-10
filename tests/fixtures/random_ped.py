"""Random valid pedigrees with overlapping generations (test helper)."""

import numpy as np

from breeding_smarter.pedigree import Pedigree


def random_arrays(n: int, p_unknown: float, rng: np.random.Generator, window: int = 15):
    """Parents drawn from the last `window` males/females; each parent unknown w.p. p_unknown."""
    sire = -np.ones(n, np.int64)
    dam = -np.ones(n, np.int64)
    sex = rng.integers(0, 2, n).astype(np.int8)
    males: list[int] = []
    females: list[int] = []
    for i in range(n):
        if males and rng.random() >= p_unknown:
            sire[i] = males[rng.integers(max(0, len(males) - window), len(males))]
        if females and rng.random() >= p_unknown:
            dam[i] = females[rng.integers(max(0, len(females) - window), len(females))]
        (males if sex[i] == 1 else females).append(i)
    return sire, dam, sex


def random_pedigree(n: int, p_unknown: float, seed: int, window: int = 15) -> Pedigree:
    rng = np.random.default_rng(seed)
    sire, dam, sex = random_arrays(n, p_unknown, rng, window)
    return Pedigree.from_arrays(sire, dam, sex, birth_year=np.arange(n) // 4 + 2000)


def realistic_pedigree(n: int, seed: int, per_year: int | None = None) -> Pedigree:
    """Overlapping generations with litters and popular sires (benchmark helper).

    Yearly cohorts of `per_year` puppies in litters of about 5; dams aged 2 to 8 years drawn
    uniformly; sires aged 2 to 10 years drawn with heavy-tailed (Pareto) weights. The first
    cohort is founders.
    """
    rng = np.random.default_rng(seed)
    per_year = per_year or max(50, n // 45)
    sire = np.full(n, -1, np.int64)
    dam = np.full(n, -1, np.int64)
    sex = rng.integers(0, 2, n).astype(np.int8)
    year = np.zeros(n, np.int64)
    i = min(per_year, n)
    y = 0
    while i < n:
        y += 1
        end = min(n, i + per_year)
        year[i:end] = y
        alive = np.flatnonzero(year[:i] >= y - 10)
        ages = y - year[alive]
        dams = alive[(sex[alive] == 0) & (ages >= 2) & (ages <= 8)]
        sires = alive[(sex[alive] == 1) & (ages >= 2) & (ages <= 10)]
        if dams.size == 0 or sires.size == 0:
            year[i:end] = y
            i = end
            continue
        w = rng.pareto(1.5, sires.size) + 0.01
        w /= w.sum()
        while i < end:
            k = min(end - i, int(rng.integers(3, 8)))
            sire[i : i + k] = rng.choice(sires, p=w)
            dam[i : i + k] = rng.choice(dams)
            i += k
    return Pedigree.from_arrays(sire, dam, sex, birth_year=year + 1980)
