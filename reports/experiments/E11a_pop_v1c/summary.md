# Experiment E11a_pop_v1c

In-silico results on synthetic populations. Means with 95% t-intervals over replicates; generation g averages the birth cohorts of (g - 0.5, g + 0.5] generations after 2026 (4.5 years per generation).

## Rates per generation by window (early: generations 0 to 5, late: 5 to 10)

dF from realised IBD of birth cohorts, dC from realised coancestry of living animals (neutral loci); Ne = 1/(2 rate); nan Ne = non-positive rate.

| breed | strategy | adoption | R_delta_f_early | R_delta_f_late | R_ne_f_early | R_ne_f_late | R_delta_c_early | R_delta_c_late |
|---|---|---|---|---|---|---|---|---|
| SYN_M | S1 | 1 | 0.415 (0.347 to 0.484) | 0.545 (0.463 to 0.626) | 126 (105 to 147) | 95 (82.4 to 108) | 0.384 (0.337 to 0.432) | 0.53 (0.446 to 0.613) |
| SYN_M | S3 | 1 | 0.533 (0.426 to 0.64) | 0.747 (0.6 to 0.894) | 103 (74.4 to 132) | 73.9 (52.2 to 95.6) | 0.302 (0.193 to 0.411) | 0.623 (0.5 to 0.747) |
| SYN_M | S3q | 1 | 0.223 (0.204 to 0.242) | 0.297 (0.257 to 0.337) | 227 (207 to 248) | 174 (150 to 198) | 0.0802 (0.0676 to 0.0928) | 0.266 (0.224 to 0.308) |
| SYN_M | S3q-gain010-c050 | 1 | 0.207 (0.192 to 0.223) | 0.252 (0.233 to 0.27) | 243 (225 to 261) | 200 (187 to 214) | 0.212 (0.195 to 0.229) | 0.271 (0.246 to 0.295) |
| SYN_S | S1 | 1 | 1.34 (1.01 to 1.66) | 1.44 (1.15 to 1.73) | 41.3 (31.8 to 50.8) | 37 (30.2 to 43.8) | 1.16 (0.919 to 1.4) | 1.43 (1.17 to 1.68) |
| SYN_S | S3 | 1 | 1.66 (1.35 to 1.97) | 2.42 (2.02 to 2.82) | 32.1 (25.9 to 38.4) | 21.9 (17.7 to 26.1) | 0.916 (0.704 to 1.13) | 2.56 (2.13 to 2.98) |
| SYN_S | S3q | 1 | 0.895 (0.754 to 1.04) | 1.14 (1.04 to 1.24) | 58.3 (49.5 to 67) | 44.5 (40.6 to 48.4) | 0.572 (0.495 to 0.649) | 1.19 (1.07 to 1.31) |
| SYN_S | S3q-gain010-c050 | 1 | 0.942 (0.769 to 1.12) | 0.87 (0.719 to 1.02) | 55.5 (47.7 to 63.3) | 62.5 (45.6 to 79.5) | 0.662 (0.579 to 0.746) | 0.891 (0.749 to 1.03) |

Rates are in % per generation.

## SYN_M: generation 10

