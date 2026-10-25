# Experiment E11d_s2_reference

In-silico results on synthetic populations. Means with 95% t-intervals over replicates; generation g averages the birth cohorts of (g - 0.5, g + 0.5] generations after 2026 (4.5 years per generation).

## Rates per generation by window (early: generations 0 to 5, late: 5 to 10)

dF from realised IBD of birth cohorts, dC from realised coancestry of living animals (neutral loci); Ne = 1/(2 rate); nan Ne = non-positive rate.

| breed | strategy | adoption | R_delta_f_early | R_delta_f_late | R_ne_f_early | R_ne_f_late | R_delta_c_early | R_delta_c_late |
|---|---|---|---|---|---|---|---|---|
| SYN_M | S2 | 1 | 0.0475 (0.0332 to 0.0617) | 0.235 (0.218 to 0.253) | 1.26e+03 (720 to 1.8e+03) | 218 (201 to 235) | -0.0318 (-0.0433 to -0.0203) | 0.22 (0.201 to 0.238) |

Rates are in % per generation.

## SYN_M: generation 10

| strategy | adoption | Realised inbreeding (IBD, truth) | Recorded pedigree COI | Ne from realised IBD (truth) | Gene diversity (recorded pedigree) | Neutral heterozygosity vs 2026 (truth) | Mean true HD breeding value (lower is better) | Offspring from top 20% of sires | Share of eligible males used | Mean litter size |
|---|---|---|---|---|---|---|---|---|---|---|
| S2 | 1 | 0.137 (0.136 to 0.137) | 0.0511 (0.0501 to 0.052) | 339 (315 to 363) | 0.946 (0.945 to 0.947) | 0.992 (0.991 to 0.993) | 0.4 (0.358 to 0.441) | 0.502 (0.497 to 0.507) | 0.136 (0.134 to 0.137) | 5.53 (5.46 to 5.6) |

### SYN_M: paired differences vs S3 (same replicate seeds)

| strategy | generation | metric | difference (95% CI) | n |
|---|---|---|---|---|
| S2 | 5 | M1_recorded_F | n/a | 0 |
| S2 | 10 | M1_recorded_F | n/a | 0 |
| S2 | 5 | M2_realised_ibd | n/a | 0 |
| S2 | 10 | M2_realised_ibd | n/a | 0 |
| S2 | 10 | M3_ne | n/a | 0 |
| S2 | 5 | M5_he_relative | n/a | 0 |
| S2 | 10 | M5_he_relative | n/a | 0 |

