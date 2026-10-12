# E8: Hips within quotas (follow-up to P12)

Written 2026-10-12, before any E8 result was looked at.

**Status: draft, waiting for Tea's approval of H7 to H9** (new criteria, not part of the P12 pre-registration). Sections 1 and 3 are fixed once Tea approves.
- The E8 parts started running on 2026-10-12, before approval.
- No E8 outcome has been computed or looked at. The pilot part printed only its runtime and memory.
- `bsm experiment report E8_hips_quotas` and `bsm experiment hypotheses --set E8` are run only after approval.

## 0. Why this experiment exists
P12 left a gap in the product story (`plan/gates/P12_report.md`, result 3 and Open questions): the product mode S3q keeps the diversity gain of coordination but loses most of S3's health and HD benefits (SYN_M, generation 10: mean true HD BV S3q 0.40, S1 0.39, S3 0.06; MDR1 affected S3q 0.29%, S1 0.32%, S3 0.01%). Quotas go to low-MK sires regardless of EBV or carrier status, and breeders can only choose among those sires.

E6 showed that gain OCS under a small ΔF budget keeps Ne and improves hips (SYN_M: `CC-gain010-mc1` Ne 288, HD BV −0.79, vs `CC-ocs-mc1` Ne 289, HD BV +0.39). The pieces already exist: gain OCS (`plan_season(control="ocs_gain")`) and the carrier x carrier HARD block (`exp_pairing_hard_carrier`, E3 arm S3hc). E8 puts them together in S3q.

## 1. Design (fixed)
- **Strategy `S3q-gainNNN[-hc]`** (`experiments/strategies.py`). Same as S3q (shared booking ledger; each adopting dam picks among the top 3 of `rank_fast` restricted to sires with quota left, with probabilities 0.5/0.3/0.2; non-adopters follow S2 and enter OCS as fixed contributions). The difference: quotas come from **gain OCS** (P12 D4 (b): maximise the mean standardised HD EBV index of the chosen sires subject to `c'Kc ≤ C_next`, with ΔF = NNN / 10⁴ per generation) instead of conservation OCS. With `-hc`, the profile `exp_pairing_hard_carrier` is used everywhere: OCS pair inputs, ranking and the non-adopters' S2.
- **Budget rule (same for both breeds).** The primary arm uses the **tightest ΔF budget on the breed's ladder**. The ladders were fixed in P12 decision D6 before any P12 result: "1.0%, 0.5%, 0.25% per generation; SYN_M also 0.1%" (`plan/13_P12_coordination.md`, commit d8308da, 2026-10-11 16:40; results 19:03). The values are in `configs/coordination/default.yaml`.
  - SYN_S: tightest rung 0.25% (`delta_f_ladder`, windig-2013 "small risk") → primary `S3q-gain025-hc`.
  - SYN_M: tightest rung 0.1% (`delta_f_extra_medium`, windig-2013) → primary `S3q-gain010-hc`.
  - The SYN_M ladder has the extra 0.1% rung because its status-quo ΔF (about 0.17%) is already below 0.25%. A 0.25% budget would not constrain it. This reason was written before P12 results.
  - Why the tightest rung: H8 puts diversity first, and the tightest rung is the most diversity-protective budget that was actually tested in each breed. It is not chosen for the best HD result: looser rungs gave more HD gain in E6 in both breeds.
  - 0.1% was never tested in SYN_S, so "0.1% in both breeds" would be a new, untested setting.
  - Decided on 2026-10-12 by Marija Perković; Tea's approval is pending (see Status).
- **Arms** (`configs/experiments/hips_quotas.yaml`, id `E8_hips_quotas`):

  | breed | replicates | primary arm | anchors | additional arms |
  |---|---|---|---|---|
  | SYN_S | 20 | `S3q-gain025-hc` | S1, S3, S3q | none |
  | SYN_M | 10 | `S3q-gain010-hc` | S1, S3, S3q | `S3q-gain025-hc` (exploratory: what better hips cost), `S3q-gain010` (exploratory: no carrier block) |

- **Seed and pairing.** Seed 20261024 (E1/E5) and the same replicate counts, so replicate r starts from the same random stream in every arm. The anchors are rerun inside E8 and not reused from E5, so every comparison comes from one code version on one machine.
- Everything else is as in E5: dataset v1, 10 generations, adoption 1.0, profile `exp_pairing`, scoring `default`, coordination `default`, COI cap 6.5%, EBVs every 5 years, every live-born puppy registered.

