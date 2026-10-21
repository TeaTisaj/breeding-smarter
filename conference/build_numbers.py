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
    ):
        numbers.update(part)
    links = yaml.safe_load((ROOT / "conference" / "links.yaml").read_text())
    numbers.update({f"link_{k}": str(v) for k, v in links.items()})
    OUT.write_text(json.dumps(numbers, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
    print(f"wrote {OUT} ({len(numbers)} values)")


if __name__ == "__main__":
    main()
