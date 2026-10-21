# Experiment E8_health_gain_quotas

In-silico results on synthetic populations. Means with 95% t-intervals over replicates; generation g averages the birth cohorts of (g - 0.5, g + 0.5] generations after 2026 (4.5 years per generation).

## Rates per generation by window (early: generations 0 to 5, late: 5 to 10)

dF from realised IBD of birth cohorts, dC from realised coancestry of living animals (neutral loci); Ne = 1/(2 rate); nan Ne = non-positive rate.

| breed | strategy | adoption | R_delta_f_early | R_delta_f_late | R_ne_f_early | R_ne_f_late | R_delta_c_early | R_delta_c_late |
|---|---|---|---|---|---|---|---|---|
| SYN_M | S1 | 1 | 0.124 (0.0942 to 0.154) | 0.282 (0.234 to 0.331) | 646 (278 to 1.01e+03) | 206 (159 to 254) | -0.00529 (-0.0259 to 0.0153) | 0.262 (0.226 to 0.297) |
| SYN_M | S3q | 1 | 0.126 (0.117 to 0.135) | 0.162 (0.148 to 0.176) | 408 (377 to 438) | 320 (290 to 349) | -0.118 (-0.123 to -0.114) | 0.133 (0.121 to 0.144) |
| SYN_M | S3q-c050 | 1 | 0.131 (0.122 to 0.14) | 0.169 (0.156 to 0.182) | 390 (362 to 417) | 304 (279 to 329) | -0.12 (-0.124 to -0.116) | 0.134 (0.124 to 0.143) |
| SYN_M | S3q-gain010 | 1 | 0.154 (0.14 to 0.167) | 0.187 (0.168 to 0.205) | 337 (306 to 369) | 278 (253 to 304) | 0.0199 (0.00951 to 0.0302) | 0.183 (0.166 to 0.2) |
| SYN_M | S3q-gain010-c050 | 1 | 0.163 (0.154 to 0.172) | 0.184 (0.17 to 0.198) | 311 (293 to 330) | 278 (258 to 298) | 0.0156 (0.00826 to 0.0229) | 0.19 (0.176 to 0.203) |
| SYN_S | S1 | 1 | 1.47 (1.24 to 1.7) | 1.6 (1.28 to 1.92) | 35.3 (30.5 to 40.2) | 33.5 (27 to 39.9) | 1.41 (1.2 to 1.62) | 1.5 (1.27 to 1.72) |
| SYN_S | S3q | 1 | 0.89 (0.788 to 0.991) | 0.961 (0.769 to 1.15) | 57.4 (51 to 63.9) | 55.6 (45.2 to 66) | 0.432 (0.373 to 0.492) | 0.925 (0.723 to 1.13) |
| SYN_S | S3q-gain025 | 1 | 0.779 (0.687 to 0.871) | 0.702 (0.549 to 0.854) | 66 (57.3 to 74.6) | 77.5 (60.5 to 94.5) | 0.621 (0.547 to 0.694) | 0.711 (0.613 to 0.808) |

Rates are in % per generation.

## SYN_M: generation 10

