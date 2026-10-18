"""Experiment figures A to F (P8 task 8.5), G to L (P12 task 12.11) and M (E8).

Fixed strategy colours, colourblind-safe palette, PNG (300 dpi) and SVG, plus a poster
variant with larger fonts. Every caption says the results are in silico."""

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
    "CC-none-rand": "no control, random",
    "CC-none-mc1": "no control, min-kinship mating",
    "CC-mkx-rand": "high-MK sires excluded, random",
    "CC-mkx-mc1": "high-MK sires excluded, MC1",
    "CC-cap-rand": "MK-scaled caps, random",
    "CC-cap-mc1": "MK-scaled caps, MC1",
    "CC-ocs-rand": "OCS quotas, random",
    "CC-ocs-mc1": "OCS quotas, MC1 (coordinated planning)",
    "CC-ocs-mc1-oracle": "OCS on true kinship (oracle)",
    "CC-gain100-mc1": "OCS gain, dF 1%",
    "CC-gain050-mc1": "OCS gain, dF 0.5%",
    "CC-gain025-mc1": "OCS gain, dF 0.25%",
    "CC-gain010-mc1": "OCS gain, dF 0.1%",
    "S3q": "S3q recommender within quotas",
}


def strategy_label(sid: str) -> str:
    """Legend label; S3q variants of E8 (`S3q-gainNNN-cBBB`) are described from their id."""
    if sid in STRATEGY_LABEL:
        return STRATEGY_LABEL[sid]
    if sid.startswith("S3q-"):
        from breeding_smarter.experiments.strategies import parse_s3q

        spec = parse_s3q(sid)
        parts = ["S3q"]
        if spec.delta_f is not None:
            parts.append(f"gain OCS dF {100 * spec.delta_f:g}%")
        if spec.carrier_factor is not None:
            parts.append(f"carrier limit {spec.carrier_factor:g}")
        if spec.hard_carrier:
            parts.append("carrier x carrier blocked")
        if spec.oracle:
            parts.append("true kinship")
        return ", ".join(parts)
    return sid


CONTROLS = {"none": "none", "mkx": "MK exclusion", "cap": "MK-scaled cap", "ocs": "OCS"}


def style(sid: str) -> tuple[str, str]:
    """(colour, line style): random mating dashed, everything else solid."""
    return plotstyle.STRATEGY_COLOURS.get(sid, "#333333"), "--" if sid.endswith("-rand") else "-"


def _save(fig: plt.Figure, out: Path, name: str, poster: bool) -> list[Path]:
    stem = out / "figures" / (f"{name}_poster" if poster else name)
    return plotstyle.save(fig, stem, NOTE)


def _band(
    ax: plt.Axes, s: pd.DataFrame, colour: str, label: str, scale: float = 1.0, ls: str = "-"
) -> None:
    s = s.sort_values("generation")
    x = s["generation"].to_numpy()
    ax.plot(x, scale * s["mean"], color=colour, label=label, lw=2, ls=ls)
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
                style(sid)[0],
                strategy_label(sid),
                100,
                style(sid)[1],
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
            color=[style(k)[0] for k in g["strategy"]],
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
                style(sid)[0],
                strategy_label(sid),
                100,
                style(sid)[1],
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


def fig_d(
    per_gen: pd.DataFrame, out: Path, poster: bool, name: str = "figD_tradeoff"
) -> list[Path]:
    """HD genetic gain (decrease of mean true liability BV) vs rate of inbreeding."""
    p = per_gen[per_gen["adoption"] == 1.0]
    tbv = p[p["metric"] == "M8_mean_tbv_hd"].pivot_table(
        index=["breed", "strategy", "replicate"], columns="generation", values="value"
    )
    df_ = p[p["metric"] == "M3_delta_f"].set_index(["breed", "strategy", "replicate"])["value"]
    gain = -(tbv[tbv.columns.max()] - tbv[tbv.columns.min()])
    data = pd.DataFrame({"gain": gain, "dF": df_}).dropna().reset_index()
    breeds = sorted(data["breed"].unique())
    fig, axes = plt.subplots(1, len(breeds), figsize=(5.5 * len(breeds), 4.5), squeeze=False)
    for ax, b in zip(axes[0], breeds, strict=True):
        for sid, g in data[data["breed"] == b].groupby("strategy"):
            c = style(str(sid))[0]
            ax.scatter(100 * g["dF"], g["gain"], color=c, alpha=0.35, s=18)
            ax.scatter(
                100 * g["dF"].mean(),
                g["gain"].mean(),
                color=c,
                s=120,
                edgecolor="black",
                label=strategy_label(sid),
                zorder=3,
            )
        ax.set(
            title=b,
            xlabel="rate of inbreeding per generation (%)",
            ylabel="HD genetic gain (liability SD, gen 1 to 10)",
        )
    axes[0][0].legend(fontsize="small")
    return _save(fig, out, name, poster)


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
                style(sid)[0],
                strategy_label(sid),
                100,
                style(sid)[1],
            )
        ax.set(
            title=b, xlabel="generations after 2026", ylabel="offspring from top 20% of sires (%)"
        )
    axes[0][0].legend(loc="lower left", fontsize="small")
    return _save(fig, out, "figF_sire_concentration", poster)


