# P8: Experiments (does the recommender actually help?)

**Goal:** produce the evidence for the talk and poster: starting from the exact end state of dataset v1, simulate 10 future generations under different breeding strategies and compare inbreeding, diversity, disease and HD outcomes, with replicates and confidence intervals.
**Effort:** 1.5 days. **Depends on:** P5 (frozen v1 with saved simulator state), P7.

Module: `src/breeding_smarter/experiments/`.

**Framing rule:** these are in-silico results inside our model. Every figure caption and the report say so. No claims about real breeds.

---

## 1. Strategies

All strategies see only **observed** information (registry pedigree, DNA tests, HD grades, EBVs), never truth. All plug into the P3 `MatingStrategy` interface.

| id | Name | Behaviour | Tag |
|---|---|---|---|
| S0 | Random | uniform choice among eligible males of the breed | [MVP] reference only |
| S1 | Status quo market | the P3/P4 `MarketStrategy` unchanged (popular sires, partial close-mating avoidance, DNA-aware) | [MVP] |
| S2 | Compliant market | S1, but candidates failing a HARD rule of `exp_pairing` are removed, and pairs with predicted COI above 6.5% are resampled (what a regulated market with a COI check looks like) | [MVP] |
| S3 | Recommender | each dam picks among the top 3 of `rank_fast` (P7) with probabilities 0.5 / 0.3 / 0.2 (breeders keep some freedom); parameter `adoption` = share of dams whose breeder uses the tool, the rest follow S2 | [MVP] |
| S4 | Coordinated planner | all dams of the breed in a year are assigned jointly: cost `c(s,d) = F_off + lambda * MK_off` (lambda 1, assumption), sire capacity from the FCI 5% rule converted to litters per year, HARD-rule pairs get cost 1e6; solved with `scipy.optimize.linear_sum_assignment` on a matrix where each sire is replicated `capacity` times | [MVP], first to cut if time is short |
| S5 | Optimum contribution selection | QP with `cvxpy`, then mate allocation | [STRETCH] |

**Same dams for every strategy.** Strategies only choose sires. Which dams are mated each year is decided by the simulator's eligibility rules and is identical across strategies. Therefore S2 to S4 use a pair-level rule profile `exp_pairing` (`configs/rules/exp_pairing.yaml`: the EU close-relative ban, carrier pairing, and the COI cap for S2). Dam-level rules such as the unverified EU minimum age would remove dams in some strategies and not others, which would confound the comparison.

## 2. Engine requirements (check before starting)
- The end-of-history `SimState` is in `state/` of the dataset v1 run (P3 task 3.9).
- `inbreeding_extend` (P2 task 2.4) and `rank_fast` (P7 task 7.6b) exist and are tested.
- MK of the reference population is recomputed once per simulated year per breed (one Colleau pass); kinship of each dam to all candidates with `kinship_to_all` (one pass per dam).
- EBVs re-evaluated every 5 simulated years with the P4 BLUP (registry data only).
- During experiments every live-born puppy is registered (simplification, state it), so the recorded pedigree keeps growing without gaps; foreign imports continue at the configured rate.

## 3. Metrics (per simulated year, cohort of births, then per generation = year / generation interval)

| id | Metric | Source of truth |
|---|---|---|
| M1 | Mean recorded pedigree F of the cohort | observed |
| M2 | Mean realised IBD `f_true_ibd` of the cohort | truth |
| M3 | Rate of inbreeding per generation (from M2) and Ne = 1 / (2 dF) | truth |
| M4 | Gene diversity of living breeding-age animals, `1 - mean MK` (recorded pedigree, base = 2026 registry) | observed |
| M5 | Expected heterozygosity at the neutral loci among living animals, relative to its 2026 value | truth |
| M6 | Risk-allele frequency and affected-puppy rate per tested locus | truth |
| M7 | Same for `NOVEL_X` (untestable) | truth |
| M8 | Mean true HD breeding value of the cohort (genetic trend) and observed D+E share | truth and observed |
| M9 | Top-sire share, top-20% sire share, share of eligible males used, number of sires above the FCI 5% threshold | observed |
| M10 | Share of eligible animals of each sex used for breeding (FCI: programmes should not exclude more than 50%) | observed |
| M11 | Mean litter size (inbreeding depression through dam F) | observed |

## 4. Experiments

