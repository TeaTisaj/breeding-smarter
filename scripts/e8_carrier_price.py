"""E8 step 1: static price of the carrier limit for one season (plan/14_E8_health_gain_quotas.md).

Dataset v1, SYN_M, season of 2027-03-01, S3q-gain010 quotas (gain OCS, dF 0.1% per generation)
with the carrier limit off and at beta in {1.0, 0.9, 0.75, 0.5, 0.25}. Reports, per beta, the
planned risk-allele transmission per tested locus, planned coancestry relative to no limit, the
planned HD merit (mean standardised EBV index of the quota sires) and whether the limit had to
be relaxed. Synthetic data; deterministic.

    uv run python scripts/e8_carrier_price.py
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from breeding_smarter.coordination.club import auto_dams, club_sires, last_year_matings
from breeding_smarter.coordination.config import load_coordination
from breeding_smarter.coordination.planner import _merit, plan_season
from breeding_smarter.experiments.runner import report_dir
from breeding_smarter.matching import load_context
from breeding_smarter.matching.components import transmission
from breeding_smarter.rules import day_number

BREED, DATE, DELTA_F = "SYN_M", "2027-03-01", 0.001
BETAS = [None, 1.0, 0.9, 0.75, 0.5, 0.25]


def _cell(v: object) -> str:
    return f"{v:.4g}" if isinstance(v, float) else str(v)


def main() -> None:
    ctx = load_context("v1")
    cfg = load_coordination()
    day = day_number(DATE)
    sires = club_sires(ctx, BREED, day)
    dams = auto_dams(ctx, BREED, day, np.random.default_rng(0))
    prev = last_year_matings(ctx, BREED, day)
    ref = ctx.reference(BREED, day)
    t = transmission(ctx.geno[sires], ref.allele_freq)
    loci = list(ctx.rules.loci)
    merit = _merit(ctx, sires)
    rows = []
    for beta in BETAS:
        plan = plan_season(
            ctx, BREED, day, dams, sires, cfg, "ocs_gain", "none",
            profile="exp_pairing", delta_f=DELTA_F, prev_matings=prev, carrier_factor=beta,
        )  # fmt: skip
        assert plan.quotas is not None
        w = plan.quotas / plan.quotas.sum()
        d = plan.diagnostics
        row = {
            "beta": "off" if beta is None else beta,
            "achieved_C": d["achieved_C"],
            "budget": d["budget"],
            "infeasible": bool(d["infeasible"]),
            "carrier_relaxed": bool(d.get("carrier_relaxed", 0.0)),
            "n_sires_with_quota": int(d["n_sires_with_quota"]),
            "planned_merit": float(w @ merit),
        }
        for j, lc in enumerate(loci):
            row[f"t_{lc}"] = float(w @ t[:, j])
        rows.append(row)
    df = pd.DataFrame(rows)
    df["dC_vs_off"] = df["achieved_C"] - df["achieved_C"].iloc[0]
    df["merit_lost_vs_off"] = df["planned_merit"].iloc[0] - df["planned_merit"]
    out = report_dir("E8_pilot")
    out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / "price_curve.csv", index=False)
    cand = {lc: float(np.nanmean(t[:, j])) for j, lc in enumerate(loci)}
    lines = [
        "# E8 static price of the carrier limit (in-silico, synthetic SYN_M, one season)",
        "",
        f"Season {DATE}: {dams.size} dams, {sires.size} candidate sires, gain OCS dF "
        f"{100 * DELTA_F:g}% per generation. Candidate mean risk-allele transmission: "
        + ", ".join(f"{k} {v:.4f}" for k, v in cand.items())
        + ". Quotas are rounded (Sainte-Laguë), so planned values are of the integer quotas.",
        "",
        "| " + " | ".join(df.columns) + " |",
        "|" + "---|" * len(df.columns),
        *("| " + " | ".join(_cell(v) for v in r) + " |" for r in df.itertuples(index=False)),
        "",
    ]
    (out / "price_curve.md").write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