def _lines(
    summ: pd.DataFrame, metric: str, sids: list[str], ylabel: str, title: str
) -> tuple[plt.Figure, np.ndarray] | None:
    s = summ[(summ["metric"] == metric) & (summ["adoption"] == 1.0) & summ["strategy"].isin(sids)]
    if s.empty:
        return None
    breeds = sorted(s["breed"].unique())
    fig, axes = plt.subplots(1, len(breeds), figsize=(6 * len(breeds), 4.5), squeeze=False)
    for ax, b in zip(axes[0], breeds, strict=True):
        for sid in [x for x in sids if x in set(s["strategy"])]:
            c, ls = style(sid)
            _band(
                ax, s[(s["breed"] == b) & (s["strategy"] == sid)], c, strategy_label(sid), 100, ls
            )
        ax.set(title=b, xlabel="generations after 2026", ylabel=ylabel)
    axes[0][0].legend(loc="upper left", fontsize="small")
    fig.suptitle(title)
    return fig, axes


def fig_g(summ: pd.DataFrame, out: Path, poster: bool) -> list[Path]:
    """Headline P12: realised inbreeding for random, status quo, recommender, coordination."""
    got = _lines(
        summ,
        "M2_realised_ibd",
        ["S0", "S1", "S3", "CC-ocs-mc1", "S3q"],
        "realised inbreeding (%)",
        "Realised inbreeding with and without coordinated sire use",
    )
    return _save(got[0], out, "figG_coordination", poster) if got else []


def fig_h(summ: pd.DataFrame, out: Path, poster: bool) -> list[Path]:
    """Factorial: late-window dF per contribution control, random vs MC1 mating."""
    s = summ[(summ["metric"] == "R_delta_f_late") & (summ["adoption"] == 1.0)]
    if not s["strategy"].str.startswith("CC-").any():
        return []
    breeds = sorted(s["breed"].unique())
    fig, axes = plt.subplots(1, len(breeds), figsize=(6 * len(breeds), 4.5), squeeze=False)
    for ax, b in zip(axes[0], breeds, strict=True):
        sb = s[s["breed"] == b].set_index("strategy")
        for j, (mating, mk, dx) in enumerate((("rand", "o", -0.12), ("mc1", "s", 0.12))):
            xs, ys, err = [], [], []
            for i, c in enumerate(CONTROLS):
                sid = f"CC-{c}-{mating}"
                if sid in sb.index:
                    r = sb.loc[sid]
                    xs.append(i + dx)
                    ys.append(100 * r["mean"])
                    err.append([100 * (r["mean"] - r["lo"]), 100 * (r["hi"] - r["mean"])])
            e = np.nan_to_num(np.array(err).T) if err else None
            label = "random mating" if j == 0 else "minimum-coancestry mating (MC1)"
            ax.errorbar(xs, ys, yerr=e, fmt=mk, capsize=4, ms=8, label=label, color="#333333")
        for anchor in ("S0", "S1", "S3"):
            if anchor in sb.index:
                ax.axhline(
                    100 * sb.loc[anchor, "mean"],
                    color=plotstyle.STRATEGY_COLOURS[anchor],
                    ls=":",
                    label=strategy_label(anchor),
                )
        ax.set_xticks(range(len(CONTROLS)), list(CONTROLS.values()))
        ax.set(title=b, xlabel="contribution control", ylabel="dF per generation, gen 5-10 (%)")
    axes[0][0].legend(fontsize="small")
    fig.suptitle("Which factor matters: contribution control or mating method")
    return _save(fig, out, "figH_factorial", poster)


def fig_i(per_gen: pd.DataFrame, out: Path, poster: bool) -> list[Path]:
    """Budget trade-off: HD genetic gain vs rate of inbreeding for the gain ladder."""
    if not per_gen["strategy"].str.startswith("CC-gain").any():
        return []
    return fig_d(per_gen, out, poster, name="figI_budget_tradeoff")


