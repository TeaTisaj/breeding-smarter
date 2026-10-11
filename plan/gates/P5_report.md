# Gate report: P5 Calibration and validation
Date: 2026-10-11

## Acceptance checklist
- [x] Dataset v1 frozen and tagged: `configs/datasets.yaml` -> `v1` = run `20261011-default-s42` (seed 42, config hash `68d35948...`, git `d3fddf8f`). Regenerating at the tagged commit reproduced `registry/animals.parquet` byte for byte. **All hard targets pass** (`bsm validate --run 20261011-default-s42`: 39 PASS, 8 WARN, 0 FAIL). Soft warnings explained below.
- [x] T12 and T13 pass (main correctness evidence): engine vs gene drop max |difference| per birth decade L 0.0001, M 0.0011, S 0.0075 (limit 0.01); regression slope L 0.994, M 1.008, S 0.959 (0.9 to 1.1), intercepts all within +/- 0.01. Pass on all four seeds (table below).
- [x] Validation report and figures generated: `reports/validation/20261011-default-s42/validation_report.md`, `targets_vs_simulated.csv`, `figures/fig1..fig8` (PNG 300 dpi + SVG). **[HUMAN] Tea has not yet looked at figure 4** (`fig4_recorded_vs_true_f.png`); I checked it: recorded COI is far below true F in all breeds, and true pedigree F and realised IBD lie on top of each other.
- [x] Seed sensitivity table (below).
- [x] All remaining `assumption: true` values listed: generated file `docs/assumptions.md` (132 lines; `bsm docs assumptions`, freshness test).

## Seed sensitivity (seeds 42 = v1, 1, 2, 3; same configs)
| Target | Breed | s42 | s1 | s2 | s3 |
|---|---|---|---|---|---|
| T05 top-20% sire share (>= 0.40) | L / M / S | 0.50 / 0.56 / 0.64 | 0.52 / 0.55 / 0.58 | 0.50 / 0.54 / 0.55 | 0.50 / 0.56 / 0.59 |
| T07 Ne individual dF | L (200-900) | 703 | 370 | 560 | 603 |
| | M (80-150) | 137 | **182 (FAIL)** | 130 | 129 |
| | S (25-50) | 41.8 | 31.4 | 34.0 | 27.0 |
| T11 recorded F < true F (2025) | all | true | true | true | true |
| T12 max abs diff | L / M / S | 0.0001 / 0.0011 / 0.0075 | 0.0002 / 0.0006 / 0.0038 | 0.0002 / 0.0006 / 0.0033 | 0.0002 / 0.0003 / 0.0030 |
| T13 intercept | S | -0.0019 | 0.0035 | -0.0087 | -0.0021 |

11 of 12 Ne values are inside their bands; with seed 1 SYN_M lands at 182, above its band (lewis-2015 archetype 80 to 150). Ne of a 300 to 600 registrations-a-year breed varies between histories by roughly +/- 30%; the results are not tied to a lucky seed, but SYN_M sits in the upper part of its band. Reported, not tuned away.

## Calibration (task 5.5)
Round 1 (`configs/calibration/grid.yaml`, 27 combinations x 2 seeds, results `reports/validation/calibration_grid*.csv`), then two second rounds over 4 seeds each (`grid_small_round2.yaml`, `grid_medium_round2.yaml`). Applied (tea pre-approved via GOAL.md; each value carries `note: tuned in P5, see ...csv`):
| Breed | popular_sire_alpha points (1935, 1999, 2000, 2026) | attractiveness_beta |
|---|---|---|
| SYN_L | 0.2, 0.6, 0.2, 0.2 | 0.6 (best: 0 hard fails both seeds) |
| SYN_M | 0.3, 0.8, 0.4, 0.4 | 0.65 (between 0.6: Ne 130-146 and 0.7: Ne 76-125, to centre the band) |
| SYN_S | 0.6, 1.2, 0.6, 0.6 | 0.8 (round 2: Ne 36 to 39 over 4 seeds) |
Candidate shares and close-mating avoidance kept at their P3 values.

