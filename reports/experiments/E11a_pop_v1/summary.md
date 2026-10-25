# Experiment E11a_pop_v1

In-silico results on synthetic populations. Means with 95% t-intervals over replicates; generation g averages the birth cohorts of (g - 0.5, g + 0.5] generations after 2026 (4.5 years per generation).

## Rates per generation by window (early: generations 0 to 5, late: 5 to 10)

dF from realised IBD of birth cohorts, dC from realised coancestry of living animals (neutral loci); Ne = 1/(2 rate); nan Ne = non-positive rate.

| breed | strategy | adoption | R_delta_f_early | R_delta_f_late | R_ne_f_early | R_ne_f_late | R_delta_c_early | R_delta_c_late |
|---|---|---|---|---|---|---|---|---|
| SYN_M | S1 | 1 | 0.1 (0.0636 to 0.137) | 0.311 (0.269 to 0.353) | 1.04e+03 (-50.7 to 2.13e+03) | 165 (145 to 185) | -0.0155 (-0.0381 to 0.00718) | 0.27 (0.229 to 0.311) |
| SYN_M | S3 | 1 | 0.316 (0.283 to 0.349) | 0.313 (0.26 to 0.365) | 161 (145 to 178) | 168 (140 to 197) | -0.0269 (-0.045 to -0.00886) | 0.248 (0.207 to 0.289) |
| SYN_M | S3q | 1 | 0.125 (0.109 to 0.141) | 0.159 (0.142 to 0.176) | 412 (358 to 467) | 322 (283 to 360) | -0.116 (-0.123 to -0.109) | 0.13 (0.119 to 0.14) |
| SYN_M | S3q-gain010-c050 | 1 | 0.17 (0.162 to 0.177) | 0.192 (0.172 to 0.212) | 296 (282 to 310) | 265 (237 to 294) | 0.0249 (0.0125 to 0.0373) | 0.189 (0.17 to 0.207) |
| SYN_S | S1 | 1 | 1.53 (1.26 to 1.8) | 1.6 (1.36 to 1.84) | 34.9 (27.3 to 42.4) | 32.6 (27.2 to 38) | 1.45 (1.22 to 1.67) | 1.7 (1.45 to 1.94) |
| SYN_S | S3 | 1 | 1.64 (1.29 to 2) | 1.59 (1.23 to 1.94) | 33.1 (25.9 to 40.3) | 34.4 (26.9 to 41.9) | 0.956 (0.729 to 1.18) | 1.59 (1.1 to 2.09) |
| SYN_S | S3q | 1 | 1.01 (0.797 to 1.22) | 0.862 (0.77 to 0.953) | 53.6 (42 to 65.2) | 59.3 (52.7 to 65.8) | 0.558 (0.456 to 0.66) | 0.872 (0.771 to 0.972) |
| SYN_S | S3q-gain010-c050 | 1 | 0.758 (0.647 to 0.869) | 0.786 (0.678 to 0.894) | 68.8 (57.2 to 80.5) | 65.6 (57.1 to 74.1) | 0.578 (0.501 to 0.656) | 0.752 (0.69 to 0.814) |

Rates are in % per generation.

## SYN_M: generation 10

