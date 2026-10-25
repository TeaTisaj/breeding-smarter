"""Pre-registered P12 success criteria H1 to H6 (plan/13_P12_coordination.md section 4).

Reads the per-replicate tables written by `write_summary` for E5, E6 (and E1 is not needed:
E5 contains the anchors S0, S1, S3 with the same seeds). All comparisons are paired by
replicate (common random numbers), 95% t-intervals, late window (generations 5 to 10).
Writes `reports/experiments/P12_hypotheses.md` and `.csv`. In-silico results only.

E8 (plan/14_E8_health_gain_quotas.md): criteria H8a to H8f from the E8 per-replicate table,
generation 10, written to `reports/experiments/E8_hypotheses/`.

E11 (plan/16_E11_paper_robustness.md): H11-pop over four populations, H11-cap, H11-free and
H11-adopt, written to `reports/experiments/E11_hypotheses/`.
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
E9, E10 = "E9_policy_dial", "E10_robustness"
E9_ARM = "S3q-gain010-c050"  # the E8 winner, replicated in E9
E11_POPS = {p: f"E11a_pop_{p}" for p in ("v1", "v1b", "v1c", "v1d")}
E11B, E11C = "E11b_controls_freedom", "E11c_adoption"
E11_FREEDOM = ("t1", "", "u5")  # "" = default 0.5 / 0.3 / 0.2
E11_MARGIN = 0.2  # equivalence margin for H11-cap, share of mean S3q Ne (assumption, plan 16)
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


def _diffs(a: pd.Series, b: pd.Series) -> np.ndarray:
    d = (a - b.reindex(a.index)).to_numpy(dtype=float)
    return d[np.isfinite(d)]


def _paired(a: pd.Series, b: pd.Series) -> tuple[float, float, float, int]:
    d = _diffs(a, b)
    m, lo, hi = t_interval(d)
    return m, lo, hi, int(d.size)


def _ne_of_mean(x: pd.Series) -> float:
    m = float(np.nanmean(x.to_numpy(dtype=float)))
    return 1.0 / (2.0 * m) if m > 0 else np.inf


def _tested_affected(pr: pd.DataFrame, breed: str, sid: str) -> pd.Series:
    return _summed(pr, breed, sid, "M6_affected_")


def _summed(
    pr: pd.DataFrame, breed: str, sid: str, prefix: str, adoption: float = 1.0
) -> pd.Series:
    """Per replicate: sum over tested loci of metric `prefix<locus>` at generation 10."""
    sub = pr[
        (pr["breed"] == breed)
        & (pr["strategy"] == sid)
        & (pr["adoption"] == adoption)
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


# ---------------------------------------------------------------- E9 and E10


def _ladder(pr: pd.DataFrame, breed: str) -> list[tuple[float, str]]:
    """(dF budget, id) of the budget-ladder arms: `-c050` arms in SYN_M, plain gain arms else."""
    pat = r"S3q-gain(\d{3})-c050" if breed == "SYN_M" else r"S3q-gain(\d{3})"
    out = []
    for sid in set(pr[pr["breed"] == breed]["strategy"]):
        m = re.fullmatch(pat, sid)
        if m:
            out.append((int(m.group(1)) / 1e4, sid))
    return sorted(out)


def pareto_front(points: dict[str, tuple[float, float]]) -> list[str]:
    """Ids not dominated in (Ne higher, HD lower)."""
    return sorted(
        a
        for a, (ne, hd) in points.items()
        if not any(
            (ne2 >= ne and hd2 <= hd) and (ne2 > ne or hd2 < hd)
            for b, (ne2, hd2) in points.items()
            if b != a
        )
    )


def evaluate_e9(pr9: pd.DataFrame, pr10: pd.DataFrame | None) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    def add(h: str, breed: str, what: str, d: tuple[float, float, float, int], ok: Any) -> None:
        m, lo, hi, n = d
        rows.append(
            {"id": h, "breed": breed, "quantity": what, "estimate": m, "lo": lo, "hi": hi,
             "n": n, "pass": ok}
        )  # fmt: skip

    def three(b: str, sid: str, pr: pd.DataFrame, ad: float = 1.0) -> dict[str, pd.Series]:
        return {
            "Ne": _val(pr, b, sid, "R_ne_f_late", ad),
            "HD": _val(pr, b, sid, "M8_mean_tbv_hd", ad),
            "freq": _summed(pr, b, sid, "M6_freq_", ad),
            "affected": _summed(pr, b, sid, "M6_affected_", ad),
        }

    def all_three(h: str, b: str, label: str, x: dict[str, pd.Series]) -> None:
        d = {k: _paired(x[k], s1[k]) for k in ("Ne", "HD", "freq")}
        add(f"{h}-Ne", b, f"Ne late: {label} - S1", d["Ne"], bool(d["Ne"][1] > 0))
        add(f"{h}-HD", b, f"HD (gen 10): {label} - S1", d["HD"], bool(d["HD"][2] < 0))
        add(f"{h}-freq", b, f"freq (gen 10): {label} - S1", d["freq"], bool(d["freq"][2] < 0))
        ok = bool(d["Ne"][1] > 0 and d["HD"][2] < 0 and d["freq"][2] < 0)
        add(h, b, f"{label}: Ne, HD and freq all better than S1", (np.nan,) * 3 + (0,), ok)

    b = "SYN_M"
    s1 = three(b, "S1", pr9)
    s3q = three(b, "S3q", pr9)
    all_three("H9-rep", b, E9_ARM, three(b, E9_ARM, pr9))

    for breed in ("SYN_M", "SYN_S"):
        ref1 = three(breed, "S1", pr9)
        ref3 = three(breed, "S3q", pr9)
        points = {"S1": ref1, "S3q": ref3}
        for _, sid in _ladder(pr9, breed):
            x = three(breed, sid, pr9)
            points[sid] = x
            for k in ("Ne", "HD") + (("freq",) if breed == "SYN_M" else ()):
                add("H9-curve", breed, f"{k}: {sid} - S1", _paired(x[k], ref1[k]), None)
                add("H9-curve", breed, f"{k}: {sid} - S3q", _paired(x[k], ref3[k]), None)
        means = {
            sid: (float(np.nanmean(v["Ne"][np.isfinite(v["Ne"])])), float(np.nanmean(v["HD"])))
            for sid, v in points.items()
            if v["Ne"].size
        }
        for sid in pareto_front(means):
            ne, hd = means[sid]
            add("H9-pareto", breed, f"on the (Ne, HD) frontier: {sid}", (ne, np.nan, hd, 0), None)

    nolim = three(b, "S3q-gain010", pr9)
    for beta in ("c100", "c075", "c050", "c025"):
        sid = f"S3q-gain010-{beta}"
        x = three(b, sid, pr9)
        if not x["Ne"].size:
            continue
        add("H9-dose", b, f"freq: {sid} - S3q-gain010", _paired(x["freq"], nolim["freq"]), None)
        add("H9-dose", b, f"Ne late: {sid} - S3q-gain010", _paired(x["Ne"], nolim["Ne"]), None)

    arm, hc = three(b, E9_ARM, pr9), three(b, "S3q-gain010-hc", pr9)
    if hc["Ne"].size:
        d = _paired(arm["freq"], hc["freq"])
        add("H9-hc", b, f"freq: {E9_ARM} - S3q-gain010-hc", d, bool(d[2] < 0))
        add("H9-hc-support", b, f"affected: {E9_ARM} - S3q-gain010-hc",
            _paired(arm["affected"], hc["affected"]), None)  # fmt: skip
        add("H9-hc-support", b, f"Ne late: {E9_ARM} - S3q-gain010-hc",
            _paired(arm["Ne"], hc["Ne"]), None)  # fmt: skip
        add("H9-hc-support", b, "freq: S3q-gain010-hc - S3q-gain010",
            _paired(hc["freq"], nolim["freq"]), None)  # fmt: skip

    orc = three(b, f"{E9_ARM}-oracle", pr9)
    if orc["Ne"].size:
        d = _paired(orc["Ne"], arm["Ne"])
        add("H10-dna", b, f"Ne late: {E9_ARM}-oracle - {E9_ARM}", d, bool(d[1] > 0))
        add("H10-dna-support", b, f"HD: {E9_ARM}-oracle - {E9_ARM}",
            _paired(orc["HD"], arm["HD"]), None)  # fmt: skip

    if pr10 is not None:
        for ad in (0.25, 0.5, 0.75):
            x = three(b, E9_ARM, pr10, ad)
            if not x["Ne"].size:
                continue
            if ad == 0.5:
                all_three("H10-adopt", b, f"{E9_ARM} at adoption 0.5", x)
            else:
                for k in ("Ne", "HD", "freq"):
                    add("H10-adopt-other", b, f"{k}: {E9_ARM} at adoption {ad:g} - S1",
                        _paired(x[k], s1[k]), None)  # fmt: skip
    add(
        "support", b, "Ne late: S3q - S1 (sanity, as E5 and E8)", _paired(s3q["Ne"], s1["Ne"]), None
    )
    return pd.DataFrame(rows)


def write_e9_report() -> Path:
    from breeding_smarter.experiments.figures import fig_n, fig_o

    pr9 = _per_rep(E9)
    p10 = report_dir(E10) / "per_generation_replicates.csv.gz"
    pr10 = pd.read_csv(p10) if p10.exists() else None
    table = evaluate_e9(pr9, pr10)
    out = report_dir("E9_hypotheses")
    out.mkdir(parents=True, exist_ok=True)
    table.to_csv(out / "hypotheses.csv", index=False)
    lines = [
        "# E9 and E10 pre-registered criteria (in-silico results on synthetic populations)",
        "",
        "Pre-registration: `plan/15_E9_E10_policy_dial.md`. Generation 10 (Ne: late window, "
        "generations 5 to 10); paired by replicate (same seeds); 95% t-intervals. Frequencies "
        "and affected shares are sums over tested loci, shown in %. HD: lower is better. "
        "H9-pareto rows list mean Ne (estimate) and mean HD (hi).",
        "",
        "| id | breed | quantity | estimate | lo | hi | n | pass |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for _, r in table.iterrows():
        pct = r["quantity"].startswith(("freq", "affected"))
        ok = "" if r["pass"] is None or pd.isna(r["pass"]) else ("yes" if r["pass"] else "no")
        lines.append(
            f"| {r['id']} | {r['breed']} | {r['quantity']} | {_fmt(r['estimate'], pct)} | "
            f"{_fmt(r['lo'], pct)} | {_fmt(r['hi'], pct)} | {r['n']} | {ok} |"
        )
    lines += ["", "## Planner diagnostics", "", "### E9", "", *e8_diagnostics(E9)]
    if pr10 is not None:
        lines += ["", "### E10", "", *e8_diagnostics(E10)]
    figs = fig_n(pr9, out) + fig_o(pr9, pr10, out)
    lines += ["", "## Figures", "", *(f"- `{f.name}`" for f in figs if f.suffix == ".png"), ""]
    (out / "hypotheses.md").write_text("\n".join(lines))
    return out / "hypotheses.md"


# ---------------------------------------------------------------- E11


def cap_reading(lo: float, hi: float, ref_ne: float, margin: float = E11_MARGIN) -> str:
    """H11-cap reading of the interval of `Ne(S3q) - Ne(simple control)` (plan 16 §6)."""
    if lo > 0:
        return "OCS better"
    if hi < 0:
        return "simple control better"
    if max(abs(lo), abs(hi)) <= margin * ref_ne:
        return "as good"
    return "inconclusive"


def _arm_values(pr: pd.DataFrame, b: str, sid: str, ad: float = 1.0) -> dict[str, pd.Series]:
    return {
        "Ne": _val(pr, b, sid, "R_ne_f_late", ad),
        "Ne_c": _val(pr, b, sid, "R_ne_c_late", ad),
        "HD": _val(pr, b, sid, "M8_mean_tbv_hd", ad),
        "freq": _summed(pr, b, sid, "M6_freq_", ad),
        "males": _val(pr, b, sid, "M10_share_sires_used", ad),
    }


def evaluate_e11(
    pops: dict[str, pd.DataFrame], prb: pd.DataFrame | None, prc: pd.DataFrame | None
) -> pd.DataFrame:
    """Rows id, breed, quantity, estimate, lo, hi, n, pass, reading (plan 16 §6)."""
    rows: list[dict[str, Any]] = []

    def add(
        h: str,
        b: str,
        q: str,
        d: tuple[float, float, float, int] = (np.nan, np.nan, np.nan, 0),
        ok: bool | None = None,
        reading: str = "",
    ) -> None:
        m, lo, hi, n = d
        rows.append(
            {"id": h, "breed": b, "quantity": q, "estimate": m, "lo": lo, "hi": hi, "n": n,
             "pass": ok, "reading": reading}
        )  # fmt: skip

    def ne_pair(
        h: str, b: str, label: str, x: dict[str, pd.Series], y: dict[str, pd.Series]
    ) -> tuple[float, float, float, int]:
        """Ne late (realised IBD) plus the coancestry cross-check; returns the IBD interval."""
        d = _paired(x["Ne"], y["Ne"])
        add(f"{h}-support", b, f"Ne late (coancestry): {label}", _paired(x["Ne_c"], y["Ne_c"]))
        return d

    # H11-pop: per population, then count, pooled and range
    contrasts = {
        "a": ("S3", "S3 - S1 males used"),
        "b": ("S3q", "S3q - S1 Ne late"),
        "c": (E9_ARM, f"{E9_ARM} - S1 Ne, HD, freq"),
    }
    for b in BREEDS:
        held = {k: 0 for k in contrasts}
        pooled: dict[str, list[np.ndarray]] = {"a": [], "b": [], "c": []}
        est: dict[str, list[float]] = {"a": [], "b": [], "c": []}
        n_pops = 0
        for pop, pr in pops.items():
            s1 = _arm_values(pr, b, "S1")
            if not s1["Ne"].size:
                continue
            n_pops += 1
            s3, s3q, arm = (_arm_values(pr, b, s) for s in ("S3", "S3q", E9_ARM))
            da = _paired(s3["males"], s1["males"])
            ok_a = bool(da[2] < 0)
            add("H11-pop-a", b, f"{pop}: S3 - S1 males used", da, ok_a)
            db = ne_pair("H11-pop-b", b, f"{pop}: S3q - S1", s3q, s1)
            ok_b = bool(db[1] > 0)
            add("H11-pop-b", b, f"{pop}: S3q - S1 Ne late", db, ok_b)
            dc = {k: _paired(arm[k], s1[k]) for k in ("Ne", "HD", "freq")}
            ne_pair("H11-pop-c", b, f"{pop}: {E9_ARM} - S1", arm, s1)
            for k, v in dc.items():
                add("H11-pop-c", b, f"{pop}: {E9_ARM} - S1 {k}", v)
            ok_c = bool(dc["Ne"][1] > 0 and dc["HD"][2] < 0 and dc["freq"][2] < 0)
            for k, ok in (("a", ok_a), ("b", ok_b), ("c", ok_c)):
                held[k] += ok
            for k, (x, y, metric) in {
                "a": (s3, s1, "males"), "b": (s3q, s1, "Ne"), "c": (arm, s1, "Ne"),
            }.items():  # fmt: skip
                pooled[k].append(_diffs(x[metric], y[metric]))
                est[k].append(float(np.mean(pooled[k][-1])) if pooled[k][-1].size else np.nan)
        if not n_pops:
            continue
        for k, (_, label) in contrasts.items():
            verdict = held[k] >= 3 if b == "SYN_M" else None
            add(f"H11-pop-{k}", b, f"{label}: holds in {held[k]} of {n_pops}", ok=verdict)
            all_d = np.concatenate(pooled[k])
            add("H11-pop-pooled", b, f"{label} (pooled, population as stratum)",
                (*t_interval(all_d), int(all_d.size)))  # fmt: skip
            add("H11-pop-range", b, f"{label}: min and max of population estimates",
                (np.nan, float(np.nanmin(est[k])), float(np.nanmax(est[k])), n_pops))  # fmt: skip

    if prb is not None:
        for b in BREEDS:
            s1 = _arm_values(prb, b, "S1")
            s3q = _arm_values(prb, b, "S3q")
            if not s1["Ne"].size:
                continue
            ref = float(np.nanmean(s3q["Ne"]))
            for ctl in ("cap", "mkx"):
                x = _arm_values(prb, b, f"S3q-{ctl}")
                if not x["Ne"].size:
                    continue
                d = ne_pair("H11-cap", b, f"S3q - S3q-{ctl}", s3q, x)
                add("H11-cap", b, f"Ne late: S3q - S3q-{ctl}", d,
                    reading=cap_reading(d[1], d[2], ref))  # fmt: skip
            ok_a = ok_b = True
            for f in E11_FREEDOM:
                suf = f"-{f}" if f else ""
                x3, xq = _arm_values(prb, b, f"S3{suf}"), _arm_values(prb, b, f"S3q{suf}")
                da = _paired(x3["males"], s1["males"])
                db = ne_pair("H11-free-b", b, f"S3q{suf} - S1", xq, s1)
                add("H11-free-a", b, f"S3{suf} - S1 males used", da, bool(da[2] < 0))
                add("H11-free-b", b, f"S3q{suf} - S1 Ne late", db, bool(db[1] > 0))
                ok_a, ok_b = ok_a and bool(da[2] < 0), ok_b and bool(db[1] > 0)
            m = b == "SYN_M"
            add("H11-free-a", b, "S3-x - S1 males used < 0 for every x", ok=ok_a if m else None)
            add("H11-free-b", b, "S3q-x - S1 Ne late > 0 for every x", ok=ok_b if m else None)

        if prc is not None:
            b = "SYN_M"
            s1 = _arm_values(prb, b, "S1")
            for ad in (0.25, 0.5, 0.75, 1.0):
                new = _arm_values(prc, b, f"{E9_ARM}f", ad)
                old = _arm_values(prc, b, E9_ARM, ad)
                if not new["Ne"].size:
                    continue
                d = _paired(new["freq"], s1["freq"])
                h = "H11-adopt" if ad == 0.5 else "H11-adopt-other"
                add(h, b, f"freq: {E9_ARM}f at adoption {ad:g} - S1", d,
                    bool(d[2] < 0) if ad == 0.5 else None)  # fmt: skip
                for k in ("Ne", "HD"):
                    add("H11-adopt-support", b, f"{k}: {E9_ARM}f at adoption {ad:g} - S1",
                        _paired(new[k], s1[k]))  # fmt: skip
                ne_pair("H11-adopt", b, f"{E9_ARM}f at adoption {ad:g} - S1", new, s1)
                add("H11-adopt-support", b, f"freq: {E9_ARM}f - {E9_ARM} at adoption {ad:g}",
                    _paired(new["freq"], old["freq"]))  # fmt: skip
    return pd.DataFrame(rows)


def carrier_dropped_lines(exp_id: str = E11C) -> list[str]:
    """Share of seasons with the carrier limit dropped, per strategy and adoption level."""
    lines = ["| strategy | adoption | seasons | carrier limit dropped |", "|---|---|---|---|"]
    try:
        df = load_results(exp_id)
    except (ValueError, FileNotFoundError):
        return lines
    d = df[df["metric"] == "D10_carrier_relaxed"]
    for (sid, ad), g in d.groupby(["strategy", "adoption"]):
        v = g["value"].to_numpy(dtype=float)
        lines.append(f"| {sid} | {ad:g} | {v.size} | {100 * v.mean():.0f}% |")
    return lines


def write_e11_report() -> Path:
    def read(exp_id: str) -> pd.DataFrame | None:
        p = report_dir(exp_id) / "per_generation_replicates.csv.gz"
        return pd.read_csv(p) if p.exists() else None

    pops = {k: pr for k, e in E11_POPS.items() if (pr := read(e)) is not None}
    table = evaluate_e11(pops, read(E11B), read(E11C))
    out = report_dir("E11_hypotheses")
    out.mkdir(parents=True, exist_ok=True)
    table.to_csv(out / "hypotheses.csv", index=False)
    lines = [
        "# E11 pre-registered criteria (in-silico results on synthetic populations)",
        "",
        "Pre-registration: `plan/16_E11_paper_robustness.md`. Generation 10 (Ne: late window, "
        "generations 5 to 10); paired by replicate (same seeds); 95% t-intervals. Frequencies "
        "and shares of males used in %. Pooled intervals treat replicates as independent and "
        "understate between-population variation; range rows list the lowest (lo) and highest "
        "(hi) population estimate.",
        "",
        "| id | breed | quantity | estimate | lo | hi | n | pass | reading |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for _, r in table.iterrows():
        pct = any(w in r["quantity"] for w in ("freq", "males used"))
        ok = "" if r["pass"] is None or pd.isna(r["pass"]) else ("yes" if r["pass"] else "no")
        lines.append(
            f"| {r['id']} | {r['breed']} | {r['quantity']} | {_fmt(r['estimate'], pct)} | "
            f"{_fmt(r['lo'], pct)} | {_fmt(r['hi'], pct)} | {r['n']} | {ok} | {r['reading']} |"
        )
    lines += ["", "## Carrier limit dropped (E11c)", "", *carrier_dropped_lines(), ""]
    (out / "hypotheses.md").write_text("\n".join(lines))
    return out / "hypotheses.md"
