"""Validation report: target vs simulated table, figures and markdown (P5 task 5.4)."""

from __future__ import annotations

import csv
import dataclasses
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from breeding_smarter.calibration import plotstyle
from breeding_smarter.calibration.data import RunData
from breeding_smarter.calibration.metrics import MetricResult
from breeding_smarter.calibration.targets import Row, TargetsConfig, evaluate, hard_failures
from breeding_smarter.io.manifest import read_manifest

INTRO = "All animals in this dataset are synthetic."
GRADES = ["A", "B", "C", "D", "E"]


def _fig_registrations(rd: RunData, out: Path) -> list[Path]:
    a = rd.animals[rd.domestic & ~rd.animals["import_flag"].to_numpy()]
    fig, ax = plt.subplots(figsize=(7, 4))
    for b in rd.breeds:
        c = a[a["breed_id"] == b].groupby("year").size()
        ax.plot(c.index.to_numpy(), c.to_numpy(), label=b, color=plotstyle.BREED_COLOURS.get(b))
        tgt = rd.breed_cfg(b).population.registrations_per_year
        years = np.arange(1980, rd.setup.sim.end_year + 1)
        ax.plot(
            years,
            [tgt.at(y) * rd.setup.sim.scale for y in years],
            ls="--",
            lw=1,
            color=plotstyle.BREED_COLOURS.get(b),
        )
    ax.set(
        yscale="log",
        xlabel="birth year",
        ylabel="registrations",
        title="Registrations per year (dashed: target)",
    )
    ax.legend()
    return plotstyle.save(fig, out / "fig1_registrations")


def _fig_litters(rd: RunData, out: Path) -> list[Path]:
    fig, ax = plt.subplots(figsize=(7, 4))
    bins = [x + 0.5 for x in range(0, 16)]
    for b in rd.breeds:
        x = rd.litters.loc[rd.litters["breed_id"] == b, "n_born"]
        col = plotstyle.BREED_COLOURS.get(b)
        ax.hist(
            x, bins=bins, histtype="step", density=True, color=col, label=f"{b} mean {x.mean():.2f}"
        )
        ax.axvline(rd.breed_cfg(b).reproduction.litter_size_mean.value, color=col, ls="--")
    ax.set(
        xlabel="puppies born",
        ylabel="share of litters",
        title="Litter size (dashed: configured mean)",
    )
    ax.legend()
    return plotstyle.save(fig, out / "fig2_litter_size")


def _fig_sires(rd: RunData, res: MetricResult, out: Path) -> list[Path]:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4))
    for b, c in res.data["counts"].items():
        col = plotstyle.BREED_COLOURS.get(b)
        s = np.sort(c)[::-1]
        ax1.loglog(np.arange(1, s.size + 1), s, label=b, color=col)
        cum = np.r_[0, np.cumsum(np.sort(c))] / max(c.sum(), 1)
        ax2.plot(np.linspace(0, 1, cum.size), cum, label=b, color=col)
    ax2.plot([0, 1], [0, 1], color="#999999", lw=1, ls=":")
    ax1.set(xlabel="sire rank", ylabel="registered offspring 2016-2025", title="Offspring per sire")
    ax2.set(
        xlabel="share of sires (ascending)",
        ylabel="share of offspring",
        title="Lorenz curve of sire use",
    )
    ax1.legend()
    return plotstyle.save(fig, out / "fig3_sire_use")


def _fig_f_by_year(rd: RunData, res: MetricResult, out: Path) -> list[Path]:
    by = res.data["f_by_year"]
    fig, axes = plt.subplots(1, len(rd.breeds), figsize=(4.2 * len(rd.breeds), 4), sharey=True)
    axes = np.atleast_1d(axes)
    for ax, b in zip(axes, rd.breeds, strict=True):
        g = by.loc[b]
        g = g[g.index >= 1980]
        x = g.index.to_numpy()
        ax.plot(x, 100 * g["recorded"], label="recorded pedigree COI", color="#D55E00")
        ax.plot(x, 100 * g["true_pedigree"], label="true pedigree F", color="#0072B2")
        ax.plot(
            x, 100 * g["realised_ibd"], label="realised IBD (gene drop)", color="#009E73", ls="--"
        )
        ax.set(title=b, xlabel="birth year")
    axes[0].set_ylabel("mean inbreeding (%)")
    axes[0].legend(loc="upper left")
    fig.suptitle("Recorded COI underestimates true inbreeding (synthetic registry)")
    return plotstyle.save(fig, out / "fig4_recorded_vs_true_f")


