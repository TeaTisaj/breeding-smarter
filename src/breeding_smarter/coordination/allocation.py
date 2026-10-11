"""Mate allocation within sire quotas (P12 decision D13).

MC1 (minimum-coancestry mating) [sonesson-meuwissen-2000]: assign each dam one sire seat
(sires replicated by quota) minimising total cost `pair kinship + w * P(affected puppy)`; at
most one litter per dam, forbidden (HARD-rule) pairs never chosen. Solved exactly as an
assignment problem (`scipy.optimize.linear_sum_assignment`). Random allocation uses the same
machinery with random costs.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import linear_sum_assignment

from breeding_smarter.pedigree.core import FloatArray, IntArray

FORBIDDEN = 1e6


def _assign(cost: FloatArray, quotas: IntArray) -> IntArray:
    """Sire index per dam (-1 if no allowed seat) for a dams x sires cost matrix."""
    n = cost.shape[0]
    out = np.full(n, -1, dtype=np.int64)
    cols = np.repeat(np.arange(cost.shape[1]), np.asarray(quotas, np.int64))
    if cols.size == 0 or n == 0:
        return out
    rows, j = linear_sum_assignment(cost[:, cols])
    ok = cost[rows, cols[j]] < FORBIDDEN
    out[rows[ok]] = cols[j[ok]]
    return out


def assign_mc1(
    K_pair: FloatArray,
    p_affected: FloatArray,
    forbidden: NDArray[np.bool_],
    quotas: IntArray,
    w_h: float = 1.0,
) -> IntArray:
    """Minimum total `kinship + w_h * P(affected)` assignment (dams x sires inputs)."""
    cost = np.where(forbidden, FORBIDDEN, np.asarray(K_pair) + w_h * np.asarray(p_affected))
    return _assign(cost, quotas)


def assign_random(
    quotas: IntArray, forbidden: NDArray[np.bool_], rng: np.random.Generator
) -> IntArray:
    """A random assignment that respects quotas and avoids forbidden pairs."""
    cost = np.where(forbidden, FORBIDDEN, rng.random(forbidden.shape))
    return _assign(cost, quotas)
