# Experiment E10_robustness

In-silico results on synthetic populations. Means with 95% t-intervals over replicates; generation g averages the birth cohorts of (g - 0.5, g + 0.5] generations after 2026 (4.5 years per generation).

## Rates per generation by window (early: generations 0 to 5, late: 5 to 10)

dF from realised IBD of birth cohorts, dC from realised coancestry of living animals (neutral loci); Ne = 1/(2 rate); nan Ne = non-positive rate.

| breed | strategy | adoption | R_delta_f_early | R_delta_f_late | R_ne_f_early | R_ne_f_late | R_delta_c_early | R_delta_c_late |
|---|---|---|---|---|---|---|---|---|
| SYN_M | S3q-gain010-c050 | 0.25 | 0.0491 (0.0366 to 0.0616) | 0.175 (0.158 to 0.193) | 1.54e+03 (958 to 2.13e+03) | 297 (270 to 324) | -0.0893 (-0.0958 to -0.0828) | 0.154 (0.141 to 0.168) |
| SYN_M | S3q-gain010-c050 | 0.5 | 0.0579 (0.0463 to 0.0695) | 0.133 (0.123 to 0.144) | 1.57e+03 (233 to 2.91e+03) | 386 (353 to 420) | -0.0909 (-0.0974 to -0.0845) | 0.118 (0.11 to 0.126) |
| SYN_M | S3q-gain010-c050 | 0.75 | 0.114 (0.107 to 0.122) | 0.128 (0.118 to 0.138) | 446 (415 to 476) | 402 (368 to 436) | -0.041 (-0.0489 to -0.033) | 0.12 (0.114 to 0.126) |

Rates are in % per generation.

## SYN_M: generation 10

| strategy | adoption | Realised inbreeding (IBD, truth) | Recorded pedigree COI | Ne from realised IBD (truth) | Gene diversity (recorded pedigree) | Neutral heterozygosity vs 2026 (truth) | Mean true HD breeding value (lower is better) | Offspring from top 20% of sires | Share of eligible males used | Mean litter size |
|---|---|---|---|---|---|---|---|---|---|---|
| S3q-gain010-c050 | 0.25 | 0.131 (0.13 to 0.132) | 0.0432 (0.0426 to 0.0439) | 453 (418 to 489) | 0.954 (0.953 to 0.954) | 0.998 (0.997 to 0.998) | 0.147 (0.106 to 0.189) | 0.503 (0.494 to 0.512) | 0.134 (0.131 to 0.137) | 5.56 (5.5 to 5.62) |
| S3q-gain010-c050 | 0.5 | 0.129 (0.128 to 0.129) | 0.0403 (0.0398 to 0.0409) | 527 (500 to 555) | 0.956 (0.955 to 0.957) | 1 (0.999 to 1) | -0.164 (-0.205 to -0.123) | 0.486 (0.474 to 0.498) | 0.136 (0.131 to 0.14) | 5.63 (5.56 to 5.7) |
| S3q-gain010-c050 | 0.75 | 0.129 (0.128 to 0.129) | 0.0393 (0.0388 to 0.0398) | 406 (393 to 419) | 0.955 (0.955 to 0.956) | 0.998 (0.997 to 0.998) | -0.493 (-0.536 to -0.45) | 0.501 (0.489 to 0.512) | 0.13 (0.126 to 0.133) | 5.6 (5.52 to 5.68) |

