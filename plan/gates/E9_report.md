# Gate report: E9 policy dial and E10 real-world robustness
Date: 2026-10-18

In-silico results on synthetic populations (no real dogs). Pre-registration: `plan/15_E9_E10_policy_dial.md` (commit `1b0eade`, before any run; one config note added before any run, see Deviations). Hypotheses table: `reports/experiments/E9_hypotheses/hypotheses.md` (generated from the CSVs). Figures: `reports/experiments/E9_hypotheses/figures/figN_policy_dial*.{png,svg}`, `figO_adoption*.{png,svg}`.

## Acceptance checklist
- [x] Criteria fixed before data (evidence: `git log plan/15_E9_E10_policy_dial.md`).
- [x] New ids `-hc`, `-oracle` with tests (`tests/unit/test_strategy_ids.py`; tiny-run contracts `test_p12_strategy_contract[S3q-gain010-hc, S3q-gain010-c050-oracle]`).
- [x] E9 (360 parts) and E10 (60 parts) complete; parts checked readable after the interrupted first run.
- [x] Hypotheses report and figures N and O generated from the per-replicate tables.
- [x] Check suite green (`scripts/check.sh`: 314 passed, 1 skipped).
- [ ] H10-dna and H10-adopt failed (reported below, not re-defined).

## Results (SYN_M, generation 10, 20 replicates, paired, 95% CI)

| id | result | pass |
|---|---|---|
| **H9-rep** | E8 replicates on an independent seed: S3q-gain010-c050 − S1: Ne +85 (+48 to +122), HD −1.17 (−1.25 to −1.09), risk-allele freq −8.9 points (−10.3 to −7.5) | **yes** |
| **H9-hc** | carrier limit vs carrier × carrier pair block: freq −21.1 points (−23.9 to −18.3); affected −0.32 points (−0.47 to −0.17); Ne −19 (−44 to +5) | **yes** |
| **H10-dna** | planning on true kinship − recorded kinship: Ne −40 (−61 to −20); HD −0.06 (−0.11 to −0.01) | **no** |
| **H10-adopt** | 50% of breeders taking part, vs S1: Ne +181 (+130 to +232) yes; HD −0.56 (−0.63 to −0.48) yes; freq +1.3 points (−1.1 to +3.7) **no** | **no** |

Absolute values (means over replicates; Ne is the mean of per-replicate late-window Ne):

| SYN_M arm | Ne | HD | risk-allele freq (sum) | affected (sum) |
|---|---|---|---|---|
| S1 market | 205 | +0.39 | 0.113 | 0.30% |
| S3q quotas | 323 | +0.39 | 0.214 | 0.57% |
| budget 0.05% + carrier 0.5 | 326 | −0.71 | 0.029 | 0.03% |
| budget 0.1% + carrier 0.5 | 290 | −0.78 | 0.023 | 0.00% |
| budget 0.15% + carrier 0.5 | 235 | −0.87 | 0.023 | 0.00% |
| budget 0.25% + carrier 0.5 | 184 | −0.95 | 0.025 | 0.02% |
| budget 0.5% + carrier 0.5 | 116 | −1.09 | 0.021 | 0.00% |
| budget 0.1%, no carrier limit | 279 | −0.81 | 0.252 | 0.80% |
| budget 0.1% + pair block (hc) | 309 | −0.75 | 0.234 | 0.32% |
| budget 0.1% + carrier 0.5, true kinship | 250 | −0.84 | 0.024 | 0.00% |

## What it means
1. **The E8 result is real, not luck.** It replicated on an independent seed with nearly identical effects (E8: Ne +71, HD −1.18, freq −8.9; E9: +85, −1.17, −8.9).
2. **The policy dial is smooth and monotone** (H9-curve, descriptive). Every step up in budget buys better hips and costs diversity; all five budgets keep disease alleles at about a fifth of the market. Two settings stand out:
   - **0.05%:** Ne equal to plain quotas (vs S3q +3, −26 to +31), HD −1.10 and freq −18.4 points vs S3q. Practically all the health and most of the hip gain at no detectable diversity cost.
   - **0.25% and above:** Ne falls to or below the market (0.25%: −21, −52 to +10; 0.5%: −89).
