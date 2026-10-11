"""One pure function per calibration metric (P5 task 5.2).

Each takes a loaded `RunData` and returns `MetricResult`: per-breed named components plus the
data behind them (for figures). Population formulas are reused from `pedigree.population`.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

from breeding_smarter.calibration.data import RunData
from breeding_smarter.pedigree.population import (
    generation_interval,
    ne_census,
    ne_individual_delta_f,
    sire_usage,
    top_share,
)

COHORT = (2016, 2025)
COHORT_EARLY = (2005, 2015)


@dataclass
class MetricResult:
    values: dict[str, dict[str, Any]]
    data: dict[str, Any] = field(default_factory=dict)


def _breed_mask(rd: RunData, breed: str) -> np.ndarray:
    return np.asarray(rd.animals["breed_id"].to_numpy() == breed)


def _born(rd: RunData, lo: int, hi: int) -> np.ndarray:
    y = rd.animals["year"].to_numpy()
    return np.asarray((y >= lo) & (y <= hi))


def litter_size(rd: RunData) -> MetricResult:
    lit = rd.litters
    f_ibd = rd.true_f_of_idx()[1]
    out = {}
    for b in rd.breeds:
        x = lit.loc[lit["breed_id"] == b, "n_born"]
        cfg = rd.breed_cfg(b).reproduction.litter_size_mean.value
        dams = lit.loc[(lit["breed_id"] == b), "dam_idx"].to_numpy()
        out[b] = {
            "mean": float(x.mean()),
            "deviation_from_config": float(x.mean() - cfg),
            "config_mean": cfg,
            "mean_dam_f_ibd": float(f_ibd[dams].mean()),
        }
    return MetricResult(out, {"litters": lit[["breed_id", "n_born"]]})


def perinatal_loss_share(rd: RunData) -> MetricResult:
    lit = rd.litters
    out = {}
    for b in rd.breeds:
        g = lit[lit["breed_id"] == b]
        out[b] = {"share": float((g["n_born_alive"] < g["n_born"]).mean())}
    return MetricResult(out)


def _parents_set(rd: RunData) -> set[int]:
    a = rd.animals
    return set(a["sire_idx"].dropna().astype(int)) | set(a["dam_idx"].dropna().astype(int))


def share_with_offspring(rd: RunData) -> MetricResult:
    parents = _parents_set(rd)
    out = {}
    for b in rd.breeds:
        m = _breed_mask(rd, b) & rd.domestic & _born(rd, *COHORT_EARLY)
        idx = rd.animals["idx"].to_numpy()[m]
        out[b] = {"share": float(np.isin(idx, list(parents)).mean()) if idx.size else np.nan}
    return MetricResult(out)


def share_males_sired(rd: RunData) -> MetricResult:
    sires = set(rd.litters["sire_idx"].astype(int))
    out = {}
    a = rd.animals
    for b in rd.breeds:
        m = _breed_mask(rd, b) & rd.domestic & _born(rd, *COHORT_EARLY)
        m &= a["sex"].to_numpy() == "M"
        idx = a["idx"].to_numpy()[m]
        out[b] = {"share": float(np.isin(idx, list(sires)).mean()) if idx.size else np.nan}
    return MetricResult(out)


def _sire_counts(rd: RunData, breed: str, lo: int, hi: int) -> np.ndarray:
    a = rd.animals
    m = _breed_mask(rd, breed) & _born(rd, lo, hi) & a["sire_idx"].notna().to_numpy()
    return a.loc[m, "sire_idx"].astype(int).value_counts().to_numpy()


def top20_sire_share(rd: RunData) -> MetricResult:
    out, data = {}, {}
    for b in rd.breeds:
        c = _sire_counts(rd, b, *COHORT)
        out[b] = {"share": top_share(c, 0.2), "n_sires": int(c.size)}
        data[b] = c
    return MetricResult(out, {"counts": data})


def fci_threshold_exceeded(rd: RunData) -> MetricResult:
    out = {}
    for b in rd.breeds:
        usages = [sire_usage(rd.ped, y, 5, b) for y in (2020, 2025)]
        out[b] = {
            "any_above": any(u.n_above_fci > 0 for u in usages),
            "max_ratio": max(u.max_fci_ratio for u in usages),
            "n_above_2025": usages[-1].n_above_fci,
        }
    return MetricResult(out)


def _cohort(rd: RunData, b: str) -> np.ndarray:
    return _breed_mask(rd, b) & rd.domestic & _born(rd, *COHORT)


def ne_delta_f(rd: RunData) -> MetricResult:
    out = {}
    for b in rd.breeds:
        ne = ne_individual_delta_f(rd.F, rd.eqg, _cohort(rd, b))
        out[b] = {"ne": ne.ne, "mean_delta_f": ne.mean_delta_f, "n_used": ne.n_used}
    return MetricResult(out)


def ne_census_metric(rd: RunData) -> MetricResult:
    out = {}
    for b in rd.breeds:
        ne = ne_census(rd.ped, _cohort(rd, b))
        out[b] = {
            "ne": ne.ne,
            "n_sires": ne.n_sires,
            "n_dams": ne.n_dams,
            "fkc_flag_le_200": ne.ne <= 200,
        }
    return MetricResult(out)


def generation_interval_metric(rd: RunData) -> MetricResult:
    out = {}
    for b in rd.breeds:
        gi = generation_interval(rd.ped, _cohort(rd, b))
        out[b] = {"overall": gi.overall, "sire": gi.sire_pathway, "dam": gi.dam_pathway}
    return MetricResult(out)


def _f_by_year(rd: RunData) -> pd.DataFrame:
    f_ped, f_ibd = rd.true_f_of_idx()
    df = pd.DataFrame(
        {
            "breed_id": rd.animals["breed_id"].to_numpy(),
            "year": rd.animals["year"].to_numpy(),
            "recorded": rd.F,
            "true_pedigree": f_ped,
            "realised_ibd": f_ibd,
        }
    )[rd.domestic]
    return df.groupby(["breed_id", "year"])[["recorded", "true_pedigree", "realised_ibd"]].mean()


def _delta_f(f0: float, f1: float, years: float, gi: float) -> float:
    """Rate of inbreeding per generation from mean F at two times."""
    return float(1.0 - ((1.0 - f1) / (1.0 - f0)) ** (gi / years))


def delta_f_periods(rd: RunData) -> MetricResult:
    by = _f_by_year(rd)
    gi = rd.setup.sim.generation_interval_years.value
    out = {}
    for b in rd.breeds:
        s = by.loc[b, "true_pedigree"]
        early = _delta_f(float(s.get(1985, np.nan)), float(s.get(1995, np.nan)), 10, gi)
        late = _delta_f(float(s.get(2010, np.nan)), float(s.get(2020, np.nan)), 10, gi)
        out[b] = {
            "delta_f_1985_1995": early,
            "delta_f_2010_2020": late,
            "early_higher": bool(early > late),
        }
    return MetricResult(out, {"f_by_year": by})


def recorded_vs_true_f(rd: RunData) -> MetricResult:
    by = _f_by_year(rd)
    out = {}
    for b in rd.breeds:
        row = by.loc[(b, 2025)]
        out[b] = {
            "recorded": float(row["recorded"]),
            "true_pedigree": float(row["true_pedigree"]),
            "realised_ibd": float(row["realised_ibd"]),
            "recorded_lower": bool(row["recorded"] < row["true_pedigree"]),
        }
    return MetricResult(out, {"f_by_year": by})


def engine_vs_gene_drop(rd: RunData, min_n: int = 50) -> MetricResult:
    t = rd.truth
    df = pd.DataFrame(
        {
            "breed_id": t["breed_id"].to_numpy(),
            "decade": (t["birth_year"].to_numpy() // 10) * 10,
            "ibd": t["f_true_ibd"].to_numpy(),
            "ped": rd.F_true,
        }
    )
    g = df.groupby(["breed_id", "decade"]).agg(
        ibd=("ibd", "mean"), ped=("ped", "mean"), n=("ibd", "size")
    )
    g = g[g["n"] >= min_n]
    g["diff"] = g["ibd"] - g["ped"]
    out = {}
    for b in rd.breeds:
        gb = g.loc[b]
        out[b] = {
            "max_abs_diff": float(gb["diff"].abs().max()),
            "worst_decade": int(gb["diff"].abs().idxmax()),
        }
    return MetricResult(out, {"by_decade": g})


def ibd_regression(rd: RunData) -> MetricResult:
    t = rd.truth
    out, data = {}, {}
    for b in rd.breeds:
        m = (t["breed_id"].to_numpy() == b) & (t["birth_year"].to_numpy() > 1980)
        x, y = rd.F_true[m], t["f_true_ibd"].to_numpy()[m]
        slope, intercept = np.polyfit(x, y, 1)
        out[b] = {
            "slope": float(slope),
            "intercept": float(intercept),
            "r": float(np.corrcoef(x, y)[0, 1]),
        }
        data[b] = (x, y)
    return MetricResult(out, {"xy": data})


def _hd(rd: RunData) -> pd.DataFrame:
    h = rd.health.merge(rd.animals[["idx", "breed_id"]], on="idx")
    h["year"] = h["test_date"].dt.year
    return h


def hd_de_trend(rd: RunData) -> MetricResult:
    h = _hd(rd)
    out = {}
    for b in rd.breeds:
        start = rd.breed_cfg(b).health.hd_screening_start_year.value
        g = h[h["breed_id"] == b]
        de = g["result"].isin(["D", "E"])
        first = float(de[(g["year"] >= start) & (g["year"] < start + 5)].mean())
        last = float(de[(g["year"] >= 2021) & (g["year"] <= 2025)].mean())
        out[b] = {"de_first_5y": first, "de_2021_2025": last, "decreased": bool(last < first)}
    return MetricResult(out, {"health": h})


def ebv_quality(rd: RunData) -> MetricResult:
    tb = rd.truth.dropna(subset=["idx"]).set_index("idx")["tbv_hd"]
    e = rd.ebv.set_index("idx")
    screened = set(rd.health["idx"])
    out = {}
    for b in rd.breeds:
        ids = [i for i in rd.animals.loc[_breed_mask(rd, b), "idx"] if i in screened]
        ids = [i for i in ids if i in e.index]
        r = float(np.corrcoef(e.loc[ids, "ebv_index"], -tb.loc[ids])[0, 1])
        acc = float(e.loc[ids, "accuracy"].mean())
        out[b] = {"corr_ebv_tbv": r, "mean_accuracy": acc, "abs_gap": abs(r - acc), "n": len(ids)}
    return MetricResult(out)


def missingness(rd: RunData) -> MetricResult:
    a = rd.animals[rd.domestic].copy()
    a["decade"] = (a["year"] // 10) * 10
    a["hur"] = a["studbook"] == "HUR"
    a["unknown_parent"] = a["sire_idx"].isna() | a["dam_idx"].isna()
    g = (
        a[a["year"] >= 1980]
        .groupby(["breed_id", "decade"])[["hur", "import_flag", "unknown_parent"]]
        .mean()
    )
    out = {}
    for b in rd.breeds:
        last = g.loc[b].iloc[-1]
        out[b] = {
            "share_hur_last_decade": float(last["hur"]),
            "share_import_last_decade": float(last["import_flag"]),
            "share_unknown_parent_last_decade": float(last["unknown_parent"]),
        }
    return MetricResult(out, {"by_decade": g})


def mean_ibd_2025(rd: RunData) -> MetricResult:
    by = _f_by_year(rd)
    return MetricResult(
        {
            b: {
                "mean_ibd": float(by.loc[(b, 2025), "realised_ibd"]),
                "published_genomic_median": 0.25,
            }
            for b in rd.breeds
        }
    )


METRICS: dict[str, Callable[[RunData], MetricResult]] = {
    "litter_size": litter_size,
    "perinatal_loss_share": perinatal_loss_share,
    "share_with_offspring": share_with_offspring,
    "share_males_sired": share_males_sired,
    "top20_sire_share": top20_sire_share,
    "fci_threshold_exceeded": fci_threshold_exceeded,
    "ne_delta_f": ne_delta_f,
    "ne_census": ne_census_metric,
    "generation_interval": generation_interval_metric,
    "delta_f_periods": delta_f_periods,
    "recorded_vs_true_f": recorded_vs_true_f,
    "engine_vs_gene_drop": engine_vs_gene_drop,
    "ibd_regression": ibd_regression,
    "hd_de_trend": hd_de_trend,
    "ebv_quality": ebv_quality,
    "missingness": missingness,
    "mean_ibd_2025": mean_ibd_2025,
}


def allele_frequencies(rd: RunData) -> MetricResult:
    """Risk-allele frequency and carrier share of registered births in 1980 and 2026 (truth)."""
    g = rd.genotypes().merge(rd.truth[["gid", "breed_id", "birth_year", "is_hidden"]], on="gid")
    g = g[~g["is_hidden"] & g["birth_year"].isin([1980, 2026])]
    freq = g.groupby(["breed_id", "locus_id", "birth_year"])["n_risk_alleles"].mean() / 2
    carrier = (
        g.assign(c=g["n_risk_alleles"] == 1)
        .groupby(["breed_id", "locus_id", "birth_year"])["c"]
        .mean()
    )
    out = {}
    for b in rd.breeds:
        comps: dict[str, Any] = {}
        for locus in sorted(g["locus_id"].unique()):
            comps[f"{locus}_freq_1980"] = float(freq.get((b, locus, 1980), np.nan))
            comps[f"{locus}_freq_2026"] = float(freq.get((b, locus, 2026), np.nan))
        out[b] = comps
    return MetricResult(out, {"freq": freq, "carrier": carrier})


METRICS["allele_frequencies"] = allele_frequencies