## 2. Expectations written before the run (not criteria)
Ne below is 1 / (2 × mean late ΔF), the H8 definition, from E5/E6 (same seeds).
- SYN_S:
  - S1 33, S3q 52, `CC-gain025-mc1` 67 (ratio to S3q 1.29);
  - HD BV: S3q +0.03, `CC-gain025-mc1` −0.69.
  - Hips and diversity both look reachable.
- SYN_M:
  - S1 188, S3q 328, `CC-ocs-mc1` 284;
  - `CC-gain010-mc1` 285 (ratio to S3q 0.87);
  - `CC-gain025-mc1` 194 (ratio 0.59).
  - **H8 may fail in SYN_M even at 0.1%, and very likely fails at 0.25%.**
  - S3q kept more diversity than the pure planner (328 vs 284). The recommender inside gain quotas may therefore also do better than the `CC-gain` arms. This is unknown.
  - The carrier block should bring MDR1 and SOD1 affected shares close to S3's levels.

## 3. Pre-registered success criteria (fixed)
All comparisons are paired by replicate, with 95% t-intervals. Ne and ΔF use the late window, generations 5 to 10, as in `experiments/summary.py` and the P12 report. HD and affected shares are taken at generation 10. P is the primary arm of the breed.

| id | Criterion | Breeds |
|---|---|---|
| H7 (hips) | Mean true HD breeding value at generation 10 (lower is better): P − S3q < 0 (CI upper bound < 0) | SYN_S and SYN_M |
| H8 (diversity, non-inferiority) | Ne(P) / Ne(S3q) with Ne = 1 / (2 × mean late ΔF) per arm (as P12 H5), i.e. mean ΔF(S3q) / mean ΔF(P) over paired replicates. **Pass if the lower bound of its 95% Fieller interval is ≥ 0.9** (at least 90% of S3q's Ne kept). Support rows, no pass/fail: each arm's Ne, and the paired late ΔF P − S3q with CI | SYN_S and SYN_M |
| H9 (health) | Affected-genotype share summed over tested loci at generation 10: P − S1 < 0 (CI upper bound < 0) | SYN_M (SYN_S has no segregating tested locus in v1) |
| H10a, H10b | Reported with CI, no pass/fail: Ne late P − S1 (paired); HD BV P − S3 (paired) | both |

Interpretation rules:
- H7, H8 and (in SYN_M) H9 all pass for P:
  - SYN_M headline: "diversity, health and hips at once";
  - SYN_S headline: "diversity and hips" (no tested locus segregates).
  - Always with the numbers and "in silico".
- Mixed: the headline states exactly which criterion passed in which breed.
- **Only H8 fails** (H7 and, in SYN_M, H9 pass). The allowed wording is generated by `e8_headlines`:
  - "hips (and health) improve at a measured diversity cost: Ne X% of S3q (95% CI lo to hi)";
  - plus "Ne still above today's market" only if the H10a interval (paired Ne P − S1) lies entirely above 0. Otherwise the wording says the Ne is not shown to be above today's market.
  - No adjective such as "small" without the numbers.
- H8 fails: report how much diversity was lost (the Ne ratio and its interval). Then analyse whether the loss comes from the ΔF budget, the carrier block or their combination: compare with the arm without the carrier block, and with `CC-gain*-mc1` from E6. This analysis is labelled additional.
- The additional SYN_M arms are evaluated with the same quantities and reported, but they do not decide the headline. `S3q-gain010` vs `S3q-gain010-hc` shows what the carrier block adds.
- No criterion or threshold is changed after results exist, and the 0.9 margin is not lowered if H8 fails. Anything else is labelled "additional (not pre-registered)".
- The product default (club planner and the app's quota toggle) is not changed by E8 alone. That is Tea's decision.

## 4. How to run and evaluate
```bash
uv run bsm experiment run configs/experiments/hips_quotas.yaml --workers 7
uv run bsm experiment report E8_hips_quotas
uv run bsm experiment hypotheses --set E8   # reports/experiments/E8_hypotheses/hypotheses.md
```
The evaluation code (`experiments/hypotheses.py`: `evaluate_e8`, `e8_headlines`) was written and tested before the run (`tests/unit/test_hypotheses.py::test_e8_known_answers`). The primary arms and the 0.9 margin are constants there (`E8_PRIMARY`, `E8_NE_MARGIN`).
