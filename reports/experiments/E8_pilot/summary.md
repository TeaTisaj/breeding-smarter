# Experiment E8_pilot

In-silico results on synthetic populations. Means with 95% t-intervals over replicates; generation g averages the birth cohorts of (g - 0.5, g + 0.5] generations after 2026 (4.5 years per generation).

## Rates per generation by window (early: generations 0 to 5, late: 5 to 10)

dF from realised IBD of birth cohorts, dC from realised coancestry of living animals (neutral loci); Ne = 1/(2 rate); nan Ne = non-positive rate.

| breed | strategy | adoption | R_delta_f_early | R_delta_f_late | R_ne_f_early | R_ne_f_late | R_delta_c_early | R_delta_c_late |
|---|---|---|---|---|---|---|---|---|
| SYN_M | S3q-gain010 | 1 | 0.166 (0.0875 to 0.244) | 0.169 (0.0902 to 0.247) | 310 (147 to 473) | 303 (176 to 430) | 0.00729 (-0.024 to 0.0386) | 0.189 (0.134 to 0.244) |
| SYN_M | S3q-gain010-c050 | 1 | 0.14 (0.118 to 0.163) | 0.176 (0.0971 to 0.254) | 358 (299 to 417) | 292 (149 to 435) | -0.00688 (-0.0196 to 0.00581) | 0.175 (0.102 to 0.248) |
| SYN_M | S3q-gain010-c075 | 1 | 0.151 (0.0998 to 0.203) | 0.168 (0.099 to 0.238) | 334 (229 to 440) | 303 (171 to 434) | -0.00542 (-0.055 to 0.0441) | 0.168 (0.131 to 0.205) |
| SYN_M | S3q-gain010-c100 | 1 | 0.155 (0.082 to 0.228) | 0.198 (0.178 to 0.218) | 330 (182 to 477) | 253 (227 to 280) | 0.00807 (-0.028 to 0.0441) | 0.186 (0.151 to 0.222) |

Rates are in % per generation.

## SYN_M: generation 10

| strategy | adoption | Realised inbreeding (IBD, truth) | Recorded pedigree COI | Ne from realised IBD (truth) | Gene diversity (recorded pedigree) | Neutral heterozygosity vs 2026 (truth) | Mean true HD breeding value (lower is better) | Offspring from top 20% of sires | Share of eligible males used | Mean litter size |
|---|---|---|---|---|---|---|---|---|---|---|
| S3q-gain010 | 1 | 0.131 (0.126 to 0.135) | 0.0421 (0.0379 to 0.0462) | 290 (230 to 349) | 0.95 (0.947 to 0.954) | 0.992 (0.988 to 0.997) | -0.809 (-0.985 to -0.632) | 0.541 (0.443 to 0.639) | 0.103 (0.0657 to 0.14) | 5.61 (5.27 to 5.94) |
| S3q-gain010-c050 | 1 | 0.13 (0.128 to 0.133) | 0.0411 (0.0367 to 0.0456) | 306 (233 to 379) | 0.952 (0.949 to 0.954) | 0.993 (0.99 to 0.996) | -0.757 (-0.892 to -0.623) | 0.522 (0.495 to 0.548) | 0.103 (0.0861 to 0.119) | 5.63 (4.86 to 6.39) |
| S3q-gain010-c075 | 1 | 0.13 (0.127 to 0.134) | 0.0419 (0.0396 to 0.0442) | 313 (238 to 388) | 0.951 (0.949 to 0.954) | 0.994 (0.992 to 0.995) | -0.791 (-0.834 to -0.748) | 0.523 (0.482 to 0.564) | 0.102 (0.0564 to 0.148) | 5.59 (5.3 to 5.88) |
| S3q-gain010-c100 | 1 | 0.132 (0.13 to 0.134) | 0.043 (0.0419 to 0.0441) | 282 (227 to 337) | 0.95 (0.949 to 0.952) | 0.992 (0.991 to 0.994) | -0.809 (-0.883 to -0.734) | 0.529 (0.513 to 0.545) | 0.0976 (0.0909 to 0.104) | 5.69 (5.32 to 6.06) |

### SYN_M: paired differences vs S3 (same replicate seeds)

| strategy | generation | metric | difference (95% CI) | n |
|---|---|---|---|---|
| S3q-gain010 | 5 | M1_recorded_F | n/a | 0 |
| S3q-gain010-c050 | 5 | M1_recorded_F | n/a | 0 |
| S3q-gain010-c075 | 5 | M1_recorded_F | n/a | 0 |
| S3q-gain010-c100 | 5 | M1_recorded_F | n/a | 0 |
| S3q-gain010 | 10 | M1_recorded_F | n/a | 0 |
| S3q-gain010-c050 | 10 | M1_recorded_F | n/a | 0 |
| S3q-gain010-c075 | 10 | M1_recorded_F | n/a | 0 |
| S3q-gain010-c100 | 10 | M1_recorded_F | n/a | 0 |
| S3q-gain010 | 5 | M2_realised_ibd | n/a | 0 |
| S3q-gain010-c050 | 5 | M2_realised_ibd | n/a | 0 |
| S3q-gain010-c075 | 5 | M2_realised_ibd | n/a | 0 |
| S3q-gain010-c100 | 5 | M2_realised_ibd | n/a | 0 |
| S3q-gain010 | 10 | M2_realised_ibd | n/a | 0 |
| S3q-gain010-c050 | 10 | M2_realised_ibd | n/a | 0 |
| S3q-gain010-c075 | 10 | M2_realised_ibd | n/a | 0 |
| S3q-gain010-c100 | 10 | M2_realised_ibd | n/a | 0 |
| S3q-gain010 | 10 | M3_ne | n/a | 0 |
| S3q-gain010-c050 | 10 | M3_ne | n/a | 0 |
| S3q-gain010-c075 | 10 | M3_ne | n/a | 0 |
| S3q-gain010-c100 | 10 | M3_ne | n/a | 0 |
| S3q-gain010 | 5 | M5_he_relative | n/a | 0 |
| S3q-gain010-c050 | 5 | M5_he_relative | n/a | 0 |
| S3q-gain010-c075 | 5 | M5_he_relative | n/a | 0 |
| S3q-gain010-c100 | 5 | M5_he_relative | n/a | 0 |
| S3q-gain010 | 10 | M5_he_relative | n/a | 0 |
| S3q-gain010-c050 | 10 | M5_he_relative | n/a | 0 |
| S3q-gain010-c075 | 10 | M5_he_relative | n/a | 0 |
| S3q-gain010-c100 | 10 | M5_he_relative | n/a | 0 |

