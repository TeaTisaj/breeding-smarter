"""Pre-registered P12 success criteria H1 to H6 (plan/13_P12_coordination.md section 4).

Reads the per-replicate tables written by `write_summary` for E5, E6 (and E1 is not needed:
E5 contains the anchors S0, S1, S3 with the same seeds). All comparisons are paired by
replicate (common random numbers), 95% t-intervals, late window (generations 5 to 10).
Writes `reports/experiments/P12_hypotheses.md` and `.csv`. In-silico results only.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from breeding_smarter.experiments.runner import load_results, report_dir
from breeding_smarter.experiments.summary import t_interval

E5, E6, E7 = "E5_coordination", "E6_budget_and_kinship", "E7_adoption_quotas"
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


def diagnostics_lines() -> list[str]:
    """Infeasible seasons and solver-time distribution per experiment, breed and strategy."""
    lines = [
        "| experiment | breed | strategy | seasons | infeasible | solver s median | p95 | max |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for exp in (E5, E6, E7):
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