def fig_j(summ: pd.DataFrame, out: Path, poster: bool) -> list[Path]:
    """Kinship source: OCS on recorded vs true kinship (late-window Ne; recorded vs true F)."""
    sids = ["CC-ocs-mc1", "CC-ocs-mc1-oracle"]
    s = summ[summ["strategy"].isin(sids) & (summ["generation"] == 10)]
    if s["strategy"].nunique() < 2:
        return []
    breeds = sorted(s["breed"].unique())
    fig, axes = plt.subplots(2, len(breeds), figsize=(5.5 * len(breeds), 7), squeeze=False)
    for col, b in enumerate(breeds):
        sb = s[s["breed"] == b]
        ax = axes[0][col]
        ne = sb[sb["metric"] == "R_ne_f_late"].set_index("strategy").reindex(sids)
        err = np.nan_to_num(np.vstack([ne["mean"] - ne["lo"], ne["hi"] - ne["mean"]]))
        ax.bar(range(2), ne["mean"], yerr=err, capsize=4, color=[style(x)[0] for x in sids])
        ax.set_xticks(range(2), ["recorded kinship", "true kinship"])
        ax.set(title=b, ylabel="Ne, generations 5-10")
        ax = axes[1][col]
        for k, (metric, lab) in enumerate(
            (("M1_recorded_F", "recorded COI"), ("M2_realised_ibd", "realised IBD"))
        ):
            v = sb[sb["metric"] == metric].set_index("strategy").reindex(sids)["mean"]
            ax.bar(np.arange(2) + (k - 0.5) * 0.38, 100 * v, width=0.38, label=lab,
                   color=["#999999", "#333333"][k])  # fmt: skip
        ax.set_xticks(range(2), ["recorded kinship", "true kinship"])
        ax.set(ylabel="inbreeding at generation 10 (%)")
        ax.legend(fontsize="small")
    fig.suptitle("Planning on recorded vs true kinship")
    return _save(fig, out, "figJ_kinship_source", poster)


def fig_k(per_gen: pd.DataFrame, out: Path, poster: bool, e2: pd.DataFrame | None) -> list[Path]:
    """Adoption: dF (10 generations) vs share of adopters, S3q vs the P8 S3 sweep (E2)."""
    p = per_gen[(per_gen["strategy"] == "S3q") & (per_gen["metric"] == "M3_delta_f")]
    if p["adoption"].nunique() < 2:
        return []
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    curves = [(b, g, "-", "S3q") for b, g in p.groupby("breed")]
    if e2 is not None:
        q = e2[(e2["strategy"] == "S3") & (e2["metric"] == "M3_delta_f")]
        curves += [(b, g, "--", "S3 (P8 E2)") for b, g in q.groupby("breed")]
    for b, g, ls, lab in curves:
        means = g.groupby("adoption")["value"].agg(["mean", "std", "count"])
        h = 1.96 * means["std"] / np.sqrt(means["count"])
        ax.errorbar(
            100 * means.index, 100 * means["mean"], yerr=100 * h, marker="o", capsize=4, ls=ls,
            label=f"{b}, {lab}", color=plotstyle.BREED_COLOURS.get(str(b)),
        )  # fmt: skip
    ax.set(
        xlabel="breeders using the tool (%)",
        ylabel="rate of inbreeding per generation (%)",
        title="Adoption: recommender with and without club quotas",
    )
    ax.legend(fontsize="small")
    return _save(fig, out, "figK_adoption_quotas", poster)


def fig_l(summ: pd.DataFrame, out: Path, poster: bool) -> list[Path]:
    """Sire use: share of eligible males used and top-5 sires' share of litters (gen 10)."""
    s = summ[(summ["generation"] == 10) & (summ["adoption"] == 1.0)]
    if "M14_top5_sire_share" not in set(s["metric"]):
        return []
    breeds = sorted(s["breed"].unique())
    fig, axes = plt.subplots(2, len(breeds), figsize=(7 * len(breeds), 8), squeeze=False)
    for col, b in enumerate(breeds):
        sb = s[s["breed"] == b]
        for row, (metric, lab) in enumerate(
            (("M10_share_sires_used", "eligible males used (%)"),
             ("M14_top5_sire_share", "litters by the top 5 sires, 5 years (%)"))
        ):  # fmt: skip
            g = sb[sb["metric"] == metric].sort_values("strategy")
            ax = axes[row][col]
            y = np.arange(len(g))
            err = np.nan_to_num(np.vstack([g["mean"] - g["lo"], g["hi"] - g["mean"]]))
            ax.barh(y, 100 * g["mean"], xerr=100 * err, capsize=3,
                    color=[style(x)[0] for x in g["strategy"]])  # fmt: skip
            ax.set_yticks(y, g["strategy"], fontsize="small")
            ax.set(xlabel=lab, title=b if row == 0 else "")
    fig.suptitle("How evenly sires are used (generation 10)")
    return _save(fig, out, "figL_sire_use", poster)


