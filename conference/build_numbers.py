"""Collect every number used in the conference materials into conference/numbers.json (P11).

Sources: the validation table of dataset v1, the experiment summaries (E1, E2, E1b), the
engine benchmark, the demo dams, and literature facts from docs/research.md (with citation
keys). Nothing in the posters, slides or one-pager is typed by hand.

Usage: uv run python conference/build_numbers.py
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "conference" / "numbers.json"


def pct(x: float, digits: int = 1) -> str:
    return f"{100 * x:.{digits}f}%"


def literature() -> dict[str, str]:
    """Facts quoted from docs/research.md (citation keys in brackets there)."""
    return {
        "lit_genomic_f": "0.249",
        "lit_breeds_genotyped": "227",
        "lit_dogs_genotyped": "49,378",
        "lit_ref_genomic_f": "bannasch-2021",
        "lit_kc_breeds_popular_sires": "215",
        "lit_ref_popular_sires": "lewis-2015",
        "lit_ne_below_100": "68 of 116",
        "lit_ne_below_50": "29",
        "lit_ref_ne": "lewis-2015",
        "lit_carrier_share": "57%",
        "lit_dogs_screened": "1,054,293",
        "lit_ref_carriers": "donner-2023",
        "lit_eu_reg_published": "10 August 2026",
        "lit_ref_eu": "eurlex-2026-1818",
        "lit_coi_guide": "6.5%",
        "lit_ref_guide": "eu-platform-guide",
    }


def validation(run_id: str) -> dict[str, str]:
    path = ROOT / "reports" / "validation" / run_id / "targets_vs_simulated.csv"
    rows = list(csv.DictReader(path.open()))
    get = {(r["id"], r["breed"], r["component"]): r["value"] for r in rows}
    st = pd.Series([r["status"] for r in rows if r["status"] != "REPORT"]).value_counts()
    from breeding_smarter.calibration.data import RunData
    from breeding_smarter.calibration.metrics import recorded_vs_true_f

    rvt = recorded_vs_true_f(RunData.load(ROOT / "data" / "generated" / run_id)).values
    out = {
        "val_pass": str(st.get("PASS", 0)),
        "val_warn": str(st.get("WARN", 0)),
        "val_fail": str(st.get("FAIL", 0)),
        "val_n_checks": str(int(st.sum())),
        "val_n_targets": str(len({r["id"] for r in rows})),
    }
    for b in ("SYN_L", "SYN_M", "SYN_S"):
        k = b[-1]
        out[f"ne_{k}"] = f"{float(get[('T07', b, 'ne')]):.0f}"
        out[f"recorded_f_2025_{k}"] = pct(rvt[b]["recorded"])
        out[f"true_f_2025_{k}"] = pct(rvt[b]["true_pedigree"])
        out[f"ibd_2025_{k}"] = pct(rvt[b]["realised_ibd"])
        out[f"engine_max_diff_{k}"] = f"{float(get[('T12', b, 'max_abs_diff')]):.4f}"
        out[f"engine_slope_{k}"] = f"{float(get[('T13', b, 'slope')]):.3f}"
        out[f"top20_{k}"] = pct(float(get[("T05", b, "share")]), 0)
    return out


def dataset(run_id: str) -> dict[str, str]:
    run = ROOT / "data" / "generated" / run_id
    m = json.loads((run / "manifest.json").read_text())
    rc = m["row_counts"]
    return {
        "run_id": run_id,
        "n_animals": f"{rc['registry/animals']:,}",
        "n_litters": f"{rc['registry/litters']:,}",
        "n_truth": f"{rc['truth/animals_truth']:,}",
        "n_dna": f"{rc['registry/dna_tests']:,}",
        "n_hd": f"{rc['registry/health_tests']:,}",
        "gen_seconds": f"{m['generator_wall_seconds']:.0f}",
        "seed": str(m["seed"]),
    }


def experiments() -> dict[str, str]:
    base = ROOT / "reports" / "experiments"
    s = pd.read_csv(base / "E1_headline" / "summary.csv")
    p = pd.read_csv(base / "E1_headline" / "paired_vs_S1.csv")
    out: dict[str, str] = {}
    g10 = s[(s["generation"] == 10) & (s["adoption"] == 1.0)]

    def val(breed: str, strat: str, metric: str) -> pd.Series:
        return g10[
            (g10["breed"] == breed) & (g10["strategy"] == strat) & (g10["metric"] == metric)
        ].iloc[0]

    for b in ("SYN_S", "SYN_M"):
        k = b[-1]
        for sid in ("S0", "S1", "S2", "S3", "S4"):
            r = val(b, sid, "M2_realised_ibd")
            out[f"e1_ibd_{k}_{sid}"] = pct(r["mean"])
            out[f"e1_ne_{k}_{sid}"] = f"{val(b, sid, 'M3_ne')['mean']:.0f}"
            out[f"e1_rec_{k}_{sid}"] = pct(val(b, sid, "M1_recorded_F")["mean"])
            out[f"e1_males_{k}_{sid}"] = pct(val(b, sid, "M10_share_sires_used")["mean"])
        for sid in ("S0", "S2", "S3", "S4"):
            for metric, key in (("M2_realised_ibd", "ibd"), ("M1_recorded_F", "rec")):
                r = p[
                    (p["breed"] == b)
                    & (p["strategy"] == sid)
                    & (p["generation"] == 10)
                    & (p["metric"] == metric)
                ].iloc[0]
                out[f"e1_d{key}_{k}_{sid}"] = f"{100 * r['diff_mean']:+.1f}"
                out[f"e1_d{key}_{k}_{sid}_abs"] = f"{abs(100 * r['diff_mean']):.1f}"
                out[f"e1_d{key}_{k}_{sid}_ci"] = f"{100 * r['lo']:+.1f} to {100 * r['hi']:+.1f}"
    for sid in ("S1", "S3"):
        out[f"e1_mdr1_M_{sid}"] = pct(val("SYN_M", sid, "M6_affected_ABCB1_MDR1")["mean"], 2)
        out[f"e1_tbv_M_{sid}"] = f"{val('SYN_M', sid, 'M8_mean_tbv_hd')['mean']:.2f}"
    nx = g10[(g10["breed"] == "SYN_S") & (g10["metric"] == "M7_affected_NOVEL_X")]["mean"]
    out["e1_novelx_range"] = f"{pct(nx.min())} to {pct(nx.max())}"
    reps = s[(s["generation"] == 10) & (s["metric"] == "M2_realised_ibd")]
    reps = reps.groupby("breed")["n"].max()
    out["e1_reps_S"] = str(int(reps["SYN_S"]))
    out["e1_reps_M"] = str(int(reps["SYN_M"]))
    s2 = pd.read_csv(base / "E2_adoption" / "summary.csv")
    e2 = s2[(s2["generation"] == 10) & (s2["metric"] == "M2_realised_ibd")]
    for _, r in e2.iterrows():
        out[f"e2_ibd_a{round(100 * r['adoption'])}"] = pct(r["mean"])
    return out


def p12() -> dict[str, str]:
    """P12 coordination numbers (E5 to E7 and the pre-registered criteria); empty if not run."""
    base = ROOT / "reports" / "experiments"
    if not (base / "P12_hypotheses" / "hypotheses.csv").exists():
        return {}
    out: dict[str, str] = {}
    h = pd.read_csv(base / "P12_hypotheses" / "hypotheses.csv")
    for _, r in h.iterrows():
        k = f"p12_{r['id'].lower().replace('-', '_')}_{r['breed'][-1]}"
        pct_like = str(r["quantity"]).startswith(("dF", "range", "affected"))
        scale = 100 if pct_like else 1
        if r["id"] == "H5":
            out[f"{k}_est"] = f"{r['estimate']:.2f}"
        else:
            out[f"{k}_est"] = f"{scale * r['estimate']:.2f}" if pct_like else f"{r['estimate']:.0f}"
        if pd.notna(r["lo"]) and pd.notna(r["hi"]) and r["n"] > 0:
            if pct_like:
                out[f"{k}_ci"] = f"{scale * r['lo']:+.2f} to {scale * r['hi']:+.2f}"
            else:
                out[f"{k}_ci"] = f"{r['lo']:+.0f} to {r['hi']:+.0f}"
        if pd.notna(r["pass"]) and r["pass"] != "":
            out[f"{k}_pass"] = "yes" if str(r["pass"]) in ("True", "true", "1") else "no"
    s = pd.read_csv(base / "E5_coordination" / "summary.csv")
    g10 = s[(s["generation"] == 10) & (s["adoption"] == 1.0)]
    for b in ("SYN_S", "SYN_M"):
        k = b[-1]
        for sid in ("S0", "S1", "S3", "CC-ocs-mc1", "S3q", "CC-ocs-rand", "CC-none-mc1"):
            tag = sid.replace("-", "_").lower()
            sel = g10[(g10["breed"] == b) & (g10["strategy"] == sid)].set_index("metric")["mean"]
            if sel.empty:
                continue
            out[f"p12_ibd_{k}_{tag}"] = pct(sel["M2_realised_ibd"])
            out[f"p12_dflate_{k}_{tag}"] = f"{100 * sel['R_delta_f_late']:.2f}"
            out[f"p12_ne_{k}_{tag}"] = f"{1 / (2 * sel['R_delta_f_late']):.0f}"
            out[f"p12_males_{k}_{tag}"] = pct(sel["M10_share_sires_used"])
    a = pd.read_csv(base / "E7_adoption_quotas" / "summary.csv")
    a10 = a[(a["generation"] == 10) & (a["metric"] == "R_delta_f_late")]
    for _, r in a10.iterrows():
        out[f"p12_e7_df_{r['breed'][-1]}_a{round(100 * r['adoption'])}"] = f"{100 * r['mean']:.2f}"
    return out


def e9() -> dict[str, str]:
    """E9 policy dial (medium breed): replication of E8 vs S1 and absolute values per arm."""
    base = ROOT / "reports" / "experiments"
    hyp = base / "E9_hypotheses" / "hypotheses.csv"
    if not hyp.exists():
        return {}
    out: dict[str, str] = {}
    h = pd.read_csv(hyp).set_index("id")
    for hid, key, scale, fmt in (
        ("H9-rep-Ne", "ne", 1, "{:+.0f}"),
        ("H9-rep-HD", "hd", 1, "{:+.2f}"),
        ("H9-rep-freq", "freq", 100, "{:+.1f}"),
    ):
        r = h.loc[hid]
        out[f"e9_rep_{key}_est"] = fmt.format(scale * r["estimate"])
        out[f"e9_rep_{key}_ci"] = f"{fmt.format(scale * r['lo'])} to {fmt.format(scale * r['hi'])}"
    pr = pd.read_csv(base / "E9_policy_dial" / "per_generation_replicates.csv.gz")
    g = pr[(pr["breed"] == "SYN_M") & (pr["generation"] == 10) & (pr["adoption"] == 1.0)]

    def mean(sid: str, metric: str) -> float:
        sub = g[g["strategy"] == sid]
        if metric == "freq":
            v = sub[sub["metric"].str.startswith("M6_freq_")].groupby("replicate")["value"].sum()
        else:
            v = sub[sub["metric"] == metric]["value"]
        return float(v.mean())

    arms = {"s1": "S1", "s3q": "S3q", "g005": "S3q-gain005-c050", "g010": "S3q-gain010-c050"}
    for tag, sid in arms.items():
        out[f"e9_ne_M_{tag}"] = f"{mean(sid, 'R_ne_f_late'):.0f}"
        out[f"e9_hd_M_{tag}"] = f"{mean(sid, 'M8_mean_tbv_hd'):+.2f}"
        out[f"e9_freq_M_{tag}"] = f"{mean(sid, 'freq'):.3f}"
    out["e9_freq_cut_vs_s1"] = pct(1 - mean("S3q-gain010-c050", "freq") / mean("S1", "freq"), 0)
    return out


def _fmt_ci(est: float, lo: float, hi: float, scale: float, fmt: str) -> tuple[str, str]:
    """Estimate and interval; a bound that rounds to zero keeps one decimal (+0.3, not +0)."""

    def f(x: float) -> str:
        s = fmt.format(scale * x)
        if scale * x != 0 and float(s) == 0:  # keep the sign visible: +0.02, not +0.0
            digits = len(s.split(".")[1]) + 1 if "." in s else 1
            while float(f"{scale * x:.{digits}f}") == 0:
                digits += 1
            return f"{scale * x:+.{digits}f}"
        return s

    return f(est), f"{f(lo)} to {f(hi)}"


def paper() -> dict[str, str]:
    """Numbers for the proceedings paper (E1b, E5, E8, E9, E11), read from the hypotheses and
    paired tables by (id, breed, quantity); a missing row raises, nothing is typed by hand."""
    base = ROOT / "reports" / "experiments"
    if not (base / "E11_hypotheses" / "hypotheses.csv").exists():
        return {}
    out: dict[str, str] = {}
    tables = {
        e: pd.read_csv(base / f"{e}_hypotheses" / "hypotheses.csv") for e in ("E8", "E9", "E11")
    }

    def row(e: str, hid: str, breed: str, quantity: str) -> pd.Series:
        t = tables[e]
        sel = t[(t["id"] == hid) & (t["breed"] == breed) & (t["quantity"] == quantity)]
        assert len(sel) == 1, (e, hid, breed, quantity, len(sel))
        return sel.iloc[0]

    def put(key: str, r: pd.Series, scale: float = 1, fmt: str = "{:+.0f}") -> None:
        out[f"{key}_est"], out[f"{key}_ci"] = _fmt_ci(r["estimate"], r["lo"], r["hi"], scale, fmt)

    def paired(exp: str, breed: str, sid: str, metric: str) -> pd.Series:
        p = pd.read_csv(base / exp / "paired_vs_S1.csv")
        sel = p[(p["breed"] == breed) & (p["strategy"] == sid) & (p["generation"] == 10)
                & (p["metric"] == metric)]  # fmt: skip
        assert len(sel) == 1, (exp, breed, sid, metric)
        r = sel.iloc[0]
        return pd.Series({"estimate": r["diff_mean"], "lo": r["lo"], "hi": r["hi"]})

    # herding in E5 (10-generation trend Ne) and the E1b weight check
    for b in ("SYN_S", "SYN_M"):
        put(f"pp_e5_s3_m3ne_{b[-1]}", paired("E5_coordination", b, "S3", "M3_ne"))
    from breeding_smarter.experiments import hypotheses as hy

    # E1b has only S3 (sire-use weight 0.25); same seed and dataset as E1, so it pairs with E1's S1
    e1b_s3 = hy._val(hy._per_rep("E1b_balanced_weights"), "SYN_M", "S3", "M3_ne")
    est, lo, hi, _ = hy._paired(e1b_s3, hy._val(hy._per_rep("E1_headline"), "SYN_M", "S1", "M3_ne"))
    out["pp_e1b_s3_m3ne_M_est"], out["pp_e1b_s3_m3ne_M_ci"] = _fmt_ci(est, lo, hi, 1, "{:+.0f}")
    e1b = pd.read_csv(base / "E1b_balanced_weights" / "summary.csv")
    m = e1b[(e1b["breed"] == "SYN_M") & (e1b["strategy"] == "S3") & (e1b["generation"] == 10)
            & (e1b["metric"] == "M10_share_sires_used") & (e1b["adoption"] == 1.0)]  # fmt: skip
    out["pp_e1b_males_M"] = pct(float(m["mean"].iloc[0]))

    # E8 (first seed) and E9 (replication)
    arm = "S3q-gain010-c050"
    put("pp_e8_ne", row("E8", "H8a", "SYN_M", f"Ne late: {arm} - S1"))
    put("pp_e8_hd", row("E8", "H8b", "SYN_M", f"true HD breeding value (gen 10): {arm} - S1"),
        fmt="{:+.2f}")  # fmt: skip
    h8c = tables["E8"][(tables["E8"]["id"] == "H8c") & (tables["E8"]["breed"] == "SYN_M")]
    put("pp_e8_freq", h8c.iloc[0], 100, "{:+.1f}")
    for budget in ("025", "050"):
        sid = f"S3q-gain{budget}-c050"
        put(f"pp_e9_ne_g{budget}", row("E9", "H9-curve", "SYN_M", f"Ne: {sid} - S1"))
        put(f"pp_e9_hd_g{budget}", row("E9", "H9-curve", "SYN_M", f"HD: {sid} - S1"), fmt="{:+.2f}")
    put("pp_e9_hc_freq", row("E9", "H9-hc", "SYN_M", f"freq: {arm} - S3q-gain010-hc"), 100,
        "{:+.1f}")  # fmt: skip
    put("pp_e9_hc_ne", row("E9", "H9-hc-support", "SYN_M", f"Ne late: {arm} - S3q-gain010-hc"))
    put(
        "pp_e9_hc_block_vs_none",
        row("E9", "H9-hc-support", "SYN_M", "freq: S3q-gain010-hc - S3q-gain010"),
        100,
        "{:+.1f}",
    )

    # E11
    pops = ("v1", "v1b", "v1c", "v1d")
    for b in ("SYN_S", "SYN_M"):
        k = b[-1]
        for pop in pops:
            put(f"pp_e11_{pop}_males_{k}", row("E11", "H11-pop-a", b, f"{pop}: S3 - S1 males used"),
                100, "{:+.1f}")  # fmt: skip
            put(f"pp_e11_{pop}_s3q_ne_{k}", row("E11", "H11-pop-b", b, f"{pop}: S3q - S1 Ne late"))
            for q, scale, fmt in (("Ne", 1, "{:+.0f}"), ("HD", 1, "{:+.2f}"),
                                  ("freq", 100, "{:+.1f}")):  # fmt: skip
                put(f"pp_e11_{pop}_arm_{q.lower()}_{k}",
                    row("E11", "H11-pop-c", b, f"{pop}: {arm} - S1 {q}"), scale, fmt)  # fmt: skip
        for c, label in (("a", "S3 - S1 males used"), ("b", "S3q - S1 Ne late"),
                         ("c", f"{arm} - S1 Ne, HD, freq")):  # fmt: skip
            t = tables["E11"]
            sel = t[(t["id"] == f"H11-pop-{c}") & (t["breed"] == b)
                    & t["quantity"].str.startswith(f"{label}: holds in")]  # fmt: skip
            out[f"pp_e11_held_{c}_{k}"] = sel["quantity"].iloc[0].split("holds in ")[1]
        put(f"pp_e11_pooled_males_{k}",
            row("E11", "H11-pop-pooled", b, "S3 - S1 males used (pooled, population as stratum)"),
            100, "{:+.1f}")  # fmt: skip
        put(
            f"pp_e11_pooled_s3q_ne_{k}",
            row("E11", "H11-pop-pooled", b, "S3q - S1 Ne late (pooled, population as stratum)"),
        )
        put(
            f"pp_e11_pooled_arm_ne_{k}",
            row("E11", "H11-pop-pooled", b, f"{arm} - S1 Ne late (pooled, population as stratum)"),
        )
        for ctl in ("cap", "mkx"):
            put(f"pp_e11_cap_{ctl}_{k}", row("E11", "H11-cap", b, f"Ne late: S3q - S3q-{ctl}"))
        for f in ("t1", "", "u5"):
            suf, tag = (f"-{f}", f) if f else ("", "def")
            put(
                f"pp_e11_free_males_{tag}_{k}",
                row("E11", "H11-free-a", b, f"S3{suf} - S1 males used"),
                100,
                "{:+.1f}",
            )
            put(f"pp_e11_free_ne_{tag}_{k}", row("E11", "H11-free-b", b, f"S3q{suf} - S1 Ne late"))
    fa = f"{arm}f"
    for ad in ("0.25", "0.5", "0.75", "1"):
        tag = ad.replace(".", "")
        hid = "H11-adopt" if ad == "0.5" else "H11-adopt-other"
        q = f"freq: {fa} at adoption {ad} - S1"
        put(f"pp_e11_adopt_freq_{tag}", row("E11", hid, "SYN_M", q), 100, "{:+.1f}")
        put(
            f"pp_e11_adopt_ne_{tag}",
            row("E11", "H11-adopt-support", "SYN_M", f"Ne: {fa} at adoption {ad} - S1"),
        )
        put(
            f"pp_e11_adopt_hd_{tag}",
            row("E11", "H11-adopt-support", "SYN_M", f"HD: {fa} at adoption {ad} - S1"),
            fmt="{:+.2f}",
        )
    from breeding_smarter.experiments.runner import load_results

    d10 = load_results(hy.E11C)
    d10 = d10[d10["metric"] == "D10_carrier_relaxed"]
    for (sid, ad), g in d10.groupby(["strategy", "adoption"]):
        tag = ("new" if sid.endswith("f") else "old") + f"_a{round(100 * ad)}"
        out[f"pp_e11_dropped_{tag}"] = pct(float(g["value"].mean()), 0)
    # additional (not pre-registered): S3 - S1 Ne on the 10-generation trend, per population
    for pop, e in hy.E11_POPS.items():
        pr = hy._per_rep(e)
        for b in ("SYN_S", "SYN_M"):
            est, lo, hi, _ = hy._paired(
                hy._val(pr, b, "S3", "M3_ne"), hy._val(pr, b, "S1", "M3_ne")
            )
            out[f"pp_e11_{pop}_s3_m3ne_{b[-1]}_est"], out[f"pp_e11_{pop}_s3_m3ne_{b[-1]}_ci"] = (
                _fmt_ci(est, lo, hi, 1, "{:+.0f}")
            )
    # populations: validation of v1b to v1d and recorded-pedigree Ne (T07)
    tags = yaml.safe_load((ROOT / "configs" / "datasets.yaml").read_text())["datasets"]
    for pop in pops:
        rid = tags[pop]["run_id"]
        rows = list(csv.DictReader((ROOT / "reports" / "validation" / rid
                                    / "targets_vs_simulated.csv").open()))  # fmt: skip
        st = pd.Series([r["status"] for r in rows if r["status"] != "REPORT"]).value_counts()
        out[f"pp_val_{pop}"] = f"{st.get('PASS', 0)} PASS, {st.get('WARN', 0)} WARN, " + (
            f"{st.get('FAIL', 0)} FAIL"
        )
        get = {(r["id"], r["breed"], r["component"]): r["value"] for r in rows}
        for b in ("SYN_S", "SYN_M"):
            out[f"pp_t07_{pop}_{b[-1]}"] = f"{float(get[('T07', b, 'ne')]):.0f}"
    return out


def paper_revision() -> dict[str, str]:
    """Paper revision (additional, not pre-registered): rates per year and per realised generation,
    realised inbreeding at generation 10, population-level intervals, failed hypotheses."""
    base = ROOT / "reports" / "experiments"
    if not (base / "E11_hypotheses" / "hypotheses.csv").exists():
        return {}
    from breeding_smarter.experiments import hypotheses as hy
    from breeding_smarter.experiments import rates as R

    out: dict[str, str] = {}

    def put(key: str, d: tuple[float, float, float, int], scale: float, fmt: str) -> None:
        out[f"{key}_est"], out[f"{key}_ci"] = _fmt_ci(d[0], d[1], d[2], scale, fmt)

    def contrast(key, pr, a, b, ad=1.0, adb=1.0, prb=None, breed="SYN_M"):  # type: ignore[no-untyped-def]
        x = R.late_rates(pr, breed, a, ad)
        y = R.late_rates(prb if prb is not None else pr, breed, b, adb)
        put(f"{key}_dfy", R.paired(x["dF_year"], y["dF_year"]), 1e4, "{:+.1f}")
        put(f"{key}_neg", R.paired(x["Ne_gen"], y["Ne_gen"]), 1, "{:+.0f}")
        put(f"{key}_f10", R.paired(x["F10"], y["F10"]), 100, "{:+.1f}")
        for tag, v in (("a", x), ("b", y)):
            out[f"{key}_L{tag}"] = f"{v['L'].mean():.1f}"
            out[f"{key}_neg{tag}"] = f"{v['Ne_gen'].mean():.0f}"
            out[f"{key}_dfy{tag}"] = f"{1e4 * v['dF_year'].mean():.1f}"
            out[f"{key}_f10{tag}"] = pct(float(v["F10"].mean()))
        return x, y

    pb = hy._per_rep(hy.E11B)
    for a in ("S3", "S3q", "S3q-cap", "S3q-mkx", "S3-t1", "S3-u5", "S3q-t1", "S3q-u5"):
        contrast(f"rv_b_{a.replace('-', '_').lower()}", pb, a, "S1")
    contrast("rv_b_s3q_vs_cap", pb, "S3q", "S3q-cap")
    contrast("rv_b_s3q_vs_mkx", pb, "S3q", "S3q-mkx")
    p9 = hy._per_rep(hy.E9)
    for g in ("005", "010", "015", "025", "050"):
        contrast(f"rv_9_g{g}", p9, f"S3q-gain{g}-c050", "S1")
        contrast(f"rv_9_g{g}_vs_s3q", p9, f"S3q-gain{g}-c050", "S3q")
    contrast("rv_9_s3q", p9, "S3q", "S3q-gain010-c050")
    p5 = hy._per_rep(hy.E5)
    for a in ("S0", "CC-mkx-rand", "CC-cap-rand", "CC-none-rand", "CC-ocs-rand", "CC-ocs-mc1",
              "CC-none-mc1", "S3q", "S3"):  # fmt: skip
        contrast(f"rv_5_{a.replace('-', '_').lower()}", p5, a, "S1")
    pops = {p: hy._per_rep(e) for p, e in hy.E11_POPS.items()}
    lev: dict[str, list[float]] = {"s3": [], "s3q": [], "arm": []}
    held = {k: 0 for k in lev}
    for pop, pr in pops.items():
        for k, sid in (("s3", "S3"), ("s3q", "S3q"), ("arm", hy.E9_ARM)):
            x, y = contrast(f"rv_{pop}_{k}", pr, sid, "S1")
            d = R.paired(x["dF_year"], y["dF_year"])
            lev[k].append(d[0])
            held[k] += bool(d[2] < 0) if k != "s3" else bool(d[1] > 0)
    f10 = [
        float(
            R.paired(
                R.late_rates(pr, "SYN_M", "S3q")["F10"], R.late_rates(pr, "SYN_M", "S1")["F10"]
            )[0]
        )
        for pr in pops.values()
    ]
    out["rv_range_s3q_f10"] = (
        f"{100 * min(abs(x) for x in f10):.1f} to {100 * max(abs(x) for x in f10):.1f}"
    )
    males = [
        float(
            t_[
                (t_["id"] == "H11-pop-a")
                & (t_["breed"] == "SYN_M")
                & (t_["quantity"] == f"{p}: S3 - S1 males used")
            ]["estimate"].iloc[0]
        )
        for p in pops
        for t_ in [pd.read_csv(base / "E11_hypotheses" / "hypotheses.csv")]
    ]
    out["rv_range_males"] = (
        f"{100 * min(abs(x) for x in males):.1f} to {100 * max(abs(x) for x in males):.1f}"
    )
    for k, v in lev.items():
        put(f"rv_poplevel_{k}_dfy", R.population_level(v), 1e4, "{:+.1f}")
        out[f"rv_held_{k}_dfy"] = f"{held[k]} of {len(v)}"
    # population-level interval of the pre-registered contrasts (populations as units)
    t = pd.read_csv(base / "E11_hypotheses" / "hypotheses.csv")
    for c, hid, q, scale, fmt in (
        ("males", "H11-pop-a", "S3 - S1 males used", 100, "{:+.1f}"),
        ("s3q", "H11-pop-b", "S3q - S1 Ne late", 1, "{:+.0f}"),
        ("arm", "H11-pop-c", f"{hy.E9_ARM} - S1 Ne", 1, "{:+.0f}"),
    ):
        est = [
            float(
                t[(t["id"] == hid) & (t["breed"] == "SYN_M") & (t["quantity"] == f"{p}: {q}")][
                    "estimate"
                ].iloc[0]
            )
            for p in pops
        ]
        put(f"rv_poplevel_{c}", R.population_level(est), scale, fmt)  # fmt: skip
    cross = t[
        (t["id"] == "H11-pop-c-support")
        & (t["breed"] == "SYN_M")
        & (t["quantity"] == f"Ne late (coancestry): v1d: {hy.E9_ARM} - S1")
    ].iloc[0]
    put("rv_v1d_arm_coanc", (cross["estimate"], cross["lo"], cross["hi"], 10), 1, "{:+.0f}")
    # adoption against the regulated market S2 (E11d, additional) if it has been run
    p_s2 = base / "E11d_s2_reference" / "per_generation_replicates.csv.gz"
    if p_s2.exists():
        prs2, prc = pd.read_csv(p_s2), hy._per_rep(hy.E11C)
        s2f = hy._summed(prs2, "SYN_M", "S2", "M6_freq_")
        for ad in (0.25, 0.5, 0.75, 1.0):
            tag = f"{round(100 * ad)}"
            contrast(f"rv_c_new_a{tag}_vs_s2", prc, f"{hy.E9_ARM}f", "S2", ad, prb=prs2)
            put(f"rv_c_new_a{tag}_vs_s2_freq",
                hy._paired(hy._summed(prc, "SYN_M", f"{hy.E9_ARM}f", "M6_freq_", ad), s2f),
                100, "{:+.1f}")  # fmt: skip
        contrast("rv_c_s2_vs_s1", prs2, "S2", "S1", prb=pb)
    # summed tested risk-allele frequency (percentage points) and realised dF per generation
    g9 = p9[(p9["breed"] == "SYN_M") & (p9["generation"] == 10) & (p9["adoption"] == 1.0)]
    for tag, sid in (("s1", "S1"), ("s3q", "S3q"), ("arm", hy.E9_ARM)):
        f = g9[(g9["strategy"] == sid) & g9["metric"].str.startswith("M6_freq_")]
        out[f"rv_9_freq_{tag}"] = f"{100 * f.groupby('replicate')['value'].sum().mean():.1f}"
    arm9 = R.late_rates(p9, "SYN_M", hy.E9_ARM)
    out["rv_9_arm_dfgen_pct"] = f"{100 * arm9['dF_gen'].mean():.2f}"
    h9 = pd.read_csv(base / "E9_hypotheses" / "hypotheses.csv")
    r = h9[(h9["id"] == "H10-dna")].iloc[0]
    put("rv_h10dna", (r["estimate"], r["lo"], r["hi"], int(r["n"])), 1, "{:+.0f}")
    # simulation diagnostics: overflow dams and infeasible (fallback) gain seasons
    from breeding_smarter.experiments.runner import load_results

    for e in (hy.E11B, hy.E11C, hy.E9):
        df = load_results(e)
        out[f"rv_overflow_{e[:4]}"] = f"{int(df[df['metric'] == 'D7_overflow']['value'].sum())}"
        out[f"rv_infeasible_{e[:4]}"] = f"{int(df[df['metric'] == 'D3_infeasible']['value'].sum())}"
        out[f"rv_seasons_{e[:4]}"] = f"{int((df['metric'] == 'D3_infeasible').sum())}"
    return out


def benchmark() -> dict[str, str]:
    text = (ROOT / "reports" / "benchmarks" / "engine.md").read_text()
    row = re.search(r"\| 250,000 \| ([\d.]+) \| ([\d.]+) \| ([\d.]+) \| ([\d.]+) \|", text)
    assert row is not None
    return {"bench_inbreeding_250k_s": row.group(1), "bench_pair_ms": row.group(4)}


def demo() -> dict[str, str]:
    d = yaml.safe_load((ROOT / "configs" / "demo.yaml").read_text())
    out = {"demo_date": d["mating_date"]}
    for i, dam in enumerate(d["dams"], 1):
        out[f"demo{i}_reg_no"] = dam["reg_no"]
        out[f"demo{i}_name"] = dam["name"]
        out[f"demo{i}_breed"] = dam["breed"]
    return out


def main() -> None:
    tags = yaml.safe_load((ROOT / "configs" / "datasets.yaml").read_text())["datasets"]
    run_id = tags["v1"]["run_id"]
    numbers: dict[str, str] = {}
    for part in (
        literature(),
        validation(run_id),
        dataset(run_id),
        experiments(),
        benchmark(),
        demo(),
        p12(),
        e9(),
        paper(),
        paper_revision(),
    ):
        numbers.update(part)
    links = yaml.safe_load((ROOT / "conference" / "links.yaml").read_text())
    numbers.update({f"link_{k}": str(v) for k, v in links.items()})
    OUT.write_text(json.dumps(numbers, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
    print(f"wrote {OUT} ({len(numbers)} values)")


if __name__ == "__main__":
    main()
