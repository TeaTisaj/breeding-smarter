# Gate report: E8 Diversity, health and hips at once
Date: 2026-10-14

In-silico results on synthetic populations (no real dogs). Pre-registration: `plan/14_E8_health_gain_quotas.md` (commit `46c0ca5`, before any E8 data; β addendum commit `ffba05e`, after the pilot and before the main run).

## Acceptance checklist
- [x] Hypotheses fixed before data (evidence: `git log plan/14_E8_health_gain_quotas.md`, `46c0ca5` precedes the pilot and main run).
- [x] Known-answer tests for the carrier constraint first (evidence: `tests/unit/test_coordination.py::test_carrier_constraint_binds_closed_form` [1, 3] litters, `test_carrier_relaxed_first_and_reported`, `test_non_binding_carrier_bound_changes_nothing`, `test_gain_with_carrier_closed_form` [1, 2, 1, 0]).
- [x] Strategy ids and contract (evidence: `tests/unit/test_strategy_ids.py`; `tests/integration/test_experiments.py::test_p12_strategy_contract[S3q-c075, S3q-gain010-c075]`, `test_s3q_carrier_limit_is_planned`, determinism).
- [x] β chosen by the pre-registered rule from a pilot on its own seed (evidence: `reports/experiments/E8_pilot/`, addendum in the pre-registration).
- [x] Main run complete: 130 of 130 parts, 0 infeasible seasons, carrier limit never relaxed (0 of 1,800 seasons).
- [x] Hypotheses report generated from the CSVs (evidence: `bsm experiment hypotheses --set e8` → `reports/experiments/E8_hypotheses/hypotheses.md`).
- [x] Figure M (`reports/experiments/E8_health_gain_quotas/figures/figM_health_gain_quotas{,_poster}.{png,svg}`), caption says in silico.
- [x] Check suite passes (`scripts/check.sh`).
- [x] Existing strategies, `configs/coordination/default.yaml` and the P1 data contract unchanged; E5 to E7 not rerun.

## Result in one sentence
**H8 passes:** in SYN_M, the recommender inside quotas from gain OCS with a carrier limit beats today's market on diversity, hips and tested disease alleles at the same time.

| id | SYN_M, generation 10, paired vs S1 (20 replicates) | estimate (95% CI) | pass |
|---|---|---|---|
| H8a | Ne late, S3q-gain010-c050 − S1 | +71 (+17 to +126) | yes |
| H8b | mean true HD breeding value | −1.18 (−1.23 to −1.13) | yes |
| H8c | tested risk-allele frequency, sum over loci | −8.9 points (−10.9 to −6.9) | yes |
| H8d | affected share at tested loci (reported only) | −0.41 points (−0.57 to −0.26) | — |

Absolute values (means, generation 10):

| SYN_M arm | Ne late | HD (lower better) | risk-allele freq, sum | affected, sum |
|---|---|---|---|---|
| S1 status quo market | 206 | +0.39 | 0.114 | 0.43% |
| S3q (P12 product mode) | 320 | +0.38 | 0.205 | 0.65% |
| S3q + carrier limit (c050) | 304 | +0.39 | 0.044 | 0.04% |
| S3q + gain OCS (gain010) | 278 | −0.82 | 0.238 | 0.52% |
| S3q + both | 278 | −0.79 | 0.025 | 0.01% |

## What the 2×2 says (H8e, attribution)
- **The carrier limit is close to free.**
  - Risk-allele frequency: −18.7 points (−20.4 to −17.0).
  - Ne: −8 (−36 to +20), no detectable cost.
  - Hips: unchanged (S3q-c050 − S3q: +0.01, −0.03 to +0.06).
- **Gain OCS buys hips with some diversity.**
  - HD: −1.19 (−1.24 to −1.15).
  - Ne: −34 (−59 to −8).

  E6 found no Ne cost for the fully coordinated arm (CC-gain010-mc1). With the recommender inside the quotas, there is a moderate one.