def _fig_ibd_scatter(rd: RunData, res: MetricResult, out: Path) -> list[Path]:
    fig, ax = plt.subplots(figsize=(5, 5))
    rng = np.random.default_rng(0)
    for b, (x, y) in res.data["xy"].items():
        k = rng.choice(x.size, size=min(3000, x.size), replace=False)
        ax.scatter(x[k], y[k], s=3, alpha=0.3, color=plotstyle.BREED_COLOURS.get(b), label=b)
    ax.plot([0, 1], [0, 1], color="#000000", lw=1)
    ax.set(
        xlim=(0, 0.7),
        ylim=(0, 0.7),
        xlabel="true pedigree F (engine)",
        ylabel="realised IBD (gene drop)",
        title="Engine vs gene drop (born after 1980)",
    )
    ax.legend(markerscale=4)
    return plotstyle.save(fig, out / "fig5_ibd_vs_pedigree_f")


def _fig_ne(rd: RunData, rows: list[Row], out: Path) -> list[Path]:
    fig, ax = plt.subplots(figsize=(6, 4))
    for i, b in enumerate(rd.breeds):
        r = next(r for r in rows if r.id == "T07" and r.breed == b)
        lo, hi = (float(v) for v in str(r.target).strip("[]").split(","))
        ax.add_patch(plt.Rectangle((i - 0.3, lo), 0.6, hi - lo, color="#cccccc"))
        ax.scatter([i], [float(str(r.value))], color=plotstyle.BREED_COLOURS.get(b), zorder=3, s=60)
    ax.set(
        xticks=range(len(rd.breeds)),
        xticklabels=rd.breeds,
        yscale="log",
        ylabel="Ne (individual delta F)",
        title="Ne 2016-2025 cohort vs target band (grey)",
    )
    return plotstyle.save(fig, out / "fig6_ne")


