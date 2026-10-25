# Experiment E11a_pop_v1b

In-silico results on synthetic populations. Means with 95% t-intervals over replicates; generation g averages the birth cohorts of (g - 0.5, g + 0.5] generations after 2026 (4.5 years per generation).

## Rates per generation by window (early: generations 0 to 5, late: 5 to 10)

dF from realised IBD of birth cohorts, dC from realised coancestry of living animals (neutral loci); Ne = 1/(2 rate); nan Ne = non-positive rate.

| breed | strategy | adoption | R_delta_f_early | R_delta_f_late | R_ne_f_early | R_ne_f_late | R_delta_c_early | R_delta_c_late |
|---|---|---|---|---|---|---|---|---|
| SYN_M | S1 | 1 | 0.506 (0.429 to 0.583) | 0.507 (0.439 to 0.574) | 104 (82.8 to 126) | 102 (88.6 to 115) | 0.425 (0.365 to 0.485) | 0.513 (0.44 to 0.585) |
| SYN_M | S3 | 1 | 0.648 (0.548 to 0.749) | 0.578 (0.462 to 0.695) | 80.8 (66.9 to 94.8) | 93.1 (73.8 to 112) | 0.366 (0.312 to 0.42) | 0.507 (0.425 to 0.59) |
| SYN_M | S3q | 1 | 0.369 (0.324 to 0.414) | 0.348 (0.336 to 0.36) | 139 (121 to 157) | 144 (139 to 149) | 0.138 (0.104 to 0.173) | 0.327 (0.305 to 0.348) |
| SYN_M | S3q-gain010-c050 | 1 | 0.334 (0.311 to 0.357) | 0.265 (0.241 to 0.289) | 151 (140 to 162) | 192 (173 to 210) | 0.263 (0.249 to 0.276) | 0.265 (0.244 to 0.287) |
| SYN_S | S1 | 1 | 2.56 (2.2 to 2.92) | 1.97 (1.61 to 2.33) | 20.2 (17.5 to 22.9) | 26.9 (21.9 to 31.8) | 2.66 (2.35 to 2.98) | 1.86 (1.55 to 2.17) |
| SYN_S | S3 | 1 | 1.76 (1.07 to 2.46) | 2.09 (1.66 to 2.52) | 33.9 (24.8 to 42.9) | 25.8 (20.5 to 31.2) | 0.841 (0.379 to 1.3) | 1.96 (1.49 to 2.43) |
| SYN_S | S3q | 1 | 0.908 (0.757 to 1.06) | 0.981 (0.784 to 1.18) | 58 (47.7 to 68.3) | 55.1 (43 to 67.1) | 0.313 (0.229 to 0.397) | 0.938 (0.727 to 1.15) |
| SYN_S | S3q-gain010-c050 | 1 | 0.822 (0.675 to 0.97) | 0.752 (0.61 to 0.893) | 63.8 (54.1 to 73.5) | 71.4 (56 to 86.7) | 0.808 (0.662 to 0.953) | 0.759 (0.675 to 0.843) |

Rates are in % per generation.

## SYN_M: generation 10

