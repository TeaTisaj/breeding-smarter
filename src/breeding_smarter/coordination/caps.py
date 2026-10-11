"""Per-sire yearly litter caps scaled by mean kinship (P12 decision D9).

`cap_s = clip(round(cap_base * MK_ref / MK_s), 1, cap_base)`: sires at or below the reference
mean kinship get the full cap, more related sires proportionally fewer litters. Per-year caps
of 5 to 10 litters [windig-2013]; flat caps can backfire [leroy-rognon-2012], hence the scaling
(a project choice).
"""

from __future__ import annotations

import numpy as np

from breeding_smarter.pedigree.core import FloatArray, IntArray


def mk_scaled_caps(mk: FloatArray, mk_ref: float, cap_base: int, scale: bool = True) -> IntArray:
    """Litters per sire this year; missing or zero MK gets the full cap."""
    mk = np.asarray(mk, dtype=float)
    if not scale:
        return np.full(mk.size, cap_base, dtype=np.int64)
    with np.errstate(divide="ignore", invalid="ignore"):
        raw = np.where((mk > 0) & np.isfinite(mk), cap_base * mk_ref / mk, cap_base)
    return np.clip(np.round(raw), 1, cap_base).astype(np.int64)
