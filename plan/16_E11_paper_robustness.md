# E11: Robustness for the paper (pre-registration)

**Status:** written before any E11 code, population or run exists. Nothing in this file is
changed after results exist; later notes go in a dated "Addendum" section at the end, and any
analysis not listed here is labelled "additional (not pre-registered)".

**Why:** the E5 to E10 results come from one simulated starting population (v1), one breeder
behaviour assumption, and a carrier limit that failed under partial adoption (H10-adopt). E11
tests whether the main findings survive four changes a reviewer would ask for. All results are
in silico, on synthetic populations.

## 1. Questions

| Part | Question |
|---|---|
| R1 populations | Do the herding failure and the quota fix hold in independent starting populations? |
| R2 simple controls | Is the recommender inside a simple control (flat MK-scaled caps, or MK exclusion) as good as inside OCS quotas? |
| R3 breeder freedom | Does herding depend on how strictly breeders follow the ranking? |
| R4 adoption | Does a carrier limit on the adopters' own sires keep the health gain at partial adoption? |

## 2. Populations (R1)

- v1 (`20261011-default-s42`) plus three new populations generated with the **same config**
  (`configs/sim/default.yaml`, hash `68d35948…`) and the current code, seeds **101, 102, 103**,
  run ids `e11-default-s101`, `e11-default-s102`, `e11-default-s103`, tags `v1b`, `v1c`, `v1d`.
- Model identity check, done before this file was written: the current code regenerates v1
  with seed 42 byte-identical in all 9 tables (39 PASS, 8 WARN, 0 FAIL after `bsm validate`).
- The old sensitivity populations (`sens-default-s1..s3`) are **not** used: they were made at a
  commit that is no longer in the repository, so their code cannot be verified.
- **All three new populations are used whatever their validation result.** Each is validated
  and its PASS/WARN/FAIL counts are reported. A hard FAIL is reported, not a reason to drop it.

## 3. New strategy ids

| id | behaviour |
|---|---|
| `S3q-cap` | the recommender inside MK-scaled flat caps (the `cap` control of `CC-cap-*`), shared booking ledger as S3q |
| `S3q-mkx` | the recommender restricted to sires with MK not above the candidates' mean (the `mkx` control of `CC-mkx-*`), no quota |
| `S3-t1`, `S3q-t1` | breeders always take the top-ranked sire (`top_probs` = 1) |
| `S3-u5`, `S3q-u5` | breeders pick uniformly from the top 5 (`top_probs` = 0.2 x 5) |
| `S3q-gain010-c050f` | as `S3q-gain010-c050`, but the carrier bound covers only the adopters' sires: `t'(x - x_fixed) <= b (1 - 1'x_fixed)` per locus, where `x_fixed` are the non-adopters' booked litters as shares |

The freedom settings are assumptions (`assumption: true`); the default stays 0.5 / 0.3 / 0.2.
All other settings as E9 (`profile exp_pairing`, scoring and coordination `default`, 10
generations, late window = generations 5 to 10).

## 4. Configs, seed and replicates

Experiment seed **20261125** for every E11 config (common random numbers within a population).

| Config | Dataset | Breeds | Strategies | Adoption | Replicates | Parts |
|---|---|---|---|---|---|---|
| `E11a_pop_v1` .. `E11a_pop_v1d` (4 configs) | v1, v1b, v1c, v1d | SYN_S, SYN_M | S1, S3, S3q, S3q-gain010-c050 | 1.0 | 10 | 320 |
| `E11b_controls_freedom` | v1 | SYN_S, SYN_M | S1, S3, S3q, S3q-cap, S3q-mkx, S3-t1, S3-u5, S3q-t1, S3q-u5 | 1.0 | 20 | 360 |
| `E11c_adoption` | v1 | SYN_M | S3q-gain010-c050, S3q-gain010-c050f | 0.25, 0.5, 0.75, 1.0 | 20 | 160 |

`E11c` uses the same seed and dataset as `E11b`, so its arms pair with E11b's S1 (as E10 paired
with E9).

