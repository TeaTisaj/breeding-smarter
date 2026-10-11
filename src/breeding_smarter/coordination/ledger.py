"""Shared booking ledger: remaining quota per sire within a season (P12 decision D14)."""

from __future__ import annotations

import numpy as np

from breeding_smarter.pedigree.core import IntArray


class BookingLedger:
    """Each booking reduces the sire's remaining quota; over-booking raises."""

    def __init__(self, sires: IntArray, quotas: IntArray):
        self.sires = np.asarray(sires, dtype=np.int64)
        self.left = np.asarray(quotas, dtype=np.int64).copy()
        self._pos = {int(s): k for k, s in enumerate(self.sires)}

    def available(self) -> IntArray:
        """Sires with quota left."""
        return self.sires[self.left > 0]

    def remaining(self, sire: int) -> int:
        k = self._pos.get(int(sire))
        return 0 if k is None else int(self.left[k])

    def book(self, sire: int) -> None:
        k = self._pos.get(int(sire))
        if k is None or self.left[k] <= 0:
            raise ValueError(f"sire {sire} has no quota left")
        self.left[k] -= 1