E8_PANELS = (
    ("R_ne_f_late", "Ne (late window)", 1.0, "higher is better"),
    ("M8_mean_tbv_hd", "mean true HD breeding value", 1.0, "lower is better"),
    ("freq", "tested risk-allele frequency, sum (%)", 100.0, "lower is better"),
)


def fig_m(summ: pd.DataFrame, per_gen: pd.DataFrame, out: Path, poster: bool) -> list[Path]:
    """E8: diversity, hips and disease alleles at generation 10 per arm, S1 as reference line."""
    from breeding_smarter.experiments.summary import t_interval

    sids = [x for x in summ["strategy"].unique() if x == "S1" or str(x).startswith("S3q")]
    if not any(str(x).startswith("S3q-") for x in sids) or "S1" not in sids:
        return []
    g10 = summ[(summ["generation"] == 10) & (summ["adoption"] == 1.0)]
    pr = per_gen[
        (per_gen["generation"] == 10)
        & (per_gen["adoption"] == 1.0)
        & per_gen["metric"].str.startswith("M6_freq_")
    ]
    freq = pr.groupby(["breed", "strategy", "replicate"])["value"].sum().reset_index()
    breeds = sorted(g10["breed"].unique())
    fig, axes = plt.subplots(len(breeds), 3, figsize=(16, 3.2 * len(breeds) + 1), squeeze=False)
    for r, b in enumerate(breeds):
        order = sorted((x for x in sids if x in set(g10[g10["breed"] == b]["strategy"])), key=len)
        for c, (metric, lab, scale, hint) in enumerate(E8_PANELS):
            ax = axes[r][c]
            if metric == "freq":
                fb = freq[freq["breed"] == b]
                stats = [t_interval(fb[fb["strategy"] == x]["value"].to_numpy()) for x in order]
            else:
                sb = g10[(g10["breed"] == b) & (g10["metric"] == metric)].set_index("strategy")
                stats = [
                    tuple(sb.loc[x, ["mean", "lo", "hi"]]) if x in sb.index else (np.nan,) * 3
                    for x in order
                ]
            m, lo, hi = (scale * np.array(v, float) for v in zip(*stats, strict=True))
            y = np.arange(len(order))
            err = np.nan_to_num(np.vstack([m - lo, hi - m]))
            ax.barh(y, m, xerr=err, capsize=3, color=[style(x)[0] for x in order])
            if "S1" in order:
                ax.axvline(m[order.index("S1")], color="#333333", lw=1, ls=":")
            ax.set_yticks(y, [strategy_label(x) for x in order] if c == 0 else [], fontsize="small")
            if metric == "freq" and not np.nansum(m):
                ax.text(0.5, 0.5, "no segregating tested locus", transform=ax.transAxes,
                        ha="center", va="center", fontsize="small")  # fmt: skip
            ax.set(xlabel=f"{lab}\n({hint})", title=b if c == 1 else "")
    fig.suptitle("Diversity, hips and disease alleles at generation 10 (dotted line: S1)")
    fig.tight_layout()
    return _save(fig, out, "figM_health_gain_quotas", poster)


def _e2_per_gen() -> pd.DataFrame | None:
    from breeding_smarter.experiments.runner import report_dir

    path = report_dir("E2_adoption") / "per_generation_replicates.csv.gz"
    return pd.read_csv(path) if path.exists() else None


def make_figures(
    exp_id: str, df: pd.DataFrame, per_gen: pd.DataFrame, summ: pd.DataFrame, out: Path
) -> list[Path]:
    paths: list[Path] = []
    for poster in (False, True):
        plotstyle.apply(poster=poster)
        p12 = bool(summ["strategy"].str.startswith(("CC-", "S3q")).any())
        if summ["strategy"].nunique() > 1:
            if not p12:
                paths += fig_a(summ, out, poster)
                paths += fig_b(summ, out, poster)
                paths += fig_d(per_gen, out, poster)
            paths += fig_c(summ, out, poster)
            paths += fig_f(summ, out, poster)
        if p12:
            paths += fig_g(summ, out, poster)
            paths += fig_h(summ, out, poster)
            paths += fig_i(per_gen, out, poster)
            paths += fig_j(summ, out, poster)
            paths += fig_k(per_gen, out, poster, _e2_per_gen())
            paths += fig_l(summ, out, poster)
            paths += fig_m(summ, per_gen, out, poster)
        else:
            paths += fig_e(per_gen, out, poster)
    plotstyle.apply()
    return paths
