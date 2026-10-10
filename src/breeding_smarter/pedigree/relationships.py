"""Exact relationship classification on the recorded pedigree (used by the rule engine)."""

from __future__ import annotations

from collections import deque
from enum import StrEnum

import numpy as np
from numpy.typing import NDArray

from breeding_smarter.pedigree.core import IntArray, Pedigree


class Relationship(StrEnum):
    SELF = "SELF"
    PARENT_OFFSPRING = "PARENT_OFFSPRING"
    FULL_SIBLINGS = "FULL_SIBLINGS"
    HALF_SIBLINGS = "HALF_SIBLINGS"
    GRANDPARENT_GRANDCHILD = "GRANDPARENT_GRANDCHILD"
    AUNT_UNCLE_NIECE_NEPHEW = "AUNT_UNCLE_NIECE_NEPHEW"
    NONE_DETECTED = "NONE_DETECTED"


def _parents(ped: Pedigree, x: int) -> set[int]:
    return {int(p) for p in (ped.sire[x], ped.dam[x]) if p >= 0}


def _grandparents(ped: Pedigree, x: int) -> set[int]:
    return {g for p in _parents(ped, x) for g in _parents(ped, p)}


def _sibling_kind(ped: Pedigree, a: int, b: int) -> Relationship | None:
    same_s = ped.sire[a] >= 0 and ped.sire[a] == ped.sire[b]
    same_d = ped.dam[a] >= 0 and ped.dam[a] == ped.dam[b]
    if same_s and same_d:
        return Relationship.FULL_SIBLINGS
    if same_s or same_d:
        return Relationship.HALF_SIBLINGS
    return None


def relationship(ped: Pedigree, a: int, b: int) -> set[Relationship]:
    """Recorded relationships between a and b.

    Full siblings share both known parents; half siblings share exactly one known parent;
    grandparent if one is a known grandparent of the other. Aunt/uncle (informational): one is
    a full or half sibling of a parent of the other.
    """
    if a == b:
        return {Relationship.SELF}
    out: set[Relationship] = set()
    if a in _parents(ped, b) or b in _parents(ped, a):
        out.add(Relationship.PARENT_OFFSPRING)
    sib = _sibling_kind(ped, a, b)
    if sib is not None:
        out.add(sib)
    if a in _grandparents(ped, b) or b in _grandparents(ped, a):
        out.add(Relationship.GRANDPARENT_GRANDCHILD)
    for x, y in ((a, b), (b, a)):
        if any(p != x and _sibling_kind(ped, x, p) for p in _parents(ped, y)):
            out.add(Relationship.AUNT_UNCLE_NIECE_NEPHEW)
    return out or {Relationship.NONE_DETECTED}


def _ancestor_depths(ped: Pedigree, x: int, max_depth: int) -> dict[int, int]:
    depth = {x: 0}
    q = deque([x])
    while q:
        y = q.popleft()
        if depth[y] >= max_depth:
            continue
        for p in _parents(ped, y):
            if p not in depth:
                depth[p] = depth[y] + 1
                q.append(p)
    return depth


def nearest_common_ancestor(
    ped: Pedigree, a: int, b: int, max_depth: int = 6
) -> tuple[int, int, int] | None:
    """(ancestor, generations from a, generations from b) of the nearest common ancestor.

    Breadth-first search upwards from both animals (an animal is its own ancestor at depth 0).
    Nearest = smallest sum of generations, ties broken by the smaller maximum, then by index.
    None if no common ancestor within `max_depth` generations.
    """
    da = _ancestor_depths(ped, a, max_depth)
    db = _ancestor_depths(ped, b, max_depth)
    common = set(da) & set(db)
    if not common:
        return None
    best = min(common, key=lambda c: (da[c] + db[c], max(da[c], db[c]), c))
    return best, da[best], db[best]


def generations_to_nearest_common_ancestor(
    ped: Pedigree, a: int, b: int, max_depth: int = 6
) -> int | None:
    """Sum of generations from a and from b to their nearest common ancestor (None if none)."""
    nca = nearest_common_ancestor(ped, a, b, max_depth)
    return None if nca is None else nca[1] + nca[2]


def close_relative_flags(
    ped: Pedigree, dam: int, sires: IntArray
) -> dict[Relationship, NDArray[np.bool_]]:
    """Vectorised relationship flags of one animal (`dam`) against many candidates.

    Same definitions as `relationship`. Used by the rule engine and the simulator market.
    """
    s = np.asarray(sires, dtype=np.int64)
    S, Dm = ped.sire, ped.dam

    def par(x: IntArray | int, arr: IntArray) -> IntArray:
        x = np.asarray(x)
        return np.where(x >= 0, arr[np.maximum(x, 0)], -1)

    ds, dd = int(S[dam]), int(Dm[dam])
    cs, cd = S[s], Dm[s]
    po = (cs == dam) | (cd == dam) | (s == ds) | (s == dd)
    same_s = (ds >= 0) & (cs == ds)
    same_d = (dd >= 0) & (cd == dd)
    full = same_s & same_d
    half = (same_s | same_d) & ~full
    dam_gp = {int(g) for g in (par(ds, S), par(ds, Dm), par(dd, S), par(dd, Dm)) if g >= 0}
    gp = np.isin(s, np.array(sorted(dam_gp), dtype=np.int64))
    cand_gp = np.stack([par(cs, S), par(cs, Dm), par(cd, S), par(cd, Dm)])
    gp |= (cand_gp == dam).any(axis=0)
    return {
        Relationship.PARENT_OFFSPRING: po,
        Relationship.FULL_SIBLINGS: full,
        Relationship.HALF_SIBLINGS: half,
        Relationship.GRANDPARENT_GRANDCHILD: gp,
    }


def pairwise_close_flags(
    sire_of: IntArray, dam_of: IntArray, dams: IntArray, sires: IntArray
) -> NDArray[np.bool_]:
    """Element-wise: is `dams[k] x sires[k]` a parent-offspring, full- or half-sibling or
    grandparent-grandchild pair? (`sire_of`/`dam_of` are the parent arrays, -1 unknown.)

    Same definitions as `relationship`; vectorised over pairs.
    """
    d = np.asarray(dams, dtype=np.int64)
    s = np.asarray(sires, dtype=np.int64)

    def par(x: IntArray, arr: IntArray) -> IntArray:
        return np.where(x >= 0, arr[np.maximum(x, 0)], -1)

    ds, dd, ss, sd = par(d, sire_of), par(d, dam_of), par(s, sire_of), par(s, dam_of)
    po = (ds == s) | (sd == d)
    sib = ((ds >= 0) & (ds == ss)) | ((dd >= 0) & (dd == sd))
    gp = (par(ds, sire_of) == s) | (par(dd, sire_of) == s)
    gp |= (par(ss, dam_of) == d) | (par(sd, dam_of) == d)
    return np.asarray(po | sib | gp)
