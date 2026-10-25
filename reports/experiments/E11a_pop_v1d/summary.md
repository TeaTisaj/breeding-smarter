# Experiment E11a_pop_v1d

In-silico results on synthetic populations. Means with 95% t-intervals over replicates; generation g averages the birth cohorts of (g - 0.5, g + 0.5] generations after 2026 (4.5 years per generation).

## Rates per generation by window (early: generations 0 to 5, late: 5 to 10)

dF from realised IBD of birth cohorts, dC from realised coancestry of living animals (neutral loci); Ne = 1/(2 rate); nan Ne = non-positive rate.

| breed | strategy | adoption | R_delta_f_early | R_delta_f_late | R_ne_f_early | R_ne_f_late | R_delta_c_early | R_delta_c_late |
|---|---|---|---|---|---|---|---|---|
| SYN_M | S1 | 1 | 0.213 (0.189 to 0.237) | 0.309 (0.266 to 0.352) | 240 (215 to 264) | 167 (147 to 186) | 0.252 (0.238 to 0.267) | 0.278 (0.246 to 0.31) |
| SYN_M | S3 | 1 | 0.554 (0.499 to 0.608) | 0.46 (0.375 to 0.545) | 91.9 (82.2 to 102) | 116 (93.2 to 138) | 0.275 (0.234 to 0.316) | 0.449 (0.383 to 0.514) |
| SYN_M | S3q | 1 | 0.291 (0.266 to 0.316) | 0.29 (0.265 to 0.316) | 174 (160 to 188) | 175 (158 to 191) | 0.0798 (0.0598 to 0.0998) | 0.272 (0.244 to 0.299) |
| SYN_M | S3q-gain010-c050 | 1 | 0.227 (0.206 to 0.248) | 0.254 (0.226 to 0.282) | 223 (204 to 242) | 201 (177 to 226) | 0.231 (0.207 to 0.255) | 0.252 (0.223 to 0.28) |
| SYN_S | S1 | 1 | 1.3 (1.02 to 1.58) | 1.45 (1.12 to 1.77) | 41.2 (33 to 49.4) | 38.3 (28.2 to 48.3) | 1.35 (1.19 to 1.51) | 1.51 (1.23 to 1.78) |
| SYN_S | S3 | 1 | 2.47 (2.1 to 2.83) | 2.27 (1.63 to 2.92) | 21.1 (17.8 to 24.4) | 24.8 (18.7 to 30.9) | 1.68 (1.27 to 2.08) | 2.14 (1.63 to 2.65) |
| SYN_S | S3q | 1 | 1.09 (0.954 to 1.23) | 0.958 (0.801 to 1.12) | 47.3 (40.4 to 54.2) | 55.2 (44.4 to 66) | 0.764 (0.65 to 0.878) | 0.974 (0.836 to 1.11) |
| SYN_S | S3q-gain010-c050 | 1 | 1.2 (1.11 to 1.3) | 0.841 (0.714 to 0.968) | 41.9 (38.8 to 45.1) | 62.4 (51.2 to 73.6) | 0.934 (0.846 to 1.02) | 0.83 (0.692 to 0.968) |

Rates are in % per generation.

## SYN_M: generation 10

