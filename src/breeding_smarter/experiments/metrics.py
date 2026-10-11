"""Per-year experiment metrics M1 to M11 (P8 section 3). Domestic population of one breed.

Observed metrics use the registry view (`ObservedRegistry`); truth metrics read the simulator
state (realised IBD, true genotypes, true breeding values).
"""

from __future__ import annotations

from typing import Any

import numpy as np

from breeding_smarter.experiments.observed import ObservedRegistry
from breeding_smarter.matching.context import DatasetContext
from breeding_smarter.pedigree.population import top_share
from breeding_smarter.sim.genetics import DogGenetics
from breeding_smarter.sim.state import DOMESTIC, SimState


def expected_heterozygosity(neutral: np.ndarray, chunk: int = 100) -> float:
    """Mean over loci of 1 - sum p_a^2 for allele arrays `[n, loci, 2]` (chunked by loci)."""
    n, L, _ = neutral.shape
    if n == 0:
        return float("nan")
    total = 0.0
    for lo in range(0, L, chunk):
        block = neutral[:, lo : lo + chunk, :]
        m = block.shape[1]
        alleles = block.transpose(1, 0, 2).reshape(m, 2 * n).astype(np.int32)
        k = int(alleles.max()) + 1
        flat = (np.arange(m, dtype=np.int64)[:, None] * k + alleles).ravel()
        p = np.bincount(flat, minlength=m * k).reshape(m, k) / (2.0 * n)
        total += float((1.0 - (p**2).sum(axis=1)).sum())
    return total / L


def living_he(state: SimState, genetics: DogGenetics, breed: int, year: int) -> float:
    a = state.animals
    holders = np.flatnonzero(genetics.row_of[: genetics.n] >= 0)
    m = holders[
        (a.breed[holders] == breed)
        & (a.subpop[holders] == DOMESTIC)
        & (a.death_year[holders] > year)
    ]
    return expected_heterozygosity(genetics.neutral[genetics.row_of[m]])


def year_metrics(
    state: SimState,
    genetics: DogGenetics,
    obs: ObservedRegistry,
    ctx: DatasetContext,
    breed: int,
    year: int,
    eligible: dict[str, int],
    he0: float,
) -> dict[str, float]:
    a = state.animals
    out: dict[str, Any] = {}
    cohort = np.flatnonzero((a.birth_year == year) & (a.breed == breed) & (a.subpop == DOMESTIC))
    idx = obs.idx(cohort)
    seen = idx >= 0
    out["M1_recorded_F"] = float(obs.F[idx[seen]].mean()) if seen.any() else np.nan
    out["M2_realised_ibd"] = float(a.f_true[cohort].mean()) if cohort.size else np.nan
    ref = ctx.reference(obs.breed_id, f"{year + 1}-01-01")
    out["M4_gene_diversity"] = 1.0 - ref.mean_mk
    he = living_he(state, genetics, breed, year)
    out["M5_he_neutral"] = he
    out["M5_he_relative"] = he / he0 if he0 else np.nan
    for j, locus in enumerate(genetics.loci.loci):
        g = genetics.geno[cohort, j]
        key = "M7" if not locus.testable else "M6"
        out[f"{key}_freq_{locus.id}"] = float(g.mean() / 2) if g.size else np.nan
        out[f"{key}_affected_{locus.id}"] = float((g == 2).mean()) if g.size else np.nan
    out["M8_mean_tbv_hd"] = float(genetics.tbv[cohort].mean()) if cohort.size else np.nan
    scr = np.flatnonzero(
        (genetics.screen_t[: genetics.n] >= year) & (genetics.screen_t[: genetics.n] < year + 1)
    )
    scr = scr[(a.breed[scr] == breed) & (a.subpop[scr] == DOMESTIC)]
    out["M8_de_share"] = float(np.isin(genetics.grade[scr], [3, 4]).mean()) if scr.size else np.nan
    win = np.flatnonzero(
        (a.birth_year > year - 5)
        & (a.birth_year <= year)
        & (a.breed == breed)
        & (a.subpop == DOMESTIC)
        & (a.sire >= 0)
    )
    _, counts = np.unique(a.sire[win], return_counts=True)
    out["M9_top_sire_share"] = float(counts.max() / counts.sum()) if counts.size else np.nan
    out["M9_top20_share"] = top_share(counts, 0.2)
    out["M9_n_sires_5y"] = float(counts.size)
    out["M9_n_above_fci"] = float((counts > 0.05 * win.size).sum()) if win.size else 0.0
    L = state.litters
    lit = np.flatnonzero((L.whelp_year == year) & (L.breed == breed) & (L.subpop == DOMESTIC))
    dams_used = np.unique(L.dam[lit]).size
    sires_used = np.unique(L.sire[lit]).size
    out["M10_share_dams_used"] = dams_used / eligible["dams"] if eligible["dams"] else np.nan
    out["M10_share_sires_used"] = sires_used / eligible["sires"] if eligible["sires"] else np.nan
    out["M11_litter_size"] = float(L.n_born[lit].mean()) if lit.size else np.nan
    out["n_births"] = float(cohort.size)
    out["n_litters"] = float(lit.size)
    return out
