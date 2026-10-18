"""Experiment summaries: means with 95% t-intervals, Ne, paired differences vs S1 (task 8.4).

All results are in-silico, on synthetic populations.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from breeding_smarter.experiments.runner import load_results, report_dir

KEY_METRICS = {
    "M2_realised_ibd": "Realised inbreeding (IBD, truth)",
    "M1_recorded_F": "Recorded pedigree COI",
    "M3_ne": "Ne from realised IBD (truth)",
    "M4_gene_diversity": "Gene diversity (recorded pedigree)",
    "M5_he_relative": "Neutral heterozygosity vs 2026 (truth)",
    "M8_mean_tbv_hd": "Mean true HD breeding value (lower is better)",
    "M9_top20_share": "Offspring from top 20% of sires",
    "M10_share_sires_used": "Share of eligible males used",
    "M11_litter_size": "Mean litter size",
}
CAPTION = "In-silico results on synthetic populations."


def t_interval(x: np.ndarray, level: float = 0.95) -> tuple[float, float, float]:
    """(mean, lower, upper) of a Student t interval; nan bounds for fewer than 2 values."""
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    if x.size == 0:
        return (np.nan, np.nan, np.nan)
    m = float(x.mean())
    if x.size < 2:
        return (m, np.nan, np.nan)
    h = float(stats.t.ppf(0.5 + level / 2, x.size - 1) * x.std(ddof=1) / np.sqrt(x.size))
    return (m, m - h, m + h)


def ne_from_series(gen: np.ndarray, f: np.ndarray) -> tuple[float, float]:
    """(delta F per generation, Ne): regression of -log(1 - F) on generation; Ne = 1/(2 dF)."""
    ok = np.isfinite(f) & (f < 1)
    if ok.sum() < 3:
        return (np.nan, np.nan)
    slope = np.polyfit(gen[ok], -np.log(1.0 - f[ok]), 1)[0]
    dF = 1.0 - np.exp(-slope)
    return (float(dF), float(1.0 / (2.0 * dF)) if dF > 0 else np.inf)


def by_generation(df: pd.DataFrame, gens: range = range(1, 11)) -> pd.DataFrame:
    """Per replicate: mean of each metric over the years of generation g (g - 0.5, g + 0.5]."""
    rows = []
    keys = ["breed", "strategy", "adoption", "replicate", "metric"]
    for g in gens:
        w = df[(df["generation"] > g - 0.5) & (df["generation"] <= g + 0.5)]
        m = w.groupby(keys)["value"].mean().reset_index()
        m["generation"] = g
        rows.append(m)
    return pd.concat(rows, ignore_index=True)


def ne_table(df: pd.DataFrame, upto: float = 10.0) -> pd.DataFrame:
    keys = ["breed", "strategy", "adoption", "replicate"]
    out = []
    for k, g in df[(df["metric"] == "M2_realised_ibd") & (df["generation"] <= upto)].groupby(keys):
        dF, ne = ne_from_series(g["generation"].to_numpy(), g["value"].to_numpy())
        out.append(dict(zip(keys, k, strict=True)) | {"delta_f": dF, "ne": ne})
    return pd.DataFrame(out)


WINDOWS = {"early": (0.0, 5.0), "late": (5.0, 10.0)}
RATE_SOURCES = {"M2_realised_ibd": "f", "M12_realised_coancestry": "c"}


def rate_table(df: pd.DataFrame, windows: dict[str, tuple[float, float]] = WINDOWS) -> pd.DataFrame:
    """Per replicate: rate per generation of realised IBD (dF) and realised coancestry (dC) in
    each window `(lo, hi]` of generations, by regression of -log(1 - x) on generation, and the
    implied Ne = 1 / (2 rate) (P12 task 12.9). Long format with metric names
    `R_delta_<f|c>_<window>` and `R_ne_<f|c>_<window>` (infinite Ne for non-positive rates is
    stored as nan and counted by `n`)."""
    keys = ["breed", "strategy", "adoption", "replicate"]
    rows = []
    for metric, tag in RATE_SOURCES.items():
        sub = df[df["metric"] == metric]
        for name, (lo, hi) in windows.items():
            w = sub[(sub["generation"] > lo) & (sub["generation"] <= hi)]
            for k, g in w.groupby(keys):
                rate, ne = ne_from_series(g["generation"].to_numpy(), g["value"].to_numpy())
                base = dict(zip(keys, k, strict=True))
                rows.append(base | {"metric": f"R_delta_{tag}_{name}", "value": rate})
                rows.append(
                    base
                    | {"metric": f"R_ne_{tag}_{name}", "value": ne if np.isfinite(ne) else np.nan}
                )
    out = pd.DataFrame(rows)
    out["generation"] = 10
    return out


def summarise(per_gen: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for k, g in per_gen.groupby(["breed", "strategy", "adoption", "generation", "metric"]):
        m, lo, hi = t_interval(g["value"].to_numpy())
        rows.append(
            dict(zip(["breed", "strategy", "adoption", "generation", "metric"], k, strict=True))
            | {"mean": m, "lo": lo, "hi": hi, "n": len(g)}
        )
    return pd.DataFrame(rows)


def paired_vs(
    per_gen: pd.DataFrame, ref: str = "S1", gens: tuple[int, ...] = (5, 10)
) -> pd.DataFrame:
    """Paired differences (strategy - ref) by replicate at the given generations."""
    sub = per_gen[per_gen["generation"].isin(gens) & (per_gen["adoption"] == 1.0)]
    base = sub[sub["strategy"] == ref].set_index(["breed", "replicate", "generation", "metric"])
    rows = []
    for k, g in sub[sub["strategy"] != ref].groupby(["breed", "strategy", "generation", "metric"]):
        g = g.set_index(["breed", "replicate", "generation", "metric"])
        joined = g["value"] - base["value"].reindex(g.index)
        m, lo, hi = t_interval(joined.to_numpy())
        rows.append(
            dict(zip(["breed", "strategy", "generation", "metric"], k, strict=True))
            | {"diff_mean": m, "lo": lo, "hi": hi, "n": int(np.isfinite(joined).sum())}
        )
    cols = ["breed", "strategy", "generation", "metric", "diff_mean", "lo", "hi", "n"]
    return pd.DataFrame(rows, columns=cols)  # same columns when empty (no reference arm, E10)


def _fmt(m: float, lo: float, hi: float, pct: bool = False) -> str:
    if not np.isfinite(m):
        return "n/a"
    s = 100.0 if pct else 1.0
    if np.isfinite(lo):
        return f"{s * m:.3g} ({s * lo:.3g} to {s * hi:.3g})"
    return f"{s * m:.3g}"


def write_summary(exp_id: str) -> list[Path]:
    from breeding_smarter.experiments.figures import make_figures

    df = load_results(exp_id)
    out = report_dir(exp_id)
    out.mkdir(parents=True, exist_ok=True)
    per_gen = by_generation(df)
    ne = ne_table(df)
    ne_rows = ne.melt(
        id_vars=["breed", "strategy", "adoption", "replicate"],
        value_vars=["delta_f", "ne"],
        var_name="metric",
    )
    ne_rows["metric"] = ne_rows["metric"].map({"delta_f": "M3_delta_f", "ne": "M3_ne"})
    ne_rows["generation"] = 10
    parts = [per_gen, ne_rows]
    if "M12_realised_coancestry" in set(df["metric"]):
        parts.append(rate_table(df))
    per_gen = pd.concat(parts, ignore_index=True)
    summ = summarise(per_gen)
    refs = [r for r in ("S1", "S3") if (per_gen["strategy"] == r).any()]
    ref = refs[0] if refs else "S3"
    paired = paired_vs(per_gen, ref=ref)
    summ.to_csv(out / "summary.csv", index=False)
    paired_files = []
    for r in refs or [ref]:
        pr = paired if r == ref else paired_vs(per_gen, ref=r)
        pr.to_csv(out / f"paired_vs_{r}.csv", index=False)
        paired_files.append(out / f"paired_vs_{r}.csv")
    per_gen.to_csv(out / "per_generation_replicates.csv.gz", index=False)
    lines = [
        f"# Experiment {exp_id}",
        "",
        CAPTION + " Means with 95% t-intervals over "
        "replicates; generation g averages the birth cohorts of (g - 0.5, g + 0.5] "
        "generations after 2026 (4.5 years per generation).",
        "",
    ]
    at10 = summ[summ["generation"] == 10]
    rates = at10[at10["metric"].str.startswith("R_")]
    if len(rates):
        cols = [f"R_delta_f_{w}" for w in WINDOWS] + [f"R_ne_f_{w}" for w in WINDOWS]
        cols += [f"R_delta_c_{w}" for w in WINDOWS]
        lines += [
            "## Rates per generation by window (early: generations 0 to 5, late: 5 to 10)",
            "",
            "dF from realised IBD of birth cohorts, dC from realised coancestry of living "
            "animals (neutral loci); Ne = 1/(2 rate); nan Ne = non-positive rate.",
            "",
            "| breed | strategy | adoption | " + " | ".join(cols) + " |",
            "|---|---|---|" + "---|" * len(cols),
        ]
        for (b, sid, ad), g in rates.groupby(["breed", "strategy", "adoption"]):
            cells = []
            for col in cols:
                sel = g[g["metric"] == col]
                if len(sel):
                    mean, lo, hi = (float(v) for v in sel[["mean", "lo", "hi"]].iloc[0])
                    cells.append(_fmt(mean, lo, hi, pct="delta" in col))
                else:
                    cells.append("n/a")
            lines.append(f"| {b} | {sid} | {ad:g} | " + " | ".join(cells) + " |")
        lines += ["", "Rates are in % per generation.", ""]
    for breed in sorted(at10["breed"].unique()):
        lines += [
            f"## {breed}: generation 10",
            "",
            "| strategy | adoption | " + " | ".join(KEY_METRICS.values()) + " |",
            "|---|---|" + "---|" * len(KEY_METRICS),
        ]
        b = at10[at10["breed"] == breed]
        for (sid, ad), g in b.groupby(["strategy", "adoption"]):
            cells = []
            for mkey in KEY_METRICS:
                r = g[g["metric"] == mkey]
                cells.append(_fmt(*r[["mean", "lo", "hi"]].iloc[0]) if len(r) else "n/a")
            lines.append(f"| {sid} | {ad:g} | " + " | ".join(cells) + " |")
        lines.append("")
        p = paired[
            (paired["breed"] == breed)
            & paired["metric"].isin(["M2_realised_ibd", "M5_he_relative", "M3_ne", "M1_recorded_F"])
        ]
        if len(p):
            lines += [
                f"### {breed}: paired differences vs {ref} (same replicate seeds)",
                "",
                "| strategy | generation | metric | difference (95% CI) | n |",
                "|---|---|---|---|---|",
            ]
            for _, r in p.sort_values(["metric", "generation", "strategy"]).iterrows():
                lines.append(
                    f"| {r['strategy']} | {r['generation']} | {r['metric']} | "
                    f"{_fmt(r['diff_mean'], r['lo'], r['hi'])} | {r['n']} |"
                )
            lines.append("")
    (out / "summary.md").write_text("\n".join(lines) + "\n")
    figs = make_figures(exp_id, df, per_gen, summ, out)
    return [out / "summary.csv", *paired_files, out / "summary.md", *figs]
