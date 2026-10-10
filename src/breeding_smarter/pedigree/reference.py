"""Dense tabular method (test oracle and benchmark baseline only; n <= 3000)."""

from __future__ import annotations

import numpy as np

from breeding_smarter.pedigree.core import FloatArray, Pedigree

MAX_DENSE = 3000


def relationship_matrix_dense(ped: Pedigree) -> FloatArray:
    """Numerator relationship matrix A by the tabular method (Emik and Terrill 1949).

    `A[i,j] = 0.5 (A[j,s] + A[j,d])` for j < i (unknown parents contribute 0) and
    `A[i,i] = 1 + 0.5 A[s,d]` when both parents are known.
    """
    n = ped.n
    if n > MAX_DENSE:
        raise ValueError(f"dense A only for n <= {MAX_DENSE}")
    A = np.zeros((n, n))
    for i in range(n):
        s, d = int(ped.sire[i]), int(ped.dam[i])
        row = np.zeros(i)
        if s >= 0:
            row += 0.5 * A[:i, s]
        if d >= 0:
            row += 0.5 * A[:i, d]
        A[i, :i] = row
        A[:i, i] = row
        A[i, i] = 1.0 + (0.5 * A[s, d] if s >= 0 and d >= 0 else 0.0)
    return A


def equivalent_generations_brute(ped: Pedigree, i: int, g: int = 1) -> float:
    """Sum over all known ancestors (every path) of (1/2)^generations; exponential, tiny n."""
    total = 0.0
    for p in (int(ped.sire[i]), int(ped.dam[i])):
        if p >= 0:
            total += 0.5**g + equivalent_generations_brute(ped, p, g + 1)
    return total