| strategy | adoption | Realised inbreeding (IBD, truth) | Recorded pedigree COI | Ne from realised IBD (truth) | Gene diversity (recorded pedigree) | Neutral heterozygosity vs 2026 (truth) | Mean true HD breeding value (lower is better) | Offspring from top 20% of sires | Share of eligible males used | Mean litter size |
|---|---|---|---|---|---|---|---|---|---|---|
| S1 | 1 | 0.142 (0.141 to 0.144) | 0.0569 (0.0551 to 0.0587) | 239 (212 to 266) | 0.943 (0.941 to 0.944) | 0.988 (0.987 to 0.99) | 0.391 (0.357 to 0.425) | 0.503 (0.492 to 0.513) | 0.133 (0.13 to 0.137) | 5.56 (5.48 to 5.65) |
| S3q | 1 | 0.128 (0.127 to 0.128) | 0.0277 (0.0272 to 0.0283) | 385 (358 to 411) | 0.968 (0.967 to 0.968) | 1 (1 to 1) | 0.382 (0.348 to 0.417) | 0.432 (0.428 to 0.437) | 0.151 (0.149 to 0.153) | 5.7 (5.63 to 5.78) |
| S3q-c050 | 1 | 0.128 (0.127 to 0.129) | 0.0281 (0.0277 to 0.0285) | 377 (357 to 397) | 0.967 (0.967 to 0.968) | 1 (1 to 1) | 0.393 (0.366 to 0.42) | 0.434 (0.43 to 0.438) | 0.155 (0.151 to 0.158) | 5.55 (5.45 to 5.64) |
| S3q-gain010 | 1 | 0.131 (0.131 to 0.132) | 0.0425 (0.0418 to 0.0433) | 300 (283 to 317) | 0.95 (0.949 to 0.951) | 0.992 (0.991 to 0.993) | -0.82 (-0.87 to -0.771) | 0.522 (0.511 to 0.533) | 0.107 (0.103 to 0.111) | 5.61 (5.5 to 5.71) |
| S3q-gain010-c050 | 1 | 0.131 (0.131 to 0.132) | 0.0422 (0.0415 to 0.0429) | 284 (273 to 295) | 0.95 (0.949 to 0.951) | 0.992 (0.991 to 0.993) | -0.79 (-0.826 to -0.753) | 0.521 (0.507 to 0.536) | 0.107 (0.102 to 0.112) | 5.66 (5.59 to 5.73) |

### SYN_M: paired differences vs S1 (same replicate seeds)

| strategy | generation | metric | difference (95% CI) | n |
|---|---|---|---|---|
| S3q | 5 | M1_recorded_F | -0.0175 (-0.019 to -0.016) | 20 |
| S3q-c050 | 5 | M1_recorded_F | -0.0175 (-0.0187 to -0.0163) | 20 |
| S3q-gain010 | 5 | M1_recorded_F | -0.0104 (-0.0116 to -0.00913) | 20 |
| S3q-gain010-c050 | 5 | M1_recorded_F | -0.0105 (-0.0119 to -0.00924) | 20 |
| S3q | 10 | M1_recorded_F | -0.0292 (-0.031 to -0.0274) | 20 |
| S3q-c050 | 10 | M1_recorded_F | -0.0288 (-0.0307 to -0.027) | 20 |
| S3q-gain010 | 10 | M1_recorded_F | -0.0144 (-0.0164 to -0.0124) | 20 |
| S3q-gain010-c050 | 10 | M1_recorded_F | -0.0147 (-0.0167 to -0.0128) | 20 |
| S3q | 5 | M2_realised_ibd | -0.00945 (-0.0107 to -0.00825) | 20 |
| S3q-c050 | 5 | M2_realised_ibd | -0.0098 (-0.011 to -0.00864) | 20 |
| S3q-gain010 | 5 | M2_realised_ibd | -0.00679 (-0.00795 to -0.00562) | 20 |
| S3q-gain010-c050 | 5 | M2_realised_ibd | -0.00705 (-0.00826 to -0.00585) | 20 |
| S3q | 10 | M2_realised_ibd | -0.0145 (-0.0162 to -0.0128) | 20 |
| S3q-c050 | 10 | M2_realised_ibd | -0.0144 (-0.0161 to -0.0126) | 20 |
| S3q-gain010 | 10 | M2_realised_ibd | -0.011 (-0.0129 to -0.00908) | 20 |
| S3q-gain010-c050 | 10 | M2_realised_ibd | -0.0109 (-0.0127 to -0.0091) | 20 |
| S3q | 10 | M3_ne | 146 (106 to 186) | 20 |
| S3q-c050 | 10 | M3_ne | 138 (102 to 173) | 20 |
| S3q-gain010 | 10 | M3_ne | 61.1 (24.5 to 97.6) | 20 |
| S3q-gain010-c050 | 10 | M3_ne | 45.2 (12.9 to 77.4) | 20 |
| S3q | 5 | M5_he_relative | 0.00673 (0.00577 to 0.00769) | 20 |
| S3q-c050 | 5 | M5_he_relative | 0.00675 (0.0058 to 0.0077) | 20 |
| S3q-gain010 | 5 | M5_he_relative | 0.000287 (-0.000659 to 0.00123) | 20 |
| S3q-gain010-c050 | 5 | M5_he_relative | 0.000435 (-0.000632 to 0.0015) | 20 |
| S3q | 10 | M5_he_relative | 0.0129 (0.0113 to 0.0146) | 20 |
| S3q-c050 | 10 | M5_he_relative | 0.0129 (0.0112 to 0.0145) | 20 |
| S3q-gain010 | 10 | M5_he_relative | 0.0041 (0.00228 to 0.00592) | 20 |
| S3q-gain010-c050 | 10 | M5_he_relative | 0.00389 (0.00215 to 0.00563) | 20 |