## Numbers worth knowing (v1)
- Rows: animals 153,641; litters 23,924; health tests 27,494; DNA tests 84,454; EBVs 145,197; truth animals 275,189; genotypes 1,375,945. Generation 70.6 s wall (simulation 22.1 s; the rest is writing, gene-drop truth tables and BLUP), peak memory about 4 GB.
- Ne (individual dF, 2016-2025): L 703, M 137, S 41.8. Census Ne: L 6,191, M 1,193, S 248.
- Mean realised IBD 2025 cohort (T17): L 0.036, M 0.126, S 0.43, next to the published genomic median of about 0.25 (bannasch-2021; different base, so only context). SYN_S is very inbred, mostly from the hidden pre-1980 history (true F about 0.39 already in 1980).
- Risk-allele frequencies 2026 (T18): L PRCD 0.04, SOD1 0.13, DNM1 0.04, NOVEL_X 0.02; M SOD1 0.19, MDR1 0.11, PRCD 0.003, NOVEL_X 0; S NOVEL_X 0.21, all tested loci lost by drift. For P8: tested-locus figures use SYN_M; NOVEL_X uses SYN_S.

## Soft-target warnings, explained
- T02 SYN_S perinatal-loss share 19.1% (target 24.6% +/- 5): small litters (mean 4) have fewer chances of a loss at a constant per-puppy rate.
- T06 SYN_M: no sire above the FCI 5% threshold in the windows ending 2020/2025 (max ratio below 1). The calibrated market is less concentrated than the historical source; T05 still passes.
- T09 SYN_M 5.08 and SYN_S 5.07 years (target 4 to 5): just above; dams breed up to 8 and sires up to 12 years.
- T10 SYN_L and SYN_S: rate of inbreeding (true pedigree) not higher in 1985-1995 than 2010-2020 despite higher alpha before 2000; in SYN_S F is dominated by the hidden history and drift. Reported, not tuned.
- T14 SYN_S: D+E share did not decrease (few screened animals; grade E exclusion has little leverage).
- T15 SYN_S: corr(EBV, TBV) 0.22 below mean reported accuracy (the reliability approximation over-states accuracy in a small, highly inbred breed).

## Deviations from the plan (and why)
1. **Neutral loci 200 -> 2000.** With 200 loci, SYN_S failed T12/T13 by 0.01 to 0.03 (population-mean realised IBD is noisy in a small inbred breed). With 1000 loci the v1 candidate still failed the T13 intercept for SYN_S (0.018); with 2000 it passes on every seed. This changes the precision of the ground-truth measurement, not the model. Alleles stored as uint16 (founder allele ids < 1,200) and the buffer is trimmed at compaction; peak memory about 4 GB.
2. **Litter-size reference F (replaces a first attempt with fixed per-breed values).** Published litter sizes are observed means that include the breed's typical inbreeding, so the configured mean now applies at the running mean dam F of registry-era litters (frozen at the end of history for P8). Dams more inbred than that have smaller litters (-10 x dF puppies, chu-2019). A fixed per-breed value tuned on one history failed on the next (SYN_S dam F varies by +/- 0.05 between histories). Consequence: **T01 is now a consistency check by construction, not independent evidence**; the datasheet and paper must say so.
3. **Tiny config runs to 2026** (plan: 1995) because every calibration target uses the 2016-2025 cohorts; it still runs in about 2 s. `configs/calibration/targets_tiny.yaml` is a relaxed copy used by CI and tests.
4. **Target T18 added** (report only): risk-allele frequencies 1980 vs 2026, needed for figure 8 and for P8.
5. **T10 uses true pedigree F** (not recorded F), which avoids the artefact of recorded pedigrees deepening after 1980.
6. Per-breed calibration grids run single-breed simulations; the combined v1 run uses a different random stream, so per-seed grid values are draws from the same distribution, not identical runs.
7. mypy: `calibration.*` and `experiments.*` relax four pandas-stubs error codes (`union-attr, index, call-overload, arg-type`); strict typing stays on for `pedigree`, `rules`, `matching`.

## Open questions for Tea
- SYN_M Ne is in the upper part of its band (182 with seed 1). If you prefer a safer centre, beta 0.7 gives mean Ne about 110; I kept 0.65 because it passed v1 and 3 of 4 sensitivity seeds and moving it now would mean re-freezing v1.
- SYN_S is far more inbred (F about 0.43) than the published genomic median. That is consistent with its archetype Ne of 25 to 50 over a long history but should be stated on the poster.

## HUMAN tasks waiting
- Look at figure 4 (`reports/validation/20261011-default-s42/figures/fig4_recorded_vs_true_f.png`).