def _fig_hd(rd: RunData, res: MetricResult, out: Path) -> list[Path]:
    h = res.data["health"]
    h = h.assign(period=(h["year"] // 5) * 5)
    fig, axes = plt.subplots(1, len(rd.breeds), figsize=(4.2 * len(rd.breeds), 4), sharey=True)
    axes = np.atleast_1d(axes)
    colours = ["#009E73", "#56B4E9", "#F0E442", "#E69F00", "#D55E00"]
    for ax, b in zip(axes, rd.breeds, strict=True):
        s = h[h["breed_id"] == b].groupby("period")["result"].value_counts(normalize=True)
        s = s.unstack().reindex(columns=GRADES).fillna(0)
        bottom = np.zeros(len(s))
        for g, c in zip(GRADES, colours, strict=True):
            ax.bar(s.index, s[g], bottom=bottom, width=4, color=c, label=g)
            bottom += s[g].to_numpy()
        ax.set(title=b, xlabel="screening period")
    axes[0].set_ylabel("share of HD results")
    axes[0].legend(title="grade", loc="lower left")
    return plotstyle.save(fig, out / "fig7_hd_grades")


def _fig_carriers(rd: RunData, res: MetricResult, out: Path) -> list[Path]:
    c = res.data["carrier"]
    fig, axes = plt.subplots(1, len(rd.breeds), figsize=(4.2 * len(rd.breeds), 4), sharey=True)
    axes = np.atleast_1d(axes)
    for ax, b in zip(axes, rd.breeds, strict=True):
        loci = sorted({k[1] for k in c.index if k[0] == b})
        x = np.arange(len(loci))
        for j, y in enumerate((1980, 2026)):
            v = [c.get((b, lc, y), 0.0) for lc in loci]
            ax.bar(x + (j - 0.5) * 0.4, v, width=0.4, label=str(y), color=["#999999", "#0072B2"][j])
        ax.set(title=b, xticks=x)
        ax.set_xticklabels(loci, rotation=45, ha="right")
    axes[0].set_ylabel("carrier share of births")
    axes[0].legend()
    return plotstyle.save(fig, out / "fig8_carriers")


def figures(
    rd: RunData, rows: list[Row], results: dict[str, MetricResult], out: Path
) -> list[Path]:
    plotstyle.apply()
    figs = out / "figures"
    paths = []
    paths += _fig_registrations(rd, figs)
    paths += _fig_litters(rd, figs)
    paths += _fig_sires(rd, results["T05"], figs)
    paths += _fig_f_by_year(rd, results["T11"], figs)
    paths += _fig_ibd_scatter(rd, results["T13"], figs)
    paths += _fig_ne(rd, rows, figs)
    paths += _fig_hd(rd, results["T14"], figs)
    if "T18" in results:
        paths += _fig_carriers(rd, results["T18"], figs)
    return paths


def write_report(
    rd: RunData, cfg: TargetsConfig, out: Path, with_figures: bool = True
) -> list[Row]:
    """Write `validation_report.md`, `targets_vs_simulated.csv` and figures to `out`."""
    out.mkdir(parents=True, exist_ok=True)
    rows, results = evaluate(rd, cfg)
    with (out / "targets_vs_simulated.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[x.name for x in dataclasses.fields(Row)])
        w.writeheader()
        for r in rows:
            w.writerow(dataclasses.asdict(r))
    if with_figures:
        figures(rd, rows, results, out)
    m = read_manifest(rd.run.manifest)
    counts = pd.Series([r.status for r in rows]).value_counts()
    lines = [
        f"# Validation report: {rd.run.run_id}",
        "",
        INTRO,
        "",
        f"Run `{rd.run.run_id}`: seed {m.get('seed')}, "
        f"config hash `{m.get('config_hash', '')[:12]}`, "
        f"git `{m.get('git_commit', '')[:12]}`, scale {m.get('scale')}.",
        "",
        f"Checks: **{counts.get('PASS', 0)} PASS, {counts.get('WARN', 0)} WARN, "
        f"{counts.get('FAIL', 0)} FAIL** ({counts.get('REPORT', 0)} report-only values). "
        "Hard targets must pass; soft targets warn only.",
        "",
        "| id | kind | breed | component | simulated | target | status | source |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        if r.status == "REPORT" and r.id not in ("T08", "T17"):
            continue
        lines.append(
            f"| {r.id} | {r.kind} | {r.breed} | {r.component} | {r.value} | "
            f"{r.target} | {r.status} | {r.source} |"
        )
    lines += ["", "## Targets", ""]
    fig_of = {
        "T01": "fig2_litter_size",
        "T05": "fig3_sire_use",
        "T06": "fig3_sire_use",
        "T07": "fig6_ne",
        "T11": "fig4_recorded_vs_true_f",
        "T12": "fig5_ibd_vs_pedigree_f",
        "T13": "fig5_ibd_vs_pedigree_f",
        "T14": "fig7_hd_grades",
        "T18": "fig8_carriers",
        "T16": "fig1_registrations",
    }
    for t in cfg.targets:
        trs = [r for r in rows if r.id == t.id]
        status = (
            "FAIL"
            if any(r.status == "FAIL" for r in trs)
            else "WARN"
            if any(r.status == "WARN" for r in trs)
            else "PASS"
            if any(r.status == "PASS" for r in trs)
            else "REPORT"
        )
        src = t.source or "assumption"
        lines += [
            f"### {t.id} ({t.kind}, {status}): {t.description}",
            "",
            f"Source: `{src}`." + (f" Note: {t.note}" if t.note else ""),
            "",
        ]
        if t.kind == "report" or status == "REPORT":
            for r in trs:
                lines.append(f"- {r.breed} {r.component}: {r.value}")
            lines.append("")
        if t.id in fig_of and with_figures:
            lines += [f"![{t.id}](figures/{fig_of[t.id]}.png)", ""]
    (out / "validation_report.md").write_text("\n".join(lines) + "\n")
    return rows


def validate_and_report(run_dir: Path, targets: TargetsConfig, out: Path) -> tuple[list[Row], bool]:
    rd = RunData.load(run_dir)
    rows = write_report(rd, targets, out)
    return rows, not hard_failures(rows)
