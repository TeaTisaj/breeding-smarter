"""Pre-registered P12 success criteria H1 to H6 (plan/13_P12_coordination.md section 4).

Reads the per-replicate tables written by `write_summary` for E5, E6 (and E1 is not needed:
E5 contains the anchors S0, S1, S3 with the same seeds). All comparisons are paired by
replicate (common random numbers), 95% t-intervals, late window (generations 5 to 10).
Writes `reports/experiments/P12_hypotheses.md` and `.csv`. In-silico results only.

E8 (plan/14_E8_health_gain_quotas.md): criteria H8a to H8f from the E8 per-replicate table,
generation 10, written to `reports/experiments/E8_hypotheses/`.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from breeding_smarter.experiments.runner import load_results, report_dir
from breeding_smarter.experiments.summary import t_interval

E5, E6, E7 = "E5_coordination", "E6_budget_and_kinship", "E7_adoption_quotas"
E8 = "E8_health_gain_quotas"
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
    return _summed(pr, breed, sid, "M6_affected_")


def _summed(pr: pd.DataFrame, breed: str, sid: str, prefix: str) -> pd.Series:
    """Per replicate: sum over tested loci of metric `prefix<locus>` at generation 10."""
    sub = pr[
        (pr["breed"] == breed)
        & (pr["strategy"] == sid)
        & (pr["adoption"] == 1.0)
        & (pr["generation"] == 10)
        & pr["metric"].str.startswith(prefix)
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


# ---------------------------------------------------------------- E8


def e8_arms(pr: pd.DataFrame) -> dict[str, str]:
    """SYN_M arm ids of the 2x2 (beta read from the id of the combined arm)."""
    ids = set(pr[pr["breed"] == "SYN_M"]["strategy"])
    both = sorted(x for x in ids if re.fullmatch(r"S3q-gain\d{3}-c\d{3}", x))
    if len(both) != 1:
        raise ValueError(f"expected one S3q-gainNNN-cBBB arm in SYN_M, found {both}")
    gain, carrier = both[0].split("-")[1:]
    return {"both": both[0], "gain": f"S3q-{gain}", "carrier": f"S3q-{carrier}", "none": "S3q"}


def evaluate_e8(pr: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    def add(h: str, breed: str, what: str, d: tuple[float, float, float, int], ok: Any) -> None:
        m, lo, hi, n = d
        rows.append(
            {"id": h, "breed": breed, "quantity": what, "estimate": m, "lo": lo, "hi": hi,
             "n": n, "pass": ok}
        )  # fmt: skip

    def one(x: pd.Series) -> tuple[float, float, float, int]:
        v = x.to_numpy(dtype=float)
        v = v[np.isfinite(v)]
        return (*t_interval(v), int(v.size))

    b, a = "SYN_M", e8_arms(pr)
    ne = {k: _val(pr, b, sid, "R_ne_f_late") for k, sid in {**a, "S1": "S1"}.items()}
    hd = {k: _val(pr, b, sid, "M8_mean_tbv_hd") for k, sid in {**a, "S1": "S1"}.items()}
    fq = {k: _summed(pr, b, sid, "M6_freq_") for k, sid in {**a, "S1": "S1"}.items()}
    af = {k: _summed(pr, b, sid, "M6_affected_") for k, sid in {**a, "S1": "S1"}.items()}
    arm = a["both"]
    h8a = _paired(ne["both"], ne["S1"])
    add("H8a", b, f"Ne late: {arm} - S1", h8a, bool(h8a[1] > 0))
    h8b = _paired(hd["both"], hd["S1"])
    add("H8b", b, f"true HD breeding value (gen 10): {arm} - S1", h8b, bool(h8b[2] < 0))
    h8c = _paired(fq["both"], fq["S1"])
    add("H8c", b, f"tested risk-allele freq, sum (gen 10): {arm} - S1", h8c, bool(h8c[2] < 0))
    ok = bool(h8a[1] > 0 and h8b[2] < 0 and h8c[2] < 0)
    add("H8", b, "diversity, health and hips at once (H8a and H8b and H8c)",
        (np.nan, np.nan, np.nan, 0), ok)  # fmt: skip
    add("H8d", b, f"affected share at tested loci (gen 10): {arm} - S1",
        _paired(af["both"], af["S1"]), None)  # fmt: skip
    for k, lab in (("none", "S3q"), ("gain", a["gain"]), ("carrier", a["carrier"])):
        add("H8-arm", b, f"Ne late: {lab} - S1", _paired(ne[k], ne["S1"]), None)
        add("H8-arm", b, f"HD (gen 10): {lab} - S1", _paired(hd[k], hd["S1"]), None)
        add("H8-arm", b, f"freq (gen 10): {lab} - S1", _paired(fq[k], fq["S1"]), None)
    for what, x in (("freq", fq), ("Ne late", ne)):
        eff = 0.5 * ((x["both"] - x["gain"]) + (x["carrier"] - x["none"]))
        add("H8e", b, f"carrier-limit effect on {what} (mean over planners)", one(eff), None)
    for what, x in (("HD", hd), ("Ne late", ne)):
        eff = 0.5 * ((x["gain"] - x["none"]) + (x["both"] - x["carrier"]))
        add("H8e", b, f"gain-OCS effect on {what} (mean over carrier levels)", one(eff), None)
    s = "SYN_S"
    gains = sorted(x for x in set(pr[pr["breed"] == s]["strategy"]) if x.startswith("S3q-gain"))
    for g in gains:
        for ref in ("S1", "S3q"):
            add(
                "H8f",
                s,
                f"Ne late: {g} - {ref}",
                _paired(_val(pr, s, g, "R_ne_f_late"), _val(pr, s, ref, "R_ne_f_late")),
                None,
            )
            add("H8f", s, f"HD (gen 10): {g} - {ref}",
                _paired(_val(pr, s, g, "M8_mean_tbv_hd"), _val(pr, s, ref, "M8_mean_tbv_hd")),
                None)  # fmt: skip
    return pd.DataFrame(rows)


def e8_diagnostics(exp_id: str = E8) -> list[str]:
    """Per breed and strategy: seasons, infeasible, carrier limit relaxed, overflow, solver s."""
    lines = [
        "| breed | strategy | seasons | infeasible | carrier relaxed | overflow (dams) | "
        "solver s median | p95 |",
        "|---|---|---|---|---|---|---|---|",
    ]
    try:
        df = load_results(exp_id)
    except (ValueError, FileNotFoundError):
        return lines
    keys = ["D3_infeasible", "D5_solver_seconds", "D7_overflow", "D10_carrier_relaxed"]
    d = df[df["metric"].isin(keys)]
    for (b, sid), g in d.groupby(["breed", "strategy"]):
        v = {k: g[g["metric"] == k]["value"].to_numpy() for k in keys}
        sec = v["D5_solver_seconds"]
        if sec.size == 0:
            continue
        rel = v["D10_carrier_relaxed"]
        rel_s = f"{int(rel.sum())} of {rel.size}" if rel.size else "n/a"
        lines.append(
            f"| {b} | {sid} | {sec.size} | {int(v['D3_infeasible'].sum())} | {rel_s} | "
            f"{int(v['D7_overflow'].sum())} | {np.median(sec):.2f} | "
            f"{np.percentile(sec, 95):.2f} |"
        )
    return lines


def write_e8_report(exp_id: str = E8) -> Path:
    table = evaluate_e8(_per_rep(exp_id))
    out = report_dir("E8_hypotheses")
    out.mkdir(parents=True, exist_ok=True)
    table.to_csv(out / "hypotheses.csv", index=False)
    lines = [
        "# E8 pre-registered criteria (in-silico results on synthetic populations)",
        "",
        "Pre-registration: `plan/14_E8_health_gain_quotas.md`. Generation 10 (Ne: late window, "
        "generations 5 to 10); paired by replicate (same seeds); 95% t-intervals. Frequencies "
        "and affected shares are sums over tested loci, shown in %. HD: lower is better.",
        "",
        "| id | breed | quantity | estimate | lo | hi | n | pass |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for _, r in table.iterrows():
        pct = any(k in r["quantity"] for k in ("freq", "affected"))
        ok = "" if r["pass"] is None or pd.isna(r["pass"]) else ("yes" if r["pass"] else "no")
        lines.append(
            f"| {r['id']} | {r['breed']} | {r['quantity']} | {_fmt(r['estimate'], pct)} | "
            f"{_fmt(r['lo'], pct)} | {_fmt(r['hi'], pct)} | {r['n']} | {ok} |"
        )
    lines += ["", "## Planner diagnostics", "", *e8_diagnostics(exp_id), ""]
    (out / "hypotheses.md").write_text("\n".join(lines))
    return out / "hypotheses.md"
