"""Pre-registered P12 success criteria H1 to H6 (plan/13_P12_coordination.md section 4) and
E8 criteria H7 to H10 (plan/14_E8_hips_quotas.md section 3).

Reads the per-replicate tables written by `write_summary` for E5, E6 (and E1 is not needed:
E5 contains the anchors S0, S1, S3 with the same seeds). All comparisons are paired by
replicate (common random numbers), 95% t-intervals, late window (generations 5 to 10).
Writes `reports/experiments/P12_hypotheses/hypotheses.md` and `.csv`; E8 reads only its own
per-replicate table (anchors S1, S3, S3q rerun with the E5 seed) and writes
`reports/experiments/E8_hypotheses/`. In-silico results only.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

from breeding_smarter.experiments.runner import load_results, report_dir
from breeding_smarter.experiments.summary import t_interval

E5, E6, E7 = "E5_coordination", "E6_budget_and_kinship", "E7_adoption_quotas"
E8 = "E8_hips_quotas"
# E8 arm that decides the headline per breed, and the H8 non-inferiority margin (fixed before
# the run; plan/14_E8_hips_quotas.md)
E8_PRIMARY = {"SYN_S": "S3q-gain025-hc", "SYN_M": "S3q-gain010-hc"}
E8_ANCHORS = ("S1", "S3", "S3q")
E8_NE_MARGIN = 0.9
BREEDS = ("SYN_S", "SYN_M")
CONTROLS = ("none", "mkx", "cap", "ocs")
MATINGS = ("rand", "mc1")


def _per_rep(exp_id: str) -> pd.DataFrame:
    p = report_dir(exp_id) / "per_generation_replicates.csv.gz"
    return pd.read_csv(p)


def _val(pr: pd.DataFrame, breed: str, sid: str, metric: str, adoption: float = 1.0) -> pd.Series:
    s = pr[
        (pr["breed"] == breed)
        & (pr["strategy"] == sid)
        & (pr["metric"] == metric)
        & (pr["adoption"] == adoption)
        & (pr["generation"] == 10)
    ]
    return s.set_index("replicate")["value"]


def _paired(a: pd.Series, b: pd.Series) -> tuple[float, float, float, int]:
    d = (a - b.reindex(a.index)).to_numpy(dtype=float)
    d = d[np.isfinite(d)]
    m, lo, hi = t_interval(d)
    return m, lo, hi, int(d.size)


def fieller_ratio(
    num: pd.Series, den: pd.Series, level: float = 0.95
) -> tuple[float, float, float, int]:
    """(mean(num) / mean(den), lower, upper, n) for paired samples (aligned on the index).

    Fieller's interval: the theta with |mean(num - theta den)| <= t sd(num - theta den) / sqrt(n),
    i.e. the roots of (dbar^2 - t^2 s_dd / n) theta^2 - 2 (nbar dbar - t^2 s_nd / n) theta +
    (nbar^2 - t^2 s_nn / n) = 0. Bounds are nan when mean(den) is not clearly away from 0 (the
    interval is then unbounded) or with fewer than 2 pairs.
    """
    a = num.to_numpy(dtype=float)
    b = den.reindex(num.index).to_numpy(dtype=float)
    ok = np.isfinite(a) & np.isfinite(b)
    a, b = a[ok], b[ok]
    n = int(a.size)
    if n == 0 or b.mean() == 0:
        return (np.nan, np.nan, np.nan, n)
    ratio = float(a.mean() / b.mean())
    if n < 2:
        return (ratio, np.nan, np.nan, n)
    t2 = float(stats.t.ppf(0.5 + level / 2, n - 1)) ** 2
    cov = np.cov(a, b, ddof=1)
    qa = b.mean() ** 2 - t2 * cov[1, 1] / n
    qb = a.mean() * b.mean() - t2 * cov[0, 1] / n
    qc = a.mean() ** 2 - t2 * cov[0, 0] / n
    disc = qb * qb - qa * qc
    if qa <= 0 or disc < 0:
        return (ratio, np.nan, np.nan, n)
    root = float(np.sqrt(disc))
    return (ratio, (qb - root) / qa, (qb + root) / qa, n)


def _ne_of_mean(x: pd.Series) -> float:
    m = float(np.nanmean(x.to_numpy(dtype=float)))
    return 1.0 / (2.0 * m) if m > 0 else np.inf


def _tested_affected(pr: pd.DataFrame, breed: str, sid: str) -> pd.Series:
    sub = pr[
        (pr["breed"] == breed)
        & (pr["strategy"] == sid)
        & (pr["adoption"] == 1.0)
        & (pr["generation"] == 10)
        & pr["metric"].str.startswith("M6_affected_")
    ]
    return sub.groupby("replicate")["value"].sum()


def evaluate() -> tuple[pd.DataFrame, list[str]]:
    e5 = _per_rep(E5)
    e6 = _per_rep(E6) if (report_dir(E6) / "per_generation_replicates.csv.gz").exists() else None
    rows: list[dict[str, Any]] = []

    def add(h: str, breed: str, what: str, est: float, lo: float, hi: float, n: int, ok: Any):
        rows.append(
            {"id": h, "breed": breed, "quantity": what, "estimate": est, "lo": lo, "hi": hi,
             "n": n, "pass": ok}
        )  # fmt: skip

    for b in BREEDS:
        ne_cc = _val(e5, b, "CC-ocs-mc1", "R_ne_f_late")
        ne_s1 = _val(e5, b, "S1", "R_ne_f_late")
        m, lo, hi, n = _paired(ne_cc, ne_s1)
        add("H1", b, "Ne late: CC-ocs-mc1 - S1 (paired)", m, lo, hi, n, bool(lo > 0))
        df_cc = _val(e5, b, "CC-ocs-mc1", "R_delta_f_late")
        df_s1 = _val(e5, b, "S1", "R_delta_f_late")
        m, lo, hi, n = _paired(df_cc, df_s1)
        add("H1-support", b, "dF late: CC-ocs-mc1 - S1 (paired)", m, lo, hi, n, None)
        df_s3 = _val(e5, b, "S3", "R_delta_f_late")
        m, lo, hi, n = _paired(df_cc, df_s3)
        add("H2", b, "dF late: CC-ocs-mc1 - S3 (paired)", m, lo, hi, n, bool(hi < 0))
        means = {
            (c, mt): float(np.nanmean(_val(e5, b, f"CC-{c}-{mt}", "R_delta_f_late")))
            for c in CONTROLS
            for mt in MATINGS
        }
        by_c = [np.mean([means[(c, mt)] for mt in MATINGS]) for c in CONTROLS]
        by_m = [np.mean([means[(c, mt)] for c in CONTROLS]) for mt in MATINGS]
        rc, rm = float(np.ptp(by_c)), float(np.ptp(by_m))
        add("H3", b, "range of late dF over controls minus over matings", rc - rm, rc, rm, 0,
            bool(rc > rm))  # fmt: skip
        if b == "SYN_M":
            aff = _tested_affected(e5, b, "S3q") - _tested_affected(e5, b, "S1")
            m, lo, hi = t_interval(aff.to_numpy(dtype=float))
            add("H4a", b, "affected share at tested loci (gen 10): S3q - S1", m, lo, hi,
                int(aff.notna().sum()), bool(m <= 0))  # fmt: skip
            m, lo, hi, n = _paired(_val(e5, b, "S3q", "R_ne_f_late"), ne_s1)
            add("H4b", b, "Ne late: S3q - S1 (paired)", m, lo, hi, n, bool(lo > 0))
        if e6 is not None:
            ne_or = _ne_of_mean(_val(e6, b, "CC-ocs-mc1-oracle", "R_delta_f_late"))
            ne_s0 = _ne_of_mean(_val(e5, b, "S0", "R_delta_f_late"))
            add("H5", b, "Ne(1/2 mean dF late): oracle / S0", ne_or / ne_s0, ne_or, ne_s0, 0,
                bool(ne_or >= 0.9 * ne_s0))  # fmt: skip
            m, lo, hi, n = _paired(
                _val(e6, b, "CC-ocs-mc1-oracle", "R_ne_f_late"),
                _val(e6, b, "CC-ocs-mc1", "R_ne_f_late"),
            )
            add("H6", b, "Ne late: oracle - recorded (paired)", m, lo, hi, n, None)
            m, lo, hi, n = _paired(
                _val(e6, b, "CC-ocs-mc1-oracle", "R_delta_f_late"),
                _val(e6, b, "CC-ocs-mc1", "R_delta_f_late"),
            )
            add("H6-support", b, "dF late: oracle - recorded (paired)", m, lo, hi, n, None)
    table = pd.DataFrame(rows)
    return table, diagnostics_lines()


def diagnostics_lines(exps: tuple[str, ...] = (E5, E6, E7)) -> list[str]:
    """Infeasible seasons and solver-time distribution per experiment, breed and strategy."""
    lines = [
        "| experiment | breed | strategy | seasons | infeasible | solver s median | p95 | max |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for exp in exps:
        try:
            df = load_results(exp)
        except (ValueError, FileNotFoundError):
            continue
        d = df[df["metric"].isin(["D3_infeasible", "D5_solver_seconds"])]
        for (b, sid, ad), g in d.groupby(["breed", "strategy", "adoption"]):
            sec = g[g["metric"] == "D5_solver_seconds"]["value"].to_numpy()
            inf = g[g["metric"] == "D3_infeasible"]["value"].to_numpy()
            if sec.size == 0:
                continue
            name = sid if ad == 1.0 else f"{sid} (adoption {ad:g})"
            lines.append(
                f"| {exp} | {b} | {name} | {inf.size} | {int(inf.sum())} | "
                f"{np.median(sec):.2f} | {np.percentile(sec, 95):.2f} | {sec.max():.2f} |"
            )
    return lines


def _fmt(x: float, pct: bool) -> str:
    if not np.isfinite(x):
        return "inf" if x == np.inf else "n/a"
    return f"{100 * x:.3f}" if pct else f"{x:.3g}"


def write_report() -> Path:
    table, diag = evaluate()
    out = report_dir("P12_hypotheses")
    out.mkdir(parents=True, exist_ok=True)
    table.to_csv(out / "hypotheses.csv", index=False)
    lines = [
        "# P12 pre-registered criteria (in-silico results on synthetic populations)",
        "",
        "Late window = generations 5 to 10; paired by replicate (same seeds); 95% t-intervals. "
        "dF rows are in % per generation. H3 lists range over controls (lo) and over matings "
        "(hi). H5 lists oracle Ne (lo) and S0 Ne (hi), each 1/(2 mean dF late).",
        "",
        "| id | breed | quantity | estimate | lo | hi | n | pass |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for _, r in table.iterrows():
        pct = r["quantity"].startswith(("dF", "range")) or r["id"] == "H4a"
        ok = "" if r["pass"] is None or pd.isna(r["pass"]) else ("yes" if r["pass"] else "no")
        lines.append(
            f"| {r['id']} | {r['breed']} | {r['quantity']} | {_fmt(r['estimate'], pct)} | "
            f"{_fmt(r['lo'], pct)} | {_fmt(r['hi'], pct)} | {r['n']} | {ok} |"
        )
    lines += ["", "## Planner diagnostics", "", *diag, ""]
    (out / "hypotheses.md").write_text("\n".join(lines))
    return out / "hypotheses.md"


def evaluate_e8() -> pd.DataFrame:
    """E8 criteria for every non-anchor arm; `primary` marks the arm that decides the headline.

    H7 hips: mean true HD BV at generation 10, arm - S3q < 0 (CI upper bound < 0).
    H8 diversity: Ne(arm) / Ne(S3q) with Ne = 1 / (2 mean late dF) (as H5), i.e. mean dF(S3q) /
    mean dF(arm) over paired replicates; pass if the lower bound of its 95% Fieller interval
    is >= 0.9.
    H9 health (SYN_M): affected share at tested loci at generation 10, arm - S1 < 0 (CI upper
    bound < 0). H10a, H10b (no pass/fail): Ne late arm - S1, HD BV arm - S3, paired.
    """
    e8 = _per_rep(E8)
    rows: list[dict[str, Any]] = []

    def add(
        h: str, b: str, sid: str, what: str, est: float, lo: float, hi: float, n: int, ok: Any
    ) -> None:
        rows.append(
            {"id": h, "breed": b, "strategy": sid, "primary": sid == E8_PRIMARY.get(b),
             "quantity": what, "estimate": est, "lo": lo, "hi": hi, "n": n, "pass": ok}
        )  # fmt: skip

    for b in BREEDS:
        arms = sorted(set(e8.loc[e8["breed"] == b, "strategy"]) - set(E8_ANCHORS))
        arms.sort(key=lambda sid: sid != E8_PRIMARY.get(b))
        for sid in arms:
            hd = _val(e8, b, sid, "M8_mean_tbv_hd")
            m, lo, hi, n = _paired(hd, _val(e8, b, "S3q", "M8_mean_tbv_hd"))
            add("H7", b, sid, f"HD BV gen 10: {sid} - S3q (paired)", m, lo, hi, n, bool(hi < 0))
            df_arm = _val(e8, b, sid, "R_delta_f_late")
            df_s3q = _val(e8, b, "S3q", "R_delta_f_late")
            r, lo, hi, n = fieller_ratio(df_s3q, df_arm)
            add("H8", b, sid, f"Ne ratio {sid} / S3q (1/(2 mean dF late), Fieller CI)", r, lo,
                hi, n, bool(np.isfinite(lo) and lo >= E8_NE_MARGIN))  # fmt: skip
            add("H8-Ne", b, sid, f"Ne(1/2 mean dF late): {sid} (lo) and S3q (hi)",
                np.nan, _ne_of_mean(df_arm), _ne_of_mean(df_s3q), 0, None)  # fmt: skip
            m, lo, hi, n = _paired(df_arm, df_s3q)
            add("H8-support", b, sid, f"dF late: {sid} - S3q (paired)", m, lo, hi, n, None)
            if b == "SYN_M":
                aff = _tested_affected(e8, b, sid) - _tested_affected(e8, b, "S1")
                m, lo, hi = t_interval(aff.to_numpy(dtype=float))
                add("H9", b, sid, f"affected share at tested loci (gen 10): {sid} - S1", m, lo,
                    hi, int(aff.notna().sum()), bool(hi < 0))  # fmt: skip
            m, lo, hi, n = _paired(
                _val(e8, b, sid, "R_ne_f_late"), _val(e8, b, "S1", "R_ne_f_late")
            )
            add("H10a", b, sid, f"Ne late: {sid} - S1 (paired)", m, lo, hi, n, None)
            m, lo, hi, n = _paired(hd, _val(e8, b, "S3", "M8_mean_tbv_hd"))
            add("H10b", b, sid, f"HD BV gen 10: {sid} - S3 (paired)", m, lo, hi, n, None)
    return pd.DataFrame(rows)


def _pct0(x: float) -> str:
    return f"{100 * x:.0f}%" if np.isfinite(x) else "n/a"


def e8_headlines(table: pd.DataFrame) -> list[str]:
    """Interpretation rules for the primary arm (plan/14_E8_hips_quotas.md section 3).

    All of H7, H8 (and H9 in SYN_M) pass: the full headline. Only H8 fails: hips (and health)
    improve at a measured diversity cost, quoted as the H8 ratio and interval; "still above
    today's market" only if the H10a interval (Ne P - S1) lies above 0. Otherwise: the list of
    passed and failed criteria.
    """
    out = []
    for b in BREEDS:
        prim = table[(table["breed"] == b) & table["primary"]]
        t = prim[prim["id"].isin(["H7", "H8", "H9"])]
        if t.empty:
            out.append(f"{b}: primary arm {E8_PRIMARY[b]} not in the results.")
            continue
        passed = [h for h, ok in zip(t["id"], t["pass"], strict=True) if ok]
        failed = [h for h, ok in zip(t["id"], t["pass"], strict=True) if not ok]
        if not failed:
            what = "diversity, health and hips at once" if b == "SYN_M" else "diversity and hips"
            out.append(f"{b} ({E8_PRIMARY[b]}): all criteria pass -> {what} (in silico).")
        elif failed == ["H8"]:
            h8 = t[t["id"] == "H8"].iloc[0]
            h10a = prim[prim["id"] == "H10a"]
            above = not h10a.empty and bool(h10a["lo"].iloc[0] > 0)
            what = "hips and health improve" if b == "SYN_M" else "hips improve"
            market = (
                "Ne still above today's market (H10a)"
                if above
                else "Ne not shown to be above today's market (H10a)"
            )
            out.append(
                f"{b} ({E8_PRIMARY[b]}): H8 fails -> {what} at a measured diversity cost: Ne "
                f"{_pct0(h8['estimate'])} of S3q (95% CI {_pct0(h8['lo'])} to "
                f"{_pct0(h8['hi'])}); {market} (in silico)."
            )
        else:
            out.append(
                f"{b} ({E8_PRIMARY[b]}): passed {', '.join(passed) or 'none'}; "
                f"failed {', '.join(failed)}."
            )
    return out


def write_report_e8() -> Path:
    table = evaluate_e8()
    out = report_dir("E8_hypotheses")
    out.mkdir(parents=True, exist_ok=True)
    table.to_csv(out / "hypotheses.csv", index=False)
    lines = [
        "# E8 pre-registered criteria (in-silico results on synthetic populations)",
        "",
        "Criteria: plan/14_E8_hips_quotas.md. Late window = generations 5 to 10; paired by "
        "replicate (same seeds); 95% t-intervals. dF rows are in % per generation. H8 is the Ne "
        "ratio arm / S3q (each 1/(2 mean dF late)) with a 95% Fieller interval; pass if its lower "
        f"bound >= {E8_NE_MARGIN:g}. Only the primary arm per breed decides the headline.",
        "",
        "## Headline",
        "",
        *[f"- {h}" for h in e8_headlines(table)],
        "",
        "| id | breed | arm | primary | quantity | estimate | lo | hi | n | pass |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for _, r in table.iterrows():
        pct = r["quantity"].startswith("dF") or r["id"] == "H9"
        ok = "" if r["pass"] is None or pd.isna(r["pass"]) else ("yes" if r["pass"] else "no")
        lines.append(
            f"| {r['id']} | {r['breed']} | {r['strategy']} | {'yes' if r['primary'] else ''} | "
            f"{r['quantity']} | {_fmt(r['estimate'], pct)} | {_fmt(r['lo'], pct)} | "
            f"{_fmt(r['hi'], pct)} | {r['n']} | {ok} |"
        )
    lines += ["", "## Planner diagnostics", "", *diagnostics_lines((E8,)), ""]
    (out / "hypotheses.md").write_text("\n".join(lines))
    return out / "hypotheses.md"
