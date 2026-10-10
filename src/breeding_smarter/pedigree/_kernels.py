"""numba kernels for the pedigree engine (ADR-004). Plain-Python twins live in `reference.py`
and `inbreeding.py` (`*_py`) and are compared in property tests.
"""

from __future__ import annotations

import numpy as np
from numba import njit
from numpy.typing import NDArray

IntArray = NDArray[np.int64]
FloatArray = NDArray[np.float64]


@njit(cache=True)
def mark_ancestors(sire: IntArray, dam: IntArray, mark: NDArray[np.bool_]) -> NDArray[np.bool_]:
    for i in range(sire.shape[0] - 1, -1, -1):
        if mark[i]:
            if sire[i] >= 0:
                mark[sire[i]] = True
            if dam[i] >= 0:
                mark[dam[i]] = True
    return mark


@njit(cache=True, inline="always")
def _heap_push(heap: IntArray, size: int, v: int) -> int:
    """Max-heap push; returns the new size."""
    k = size
    heap[k] = v
    while k > 0:
        parent = (k - 1) >> 1
        if heap[parent] >= heap[k]:
            break
        heap[parent], heap[k] = heap[k], heap[parent]
        k = parent
    return size + 1


@njit(cache=True, inline="always")
def _heap_pop(heap: IntArray, size: int) -> int:
    """Max-heap pop of heap[0]; caller reads heap[0] first. Returns the new size."""
    size -= 1
    heap[0] = heap[size]
    k = 0
    while True:
        left = 2 * k + 1
        if left >= size:
            break
        child = left
        right = left + 1
        if right < size and heap[right] > heap[left]:
            child = right
        if heap[k] >= heap[child]:
            break
        heap[k], heap[child] = heap[child], heap[k]
        k = child
    return size


@njit(cache=True)
def _row_traverse(
    sire: IntArray,
    dam: IntArray,
    D: FloatArray,
    L: FloatArray,
    heap: IntArray,
    in_heap: NDArray[np.bool_],
    touched: IntArray,
    seeds: IntArray,
    seed_vals: FloatArray,
    n_seeds: int,
) -> tuple[float, int]:
    """Propagate L from seeds to all ancestors, oldest last; accumulate sum L_j^2 D_j.

    Ancestors have smaller indices than descendants, so popping the largest index first
    guarantees that all contributions to L[j] have arrived before j is processed. Returns
    (sum L^2 D, number of touched entries); the caller must zero L[touched[:k]].
    """
    size = 0
    nt = 0
    for k in range(n_seeds):
        j = seeds[k]
        if j < 0:
            continue
        if not in_heap[j]:
            in_heap[j] = True
            touched[nt] = j
            nt += 1
            size = _heap_push(heap, size, j)
        L[j] += seed_vals[k]
    acc = 0.0
    while size > 0:
        j = heap[0]
        size = _heap_pop(heap, size)
        in_heap[j] = False
        lj = L[j]
        acc += lj * lj * D[j]
        s = sire[j]
        if s >= 0:
            if L[s] == 0.0 and not in_heap[s]:
                touched[nt] = s
                nt += 1
            L[s] += 0.5 * lj
            if not in_heap[s]:
                in_heap[s] = True
                size = _heap_push(heap, size, s)
        d = dam[j]
        if d >= 0:
            if L[d] == 0.0 and not in_heap[d]:
                touched[nt] = d
                nt += 1
            L[d] += 0.5 * lj
            if not in_heap[d]:
                in_heap[d] = True
                size = _heap_push(heap, size, d)
    return acc, nt


@njit(cache=True)
def meuwissen_luo(
    sire: IntArray, dam: IntArray, F: FloatArray, D: FloatArray, start: int, shortcut: bool
) -> None:
    """Fill F[i], D[i] for i >= start in place (Meuwissen and Luo 1992)."""
    n = sire.shape[0]
    L = np.zeros(n)
    heap = np.empty(n + 2, np.int64)
    in_heap = np.zeros(n, np.bool_)
    touched = np.empty(n + 2, np.int64)
    seeds = np.empty(1, np.int64)
    vals = np.ones(1)
    for i in range(start, n):
        s = sire[i]
        d = dam[i]
        fs = F[s] if s >= 0 else -1.0
        fd = F[d] if d >= 0 else -1.0
        D[i] = 0.5 - 0.25 * (fs + fd)
        if s < 0 or d < 0:
            F[i] = 0.0
            continue
        if shortcut and i > 0 and s == sire[i - 1] and d == dam[i - 1]:
            F[i] = F[i - 1]
            continue
        seeds[0] = i
        acc, nt = _row_traverse(sire, dam, D, L, heap, in_heap, touched, seeds, vals, 1)
        F[i] = acc - 1.0
        for k in range(nt):
            L[touched[k]] = 0.0


@njit(cache=True)
def l_row(
    sire: IntArray, dam: IntArray, D: FloatArray, seeds: IntArray, seed_vals: FloatArray
) -> tuple[IntArray, FloatArray, float]:
    """Non-zero entries of the L row seeded by `seeds` (sorted by index) and sum L^2 D."""
    n = sire.shape[0]
    L = np.zeros(n)
    heap = np.empty(n + 2, np.int64)
    in_heap = np.zeros(n, np.bool_)
    touched = np.empty(n + 2, np.int64)
    acc, nt = _row_traverse(
        sire, dam, D, L, heap, in_heap, touched, seeds, seed_vals, seeds.shape[0]
    )
    idx = np.sort(touched[:nt])
    return idx, L[idx], acc


@njit(cache=True)
def colleau_T_transpose(sire: IntArray, dam: IntArray, u: FloatArray) -> None:
    """In place u <- T' u (youngest to oldest). Works on 1-D or 2-D (n, k) arrays."""
    for i in range(sire.shape[0] - 1, -1, -1):
        s = sire[i]
        d = dam[i]
        if s >= 0:
            u[s] += 0.5 * u[i]
        if d >= 0:
            u[d] += 0.5 * u[i]


@njit(cache=True)
def colleau_T(sire: IntArray, dam: IntArray, w: FloatArray) -> FloatArray:
    """y = T w (oldest to youngest)."""
    y = np.empty_like(w)
    for i in range(sire.shape[0]):
        y[i] = w[i]
        s = sire[i]
        d = dam[i]
        if s >= 0:
            y[i] += 0.5 * y[s]
        if d >= 0:
            y[i] += 0.5 * y[d]
    return y


@njit(cache=True)
def equivalent_generations(sire: IntArray, dam: IntArray) -> FloatArray:
    e = np.zeros(sire.shape[0])
    for i in range(sire.shape[0]):
        s = sire[i]
        d = dam[i]
        if s >= 0:
            e[i] += 0.5 * (1.0 + e[s])
        if d >= 0:
            e[i] += 0.5 * (1.0 + e[d])
    return e


@njit(cache=True)
def generation_depths(sire: IntArray, dam: IntArray) -> tuple[IntArray, IntArray]:
    """(maximum generations, complete generations) per animal."""
    n = sire.shape[0]
    mx = np.zeros(n, np.int64)
    comp = np.zeros(n, np.int64)
    for i in range(n):
        s = sire[i]
        d = dam[i]
        ms = mx[s] if s >= 0 else -1
        md = mx[d] if d >= 0 else -1
        if s >= 0 or d >= 0:
            mx[i] = 1 + max(ms, md)
        if s >= 0 and d >= 0:
            comp[i] = 1 + min(comp[s], comp[d])
    return mx, comp