- **Without the limit, gain OCS makes disease alleles worse:** S3q-gain010 has a frequency of 0.238 vs 0.205 for S3q. The static price curve shows why: gain OCS favours sires with above-average risk-allele transmission (`reports/experiments/E8_pilot/price_curve.md`).
- **The full arm vs today's S3q:**
  - Ne −42 (−82 to −2);
  - HD −1.17 (−1.22 to −1.12);
  - frequency −18.0 points (−20.2 to −15.9).

  It is a trade: less diversity than S3q, though still well above the market, for large hip and health gains.

**SYN_S (H8f, reported only):**
- S3q-gain025 vs S1: Ne +44 (+27 to +61), HD −0.65 (−0.84 to −0.47).
- vs S3q: Ne +22 (−2 to +46), HD −0.73 (−0.90 to −0.56).
- In the small breed, the hips budget did not cost diversity.
- The carrier limit could not be tested there (no segregating tested locus in v1).

## What was built
- `coordination/ocs.py`: optional constraint Σᵢ xᵢ·tᵢₗ ≤ bₗ per tested locus; it is dropped first on infeasibility, before age and depth.
- `coordination/planner.py`: `plan_season(carrier_factor=β)` builds t from the observed DNA panel (genotype/2, else the reference allele frequency) and the bound β × candidate mean. It adds the diagnostics `carrier_relaxed` and `carrier_planned`.
- `experiments/strategies.py`: `parse_s3q`; S3q variants `S3q[-gainNNN][-cBBB]`.
- `experiments/runner.py`: new diagnostics `D10_carrier_relaxed`, `D11_carrier_planned`.
- `experiments/hypotheses.py`: `evaluate_e8`, `write_e8_report`.
- `cli.py`: `bsm experiment hypotheses --set e8`.
- `experiments/figures.py`: figure M, plus a label fallback for S3q variants. Before this, figures C and F would have raised `KeyError` for any id without a hand-written label.
- `calibration/plotstyle.py`: colours for the E8 arms.
- Configs `configs/experiments/e8_pilot.yaml` and `health_gain_quotas.yaml`; script `scripts/e8_carrier_price.py`.

## Deviations from the plan (and why)
1. Tests and implementation were committed together, not as a separate red commit, so every commit passes the suite.
2. 12 workers instead of 6 (machine has 12 cores).
3. Figure colours and the "no segregating tested locus" note were added after seeing the first rendering (presentation only).

## Numbers worth knowing
- **Pilot:** 12 parts, about 9.5 min each under 12-way load.
- **Main run:** 130 parts in 47 min (21:34 to 22:21).
- **Solver time per season, median (p95):**

  | arm | SYN_M | SYN_S |
  |---|---|---|
  | S3q | 3.0 s (3.7) | — |
  | gain arms | 9.8–10.1 s (12.9) | 0.5 s |

- **Planned risk-allele transmission** in the carrier arms (D11, mean over loci) falls from 0.052 (2027) to 0.007–0.011 (2067).
- **Overflow:** dams that found no allowed sire with quota left. 2 dams in 900 seasons for S3q-c050; 29–31 for the gain arms.
- **Sanity:** S1 vs S3q points the same way as in E5 (Ne +113 here vs +136 in E5; S3q again has a higher risk-allele frequency than S1).

## Open questions for Tea
- **Product default.** Two candidates:
  - (a) **S3q + carrier limit**: best diversity of the coordinated options, 79% fewer risk alleles than S3q (61% fewer than the market), hips as today, no detectable diversity cost vs S3q.
  - (b) **S3q + gain OCS + carrier limit**: the "all three at once" claim, but with about 40 lower Ne than S3q.

  My suggestion: (a) as the default; (b) as the "breeding for hips" option with a visible diversity budget.
- **Poster/slides wording (cutoff 17 Oct).** Suggestion: "Adding a carrier limit to club quotas cut disease alleles by 80% at no detectable diversity cost; with a hips budget, the same planner beat today's market on diversity, hips and disease alleles at once (synthetic medium breed, 20 replicates)." Nothing in `conference/` has been changed.
- **β = 0.5 is an assumption,** chosen by the pilot rule; a real club would set it as a policy.

## HUMAN tasks waiting
- Decide on the product default and whether E8 goes on the poster or slides (by 17 Oct).
- Earlier HUMAN tasks in `plan/STATUS.md` are unchanged.