**Pilot and reduction rule (fixed now):** run one replicate of every SYN_M arm first and
extrapolate. If the full set is estimated above 14 hours wall-clock on 6 workers, reduce in
this order until it fits, and report the reduction: (1) R3 to SYN_M only; (2) R1 SYN_S arm
`S3q-gain010-c050` dropped; (3) E11c adoption 0.75 dropped. Replicates are never reduced.

## 5. Metrics and statistics

Same as E9: late-window Ne (`R_ne_f_late`, mean of per-replicate values), mean true HD breeding
value at generation 10 (`M8_mean_tbv_hd`), tested risk-allele frequency summed over loci
(`M6_freq_*`), share of eligible males used at generation 10 (`M10_share_sires_used`). Paired
differences by replicate, 95% t-intervals. Secondary Ne cross-check from realised coancestry
(`R_ne_c_late`) is reported for every Ne comparison.

## 6. Hypotheses and how each result is read

**H11-pop (R1).**
- (a) `S3 - S1` share of males used < 0 (CI below 0), SYN_M, in each population.
- (b) `S3q - S1` late Ne > 0 (CI above 0), SYN_M, in each population.
- (c) `S3q-gain010-c050 - S1`: Ne > 0, HD < 0 and freq < 0 (all CIs), SYN_M, in each population.
- Pass for each of (a), (b), (c): it holds in **at least 3 of the 4** populations.
- Reported also: the same contrasts in SYN_S, and a pooled estimate over all 40 replicates
  (population as stratum) together with the range of the four population estimates. The pooled
  interval treats replicates as independent and so understates between-population variation;
  the paper says this and leads with the per-population results.
- Reading: if (b) or (c) fails, the paper's claim is restricted to "in the reference
  population" and the R1 result is reported as is.

**H11-cap (R2).** `S3q - S3q-cap` and `S3q - S3q-mkx`, late Ne, SYN_M and SYN_S, two-sided.
- OCS better: CI above 0.
- Simple control as good: CI includes 0 **and** lies within ±20% of mean S3q Ne (equivalence
  margin; `assumption: true`).
- Simple control better: CI below 0.
- Otherwise: inconclusive. All four readings are reported; none changes the main claim, which
  is about contribution control, not about OCS in particular.

**H11-free (R3).** SYN_M.
- (a) `S3-x - S1` share of males used < 0 (CI below 0) for every freedom setting x in {t1, default, u5}.
- (b) `S3q-x - S1` late Ne > 0 (CI above 0) for every x.
- Reading: if (a) fails at u5, the paper reports that more breeder freedom reduces herding, as
  a design result.

**H11-adopt (R4).** SYN_M, `S3q-gain010-c050f` at adoption 0.5 vs S1: freq < 0 (CI below 0).
- Reported also: Ne and HD vs S1, and freq vs `S3q-gain010-c050` at each adoption level.
- Reported also: the share of seasons in which the carrier limit was dropped, per arm and level.
- Reading: if H11-adopt fails, the limitation stated in the paper stays.

**No result leads to dropping, rerunning or re-seeding any part.**

## 7. Code changes (tests first)

1. `parse_s3q` and `make_strategy`: the ids above. Contract tests for each new id, and an
   unknown-id test.
2. `RecommenderWithQuotas` with `control="cap"` and `control="mkx"`. For mkx: sires above the
   candidates' mean MK get quota 0, the rest are unlimited. Known-answer test.
3. `OCSProblem.carrier_free_only` and the constraint in §3. Closed-form test with one fixed
   sire, and a test that it equals the old constraint when nothing is fixed.
4. Per-arm `top_probs` (`-t1`, `-u5`). Test that the probabilities used are the ones in §3.
5. `evaluate_e11` / `write_e11_report` and `bsm experiment hypotheses --set e11`.
6. Existing ids, configs and results are unchanged; E5 to E10 are not rerun.

## 8. Outputs

`plan/gates/E11_report.md`, `reports/experiments/E11_hypotheses/hypotheses.{md,csv}`, a
validation report per new population, and a robustness figure for the paper.

## Addendum

(none yet)
