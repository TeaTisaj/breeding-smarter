"""Rate-of-inbreeding targets and their yearly form (P12 task 12.2).

Ne = 1 / (2 dF) [fao-2013]; per-year rate `1 - (1 - dF)^(1/L)` (about dF / L) [lewis-2015];
yearly kinship budget `C_next = 1 - (1 - C_now)(1 - dF)^(1/L)` [du-2025; exact yearly form
unverified, see docs/research.md section 10].
"""

from __future__ import annotations

import math

import numpy as np

from breeding_smarter.pedigree.core import Pedigree
from breeding_smarter.pedigree.population import generation_interval


def per_year(delta_f_gen: float, L: float) -> float:
    """Per-year rate equivalent to `delta_f_gen` per generation: `1 - (1 - dF)^(1/L)`."""
    return float(1.0 - (1.0 - delta_f_gen) ** (1.0 / L))


def next_budget(C_now: float, delta_f_gen: float, L: float) -> float:
    """Kinship allowed after one year: `1 - (1 - C_now)(1 - dF)^(1/L)`."""
    return float(1.0 - (1.0 - C_now) * (1.0 - delta_f_gen) ** (1.0 / L))


def ne_from_delta(delta: float) -> float:
    """`Ne = 1 / (2 delta)` (infinite for a non-positive rate)."""
    return 1.0 / (2.0 * delta) if delta > 0 else math.inf


def estimate_generation_interval(ped: Pedigree, year: int, window: int) -> float:
    """Mean parent age at birth (years, both sexes) of animals born in `(year - window, year]`."""
    by = ped.birth_year.astype(np.int64)
    ref = (by > year - window) & (by <= year)
    return generation_interval(ped, ref).overall
