"""Population metrics: generation interval, Ne, gene diversity, founders, sire usage."""

from __future__ import annotations

import math

import numpy as np
from numpy.typing import NDArray
from pydantic import BaseModel

from breeding_smarter.pedigree.core import FloatArray, IntArray, Pedigree
from breeding_smarter.pedigree.kinship import contributions, mean_kinship

BoolArray = NDArray[np.bool_]


class GenerationInterval(BaseModel):
    overall: float
    sire_pathway: float
    dam_pathway: float
    n_parent_links: int


class NeEstimate(BaseModel):
    method: str
    ne: float
    n_used: int
    n_excluded: int = 0
    mean_delta_f: float | None = None
    n_sires: int | None = None
    n_dams: int | None = None


class FounderStats(BaseModel):
    n_founders_contributing: int
    fe: float
    fg: float
    sum_contributions: float
    top_founders: list[tuple[int, float]]


class SireUsage(BaseModel):
    year: int
    window_years: int
    n_offspring: int
    n_sires: int
    top_sire_share: float
    top20_share: float
    gini: float
    n_males_breeding_age: int
    share_males_used: float
    n_above_fci: int
    max_fci_ratio: float


class PopulationReport(BaseModel):
    breed: str
    year: int
    reference_years: tuple[int, int]
    n_reference: int
    mean_F: float
    mean_mk: float
    mean_eqg: float
    gene_diversity: float
    ne_delta_f: NeEstimate
    ne_census: NeEstimate
    generation_interval: GenerationInterval
    founders: FounderStats
    sire_usage: SireUsage


def reference_mask(
    ped: Pedigree, year: int, interval_years: float, breed_id: str | None = None
) -> BoolArray:
    """Animals born in the last generation interval up to `year`: `year - L < birth <= year`."""
    by = ped.birth_year.astype(np.int64)
    mask = (by > year - interval_years) & (by <= year)
    if breed_id is not None:
        mask &= ped.breed_mask(breed_id)
    return np.asarray(mask)


def generation_interval(ped: Pedigree, ref_mask: BoolArray) -> GenerationInterval:
    """Mean age (years) of parents at the birth of reference animals (all pathways pooled).

    Also the sire and dam pathways separately. Uses birth years (integer resolution).
    """
    i = np.flatnonzero(ref_mask)
    ages = []
    out = []
    for par in (ped.sire, ped.dam):
        p = par[i]
        known = p >= 0
        a = ped.birth_year[i[known]].astype(float) - ped.birth_year[p[known]].astype(float)
        ages.append(a)
        out.append(float(a.mean()) if a.size else math.nan)
    pooled = np.concatenate(ages)
    return GenerationInterval(
        overall=float(pooled.mean()) if pooled.size else math.nan,
        sire_pathway=out[0],
        dam_pathway=out[1],
        n_parent_links=int(pooled.size),
    )


def ne_individual_delta_f(F: FloatArray, eqg: FloatArray, ref_mask: BoolArray) -> NeEstimate:
    """Ne from the individual increase in inbreeding (Gutiérrez et al. 2008, 2009).

    `dF_i = 1 - (1 - F_i)^(1 / (t_i - 1))` with `t_i = EqG_i`, for animals with `t_i > 1`;
    `Ne = 1 / (2 mean dF)`. Animals with `t_i <= 1` are excluded and counted.
    """
    sel = np.asarray(ref_mask, dtype=bool)
    t = eqg[sel]
    f = F[sel]
    use = t > 1
    df = 1.0 - np.power(1.0 - f[use], 1.0 / (t[use] - 1.0))
    mean_df = float(df.mean()) if df.size else math.nan
    ne = 1.0 / (2.0 * mean_df) if df.size and mean_df > 0 else math.inf
    return NeEstimate(
        method="individual delta F",
        ne=ne,
        n_used=int(use.sum()),
        n_excluded=int((~use).sum()),
        mean_delta_f=mean_df,
    )


def ne_census(ped: Pedigree, ref_mask: BoolArray) -> NeEstimate:
    """Census Ne of breeding animals: `4 Nm Nf / (Nm + Nf)` with Nm, Nf the distinct sires and
    dams of the reference cohort ("census (breeding animals)")."""
    i = np.flatnonzero(ref_mask)
    nm = int(np.unique(ped.sire[i][ped.sire[i] >= 0]).size)
    nf = int(np.unique(ped.dam[i][ped.dam[i] >= 0]).size)
    ne = 4.0 * nm * nf / (nm + nf) if nm + nf else 0.0
    return NeEstimate(
        method="census (breeding animals)", ne=ne, n_used=int(i.size), n_sires=nm, n_dams=nf
    )


def gene_diversity(mk: FloatArray, ref_mask: BoolArray) -> float:
    """`GD = 1 - mean(MK over the reference population)` (Lacy 1995)."""
    return float(1.0 - mk[np.asarray(ref_mask, dtype=bool)].mean())


