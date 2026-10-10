"""Inbreeding (Meuwissen and Luo 1992), L-rows, pair kinship and its exact decomposition."""

from __future__ import annotations

import heapq

import numpy as np

from breeding_smarter.pedigree import _kernels as K
from breeding_smarter.pedigree.core import FloatArray, IntArray, Pedigree


def inbreeding(ped: Pedigree, shortcut: bool = True) -> tuple[FloatArray, FloatArray]:
    """Inbreeding coefficients F and Mendelian sampling variances D of every animal.

    Meuwissen and Luo (1992): with `A = L D L'`, `F_i = sum_j L_ij^2 D_j - 1` over the
    ancestors j of i (including i), `D_i = 0.5 - 0.25 (F_s + F_d)` with `F[-1] = -1`.
    Rows of L are built by pushing contributions from the animal to its ancestors in
    decreasing index order (max-heap). `shortcut` reuses F of the previous animal when it is a
    full sib (litter mates have consecutive indices); it is an optimisation only.
    """
    n = ped.n
    F = np.zeros(n)
    D = np.zeros(n)
    if n:
        K.meuwissen_luo(ped.sire, ped.dam, F, D, 0, shortcut)
    return F, D


def inbreeding_extend(
    ped: Pedigree, F: FloatArray, D: FloatArray, start: int, shortcut: bool = True
) -> tuple[FloatArray, FloatArray]:
    """F and D for animals with index >= `start`, reusing the given values for older animals.

    The Meuwissen and Luo loop is naturally incremental because animals only depend on their
    ancestors (smaller indices). Returns new arrays of length `ped.n`.
    """
    n = ped.n
    if start > F.shape[0] or start > D.shape[0]:
        raise ValueError("start beyond the given F/D arrays")
    F2 = np.zeros(n)
    D2 = np.zeros(n)
    F2[:start] = F[:start]
    D2[:start] = D[:start]
    if n > start:
        K.meuwissen_luo(ped.sire, ped.dam, F2, D2, start, shortcut)
    return F2, D2


def inbreeding_py(ped: Pedigree) -> tuple[FloatArray, FloatArray]:
    """Plain-Python twin of `inbreeding` (dict-based, no shortcut); used in tests."""
    n = ped.n
    sire = ped.sire.tolist()
    dam = ped.dam.tolist()
    F = [0.0] * n
    D = [0.0] * n
    for i in range(n):
        s, d = sire[i], dam[i]
        D[i] = 0.5 - 0.25 * ((F[s] if s >= 0 else -1.0) + (F[d] if d >= 0 else -1.0))
        if s < 0 or d < 0:
            continue
        L = {i: 1.0}
        heap = [-i]
        acc = 0.0
        while heap:
            j = -heapq.heappop(heap)
            acc += L[j] ** 2 * D[j]
            for p in (sire[j], dam[j]):
                if p >= 0:
                    if p not in L:
                        heapq.heappush(heap, -p)
                        L[p] = 0.0
                    L[p] += 0.5 * L[j]
        F[i] = acc - 1.0
    return np.array(F), np.array(D)


def l_row(ped: Pedigree, D: FloatArray, i: int) -> tuple[IntArray, FloatArray]:
    """Non-zero entries of row i of L: ancestors of i plus i itself (`L_ii = 1`), sorted."""
    anc, vals, _ = K.l_row(ped.sire, ped.dam, D, np.array([i], np.int64), np.ones(1))
    return anc, vals


def l_row_virtual(
    ped: Pedigree, D: FloatArray, F: FloatArray, a: int, b: int
) -> tuple[IntArray, FloatArray, float]:
    """L row of a hypothetical offspring x of a x b, excluding x itself, plus `D_x`.

    `D_x = 0.5 - 0.25 (F_a + F_b)`. Entries are the ancestors of x (a, b and their ancestors).
    """
    anc, vals, _ = K.l_row(ped.sire, ped.dam, D, np.array([a, b], np.int64), np.full(2, 0.5))
    return anc, vals, 0.5 - 0.25 * (float(F[a]) + float(F[b]))


def pair_kinship(ped: Pedigree, F: FloatArray, D: FloatArray, a: int, b: int) -> float:
    """Kinship f_ab = F of a virtual offspring of a x b = `sum_j Lx_j^2 D_j - 1`.

    The virtual row includes `D_x = 0.5 - 0.25 (F_a + F_b)` with `Lx_x = 1`. For `a == b`
    returns `(1 + F_a) / 2`.
    """
    if a == b:
        return 0.5 * (1.0 + float(F[a]))
    _, _, acc = K.l_row(ped.sire, ped.dam, D, np.array([a, b], np.int64), np.full(2, 0.5))
    d_x = 0.5 - 0.25 * (float(F[a]) + float(F[b]))
    return float(acc + d_x - 1.0)


def pair_kinship_decomposed(
    ped: Pedigree, F: FloatArray, D: FloatArray, a: int, b: int
) -> dict[int, float]:
    """Exact additive decomposition of f_ab over ancestors: `c_j = 0.5 L_aj L_bj D_j`.

    Summed over the ancestors j common to the L rows of a and b (a or b themselves included
    when one is an ancestor of the other), the contributions add up to f_ab exactly because
    `A = L D L'`. Each `c_j` is the part of the kinship that traces to Mendelian sampling
    variation originating in ancestor j. Keys are pedigree indices.
    """
    ia, la = l_row(ped, D, a)
    ib, lb = l_row(ped, D, b)
    common, pa, pb = np.intersect1d(ia, ib, assume_unique=True, return_indices=True)
    contrib = 0.5 * la[pa] * lb[pb] * D[common]
    return {int(j): float(c) for j, c in zip(common, contrib, strict=True)}
