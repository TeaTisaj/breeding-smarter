# Gate report: P8 Experiments
Date: 2026-10-11

All results are in-silico, on synthetic populations, inside our model. No claims about real breeds.

## Acceptance checklist
- [x] E1 and E2 complete with the planned replicates (no reduction needed). Task 8.7: one replicate first (SYN_S 6 s, SYN_M 25 s), extrapolated E1 + E2 at about 75 CPU-minutes, far below 6 hours; ran with 5 workers. Actual: E1 150 parts, 3,774 CPU-seconds (SYN_S 8 to 20 s per part, SYN_M 45 to 82 s); E2 50 parts, 684 CPU-seconds.
- [x] `summary.md` and figures A to F generated: `reports/experiments/E1_headline/` (summary.md, summary.csv, paired_vs_S1.csv, figures A, B, C, D, F as PNG 300 dpi + SVG + poster variants) and `reports/experiments/E2_adoption/` (figure E). Every figure carries "In-silico results on synthetic populations".
- [x] Headline numbers in plain words (from `summary.csv` / `paired_vs_S1.csv`, generation 10 = cohorts born 2069 to 2073):
  - **SYN_S:** realised inbreeding rose from about 0.43 to 0.508 (95% CI 0.503 to 0.514) under S1 (status quo) and to 0.494 (0.487 to 0.500) under S3 (recommender); paired difference S3 - S1 = -1.5 points (-2.3 to -0.6). Ne (from realised IBD over 10 generations) was 34.7 (31.3 to 38.1) under S1 vs 32.1 (28.7 to 35.5) under S3 (paired difference -2.6, CI -8.2 to +3.1: no difference). S4 (coordinated planner): IBD 0.486, Ne 34.4. S0 (random mating): IBD 0.465, Ne 87.5.
  - **SYN_M:** realised inbreeding 0.140 (0.137 to 0.142) under S1 vs 0.135 (0.131 to 0.138) under S3 (paired -0.5 points, -1.0 to -0.07). Ne 298 (256 to 341) under S1 vs 187 (163 to 211) under S3 and 106 (91 to 122) under S4. S0: Ne about 2,660.
  - **Recorded vs true:** S3 cuts recorded pedigree COI far more than true inbreeding (SYN_S: recorded -12.0 points vs realised -1.5; SYN_M: -3.1 vs -0.5).
  - **Health:** S3 almost removes affected-genotype puppies at the tested loci in SYN_M (ABCB1_MDR1 0.01% vs 0.32% under S1; SOD1_DM 0.10% vs 0.25%) and gives the best HD genetic trend (SYN_M mean true liability BV 0.065 vs 0.389 under S1, lower is better). No strategy controls the untestable NOVEL_X in SYN_S (affected genotypes 4.2% to 5.2% at generation 10 in every strategy).
  - **Adoption (E2, SYN_S):** realised inbreeding at generation 10 was 0.508 at 0% adoption (= S2), 0.508 at 25%, 0.497 at 50%, 0.490 at 75%, 0.495 at 100%; recorded COI falls steadily (0.157 to 0.061). Benefits on true inbreeding appear from about 50% adoption and are small.
- [x] **Results that contradict the expected story (reported, not tuned away):**
  1. **Random mating (S0) beats every strategy on true diversity** in both breeds (lowest realised IBD, highest Ne). It spreads use across many sires; the strategies that choose "the best" sire concentrate use.
  2. **S3 and S4 do not raise Ne; in SYN_M they lower it** (187 and 106 vs 298). Ranking each dam's candidates by recorded kinship sends many dams to the same few low-kinship sires: share of eligible males used 6.6% (S3) and 4.6% (S4) vs 13.4% (S1) in SYN_M. Short-term COI goes down, the long-term rate of inbreeding goes up.
  3. **Optimising the recorded pedigree overstates the gain** about 8-fold in SYN_S, because recorded kinship underestimates true kinship (shallow foreign records rank high, see P7).
  4. **S2 (COI-capped market) is slightly worse than S1 in SYN_S** (IBD +1.0 point, CI +0.2 to +1.7; Ne 27.5 vs 34.7).
  5. **E3 is not run yet** (GOAL.md: only after P9 to P11).

## Additional analysis (not in the plan; same seeds as E1)
`E1b_balanced_weights` (`configs/experiments/balanced.yaml`, `configs/scoring/balanced.yaml`): S3 with sire-use weight 0.25 instead of 0.10. SYN_S: IBD -1.8 points vs S1 (-2.7 to -0.9), Ne unchanged (paired -0.7, -5.5 to +4.1). SYN_M: more sires used (8.7% vs 6.6%) and Ne 215 (vs 187 for S3) but still below S1 (paired -84, -161 to -7). Conclusion: per-dam ranking with any reasonable weights concentrates sire use; controlling long-term inbreeding needs a population-level constraint on contributions (optimum contribution selection, S5, a STRETCH task) or explicit sire caps. This is the honest message for the talk: the tool clearly reduces disease risk, close matings and short-term COI, and improves HD, but long-term diversity needs coordinated planning.