| strategy | adoption | Realised inbreeding (IBD, truth) | Recorded pedigree COI | Ne from realised IBD (truth) | Gene diversity (recorded pedigree) | Neutral heterozygosity vs 2026 (truth) | Mean true HD breeding value (lower is better) | Offspring from top 20% of sires | Share of eligible males used | Mean litter size |
|---|---|---|---|---|---|---|---|---|---|---|
| S1 | 1 | 0.183 (0.181 to 0.186) | 0.0819 (0.0796 to 0.0842) | 97.1 (89.7 to 104) | 0.917 (0.915 to 0.919) | 0.956 (0.953 to 0.959) | -0.305 (-0.411 to -0.199) | 0.561 (0.547 to 0.576) | 0.131 (0.126 to 0.136) | 5.06 (4.94 to 5.18) |
| S3 | 1 | 0.174 (0.17 to 0.178) | 0.0302 (0.0278 to 0.0326) | 90.6 (84.2 to 97.1) | 0.96 (0.959 to 0.961) | 0.961 (0.958 to 0.964) | -0.555 (-0.628 to -0.483) | 0.518 (0.49 to 0.546) | 0.0732 (0.0656 to 0.0809) | 5.1 (4.99 to 5.22) |
| S3q | 1 | 0.162 (0.16 to 0.164) | 0.0379 (0.0371 to 0.0387) | 146 (135 to 156) | 0.957 (0.956 to 0.957) | 0.978 (0.976 to 0.981) | -0.257 (-0.307 to -0.207) | 0.438 (0.43 to 0.446) | 0.159 (0.155 to 0.164) | 5.22 (5.11 to 5.32) |
| S3q-gain010-c050 | 1 | 0.159 (0.158 to 0.16) | 0.0584 (0.0566 to 0.0602) | 174 (166 to 182) | 0.935 (0.933 to 0.936) | 0.975 (0.974 to 0.977) | -1.28 (-1.35 to -1.21) | 0.524 (0.505 to 0.544) | 0.106 (0.0971 to 0.115) | 5.26 (5.18 to 5.34) |

### SYN_M: paired differences vs S1 (same replicate seeds)

| strategy | generation | metric | difference (95% CI) | n |
|---|---|---|---|---|
| S3 | 5 | M1_recorded_F | -0.0338 (-0.037 to -0.0305) | 10 |
| S3q | 5 | M1_recorded_F | -0.0263 (-0.029 to -0.0235) | 10 |
| S3q-gain010-c050 | 5 | M1_recorded_F | -0.0147 (-0.017 to -0.0124) | 10 |
| S3 | 10 | M1_recorded_F | -0.0517 (-0.0556 to -0.0479) | 10 |
| S3q | 10 | M1_recorded_F | -0.044 (-0.0462 to -0.0418) | 10 |
| S3q-gain010-c050 | 10 | M1_recorded_F | -0.0235 (-0.0255 to -0.0214) | 10 |
| S3 | 5 | M2_realised_ibd | -0.0104 (-0.0144 to -0.0063) | 10 |
| S3q | 5 | M2_realised_ibd | -0.0156 (-0.0185 to -0.0127) | 10 |
| S3q-gain010-c050 | 5 | M2_realised_ibd | -0.0142 (-0.0166 to -0.0118) | 10 |
| S3 | 10 | M2_realised_ibd | -0.00941 (-0.0135 to -0.00533) | 10 |
| S3q | 10 | M2_realised_ibd | -0.0214 (-0.0251 to -0.0178) | 10 |
| S3q-gain010-c050 | 10 | M2_realised_ibd | -0.024 (-0.0269 to -0.021) | 10 |
| S3 | 10 | M3_ne | -6.44 (-15 to 2.08) | 10 |
| S3q | 10 | M3_ne | 48.4 (31.5 to 65.3) | 10 |
| S3q-gain010-c050 | 10 | M3_ne | 76.6 (63.1 to 90.2) | 10 |
| S3 | 5 | M5_he_relative | 0.00401 (0.000204 to 0.00781) | 10 |
| S3q | 5 | M5_he_relative | 0.0139 (0.0116 to 0.0163) | 10 |
| S3q-gain010-c050 | 5 | M5_he_relative | 0.00824 (0.00575 to 0.0107) | 10 |
| S3 | 10 | M5_he_relative | 0.00505 (0.000914 to 0.00918) | 10 |
| S3q | 10 | M5_he_relative | 0.0227 (0.0181 to 0.0273) | 10 |
| S3q-gain010-c050 | 10 | M5_he_relative | 0.0197 (0.016 to 0.0233) | 10 |

## SYN_S: generation 10