| strategy | adoption | Realised inbreeding (IBD, truth) | Recorded pedigree COI | Ne from realised IBD (truth) | Gene diversity (recorded pedigree) | Neutral heterozygosity vs 2026 (truth) | Mean true HD breeding value (lower is better) | Offspring from top 20% of sires | Share of eligible males used | Mean litter size |
|---|---|---|---|---|---|---|---|---|---|---|
| S1 | 1 | 0.142 (0.14 to 0.144) | 0.0574 (0.0555 to 0.0594) | 247 (212 to 281) | 0.943 (0.941 to 0.945) | 0.989 (0.986 to 0.991) | 0.362 (0.282 to 0.443) | 0.504 (0.492 to 0.516) | 0.133 (0.13 to 0.136) | 5.48 (5.37 to 5.59) |
| S3 | 1 | 0.134 (0.131 to 0.137) | 0.0228 (0.0207 to 0.0249) | 202 (176 to 228) | 0.968 (0.967 to 0.969) | 0.993 (0.991 to 0.995) | 0.103 (0.00322 to 0.202) | 0.543 (0.521 to 0.566) | 0.0595 (0.0505 to 0.0684) | 5.66 (5.52 to 5.79) |
| S3q | 1 | 0.128 (0.127 to 0.128) | 0.0284 (0.0277 to 0.0291) | 395 (367 to 422) | 0.967 (0.966 to 0.968) | 1 (1 to 1) | 0.373 (0.302 to 0.445) | 0.431 (0.425 to 0.438) | 0.151 (0.149 to 0.154) | 5.73 (5.63 to 5.84) |
| S3q-gain010-c050 | 1 | 0.132 (0.132 to 0.132) | 0.0426 (0.042 to 0.0433) | 275 (267 to 283) | 0.95 (0.949 to 0.951) | 0.992 (0.991 to 0.992) | -0.788 (-0.855 to -0.722) | 0.544 (0.522 to 0.566) | 0.0985 (0.0923 to 0.105) | 5.66 (5.55 to 5.76) |

### SYN_M: paired differences vs S1 (same replicate seeds)

| strategy | generation | metric | difference (95% CI) | n |
|---|---|---|---|---|
| S3 | 5 | M1_recorded_F | -0.0194 (-0.0211 to -0.0177) | 10 |
| S3q | 5 | M1_recorded_F | -0.016 (-0.0177 to -0.0143) | 10 |
| S3q-gain010-c050 | 5 | M1_recorded_F | -0.00933 (-0.0108 to -0.00782) | 10 |
| S3 | 10 | M1_recorded_F | -0.0346 (-0.037 to -0.0323) | 10 |
| S3q | 10 | M1_recorded_F | -0.029 (-0.0312 to -0.0268) | 10 |
| S3q-gain010-c050 | 10 | M1_recorded_F | -0.0148 (-0.0167 to -0.0129) | 10 |
| S3 | 5 | M2_realised_ibd | -0.00683 (-0.00885 to -0.00482) | 10 |
| S3q | 5 | M2_realised_ibd | -0.00841 (-0.00993 to -0.00689) | 10 |
| S3q-gain010-c050 | 5 | M2_realised_ibd | -0.00571 (-0.007 to -0.00441) | 10 |
| S3 | 10 | M2_realised_ibd | -0.00797 (-0.012 to -0.00394) | 10 |
| S3q | 10 | M2_realised_ibd | -0.0149 (-0.017 to -0.0127) | 10 |
| S3q-gain010-c050 | 10 | M2_realised_ibd | -0.0104 (-0.0123 to -0.00855) | 10 |
| S3 | 10 | M3_ne | -44.5 (-89.2 to 0.0915) | 10 |
| S3q | 10 | M3_ne | 148 (102 to 195) | 10 |
| S3q-gain010-c050 | 10 | M3_ne | 28.4 (-4.23 to 61.1) | 10 |
| S3 | 5 | M5_he_relative | 0.00351 (0.00234 to 0.00467) | 10 |
| S3q | 5 | M5_he_relative | 0.00589 (0.00489 to 0.00688) | 10 |
| S3q-gain010-c050 | 5 | M5_he_relative | -0.000531 (-0.00144 to 0.000381) | 10 |
| S3 | 10 | M5_he_relative | 0.00433 (0.000964 to 0.0077) | 10 |
| S3q | 10 | M5_he_relative | 0.0124 (0.0101 to 0.0147) | 10 |
| S3q-gain010-c050 | 10 | M5_he_relative | 0.00304 (0.000692 to 0.00539) | 10 |

## SYN_S: generation 10