| strategy | adoption | Realised inbreeding (IBD, truth) | Recorded pedigree COI | Ne from realised IBD (truth) | Gene diversity (recorded pedigree) | Neutral heterozygosity vs 2026 (truth) | Mean true HD breeding value (lower is better) | Offspring from top 20% of sires | Share of eligible males used | Mean litter size |
|---|---|---|---|---|---|---|---|---|---|---|
| S1 | 1 | 0.148 (0.146 to 0.15) | 0.0658 (0.0644 to 0.0673) | 196 (180 to 211) | 0.934 (0.932 to 0.935) | 0.974 (0.973 to 0.976) | 0.101 (0.0254 to 0.177) | 0.509 (0.494 to 0.525) | 0.14 (0.135 to 0.144) | 5.26 (5.16 to 5.35) |
| S3 | 1 | 0.15 (0.146 to 0.155) | 0.0255 (0.023 to 0.0281) | 104 (93.9 to 114) | 0.965 (0.964 to 0.967) | 0.966 (0.964 to 0.969) | -0.126 (-0.203 to -0.05) | 0.531 (0.508 to 0.554) | 0.0647 (0.0556 to 0.0737) | 5.21 (5.09 to 5.32) |
| S3q | 1 | 0.138 (0.137 to 0.139) | 0.0331 (0.0317 to 0.0345) | 177 (165 to 189) | 0.962 (0.96 to 0.963) | 0.983 (0.982 to 0.984) | 0.158 (0.102 to 0.214) | 0.435 (0.426 to 0.444) | 0.158 (0.152 to 0.164) | 5.34 (5.24 to 5.44) |
| S3q-gain010-c050 | 1 | 0.138 (0.136 to 0.14) | 0.0554 (0.0536 to 0.0572) | 204 (189 to 219) | 0.936 (0.934 to 0.938) | 0.977 (0.975 to 0.979) | -1.03 (-1.13 to -0.93) | 0.531 (0.517 to 0.546) | 0.0986 (0.0938 to 0.103) | 5.41 (5.28 to 5.53) |

### SYN_M: paired differences vs S1 (same replicate seeds)

| strategy | generation | metric | difference (95% CI) | n |
|---|---|---|---|---|
| S3 | 5 | M1_recorded_F | -0.0303 (-0.0321 to -0.0285) | 10 |
| S3q | 5 | M1_recorded_F | -0.0223 (-0.0241 to -0.0204) | 10 |
| S3q-gain010-c050 | 5 | M1_recorded_F | -0.00952 (-0.0105 to -0.00855) | 10 |
| S3 | 10 | M1_recorded_F | -0.0403 (-0.0435 to -0.037) | 10 |
| S3q | 10 | M1_recorded_F | -0.0327 (-0.035 to -0.0305) | 10 |
| S3q-gain010-c050 | 10 | M1_recorded_F | -0.0104 (-0.0129 to -0.0079) | 10 |
| S3 | 5 | M2_realised_ibd | -0.00287 (-0.00502 to -0.000723) | 10 |
| S3q | 5 | M2_realised_ibd | -0.0097 (-0.0107 to -0.00872) | 10 |
| S3q-gain010-c050 | 5 | M2_realised_ibd | -0.00836 (-0.0096 to -0.00712) | 10 |
| S3 | 10 | M2_realised_ibd | 0.00193 (-0.00199 to 0.00585) | 10 |
| S3q | 10 | M2_realised_ibd | -0.0102 (-0.0122 to -0.00823) | 10 |
| S3q-gain010-c050 | 10 | M2_realised_ibd | -0.0105 (-0.0133 to -0.00776) | 10 |
| S3 | 10 | M3_ne | -92.2 (-105 to -79) | 10 |
| S3q | 10 | M3_ne | -19.2 (-37 to -1.32) | 10 |
| S3q-gain010-c050 | 10 | M3_ne | 7.97 (-15.5 to 31.4) | 10 |
| S3 | 5 | M5_he_relative | 0.00023 (-0.00134 to 0.0018) | 10 |
| S3q | 5 | M5_he_relative | 0.0084 (0.00736 to 0.00945) | 10 |
| S3q-gain010-c050 | 5 | M5_he_relative | 0.00145 (3.55e-06 to 0.00289) | 10 |
| S3 | 10 | M5_he_relative | -0.008 (-0.0102 to -0.00582) | 10 |
| S3q | 10 | M5_he_relative | 0.00858 (0.00664 to 0.0105) | 10 |
| S3q-gain010-c050 | 10 | M5_he_relative | 0.00276 (-7.37e-05 to 0.00559) | 10 |

## SYN_S: generation 10