| strategy | adoption | Realised inbreeding (IBD, truth) | Recorded pedigree COI | Ne from realised IBD (truth) | Gene diversity (recorded pedigree) | Neutral heterozygosity vs 2026 (truth) | Mean true HD breeding value (lower is better) | Offspring from top 20% of sires | Share of eligible males used | Mean litter size |
|---|---|---|---|---|---|---|---|---|---|---|
| S1 | 1 | 0.49 (0.481 to 0.499) | 0.25 (0.237 to 0.263) | 23.8 (21.9 to 25.8) | 0.752 (0.74 to 0.764) | 0.804 (0.791 to 0.817) | 0.187 (0.0535 to 0.32) | 0.552 (0.513 to 0.591) | 0.178 (0.164 to 0.192) | 2.56 (2.46 to 2.66) |
| S3 | 1 | 0.438 (0.415 to 0.461) | 0.0702 (0.0558 to 0.0846) | 26.9 (21.7 to 32.1) | 0.903 (0.892 to 0.914) | 0.87 (0.842 to 0.898) | -0.0846 (-0.156 to -0.0133) | 0.511 (0.468 to 0.554) | 0.115 (0.0935 to 0.137) | 3.09 (2.84 to 3.34) |
| S3q | 1 | 0.39 (0.382 to 0.398) | 0.0955 (0.0866 to 0.104) | 56.5 (47.9 to 65.1) | 0.889 (0.882 to 0.897) | 0.94 (0.93 to 0.95) | 0.0279 (-0.0255 to 0.0813) | 0.437 (0.424 to 0.45) | 0.175 (0.167 to 0.183) | 3.47 (3.34 to 3.6) |
| S3q-gain010-c050 | 1 | 0.401 (0.397 to 0.406) | 0.141 (0.131 to 0.151) | 61.2 (56.5 to 66) | 0.849 (0.838 to 0.859) | 0.924 (0.918 to 0.93) | -0.606 (-0.695 to -0.516) | 0.493 (0.466 to 0.519) | 0.149 (0.131 to 0.166) | 3.42 (3.32 to 3.53) |

### SYN_S: paired differences vs S1 (same replicate seeds)

| strategy | generation | metric | difference (95% CI) | n |
|---|---|---|---|---|
| S3 | 5 | M1_recorded_F | -0.134 (-0.146 to -0.121) | 10 |
| S3q | 5 | M1_recorded_F | -0.108 (-0.12 to -0.096) | 10 |
| S3q-gain010-c050 | 5 | M1_recorded_F | -0.0696 (-0.0821 to -0.057) | 10 |
| S3 | 10 | M1_recorded_F | -0.18 (-0.193 to -0.167) | 10 |
| S3q | 10 | M1_recorded_F | -0.154 (-0.17 to -0.139) | 10 |
| S3q-gain010-c050 | 10 | M1_recorded_F | -0.109 (-0.126 to -0.0919) | 10 |
| S3 | 5 | M2_realised_ibd | -0.0591 (-0.0776 to -0.0407) | 10 |
| S3q | 5 | M2_realised_ibd | -0.0778 (-0.0868 to -0.0688) | 10 |
| S3q-gain010-c050 | 5 | M2_realised_ibd | -0.0597 (-0.0657 to -0.0537) | 10 |
| S3 | 10 | M2_realised_ibd | -0.0523 (-0.0778 to -0.0269) | 10 |
| S3q | 10 | M2_realised_ibd | -0.1 (-0.112 to -0.0887) | 10 |
| S3q-gain010-c050 | 10 | M2_realised_ibd | -0.0891 (-0.0975 to -0.0807) | 10 |
| S3 | 10 | M3_ne | 3.02 (-2.44 to 8.49) | 10 |
| S3q | 10 | M3_ne | 32.7 (24.1 to 41.2) | 10 |
| S3q-gain010-c050 | 10 | M3_ne | 37.4 (31.6 to 43.1) | 10 |
| S3 | 5 | M5_he_relative | 0.0766 (0.0532 to 0.1) | 10 |
| S3q | 5 | M5_he_relative | 0.101 (0.0889 to 0.114) | 10 |
| S3q-gain010-c050 | 5 | M5_he_relative | 0.0766 (0.0659 to 0.0873) | 10 |
| S3 | 10 | M5_he_relative | 0.0665 (0.0358 to 0.0972) | 10 |
| S3q | 10 | M5_he_relative | 0.136 (0.123 to 0.15) | 10 |
| S3q-gain010-c050 | 10 | M5_he_relative | 0.12 (0.107 to 0.133) | 10 |