## What was built
`configs/rules/exp_pairing.yaml`; `experiments/observed.py` (`ObservedRegistry`: the registry's incremental view, F/D by `inbreeding_extend`, observations, registry-only BLUP every 5 years, `DatasetContext` per year); `experiments/strategies.py` (S0 to S4); `experiments/metrics.py` (M1 to M11; M3 computed in the summary); `experiments/runner.py` (per-breed slim state, common random numbers, checkpointed parts, ProcessPool, debug `ContractChecker`); `experiments/summary.py` (means, 95% t-intervals, Ne from the realised-IBD trend, paired differences vs S1 at generations 5 and 10); `experiments/figures.py` (A to F, poster variants); CLI `bsm experiment run|report`. Shared code: `RuleContext.from_arrays`, `evaluation.blup.evaluate_arrays`, `DatasetContext(foreign=..., extra_offspring=...)`, `rank_fast(candidates=...)`.

Tests (`tests/integration/test_experiments.py`, tiny run): every strategy returns valid sires and S2 to S4 never violate a HARD rule (debug checker); determinism; incremental registry = full recompute of F and D, MK and litter counts match; S4 respects sire capacities; summary statistics on toy data.

## Deviations from the plan (and why)
1. Candidate sires for S3/S4 = the simulator's eligible domestic males plus eligible foreign males that already have a registry record (a breeder can only evaluate dogs with a record). S1/S2 still use unregistered foreign AI sires as in the history.
2. S3 updates planned offspring within the year (later dams see the sire-use of earlier picks).
3. S2 falls back to "HARD rules only" when no candidate passes the COI cap (counted in `stats`).
4. S4 capacity = max(1, round(0.05 x breed registrations in 5 years / 5 / expected litter)) litters per sire per year.
5. Recorded parent links are fixed at registration; a root record refreshed later (an import that was first a stub) keeps its first links in the observed view.
6. Rule checks use mating date July 1 of each year; generation g averages the cohorts born (g - 0.5, g + 0.5] generations after 2026.
7. M6/M7 report affected-genotype shares (penetrance not applied).
8. Workers load a slimmed state with only the experiment breed's neutral alleles (cached in the run's `cache/`), which cut memory from 4.3 GB to about 1.3 GB per worker.

## Numbers worth knowing
- One replicate: SYN_S 8 s, SYN_M 45 s (S2 slower: rules for every dam x sire). Peak memory about 1.3 GB per worker.

## Open questions for Tea
- How to frame the contradicting result on the poster: suggestion "The recommender cuts disease risk and short-term COI; long-term diversity needs coordinated planning (all breeders together), and random mating is a strong baseline."
- Should STRETCH S5 (optimum contribution selection) be attempted after P11? It is the natural fix the data points to.

## HUMAN tasks waiting
- None new.

## E3 carrier-policy ablation (run after P9 to P11, as GOAL.md requires)
`configs/experiments/ablation.yaml`, report `reports/experiments/E3_carrier_policy/`
(summary.md, summary.csv, `paired_vs_S3.csv`, figures). S3 with (a) carrier x carrier
penalised (default), (b) carrier x carrier HARD-blocked (`configs/rules/exp_pairing_hard_carrier.yaml`,
strategy `S3hc`), (c) all known carriers excluded from breeding (strategy `S3xc`), 10
replicates each, generation 10:
- **Deviation:** run on SYN_S as planned **and on SYN_M**, because SYN_S has no segregating
  tested locus in v1 (all lost by drift), which makes the three policies identical there
  (confirmed: identical results).
- **(b) = (a) exactly in both breeds:** the recommender's health component already keeps
  carrier x carrier pairs out of every top-3 choice, so the HARD block never binds.
- **(c) in SYN_M:** tested risk alleles fall far faster (SOD1_DM frequency 0.087 -> 0.007,
  paired -0.081, CI -0.110 to -0.051; ABCB1_MDR1 0.069 -> 0.009), at a diversity cost that is
  small in this breed: Ne 190 -> 163, realised IBD +0.3 points (CI -0.35 to +0.97, not
  significant), neutral heterozygosity -0.3 points (CI -0.7 to +0.1). Direction as expected,
  effect small.
- The expected NOVEL_X effect cannot be tested here: NOVEL_X is absent in SYN_M, and in SYN_S
  the policies do not differ. Reported, not tuned.