| strategy | adoption | Realised inbreeding (IBD, truth) | Recorded pedigree COI | Ne from realised IBD (truth) | Gene diversity (recorded pedigree) | Neutral heterozygosity vs 2026 (truth) | Mean true HD breeding value (lower is better) | Offspring from top 20% of sires | Share of eligible males used | Mean litter size |
|---|---|---|---|---|---|---|---|---|---|---|
| S1 | 1 | 0.18 (0.175 to 0.185) | 0.0886 (0.0837 to 0.0935) | 105 (89.5 to 120) | 0.912 (0.907 to 0.917) | 0.957 (0.951 to 0.962) | -0.688 (-0.763 to -0.613) | 0.498 (0.481 to 0.515) | 0.144 (0.139 to 0.149) | 5.07 (4.96 to 5.18) |
| S3 | 1 | 0.178 (0.172 to 0.184) | 0.028 (0.0249 to 0.031) | 82 (74.6 to 89.3) | 0.959 (0.957 to 0.961) | 0.957 (0.953 to 0.962) | -0.856 (-0.945 to -0.767) | 0.557 (0.51 to 0.604) | 0.0564 (0.0462 to 0.0665) | 5.25 (5.13 to 5.36) |
| S3q | 1 | 0.152 (0.15 to 0.154) | 0.039 (0.0378 to 0.0403) | 199 (175 to 224) | 0.955 (0.953 to 0.956) | 0.983 (0.981 to 0.985) | -0.726 (-0.774 to -0.678) | 0.434 (0.425 to 0.443) | 0.154 (0.15 to 0.157) | 5.38 (5.25 to 5.51) |
| S3q-gain010-c050 | 1 | 0.153 (0.151 to 0.154) | 0.0594 (0.0578 to 0.0609) | 209 (197 to 221) | 0.932 (0.931 to 0.934) | 0.977 (0.976 to 0.978) | -1.48 (-1.54 to -1.42) | 0.536 (0.516 to 0.556) | 0.106 (0.0991 to 0.114) | 5.3 (5.22 to 5.37) |

### SYN_M: paired differences vs S1 (same replicate seeds)

| strategy | generation | metric | difference (95% CI) | n |
|---|---|---|---|---|
| S3 | 5 | M1_recorded_F | -0.0395 (-0.0445 to -0.0345) | 10 |
| S3q | 5 | M1_recorded_F | -0.0298 (-0.0328 to -0.0268) | 10 |
| S3q-gain010-c050 | 5 | M1_recorded_F | -0.018 (-0.0207 to -0.0153) | 10 |
| S3 | 10 | M1_recorded_F | -0.0606 (-0.067 to -0.0542) | 10 |
| S3q | 10 | M1_recorded_F | -0.0496 (-0.0543 to -0.0448) | 10 |
| S3q-gain010-c050 | 10 | M1_recorded_F | -0.0292 (-0.0338 to -0.0246) | 10 |
| S3 | 5 | M2_realised_ibd | -0.0117 (-0.0153 to -0.00807) | 10 |
| S3q | 5 | M2_realised_ibd | -0.0177 (-0.0206 to -0.0148) | 10 |
| S3q-gain010-c050 | 5 | M2_realised_ibd | -0.0155 (-0.0184 to -0.0126) | 10 |
| S3 | 10 | M2_realised_ibd | -0.0021 (-0.00802 to 0.00382) | 10 |
| S3q | 10 | M2_realised_ibd | -0.0277 (-0.0334 to -0.022) | 10 |
| S3q-gain010-c050 | 10 | M2_realised_ibd | -0.0275 (-0.0328 to -0.0221) | 10 |
| S3 | 10 | M3_ne | -23 (-39.4 to -6.61) | 10 |
| S3q | 10 | M3_ne | 94.4 (60.9 to 128) | 10 |
| S3q-gain010-c050 | 10 | M3_ne | 104 (82 to 127) | 10 |
| S3 | 5 | M5_he_relative | 0.00451 (0.000487 to 0.00854) | 10 |
| S3q | 5 | M5_he_relative | 0.0143 (0.0117 to 0.0168) | 10 |
| S3q-gain010-c050 | 5 | M5_he_relative | 0.00825 (0.00596 to 0.0105) | 10 |
| S3 | 10 | M5_he_relative | 0.000423 (-0.00582 to 0.00666) | 10 |
| S3q | 10 | M5_he_relative | 0.0261 (0.0198 to 0.0325) | 10 |
| S3q-gain010-c050 | 10 | M5_he_relative | 0.0201 (0.0142 to 0.026) | 10 |

## SYN_S: generation 10

