# E9 policy dial and E10 real-world robustness (pre-registration)

Written 18 Oct 2026, before any E9 or E10 run. Builds on E8 (`plan/14_E8_health_gain_quotas.md`, `plan/gates/E8_report.md`). In-silico results on synthetic populations only; everything is reported whatever it shows; no criterion changes after the runs.

**Why:** E8 showed one good point (SYN_M: S3q + gain OCS at dF 0.1% + carrier limit β 0.5 beats S1 on Ne, HD and tested risk-allele frequency) on one seed, one budget, one β and with every breeder taking part. E9 and E10 test whether that point replicates, where it sits on the trade-off curve, whether it survives partial participation, how it compares with Marija's carrier × carrier pair block (branch `feature/e8-hips-quotas`), and what better kinship information adds.

## 1. Arms

Strategy ids `S3q[-gainNNN][-cBBB][-hc][-oracle]`: gain budget dF = NNN / 10⁴ per generation; carrier limit β = BBB / 100 (E8 definition); `-hc` = carrier × carrier pairs HARD-blocked (profile `exp_pairing_hard_carrier`, as E3 arm S3hc and Marija's E8 design); `-oracle` = planning on true-pedigree kinship (as P12 `CC-ocs-mc1-oracle`), a stand-in for genomic kinship.

**E9 `E9_policy_dial`** (`configs/experiments/policy_dial.yaml`), seed 20261115, 10 generations, adoption 1.0, dataset v1, other settings as E8:

| breed | replicates | arms |
|---|---|---|
| SYN_M | 20 | S1, S3q; budget ladder with β 0.5: S3q-gain005-c050, -gain010-c050, -gain015-c050, -gain025-c050, -gain050-c050; carrier dose at 0.1%: S3q-gain010 (no limit), S3q-gain010-c100, -c075, -c025; pair block: S3q-gain010-hc |
| SYN_S | 20 | S1, S3q, S3q-gain025, S3q-gain050, S3q-gain100 (no carrier arms: no segregating tested locus in v1) |

**E10 `E10_robustness`** (`configs/experiments/robustness.yaml`), same seed and replicate count as E9 for SYN_M, so its arms pair with E9's S1 and S3q:
- S3q-gain010-c050 at adoption 0.25, 0.5, 0.75 (non-adopters follow S2 and enter OCS as fixed contributions, as S3q in E7);
- S3q-gain010-c050-oracle at adoption 1.0. Config note (18 Oct, before any run): this arm is listed in `policy_dial.yaml` (E9), because the runner applies the adoption list to every S3q arm of a config; same seed, so it pairs exactly as planned. H10-dna is evaluated from the E9 table.

Run order (checkpointed; if compute runs short, the last groups are cut and the cut is reported): anchors and budget ladder, E10 adoption, oracle, carrier dose, pair block, SYN_S.

## 2. Criteria

Generation 10; Ne = `R_ne_f_late` (late window, generations 5 to 10); HD = `M8_mean_tbv_hd` (lower is better); freq = Σ `M6_freq_*` over tested loci; affected = Σ `M6_affected_*`. Paired by replicate, 95% t-intervals. Few primary criteria on purpose (multiple comparisons); the rest is descriptive.

| id | breed | criterion | pass |
|---|---|---|---|
| **H9-rep** | SYN_M | E8 replication: S3q-gain010-c050 − S1 on Ne, HD and freq | Ne CI lower bound > 0, HD CI upper bound < 0, freq CI upper bound < 0 |
| H9-curve | both | per budget arm: Ne, HD, freq vs S1 and S3q; Pareto frontier over (Ne, HD) | descriptive. Expected: HD better and Ne lower as the budget grows |
| H9-dose | SYN_M | per β at 0.1% (no limit, 1.0, 0.75, 0.5, 0.25): freq and Ne vs the no-limit arm S3q-gain010, paired | descriptive |
| **H9-hc** | SYN_M | freq(S3q-gain010-c050) − freq(S3q-gain010-hc) | CI upper bound < 0. Affected share and Ne reported |
| **H10-adopt** | SYN_M | at adoption 0.5: S3q-gain010-c050 − S1 on Ne, HD and freq | as H9-rep; 0.25 and 0.75 reported |
| **H10-dna** | SYN_M | Ne(S3q-gain010-c050-oracle) − Ne(S3q-gain010-c050) | CI lower bound > 0 |
| D | both | infeasible seasons, carrier limit relaxed, overflow, solver time | reported |

Expectation written now (not a criterion): the pair block (`-hc`) prevents affected puppies but leaves the carrier frequency close to S3q-gain010, so H9-hc should pass; partial adoption weakens all three effects roughly in proportion; oracle kinship raises Ne (P12 H6: CC-ocs-mc1-oracle 786 vs 289 in SYN_M).

## 3. Out of scope
No change to dataset v1, the P1 data contract, `configs/coordination/default.yaml` or existing strategies. SYN_L and an EU 2026/1818 impact study are post-congress. Conference texts change only after Tea approves the results.