## SYN_S: generation 10

| strategy | adoption | Realised inbreeding (IBD, truth) | Recorded pedigree COI | Ne from realised IBD (truth) | Gene diversity (recorded pedigree) | Neutral heterozygosity vs 2026 (truth) | Mean true HD breeding value (lower is better) | Offspring from top 20% of sires | Share of eligible males used | Mean litter size |
|---|---|---|---|---|---|---|---|---|---|---|
| S1 | 1 | 0.511 (0.501 to 0.521) | 0.185 (0.167 to 0.203) | 34.9 (29.1 to 40.7) | 0.814 (0.798 to 0.829) | 0.865 (0.851 to 0.879) | 0.0362 (-0.0978 to 0.17) | 0.589 (0.567 to 0.611) | 0.144 (0.136 to 0.152) | 3 (2.87 to 3.13) |
| S3q | 1 | 0.462 (0.455 to 0.47) | 0.0792 (0.07 to 0.0884) | 59.4 (49.5 to 69.4) | 0.906 (0.897 to 0.914) | 0.935 (0.925 to 0.946) | 0.112 (-0.0261 to 0.25) | 0.436 (0.421 to 0.451) | 0.167 (0.156 to 0.177) | 3.39 (3.31 to 3.47) |
| S3q-gain025 | 1 | 0.461 (0.457 to 0.466) | 0.12 (0.113 to 0.127) | 67.3 (59.1 to 75.5) | 0.868 (0.861 to 0.876) | 0.934 (0.928 to 0.94) | -0.617 (-0.717 to -0.517) | 0.509 (0.467 to 0.551) | 0.125 (0.113 to 0.137) | 3.41 (3.17 to 3.65) |

### SYN_S: paired differences vs S1 (same replicate seeds)

| strategy | generation | metric | difference (95% CI) | n |
|---|---|---|---|---|
| S3q | 5 | M1_recorded_F | -0.0624 (-0.0767 to -0.0481) | 10 |
| S3q-gain025 | 5 | M1_recorded_F | -0.036 (-0.0466 to -0.0254) | 10 |
| S3q | 10 | M1_recorded_F | -0.106 (-0.129 to -0.083) | 10 |
| S3q-gain025 | 10 | M1_recorded_F | -0.0652 (-0.0811 to -0.0492) | 10 |
| S3q | 5 | M2_realised_ibd | -0.0347 (-0.04 to -0.0295) | 10 |
| S3q-gain025 | 5 | M2_realised_ibd | -0.0295 (-0.0359 to -0.0231) | 10 |
| S3q | 10 | M2_realised_ibd | -0.0486 (-0.0588 to -0.0383) | 10 |
| S3q-gain025 | 10 | M2_realised_ibd | -0.0495 (-0.0598 to -0.0392) | 10 |
| S3q | 10 | M3_ne | 24.5 (14 to 35.1) | 10 |
| S3q-gain025 | 10 | M3_ne | 32.4 (23.4 to 41.4) | 10 |
| S3q | 5 | M5_he_relative | 0.0463 (0.0376 to 0.0551) | 10 |
| S3q-gain025 | 5 | M5_he_relative | 0.0363 (0.0279 to 0.0447) | 10 |
| S3q | 10 | M5_he_relative | 0.0702 (0.0558 to 0.0846) | 10 |
| S3q-gain025 | 10 | M5_he_relative | 0.0693 (0.0564 to 0.0822) | 10 |

