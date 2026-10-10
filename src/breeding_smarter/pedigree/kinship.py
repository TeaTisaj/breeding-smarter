"""Kinship products without forming A (Colleau 2002; Sargolzaei et al. 2005)."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from breeding_smarter.pedigree import _kernels as K
from breeding_smarter.pedigree.core import FloatArray, Pedigree


def A_times(ped: Pedigree, D: FloatArray, x: FloatArray) -> FloatArray:
    """`y = A x` in O(n) via `A = T D T'` (Colleau's indirect method).

    Step 1: `u = T' x` (youngest to oldest: each animal passes half its value to each known
    parent). Step 2: `w = D u`. Step 3: `y = T w` (oldest to youngest: `y_i = w_i + (y_s +
    y_d) / 2`). `x` may be (n,) or (n, k).
    """
    u = np.array(x, dtype=np.float64, copy=True, order="C")
    K.colleau_T_transpose(ped.sire, ped.dam, u)
    w = (D * u.T).T if u.ndim == 2 else D * u
    return K.colleau_T(ped.sire, ped.dam, np.ascontiguousarray(w))


def kinship_to_all(ped: Pedigree, D: FloatArray, a: int) -> FloatArray:
    """Kinship of animal `a` with every animal: `0.5 A e_a` (one O(n) pass)."""
    e = np.zeros(ped.n)
    e[a] = 1.0
    return 0.5 * A_times(ped, D, e)


def mean_kinship(ped: Pedigree, D: FloatArray, ref_mask: NDArray[np.bool_]) -> FloatArray:
    """Mean kinship of every animal to the reference population: `0.5 A (r / N)`.

    Self-kinship is included for reference members (PMx convention, Ballou and Lacy 1995):
    `MK_i = (1/N) sum_{j in ref} f_ij`.
    """
    ref = np.asarray(ref_mask, dtype=np.float64)
    total = ref.sum()
    if total == 0:
        raise ValueError("empty reference population")
    return 0.5 * A_times(ped, D, ref / total)


def kinship_matrix(ped: Pedigree, D: FloatArray, members: NDArray[np.int64]) -> FloatArray:
    """Dense kinship matrix among `members` (K up to about 2000).

    Prunes to the ancestors of the members first; F and D are unchanged by pruning, so the
    given D is re-indexed. Then one multi-column Colleau pass.
    """
    members = np.asarray(members, dtype=np.int64)
    pruned, old_to_new = ped.prune(members)
    keep = old_to_new >= 0
    D_p = D[keep]
    new_idx = old_to_new[members]
    X = np.zeros((pruned.n, members.shape[0]))
    X[new_idx, np.arange(members.shape[0])] = 1.0
    Y = A_times(pruned, D_p, X)
    return 0.5 * Y[new_idx, :]


def contributions(ped_with_phantoms: Pedigree, ref_mask: NDArray[np.bool_]) -> FloatArray:
    """Expected genetic contributions `u = T' (r / N)` (step 1 of Colleau only).

    For founders (both parents unknown) `u_k` is the expected genetic contribution `p_k` of
    founder k to the reference population; on a pedigree with phantom parents the founder
    contributions sum to 1 (Lacy 1989).
    """
    ref = np.asarray(ref_mask, dtype=np.float64)
    u = ref / ref.sum()
    K.colleau_T_transpose(ped_with_phantoms.sire, ped_with_phantoms.dam, u)
    return u