### E1 Headline [MVP]
`configs/experiments/headline.yaml`: breeds SYN_S and SYN_M; 10 generations (45 years with a 4.5-year interval); replicates SYN_S 20, SYN_M 10; strategies S0 to S4; adoption 1.0 for S3; profile `exp_pairing`; default scoring weights. Only the selected breed's subpopulations (domestic and foreign) are simulated forward.

### E2 Adoption sweep [MVP]
SYN_S only, S3 with adoption 0, 0.25, 0.5, 0.75, 1.0; 10 replicates. Answers "what if only some breeders use it?" (adoption 0 equals S2).

### E3 Carrier policy ablation [MVP if time, else STRETCH]
SYN_S, S3 with three health policies: (a) default (carrier x carrier penalised), (b) carrier x carrier HARD-blocked, (c) all known carriers excluded from breeding. Compare M4, M5, M6, M7 and M10. Expected story (to be confirmed by the data, not assumed): excluding all carriers lowers the tested disease faster but costs diversity and raises the untestable `NOVEL_X` and overall inbreeding.

### E4 SYN_L [STRETCH]
Headline strategies on the large breed at scale 0.25.

## 5. Tasks
- **8.0 [MVP]** `configs/rules/exp_pairing.yaml` (section 1) with its own loader test.
- **8.1 [MVP]** Implement S0, S2, S3, S4 in `experiments/strategies.py` (S1 exists). S3 calls the P7 code with an in-memory `DatasetContext` that is updated each year (do not reload from disk; build an `IncrementalContext` that appends new animals, extends F and D, updates MK, offspring counts, DNA and HD observations).
- **8.2 [MVP]** `experiments/runner.py`: load v1 state, fork per (strategy, replicate), run, collect metrics each year into a long-format table `(experiment, breed, strategy, adoption, replicate, year, generation, metric, value)`. Parallel over replicates with `concurrent.futures.ProcessPoolExecutor` (`--workers`). Seeds: replicate `r` uses child seed `r` of the experiment seed for every strategy (common random numbers as far as possible; state that strategies still diverge).
- **8.3 [MVP]** Checkpointing: write each finished (strategy, replicate) to its own Parquet file; a rerun skips finished parts.
- **8.4 [MVP]** `experiments/summary.py`: per (breed, strategy, generation) mean and 95% t-interval over replicates; paired differences vs S1 at generations 5 and 10 with 95% intervals. Output `summary.csv` and `summary.md` (tables ready for the paper).
- **8.5 [MVP]** `experiments/figures.py` (reuse `calibration/plotstyle.py`, colourblind-safe palette, fixed strategy colours across all figures):
  - **Fig A (headline):** M2 realised inbreeding vs generation, one panel per breed, mean line plus 95% band per strategy.
  - Fig B: Ne (M3) at generation 10 per strategy, bars with intervals.
  - Fig C: affected-puppy rate for one tested locus and for `NOVEL_X` over generations.
  - Fig D: trade-off scatter: HD genetic gain vs rate of inbreeding per strategy (replicate points plus mean).
  - Fig E: adoption sweep (E2): dF vs adoption share.
  - Fig F: sire concentration (M9) per strategy.
  Each figure as PNG (300 dpi) and SVG, plus a poster variant with larger fonts.
- **8.6 [MVP]** CLI: `bsm experiment run <config> [--workers N]`, `bsm experiment report <experiment_id>`.
- **8.7 [MVP]** Runtime planning: run 1 replicate of E1 first, measure, extrapolate total time, report it to Tea before launching the full run. If the full run would exceed 6 hours on Tea's machine, reduce replicates (never generations) and say so.

## 6. Tests
- Strategy contract: every strategy returns a valid sire (eligible, right breed, or -1) for every dam; S2, S3, S4 never produce a HARD-rule violation (assert inside the runner in debug mode and in a test on the tiny run).
- `IncrementalContext` after k years equals a `DatasetContext` rebuilt from scratch on the same data (F, MK, counts).
- S4 respects sire capacities.
- Determinism: same experiment seed gives identical results tables.
- Summary statistics on a toy table with known means and intervals.

## 7. Acceptance checklist (gate)
- [ ] E1 and E2 complete with the planned replicates (or the documented reduction).
- [ ] `summary.md` and figures A to F generated.
- [ ] Gate report states the headline numbers in plain words, for example: "After 10 generations in SYN_S, realised inbreeding rose by X (95% CI) under S1 and by Y under S3; Ne was A vs B." Numbers come from `summary.csv`, nothing typed by hand.
- [ ] Gate report lists any result that contradicts the expected story; we report it honestly instead of tuning it away.