| strategy | adoption | Realised inbreeding (IBD, truth) | Recorded pedigree COI | Ne from realised IBD (truth) | Gene diversity (recorded pedigree) | Neutral heterozygosity vs 2026 (truth) | Mean true HD breeding value (lower is better) | Offspring from top 20% of sires | Share of eligible males used | Mean litter size |
|---|---|---|---|---|---|---|---|---|---|---|
| S1 | 1 | 0.42 (0.407 to 0.433) | 0.177 (0.162 to 0.193) | 36.7 (30.4 to 43) | 0.82 (0.807 to 0.833) | 0.873 (0.856 to 0.889) | 0.139 (-0.0246 to 0.302) | 0.56 (0.538 to 0.583) | 0.161 (0.151 to 0.171) | 2.9 (2.69 to 3.1) |
| S3 | 1 | 0.439 (0.427 to 0.45) | 0.05 (0.0423 to 0.0578) | 23 (20.8 to 25.2) | 0.924 (0.918 to 0.93) | 0.836 (0.821 to 0.851) | -0.0168 (-0.115 to 0.0811) | 0.507 (0.466 to 0.548) | 0.136 (0.114 to 0.158) | 2.74 (2.55 to 2.92) |
| S3q | 1 | 0.381 (0.373 to 0.388) | 0.0854 (0.0797 to 0.0912) | 51.5 (45.2 to 57.9) | 0.901 (0.895 to 0.907) | 0.923 (0.914 to 0.931) | 0.097 (-0.00596 to 0.2) | 0.436 (0.418 to 0.454) | 0.173 (0.163 to 0.183) | 3.32 (3.2 to 3.43) |
| S3q-gain010-c050 | 1 | 0.382 (0.375 to 0.389) | 0.121 (0.111 to 0.13) | 52.2 (46 to 58.4) | 0.869 (0.862 to 0.875) | 0.92 (0.912 to 0.928) | -0.475 (-0.564 to -0.386) | 0.483 (0.438 to 0.528) | 0.149 (0.13 to 0.168) | 3.13 (2.95 to 3.31) |

### SYN_S: paired differences vs S1 (same replicate seeds)

| strategy | generation | metric | difference (95% CI) | n |
|---|---|---|---|---|
| S3 | 5 | M1_recorded_F | -0.0836 (-0.0993 to -0.0678) | 10 |
| S3q | 5 | M1_recorded_F | -0.051 (-0.0594 to -0.0425) | 10 |
| S3q-gain010-c050 | 5 | M1_recorded_F | -0.0285 (-0.039 to -0.018) | 10 |
| S3 | 10 | M1_recorded_F | -0.127 (-0.143 to -0.112) | 10 |
| S3q | 10 | M1_recorded_F | -0.092 (-0.108 to -0.0763) | 10 |
| S3q-gain010-c050 | 10 | M1_recorded_F | -0.0569 (-0.0782 to -0.0356) | 10 |
| S3 | 5 | M2_realised_ibd | 0.00307 (-0.00382 to 0.00996) | 10 |
| S3q | 5 | M2_realised_ibd | -0.0255 (-0.0339 to -0.0171) | 10 |
| S3q-gain010-c050 | 5 | M2_realised_ibd | -0.0195 (-0.0265 to -0.0125) | 10 |
| S3 | 10 | M2_realised_ibd | 0.0189 (-0.00102 to 0.0389) | 10 |
| S3q | 10 | M2_realised_ibd | -0.0393 (-0.0553 to -0.0232) | 10 |
| S3q-gain010-c050 | 10 | M2_realised_ibd | -0.0378 (-0.0541 to -0.0214) | 10 |
| S3 | 10 | M3_ne | -13.8 (-20.9 to -6.65) | 10 |
| S3q | 10 | M3_ne | 14.8 (5.09 to 24.5) | 10 |
| S3q-gain010-c050 | 10 | M3_ne | 15.5 (5.53 to 25.4) | 10 |
| S3 | 5 | M5_he_relative | -0.0124 (-0.0269 to 0.00217) | 10 |
| S3q | 5 | M5_he_relative | 0.0282 (0.0188 to 0.0377) | 10 |
| S3q-gain010-c050 | 5 | M5_he_relative | 0.0195 (0.0122 to 0.0268) | 10 |
| S3 | 10 | M5_he_relative | -0.0367 (-0.0619 to -0.0115) | 10 |
| S3q | 10 | M5_he_relative | 0.0498 (0.0301 to 0.0695) | 10 |
| S3q-gain010-c050 | 10 | M5_he_relative | 0.0472 (0.0269 to 0.0675) | 10 |

