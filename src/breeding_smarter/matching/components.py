"""Vectorised score components for one dam vs many sires (P7 task 7.3).

| component  | raw value                                  | sub-score in [0, 1]                    |
|------------|--------------------------------------------|----------------------------------------|
| inbreeding | F_off = f(s, d)                            | 1 below f_low, 0 above f_high, linear  |
| diversity  | MK_off = (MK_s + MK_d) / 2                 | 1 - Phi((MK_off - mean) / sd)          |
| health     | P_any = 1 - prod(1 - t_s t_d penetrance)   | 1 - min(1, P_any / 0.25)               |
| ebv        | (EBV_s + EBV_d) / 2, missing = 100         | Phi((index - 100) / 10)                |
| sire_use   | offspring_5y / (0.05 breed regs 5y)        | 1 - min(1, ratio)                      |
| depth      | (EqG_s + EqG_d) / 2                        | min(1, value / eqg_target)             |

Transmission probability t: 0 clear, 0.5 carrier, 1 affected, breed allele frequency q if
unknown. The frequency is estimated from tested animals and is biased by who gets tested.
Untestable loci (e.g. NOVEL_X in the synthetic truth) are never visible here.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy.special import ndtr

from breeding_smarter.matching.config import COMPONENTS, ScoringConfig
from breeding_smarter.matching.context import BreedReference, DatasetContext
from breeding_smarter.pedigree.core import FloatArray, IntArray


@dataclass
class Components:
    sires: IntArray
    f_off: FloatArray
    mk_off: FloatArray
    p_aff: FloatArray  # [k, loci]
    p_carrier: FloatArray  # [k, loci]
    p_any: FloatArray
    ebv_mean: FloatArray
    ebv_missing: NDArray[np.bool_]
    sire_offspring_5y: FloatArray
    sire_use_ratio: FloatArray
    depth: FloatArray
    sub: dict[str, FloatArray]

    def total(self, scoring: ScoringConfig) -> FloatArray:
        w = scoring.weights.value
        return np.asarray(100.0 * sum(w[c] * self.sub[c] for c in COMPONENTS), dtype=float)

    def points(self, scoring: ScoringConfig, k: int) -> dict[str, float]:
        w = scoring.weights.value
        return {c: 100.0 * w[c] * float(self.sub[c][k]) for c in COMPONENTS}


def transmission(geno: NDArray[np.int8], q: FloatArray) -> FloatArray:
    """Probability of transmitting the risk allele: genotype / 2, or q if unknown."""
    g = geno.astype(float)
    return np.where(geno >= 0, g / 2.0, q[None, :] if g.ndim == 2 else q)


def inbreeding_subscore(f: FloatArray, scoring: ScoringConfig) -> FloatArray:
    lo, hi = scoring.inbreeding.f_low.value, scoring.inbreeding.f_high.value
    return np.asarray(np.clip((hi - f) / (hi - lo), 0.0, 1.0))


def compute_components(
    ctx: DatasetContext,
    dam: int,
    sires: IntArray,
    day: int,
    ref: BreedReference,
    scoring: ScoringConfig,
) -> Components:
    sires = np.asarray(sires, dtype=np.int64)
    f_off = ctx.rules.kinship_row(dam)[sires]
    mk_off = 0.5 * (ref.mk[sires] + ref.mk[dam])
    t_s = transmission(ctx.geno[sires], ref.allele_freq)
    t_d = transmission(ctx.geno[dam : dam + 1], ref.allele_freq)
    p_aff = t_s * t_d * ctx.penetrance[None, :]
    p_carrier = t_s * (1 - t_d) + t_d * (1 - t_s)
    p_any = 1.0 - np.prod(1.0 - p_aff, axis=1) if p_aff.shape[1] else np.zeros(sires.size)
    e_s, e_d = ctx.ebv_index[sires], ctx.ebv_index[dam]
    missing = np.isnan(e_s) | np.isnan(e_d)
    mean_idx = scoring.ebv.index_mean.value
    ebv = 0.5 * (np.nan_to_num(e_s, nan=mean_idx) + (mean_idx if np.isnan(e_d) else e_d))
    su = scoring.sire_use
    since = day - int(365.25 * su.window_years.value)
    off = ctx.rules.sire_offspring.count_before(sires, day, since).astype(float)
    bcode = int(ctx.ped.breed[dam])
    regs = float(ctx.rules.breed_births.count_before(np.array([bcode]), day, since)[0])
    ratio = off / max(su.fci_share.value * regs, 1e-9)
    depth = 0.5 * (ctx.eqg[sires] + ctx.eqg[dam])
    sub = {
        "inbreeding": inbreeding_subscore(f_off, scoring),
        "diversity": 1.0 - ndtr((mk_off - ref.mean_mk) / ref.sd_mk),
        "health": 1.0 - np.minimum(1.0, p_any / scoring.health.p_any_zero_score.value),
        "ebv": ndtr((ebv - mean_idx) / scoring.ebv.index_sd.value),
        "sire_use": 1.0 - np.minimum(1.0, ratio),
        "depth": np.minimum(1.0, depth / scoring.depth.eqg_target.value),
    }
    return Components(
        sires=sires,
        f_off=f_off,
        mk_off=mk_off,
        p_aff=p_aff,
        p_carrier=p_carrier,
        p_any=p_any,
        ebv_mean=ebv,
        ebv_missing=missing,
        sire_offspring_5y=off,
        sire_use_ratio=ratio,
        depth=depth,
        sub=sub,
    )