| strategy | adoption | Realised inbreeding (IBD, truth) | Recorded pedigree COI | Ne from realised IBD (truth) | Gene diversity (recorded pedigree) | Neutral heterozygosity vs 2026 (truth) | Mean true HD breeding value (lower is better) | Offspring from top 20% of sires | Share of eligible males used | Mean litter size |
|---|---|---|---|---|---|---|---|---|---|---|
| S1 | 1 | 0.447 (0.436 to 0.458) | 0.204 (0.189 to 0.218) | 36.8 (31.5 to 42.1) | 0.794 (0.781 to 0.808) | 0.883 (0.869 to 0.897) | 0.12 (-0.00217 to 0.242) | 0.561 (0.525 to 0.597) | 0.142 (0.133 to 0.15) | 3.1 (2.88 to 3.32) |
| S3 | 1 | 0.461 (0.449 to 0.472) | 0.0784 (0.0651 to 0.0916) | 24 (20.1 to 28) | 0.894 (0.882 to 0.906) | 0.848 (0.828 to 0.868) | 0.117 (0.00864 to 0.226) | 0.527 (0.457 to 0.598) | 0.142 (0.118 to 0.167) | 2.9 (2.7 to 3.1) |
| S3q | 1 | 0.418 (0.415 to 0.422) | 0.101 (0.0957 to 0.106) | 47.6 (44.1 to 51.1) | 0.884 (0.879 to 0.889) | 0.919 (0.913 to 0.925) | 0.125 (-0.00247 to 0.253) | 0.424 (0.414 to 0.434) | 0.179 (0.166 to 0.192) | 3.23 (3.09 to 3.38) |
| S3q-gain010-c050 | 1 | 0.412 (0.408 to 0.417) | 0.138 (0.124 to 0.151) | 56.1 (50.1 to 62) | 0.851 (0.839 to 0.863) | 0.926 (0.919 to 0.933) | -0.369 (-0.486 to -0.253) | 0.481 (0.453 to 0.509) | 0.149 (0.135 to 0.162) | 3.31 (3.17 to 3.45) |

### SYN_S: paired differences vs S1 (same replicate seeds)

| strategy | generation | metric | difference (95% CI) | n |
|---|---|---|---|---|
| S3 | 5 | M1_recorded_F | -0.082 (-0.105 to -0.0592) | 10 |
| S3q | 5 | M1_recorded_F | -0.0603 (-0.0726 to -0.0479) | 10 |
| S3q-gain010-c050 | 5 | M1_recorded_F | -0.0359 (-0.0462 to -0.0257) | 10 |
| S3 | 10 | M1_recorded_F | -0.125 (-0.146 to -0.105) | 10 |
| S3q | 10 | M1_recorded_F | -0.103 (-0.119 to -0.0868) | 10 |
| S3q-gain010-c050 | 10 | M1_recorded_F | -0.0663 (-0.0877 to -0.0448) | 10 |
| S3 | 5 | M2_realised_ibd | -0.0145 (-0.0223 to -0.00672) | 10 |
| S3q | 5 | M2_realised_ibd | -0.0233 (-0.031 to -0.0157) | 10 |
| S3q-gain010-c050 | 5 | M2_realised_ibd | -0.0204 (-0.0282 to -0.0126) | 10 |
| S3 | 10 | M2_realised_ibd | 0.0138 (0.00298 to 0.0246) | 10 |
| S3q | 10 | M2_realised_ibd | -0.0286 (-0.0377 to -0.0196) | 10 |
| S3q-gain010-c050 | 10 | M2_realised_ibd | -0.0345 (-0.0474 to -0.0215) | 10 |
| S3 | 10 | M3_ne | -12.8 (-17.7 to -7.82) | 10 |
| S3q | 10 | M3_ne | 10.8 (6.96 to 14.6) | 10 |
| S3q-gain010-c050 | 10 | M3_ne | 19.3 (9.91 to 28.6) | 10 |
| S3 | 5 | M5_he_relative | 0.00873 (-0.0031 to 0.0206) | 10 |
| S3q | 5 | M5_he_relative | 0.026 (0.0156 to 0.0365) | 10 |
| S3q-gain010-c050 | 5 | M5_he_relative | 0.0212 (0.00931 to 0.033) | 10 |
| S3 | 10 | M5_he_relative | -0.0349 (-0.0536 to -0.0162) | 10 |
| S3q | 10 | M5_he_relative | 0.0362 (0.0252 to 0.0472) | 10 |
| S3q-gain010-c050 | 10 | M5_he_relative | 0.0432 (0.0261 to 0.0604) | 10 |

