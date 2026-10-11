"""Experiment figures A to F (P8 task 8.5). Fixed strategy colours, colourblind-safe palette,
PNG (300 dpi) and SVG, plus a poster variant with larger fonts. Every caption says the
results are in silico."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from breeding_smarter.calibration import plotstyle

NOTE = "In-silico results on synthetic populations. Mean and 95% interval over replicates."
STRATEGY_LABEL = {
    "S0": "S0 random",
    "S1": "S1 status quo market",
    "S2": "S2 compliant market",
    "S3": "S3 recommender",
    "S4": "S4 coordinated planner",
    "S3hc": "S3, carrier x carrier blocked",
    "S3xc": "S3, all known carriers excluded",
}


def _save(fig: plt.Figure, out: Path, name: str, poster: bool) -> list[Path]:
    stem = out / "figures" / (f"{name}_poster" if poster else name)
    return plotstyle.save(fig, stem, NOTE)


def _band(ax: plt.Axes, s: pd.DataFrame, colour: str, label: str, scale: float = 1.0) -> None:
    s = s.sort_values("generation")
    x = s["generation"].to_numpy()
    ax.plot(x, scale * s["mean"], color=colour, label=label, lw=2)
    ax.fill_between(x, scale * s["lo"], scale * s["hi"], color=colour, alpha=0.2, lw=0)


def fig_a(summ: pd.DataFrame, out: Path, poster: bool) -> list[Path]:
    s = summ[(summ["metric"] == "M2_realised_ibd") & (summ["adoption"] == 1.0)]
    breeds = sorted(s["breed"].unique())
    fig, axes = plt.subplots(1, len(breeds), figsize=(6 * len(breeds), 4.5), squeeze=False)
    for ax, b in zip(axes[0], breeds, strict=True):
        for sid in sorted(s["strategy"].unique()):
            _band(
                ax,
                s[(s["breed"] == b) & (s["strategy"] == sid)],
                plotstyle.STRATEGY_COLOURS[sid],
                STRATEGY_LABEL[sid],
                100,
            )
        ax.set(title=b, xlabel="generations after 2026", ylabel="realised inbreeding (%)")
    axes[0][0].legend(loc="upper left")
    fig.suptitle("Realised inbreeding under five breeding strategies")
    return _save(fig, out, "figA_realised_inbreeding", poster)


def fig_b(summ: pd.DataFrame, out: Path, poster: bool) -> list[Path]:
    s = summ[(summ["metric"] == "M3_ne") & (summ["adoption"] == 1.0)]
    breeds = sorted(s["breed"].unique())
    fig, axes = plt.subplots(1, len(breeds), figsize=(5.5 * len(breeds), 4), squeeze=False)
    for ax, b in zip(axes[0], breeds, strict=True):
        g = s[s["breed"] == b].sort_values("strategy")
        x = np.arange(len(g))
        err = np.vstack([g["mean"] - g["lo"], g["hi"] - g["mean"]])
        ax.bar(
            x,
            g["mean"],
            yerr=np.nan_to_num(err),
            capsize=4,
            color=[plotstyle.STRATEGY_COLOURS[k] for k in g["strategy"]],
        )
        ax.set(xticks=x, title=b, ylabel="Ne from realised IBD (10 generations)")
        ax.set_xticklabels(g["strategy"])
    fig.suptitle("Effective population size by strategy")
    return _save(fig, out, "figB_ne", poster)


def fig_c(summ: pd.DataFrame, out: Path, poster: bool) -> list[Path]:
    panels = []
    for b in sorted(summ["breed"].unique()):
        sb = summ[(summ["breed"] == b) & (summ["adoption"] == 1.0)]
        tested = [m for m in sb["metric"].unique() if m.startswith("M6_affected_")]
        start = sb[sb["generation"] == 1]
        live = [m for m in tested if start[start["metric"] == m]["mean"].max() > 0]
        if live:
            panels.append((b, live[0]))
        if (sb["metric"] == "M7_affected_NOVEL_X").any() and start[
            start["metric"] == "M7_affected_NOVEL_X"
        ]["mean"].max() > 0:
            panels.append((b, "M7_affected_NOVEL_X"))
    if not panels:
        return []
    fig, axes = plt.subplots(1, len(panels), figsize=(5.5 * len(panels), 4), squeeze=False)
    for ax, (b, m) in zip(axes[0], panels, strict=True):
        s = summ[(summ["breed"] == b) & (summ["metric"] == m) & (summ["adoption"] == 1.0)]
        for sid in sorted(s["strategy"].unique()):
            _band(
                ax,
                s[s["strategy"] == sid],
                plotstyle.STRATEGY_COLOURS[sid],
                STRATEGY_LABEL[sid],
                100,
            )
        locus = m.split("_", 2)[2]
        kind = "untestable" if m.startswith("M7") else "tested"
        ax.set(
            title=f"{b}: {locus} ({kind})",
            xlabel="generations after 2026",
            ylabel="affected-genotype puppies (%)",
        )
    axes[0][0].legend(loc="upper left")
    return _save(fig, out, "figC_disease", poster)


def fig_d(per_gen: pd.DataFrame, out: Path, poster: bool) -> list[Path]:
    """HD genetic gain (decrease of mean true liability BV) vs rate of inbreeding."""
    p = per_gen[per_gen["adoption"] == 1.0]
    tbv = p[p["metric"] == "M8_mean_tbv_hd"].pivot_table(
        index=["breed", "strategy", "replicate"], columns="generation", values="value"
    )
    df_ = p[p["metric"] == "M3_delta_f"].set_index(["breed", "strategy", "replicate"])["value"]
    gain = -(tbv[10] - tbv[1])
    data = pd.DataFrame({"gain": gain, "dF": df_}).dropna().reset_index()
    breeds = sorted(data["breed"].unique())
    fig, axes = plt.subplots(1, len(breeds), figsize=(5.5 * len(breeds), 4.5), squeeze=False)
    for ax, b in zip(axes[0], breeds, strict=True):
        for sid, g in data[data["breed"] == b].groupby("strategy"):
            c = plotstyle.STRATEGY_COLOURS[sid]
            ax.scatter(100 * g["dF"], g["gain"], color=c, alpha=0.35, s=18)
            ax.scatter(
                100 * g["dF"].mean(),
                g["gain"].mean(),
                color=c,
                s=120,
                edgecolor="black",
                label=STRATEGY_LABEL[sid],
                zorder=3,
            )
        ax.set(
            title=b,
            xlabel="rate of inbreeding per generation (%)",
            ylabel="HD genetic gain (liability SD, gen 1 to 10)",
        )
    axes[0][0].legend(fontsize="small")
    return _save(fig, out, "figD_tradeoff", poster)


def fig_e(per_gen: pd.DataFrame, out: Path, poster: bool) -> list[Path]:
    p = per_gen[(per_gen["strategy"] == "S3") & (per_gen["metric"] == "M3_delta_f")]
    if p["adoption"].nunique() < 2:
        return []
    fig, ax = plt.subplots(figsize=(6, 4.5))
    for b, g in p.groupby("breed"):
        means = g.groupby("adoption")["value"].agg(["mean", "std", "count"])
        h = 1.96 * means["std"] / np.sqrt(means["count"])
        ax.errorbar(
            100 * means.index,
            100 * means["mean"],
            yerr=100 * h,
            marker="o",
            capsize=4,
            label=b,
            color=plotstyle.BREED_COLOURS.get(str(b)),
        )
    ax.set(
        xlabel="breeders using the recommender (%)",
        ylabel="rate of inbreeding per generation (%)",
        title="Adoption sweep (non-users follow S2)",
    )
    ax.legend()
    return _save(fig, out, "figE_adoption", poster)


def fig_f(summ: pd.DataFrame, out: Path, poster: bool) -> list[Path]:
    s = summ[(summ["metric"] == "M9_top20_share") & (summ["adoption"] == 1.0)]
    breeds = sorted(s["breed"].unique())
    fig, axes = plt.subplots(1, len(breeds), figsize=(6 * len(breeds), 4.5), squeeze=False)
    for ax, b in zip(axes[0], breeds, strict=True):
        for sid in sorted(s["strategy"].unique()):
            _band(
                ax,
                s[(s["breed"] == b) & (s["strategy"] == sid)],
                plotstyle.STRATEGY_COLOURS[sid],
                STRATEGY_LABEL[sid],
                100,
            )
        ax.set(
            title=b, xlabel="generations after 2026", ylabel="offspring from top 20% of sires (%)"
        )
    axes[0][0].legend(loc="lower left", fontsize="small")
    return _save(fig, out, "figF_sire_concentration", poster)


def make_figures(
    exp_id: str, df: pd.DataFrame, per_gen: pd.DataFrame, summ: pd.DataFrame, out: Path
) -> list[Path]:
    paths: list[Path] = []
    for poster in (False, True):
        plotstyle.apply(poster=poster)
        if summ["strategy"].nunique() > 1:
            paths += fig_a(summ, out, poster)
            paths += fig_b(summ, out, poster)
            paths += fig_c(summ, out, poster)
            paths += fig_d(per_gen, out, poster)
            paths += fig_f(summ, out, poster)
        paths += fig_e(per_gen, out, poster)
    plotstyle.apply()
    return paths
