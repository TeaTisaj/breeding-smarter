"""Whole-litter quotas from continuous contributions (P12 decision D12).

Sainte-Laguë (Webster) apportionment: seats go one at a time to the sire with the largest
`expected_i / (2 q_i + 1)`, skipping sires at their cap; sires with fewer than
`min_expected` expected litters get none [du-2025]. Ties go to the lower index.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from breeding_smarter.pedigree.core import FloatArray, IntArray


@dataclass
class Quotas:
    quota: IntArray
    relaxed: int  # cap increases needed to place every litter


def sainte_lague(
    expected: FloatArray,
    total: int,
    caps: IntArray,
    min_expected: float = 0.25,
    relax_order: IntArray | None = None,
) -> Quotas:
    """Apportion `total` litters. If the eligible sires' caps cannot hold `total`, caps of
    eligible sires are raised by one at a time in `relax_order` (default: by index)."""
    e = np.asarray(expected, dtype=float)
    caps = np.asarray(caps, dtype=np.int64).copy()
    eligible = e >= min_expected
    if not eligible.any() and total > 0:
        eligible = e >= e.max()
    q = np.zeros(e.size, dtype=np.int64)
    relaxed = 0
    order = np.arange(e.size) if relax_order is None else np.asarray(relax_order, np.int64)
    order = order[eligible[order]]
    k = 0
    while caps[eligible].sum() < total:
        caps[order[k % order.size]] += 1
        relaxed += 1
        k += 1
    for _ in range(total):
        pri = np.where(eligible & (q < caps), e / (2 * q + 1), -np.inf)
        j = int(np.argmax(pri))
        q[j] += 1
    return Quotas(quota=q, relaxed=relaxed)