def founder_stats(ped: Pedigree, ref_mask: BoolArray, D: FloatArray, top: int = 10) -> FounderStats:
    """Founder contributions, effective number of founders and founder genome equivalents.

    `p_k` from `contributions` on the pedigree with phantom parents (sums to 1);
    `fe = 1 / sum p_k^2` (Lacy 1989); `fg = 1 / (2 mean kinship of the reference population)`
    (Lacy 1995; Ballou and Lacy 1995), self-kinship included.
    """
    ph, old_to_new = ped.with_phantom_parents()
    ref_ph = np.zeros(ph.n, dtype=bool)
    ref_ph[old_to_new[np.asarray(ref_mask, dtype=bool)]] = True
    u = contributions(ph, ref_ph)
    founders = (ph.sire < 0) & (ph.dam < 0)
    p = u[founders]
    ids = ph.ids[founders]
    s = float(p.sum())
    if abs(s - 1.0) > 1e-9:
        raise AssertionError(f"founder contributions sum to {s}, expected 1")
    mk = mean_kinship(ped, D, ref_mask)
    fg = 1.0 / (2.0 * float(mk[np.asarray(ref_mask, dtype=bool)].mean()))
    order = np.argsort(-p, kind="stable")[:top]
    return FounderStats(
        n_founders_contributing=int((p > 0).sum()),
        fe=float(1.0 / np.sum(p**2)),
        fg=fg,
        sum_contributions=s,
        top_founders=[(int(ids[k]), float(p[k])) for k in order],
    )


def gini(x: NDArray[np.float64] | IntArray) -> float:
    """Gini coefficient of non-negative values (0 = equal)."""
    v = np.sort(np.asarray(x, dtype=float))
    n = v.size
    if n == 0 or v.sum() == 0:
        return 0.0
    i = np.arange(1, n + 1)
    return float(np.sum((2 * i - n - 1) * v) / (n * v.sum()))


def top_share(counts: NDArray[np.float64] | IntArray, fraction: float = 0.2) -> float:
    """Share of the total held by the top `fraction` of units (at least one unit)."""
    c = np.sort(np.asarray(counts, dtype=float))[::-1]
    if c.size == 0 or c.sum() == 0:
        return 0.0
    k = max(1, round(fraction * c.size))
    return float(c[:k].sum() / c.sum())


def offspring_per_sire(ped: Pedigree, mask: BoolArray) -> tuple[IntArray, IntArray]:
    """(sire indices, offspring counts) among the animals in `mask`."""
    s = ped.sire[np.asarray(mask, dtype=bool)]
    sires, counts = np.unique(s[s >= 0], return_counts=True)
    return sires.astype(np.int64), counts.astype(np.int64)


def sire_usage(
    ped: Pedigree,
    year: int,
    window_years: int = 5,
    breed_id: str | None = None,
    fci_share: float = 0.05,
    male_age_years: tuple[int, int] = (1, 12),
) -> SireUsage:
    """Sire concentration over the `window_years` up to `year`.

    Offspring per sire among animals born in the window; top-sire share, top-20% share, Gini,
    share of males of breeding age (born `year - max_age .. year - min_age`, mortality ignored)
    that sired at least one registered offspring in the window, and the FCI ratio
    `offspring / (fci_share * registrations in the window)` (fci-strategies: 5% in 5 years).
    """
    by = ped.birth_year.astype(np.int64)
    breed = ped.breed_mask(breed_id) if breed_id is not None else np.ones(ped.n, dtype=bool)
    win = breed & (by > year - window_years) & (by <= year)
    sires, counts = offspring_per_sire(ped, win)
    n_off = int(win.sum())
    lo, hi = male_age_years
    males = breed & (ped.sex == 1) & (by >= year - hi) & (by <= year - lo)
    n_males = int(males.sum())
    used = int(np.isin(np.flatnonzero(males), sires).sum())
    ratio = counts / (fci_share * n_off) if n_off else np.zeros(0)
    return SireUsage(
        year=year,
        window_years=window_years,
        n_offspring=n_off,
        n_sires=int(sires.size),
        top_sire_share=float(counts.max() / counts.sum()) if counts.size else 0.0,
        top20_share=top_share(counts),
        gini=gini(counts),
        n_males_breeding_age=n_males,
        share_males_used=used / n_males if n_males else 0.0,
        n_above_fci=int((ratio > 1).sum()),
        max_fci_ratio=float(ratio.max()) if ratio.size else 0.0,
    )


def population_report(
    ped: Pedigree,
    F: FloatArray,
    D: FloatArray,
    eqg: FloatArray,
    breed_id: str,
    year: int,
    interval_years: float = 4.5,
) -> PopulationReport:
    """All population metrics for one breed and reference cohort (`reference_mask`).

    Works on the breed sub-pedigree (breed animals plus ancestors); F, D and EqG are reused
    because pruning to ancestors does not change them.
    """
    sub, old_to_new = ped.prune(ped.breed_mask(breed_id))
    keep = old_to_new >= 0
    F_s, D_s, e_s = F[keep], D[keep], eqg[keep]
    ref = reference_mask(sub, year, interval_years, breed_id)
    if not ref.any():
        raise ValueError(f"no reference animals for {breed_id} in {year}")
    mk = mean_kinship(sub, D_s, ref)
    lo = math.floor(year - interval_years) + 1
    return PopulationReport(
        breed=breed_id,
        year=year,
        reference_years=(lo, year),
        n_reference=int(ref.sum()),
        mean_F=float(F_s[ref].mean()),
        mean_mk=float(mk[ref].mean()),
        mean_eqg=float(e_s[ref].mean()),
        gene_diversity=gene_diversity(mk, ref),
        ne_delta_f=ne_individual_delta_f(F_s, e_s, ref),
        ne_census=ne_census(sub, ref),
        generation_interval=generation_interval(sub, ref),
        founders=founder_stats(sub, ref, D_s),
        sire_usage=sire_usage(sub, year, 5, breed_id),
    )
