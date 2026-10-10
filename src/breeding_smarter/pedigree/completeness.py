"""Pedigree completeness: equivalent, maximum and complete generations."""

from __future__ import annotations

import numpy as np

from breeding_smarter.pedigree import _kernels as K
from breeding_smarter.pedigree.core import FloatArray, IntArray, Pedigree


def equivalent_generations(ped: Pedigree) -> FloatArray:
    """Equivalent complete generations (EqG, Maignel et al. 1996).

    `EqG_i = sum over known parents p of 0.5 (1 + EqG_p)` (forward pass, O(n)); equals the sum
    over all known ancestors, counting every path, of `(1/2)^generations`.
    """
    if ped.n == 0:
        return np.zeros(0)
    return K.equivalent_generations(ped.sire, ped.dam)


def max_generations(ped: Pedigree) -> IntArray:
    """Number of generations to the most remote known ancestor (`1 + max` over parents)."""
    return K.generation_depths(ped.sire, ped.dam)[0] if ped.n else np.zeros(0, np.int64)


def complete_generations(ped: Pedigree) -> IntArray:
    """Fully known generations: `1 + min(complete_s, complete_d)` if both parents known."""
    return K.generation_depths(ped.sire, ped.dam)[1] if ped.n else np.zeros(0, np.int64)