| strategy | adoption | Realised inbreeding (IBD, truth) | Recorded pedigree COI | Ne from realised IBD (truth) | Gene diversity (recorded pedigree) | Neutral heterozygosity vs 2026 (truth) | Mean true HD breeding value (lower is better) | Offspring from top 20% of sires | Share of eligible males used | Mean litter size |
|---|---|---|---|---|---|---|---|---|---|---|
| S1 | 1 | 0.513 (0.502 to 0.524) | 0.183 (0.169 to 0.196) | 32.9 (26.5 to 39.4) | 0.813 (0.801 to 0.824) | 0.855 (0.839 to 0.871) | 0.188 (0.13 to 0.245) | 0.569 (0.53 to 0.609) | 0.146 (0.137 to 0.155) | 3.03 (2.9 to 3.16) |
| S3 | 1 | 0.49 (0.479 to 0.5) | 0.0622 (0.052 to 0.0724) | 33.5 (28.2 to 38.8) | 0.913 (0.905 to 0.921) | 0.884 (0.866 to 0.902) | 0.0557 (-0.0545 to 0.166) | 0.506 (0.453 to 0.558) | 0.119 (0.0993 to 0.14) | 3.31 (3.18 to 3.45) |
| S3q | 1 | 0.465 (0.46 to 0.47) | 0.0812 (0.0767 to 0.0856) | 54.8 (47.9 to 61.8) | 0.905 (0.9 to 0.911) | 0.931 (0.923 to 0.939) | -0.0474 (-0.131 to 0.0361) | 0.442 (0.43 to 0.453) | 0.168 (0.161 to 0.175) | 3.47 (3.25 to 3.69) |
| S3q-gain010-c050 | 1 | 0.461 (0.459 to 0.464) | 0.105 (0.0978 to 0.111) | 67.3 (62.3 to 72.3) | 0.885 (0.879 to 0.89) | 0.935 (0.932 to 0.939) | -0.519 (-0.608 to -0.43) | 0.518 (0.487 to 0.55) | 0.131 (0.118 to 0.144) | 3.46 (3.28 to 3.63) |

### SYN_S: paired differences vs S1 (same replicate seeds)

| strategy | generation | metric | difference (95% CI) | n |
|---|---|---|---|---|
| S3 | 5 | M1_recorded_F | -0.0799 (-0.0984 to -0.0614) | 10 |
| S3q | 5 | M1_recorded_F | -0.0626 (-0.0733 to -0.0519) | 10 |
| S3q-gain010-c050 | 5 | M1_recorded_F | -0.0439 (-0.0553 to -0.0324) | 10 |
| S3 | 10 | M1_recorded_F | -0.12 (-0.139 to -0.102) | 10 |
| S3q | 10 | M1_recorded_F | -0.102 (-0.114 to -0.0891) | 10 |
| S3q-gain010-c050 | 10 | M1_recorded_F | -0.0781 (-0.0892 to -0.067) | 10 |
| S3 | 5 | M2_realised_ibd | -0.0266 (-0.0348 to -0.0183) | 10 |
| S3q | 5 | M2_realised_ibd | -0.0328 (-0.0425 to -0.0231) | 10 |
| S3q-gain010-c050 | 5 | M2_realised_ibd | -0.0348 (-0.0424 to -0.0271) | 10 |
| S3 | 10 | M2_realised_ibd | -0.0231 (-0.0343 to -0.012) | 10 |
| S3q | 10 | M2_realised_ibd | -0.048 (-0.063 to -0.0329) | 10 |
| S3q-gain010-c050 | 10 | M2_realised_ibd | -0.0516 (-0.0618 to -0.0414) | 10 |
| S3 | 10 | M3_ne | 0.557 (-5.78 to 6.89) | 10 |
| S3q | 10 | M3_ne | 21.9 (10.1 to 33.8) | 10 |
| S3q-gain010-c050 | 10 | M3_ne | 34.4 (27.6 to 41.1) | 10 |
| S3 | 5 | M5_he_relative | 0.0238 (0.013 to 0.0346) | 10 |
| S3q | 5 | M5_he_relative | 0.0437 (0.0317 to 0.0557) | 10 |
| S3q-gain010-c050 | 5 | M5_he_relative | 0.0417 (0.0325 to 0.051) | 10 |
| S3 | 10 | M5_he_relative | 0.0291 (0.00946 to 0.0488) | 10 |
| S3q | 10 | M5_he_relative | 0.0764 (0.0539 to 0.0989) | 10 |
| S3q-gain010-c050 | 10 | M5_he_relative | 0.0807 (0.0654 to 0.096) | 10 |