3. **The carrier limit is cheap at every strength tested** (H9-dose, descriptive). Against the no-limit arm, β 1.0 / 0.75 / 0.5 / 0.25 cut freq by 11 / 18 / 23 / 24 points, and no β shows a detectable Ne cost (all Ne intervals include 0).
4. **A population limit beats a pair block** (H9-hc). Blocking carrier × carrier pairs (Marija's design) prevents affected puppies (0.80% → 0.32%) but leaves the allele frequency where it was (0.252 → 0.234, −1.8 points, −4.5 to +0.9). The carrier limit removes both. The pair block also conflicts with quotas: 639 dams in 900 seasons found no allowed sire with quota left (overflow), vs 35 with the carrier limit.
5. **Small breed (SYN_S):** the hips budget beats both the market and plain quotas on Ne and HD at 0.25% and 0.5% (0.5%: Ne 74 vs S3q 52 and S1 31; HD −0.70 vs +0.06). At 1%, Ne is no longer above S3q.

## Failed hypotheses (reported as they are)
- **H10-dna: true kinship lowered Ne in the hips-budget planner** (250 vs 290). This is the opposite of P12, where true kinship raised Ne for the pure-diversity planner (CC-ocs-mc1-oracle 786 vs 289). The mechanism is not established. On true kinship the coancestry levels the budget is computed from are about three times higher (mean C_now 0.136 vs 0.046), and the planner spent its budget slightly more on hips (HD −0.06). **Do not claim that genomic data improves this planner.** The P12 statement (genomic data helps the diversity planner) still stands.
- **H10-adopt: with 50% of breeders taking part, the health gain disappears.** The cause is a design flaw in the carrier limit. Its bound covers every mating in the season, including the non-adopters' sires (they follow S2 and enter OCS as fixed contributions). When those alone exceed the bound, the season is infeasible and the limit is dropped:

  | breeders taking part | seasons with the carrier limit dropped |
  |---|---|
  | 25% | 99% |
  | 50% | 72% |
  | 75% | 21% |

  Diversity and hips still beat the market at every participation level (Ne +92 / +181 / +197; HD −0.25 / −0.56 / −0.89). Ne is even higher than at 100%, partly because infeasible gain seasons fall back to conservation planning (30% of seasons at 25%).

## Deviations from the plan
1. **The oracle arm was moved from E10 to E9** before any run, because the runner applies the adoption list to every S3q arm of a config. Same seed, so it pairs as planned. Noted in the pre-registration before the run.
2. **The first run used 12 workers on an 8-core, 16 GB machine** and thrashed memory (load average about 115, about 3.4 GB of swap). It was stopped after 76 parts (all readable) and resumed in the pre-registered priority order with 6 single-threaded workers (17:36 to 20:53). Results do not depend on worker count (seeded per replicate; determinism test). Solver times for the two arms that ran mostly during the thrash (gain005-c050, gain010-c050: median about 11.7 s vs about 4.3 s) are inflated and not comparable.
3. **Bug fixed:** `summary.paired_vs` returned a table without columns when an experiment has no reference arm (E10), and `bsm experiment report E10_robustness` crashed. It now always returns its columns (`tests/unit/test_summary_paired.py`).

## Numbers worth knowing
- E9 + E10: 420 parts.
- Infeasible seasons:
  - E9 SYN_M: 0 in every arm;
  - E9 SYN_S: 5 / 3 / 1 of 900 (budgets 0.25 / 0.5 / 1%);
  - E10: 277 of 2,700.
- Carrier limit dropped: 0 of 900 in every E9 arm.
- Sanity: S3q − S1 Ne +118 (E5 +136, E8 +113).

## Open questions for Tea
1. **Poster headline** (cutoff 21 Oct). Suggestion: "Replicated on an independent seed: club quotas with a hips budget and a carrier limit beat today's market on diversity, hips and disease alleles at once (synthetic medium breed)", with figure N. Optional second line: "At the lowest budget (0.05%), diversity equals plain quotas while hips and disease alleles improve."
2. **Product default:** budget 0.05% with carrier limit 0.5 is the strongest setting found. It was chosen after seeing E9, so present it as an observation, not as a pre-registered result.
3. **Follow-up E11 (not run; needs a new pre-registration):** apply the carrier limit to the adopters' own contributions (bound on the free part, with non-adopters' sires excluded from the left-hand side), then rerun 25 / 50 / 75% participation. About 1 h of compute, could be ready on 20 Oct. Without it, the honest statement is: "the carrier limit works when most of the club takes part".
4. **Talk to Marija** about H9-hc: her pair block is now an arm, and the comparison is a result she can co-own.

## HUMAN tasks waiting
- Decide the poster wording and whether E11 runs before the poster.
- Earlier HUMAN tasks in `plan/STATUS.md` are unchanged.
