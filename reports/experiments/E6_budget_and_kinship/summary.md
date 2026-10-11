# Experiment E6_budget_and_kinship

In-silico results on synthetic populations. Means with 95% t-intervals over replicates; generation g averages the birth cohorts of (g - 0.5, g + 0.5] generations after 2026 (4.5 years per generation).

## Rates per generation by window (early: generations 0 to 5, late: 5 to 10)

dF from realised IBD of birth cohorts, dC from realised coancestry of living animals (neutral loci); Ne = 1/(2 rate); nan Ne = non-positive rate.

| breed | strategy | adoption | R_delta_f_early | R_delta_f_late | R_ne_f_early | R_ne_f_late | R_delta_c_early | R_delta_c_late |
|---|---|---|---|---|---|---|---|---|
| SYN_M | CC-gain010-mc1 | 1 | 0.231 (0.211 to 0.251) | 0.176 (0.16 to 0.191) | 219 (200 to 238) | 288 (265 to 312) | 0.0138 (0.00112 to 0.0265) | 0.178 (0.158 to 0.199) |
| SYN_M | CC-gain025-mc1 | 1 | 0.281 (0.263 to 0.299) | 0.258 (0.234 to 0.282) | 179 (168 to 190) | 197 (179 to 215) | 0.104 (0.0836 to 0.123) | 0.274 (0.247 to 0.301) |
| SYN_M | CC-gain050-mc1 | 1 | 0.367 (0.336 to 0.398) | 0.448 (0.43 to 0.467) | 138 (125 to 151) | 112 (107 to 117) | 0.265 (0.227 to 0.302) | 0.428 (0.41 to 0.447) |
| SYN_M | CC-gain100-mc1 | 1 | 0.618 (0.565 to 0.671) | 0.857 (0.796 to 0.918) | 82 (74.7 to 89.3) | 58.9 (54.7 to 63) | 0.506 (0.465 to 0.546) | 0.842 (0.801 to 0.883) |
| SYN_M | CC-ocs-mc1 | 1 | 0.236 (0.221 to 0.251) | 0.176 (0.158 to 0.194) | 213 (199 to 228) | 289 (259 to 319) | -0.122 (-0.128 to -0.116) | 0.145 (0.127 to 0.162) |
| SYN_M | CC-ocs-mc1-oracle | 1 | 0.438 (0.424 to 0.451) | 0.0655 (0.0571 to 0.074) | 114 (111 to 118) | 786 (682 to 890) | -0.119 (-0.123 to -0.116) | 0.0547 (0.0521 to 0.0573) |
| SYN_S | CC-gain025-mc1 | 1 | 0.939 (0.878 to 1) | 0.749 (0.667 to 0.83) | 54.3 (50.4 to 58.3) | 70.2 (62.7 to 77.8) | 0.704 (0.644 to 0.764) | 0.759 (0.672 to 0.846) |
| SYN_S | CC-gain050-mc1 | 1 | 1.04 (0.954 to 1.12) | 0.787 (0.697 to 0.876) | 49.7 (45.6 to 53.7) | 67.5 (59.4 to 75.6) | 0.82 (0.729 to 0.911) | 0.811 (0.716 to 0.907) |
| SYN_S | CC-gain100-mc1 | 1 | 1.39 (1.3 to 1.48) | 1.04 (0.937 to 1.14) | 36.7 (34.2 to 39.1) | 50 (45.5 to 54.6) | 1.1 (1.02 to 1.19) | 1.05 (0.969 to 1.13) |
| SYN_S | CC-ocs-mc1 | 1 | 1.13 (1.07 to 1.2) | 0.926 (0.83 to 1.02) | 44.8 (42.2 to 47.3) | 56.6 (50.7 to 62.5) | 0.544 (0.498 to 0.59) | 0.928 (0.836 to 1.02) |
| SYN_S | CC-ocs-mc1-oracle | 1 | 0.618 (0.59 to 0.646) | 0.227 (0.202 to 0.252) | 81.6 (77.8 to 85.4) | 234 (205 to 264) | 0.074 (0.0582 to 0.0899) | 0.208 (0.196 to 0.221) |

Rates are in % per generation.

## SYN_M: generation 10

| strategy | adoption | Realised inbreeding (IBD, truth) | Recorded pedigree COI | Ne from realised IBD (truth) | Gene diversity (recorded pedigree) | Neutral heterozygosity vs 2026 (truth) | Mean true HD breeding value (lower is better) | Offspring from top 20% of sires | Share of eligible males used | Mean litter size |
|---|---|---|---|---|---|---|---|---|---|---|
| CC-gain010-mc1 | 1 | 0.129 (0.128 to 0.129) | 0.0396 (0.0384 to 0.0408) | 277 (259 to 295) | 0.951 (0.95 to 0.952) | 0.992 (0.992 to 0.993) | -0.789 (-0.865 to -0.712) | 0.523 (0.504 to 0.542) | 0.0975 (0.0909 to 0.104) | 5.6 (5.5 to 5.71) |
| CC-gain025-mc1 | 1 | 0.135 (0.134 to 0.136) | 0.047 (0.0463 to 0.0478) | 191 (183 to 198) | 0.942 (0.941 to 0.943) | 0.984 (0.983 to 0.985) | -0.963 (-1.04 to -0.88) | 0.552 (0.541 to 0.563) | 0.0855 (0.0779 to 0.0931) | 5.6 (5.52 to 5.68) |
| CC-gain050-mc1 | 1 | 0.147 (0.145 to 0.148) | 0.0599 (0.0587 to 0.0611) | 122 (116 to 129) | 0.928 (0.927 to 0.929) | 0.97 (0.968 to 0.971) | -1.12 (-1.21 to -1.03) | 0.586 (0.565 to 0.607) | 0.0646 (0.0606 to 0.0687) | 5.49 (5.38 to 5.59) |
| CC-gain100-mc1 | 1 | 0.174 (0.172 to 0.175) | 0.0899 (0.088 to 0.0917) | 63.4 (61.3 to 65.4) | 0.899 (0.897 to 0.9) | 0.94 (0.938 to 0.941) | -1.35 (-1.44 to -1.25) | 0.525 (0.488 to 0.562) | 0.0468 (0.0421 to 0.0515) | 5.27 (5.16 to 5.37) |
| CC-ocs-mc1 | 1 | 0.127 (0.126 to 0.127) | 0.0269 (0.026 to 0.0278) | 283 (261 to 304) | 0.967 (0.966 to 0.968) | 1 (1 to 1) | 0.386 (0.324 to 0.449) | 0.441 (0.433 to 0.45) | 0.152 (0.147 to 0.157) | 5.66 (5.52 to 5.79) |
| CC-ocs-mc1-oracle | 1 | 0.121 (0.121 to 0.121) | 0.0356 (0.0354 to 0.0359) | 266 (260 to 272) | 0.96 (0.96 to 0.961) | 1.01 (1.01 to 1.01) | 0.392 (0.344 to 0.44) | 0.42 (0.415 to 0.426) | 0.153 (0.151 to 0.156) | 5.71 (5.56 to 5.85) |

### SYN_M: paired differences vs S3 (same replicate seeds)

| strategy | generation | metric | difference (95% CI) | n |
|---|---|---|---|---|
| CC-gain010-mc1 | 5 | M1_recorded_F | n/a | 0 |
| CC-gain025-mc1 | 5 | M1_recorded_F | n/a | 0 |
| CC-gain050-mc1 | 5 | M1_recorded_F | n/a | 0 |
| CC-gain100-mc1 | 5 | M1_recorded_F | n/a | 0 |
| CC-ocs-mc1 | 5 | M1_recorded_F | n/a | 0 |
| CC-ocs-mc1-oracle | 5 | M1_recorded_F | n/a | 0 |
| CC-gain010-mc1 | 10 | M1_recorded_F | n/a | 0 |
| CC-gain025-mc1 | 10 | M1_recorded_F | n/a | 0 |
| CC-gain050-mc1 | 10 | M1_recorded_F | n/a | 0 |
| CC-gain100-mc1 | 10 | M1_recorded_F | n/a | 0 |
| CC-ocs-mc1 | 10 | M1_recorded_F | n/a | 0 |
| CC-ocs-mc1-oracle | 10 | M1_recorded_F | n/a | 0 |
| CC-gain010-mc1 | 5 | M2_realised_ibd | n/a | 0 |
| CC-gain025-mc1 | 5 | M2_realised_ibd | n/a | 0 |
| CC-gain050-mc1 | 5 | M2_realised_ibd | n/a | 0 |
| CC-gain100-mc1 | 5 | M2_realised_ibd | n/a | 0 |
| CC-ocs-mc1 | 5 | M2_realised_ibd | n/a | 0 |
| CC-ocs-mc1-oracle | 5 | M2_realised_ibd | n/a | 0 |
| CC-gain010-mc1 | 10 | M2_realised_ibd | n/a | 0 |
| CC-gain025-mc1 | 10 | M2_realised_ibd | n/a | 0 |
| CC-gain050-mc1 | 10 | M2_realised_ibd | n/a | 0 |
| CC-gain100-mc1 | 10 | M2_realised_ibd | n/a | 0 |
| CC-ocs-mc1 | 10 | M2_realised_ibd | n/a | 0 |
| CC-ocs-mc1-oracle | 10 | M2_realised_ibd | n/a | 0 |
| CC-gain010-mc1 | 10 | M3_ne | n/a | 0 |
| CC-gain025-mc1 | 10 | M3_ne | n/a | 0 |
| CC-gain050-mc1 | 10 | M3_ne | n/a | 0 |
| CC-gain100-mc1 | 10 | M3_ne | n/a | 0 |
| CC-ocs-mc1 | 10 | M3_ne | n/a | 0 |
| CC-ocs-mc1-oracle | 10 | M3_ne | n/a | 0 |
| CC-gain010-mc1 | 5 | M5_he_relative | n/a | 0 |
| CC-gain025-mc1 | 5 | M5_he_relative | n/a | 0 |
| CC-gain050-mc1 | 5 | M5_he_relative | n/a | 0 |
| CC-gain100-mc1 | 5 | M5_he_relative | n/a | 0 |
| CC-ocs-mc1 | 5 | M5_he_relative | n/a | 0 |
| CC-ocs-mc1-oracle | 5 | M5_he_relative | n/a | 0 |
| CC-gain010-mc1 | 10 | M5_he_relative | n/a | 0 |
| CC-gain025-mc1 | 10 | M5_he_relative | n/a | 0 |
| CC-gain050-mc1 | 10 | M5_he_relative | n/a | 0 |
| CC-gain100-mc1 | 10 | M5_he_relative | n/a | 0 |
| CC-ocs-mc1 | 10 | M5_he_relative | n/a | 0 |
| CC-ocs-mc1-oracle | 10 | M5_he_relative | n/a | 0 |

## SYN_S: generation 10

| strategy | adoption | Realised inbreeding (IBD, truth) | Recorded pedigree COI | Ne from realised IBD (truth) | Gene diversity (recorded pedigree) | Neutral heterozygosity vs 2026 (truth) | Mean true HD breeding value (lower is better) | Offspring from top 20% of sires | Share of eligible males used | Mean litter size |
|---|---|---|---|---|---|---|---|---|---|---|
| CC-gain025-mc1 | 1 | 0.458 (0.456 to 0.46) | 0.115 (0.109 to 0.121) | 63.1 (59.5 to 66.7) | 0.865 (0.86 to 0.871) | 0.929 (0.925 to 0.932) | -0.687 (-0.752 to -0.622) | 0.532 (0.51 to 0.554) | 0.119 (0.107 to 0.132) | 3.49 (3.36 to 3.62) |
| CC-gain050-mc1 | 1 | 0.461 (0.458 to 0.464) | 0.131 (0.126 to 0.136) | 59.3 (54 to 64.5) | 0.849 (0.844 to 0.855) | 0.922 (0.916 to 0.928) | -0.752 (-0.819 to -0.684) | 0.549 (0.529 to 0.569) | 0.108 (0.0985 to 0.117) | 3.51 (3.35 to 3.67) |
| CC-gain100-mc1 | 1 | 0.475 (0.471 to 0.478) | 0.157 (0.15 to 0.164) | 45.3 (42.3 to 48.4) | 0.826 (0.82 to 0.832) | 0.9 (0.895 to 0.905) | -0.879 (-0.939 to -0.818) | 0.604 (0.587 to 0.622) | 0.0891 (0.0802 to 0.098) | 3.36 (3.29 to 3.44) |
| CC-ocs-mc1 | 1 | 0.463 (0.46 to 0.466) | 0.0784 (0.0747 to 0.0822) | 51.1 (47.9 to 54.3) | 0.904 (0.9 to 0.907) | 0.929 (0.924 to 0.933) | 0.0866 (0.033 to 0.14) | 0.447 (0.435 to 0.46) | 0.168 (0.163 to 0.174) | 3.49 (3.39 to 3.59) |
| CC-ocs-mc1-oracle | 1 | 0.43 (0.429 to 0.431) | 0.102 (0.1 to 0.104) | 135 (131 to 140) | 0.889 (0.887 to 0.89) | 0.984 (0.983 to 0.985) | 0.000348 (-0.0385 to 0.0392) | 0.435 (0.425 to 0.445) | 0.163 (0.155 to 0.17) | 3.73 (3.57 to 3.89) |

### SYN_S: paired differences vs S3 (same replicate seeds)

| strategy | generation | metric | difference (95% CI) | n |
|---|---|---|---|---|
| CC-gain025-mc1 | 5 | M1_recorded_F | n/a | 0 |
| CC-gain050-mc1 | 5 | M1_recorded_F | n/a | 0 |
| CC-gain100-mc1 | 5 | M1_recorded_F | n/a | 0 |
| CC-ocs-mc1 | 5 | M1_recorded_F | n/a | 0 |
| CC-ocs-mc1-oracle | 5 | M1_recorded_F | n/a | 0 |
| CC-gain025-mc1 | 10 | M1_recorded_F | n/a | 0 |
| CC-gain050-mc1 | 10 | M1_recorded_F | n/a | 0 |
| CC-gain100-mc1 | 10 | M1_recorded_F | n/a | 0 |
| CC-ocs-mc1 | 10 | M1_recorded_F | n/a | 0 |
| CC-ocs-mc1-oracle | 10 | M1_recorded_F | n/a | 0 |
| CC-gain025-mc1 | 5 | M2_realised_ibd | n/a | 0 |
| CC-gain050-mc1 | 5 | M2_realised_ibd | n/a | 0 |
| CC-gain100-mc1 | 5 | M2_realised_ibd | n/a | 0 |
| CC-ocs-mc1 | 5 | M2_realised_ibd | n/a | 0 |
| CC-ocs-mc1-oracle | 5 | M2_realised_ibd | n/a | 0 |
| CC-gain025-mc1 | 10 | M2_realised_ibd | n/a | 0 |
| CC-gain050-mc1 | 10 | M2_realised_ibd | n/a | 0 |
| CC-gain100-mc1 | 10 | M2_realised_ibd | n/a | 0 |
| CC-ocs-mc1 | 10 | M2_realised_ibd | n/a | 0 |
| CC-ocs-mc1-oracle | 10 | M2_realised_ibd | n/a | 0 |
| CC-gain025-mc1 | 10 | M3_ne | n/a | 0 |
| CC-gain050-mc1 | 10 | M3_ne | n/a | 0 |
| CC-gain100-mc1 | 10 | M3_ne | n/a | 0 |
| CC-ocs-mc1 | 10 | M3_ne | n/a | 0 |
| CC-ocs-mc1-oracle | 10 | M3_ne | n/a | 0 |
| CC-gain025-mc1 | 5 | M5_he_relative | n/a | 0 |
| CC-gain050-mc1 | 5 | M5_he_relative | n/a | 0 |
| CC-gain100-mc1 | 5 | M5_he_relative | n/a | 0 |
| CC-ocs-mc1 | 5 | M5_he_relative | n/a | 0 |
| CC-ocs-mc1-oracle | 5 | M5_he_relative | n/a | 0 |
| CC-gain025-mc1 | 10 | M5_he_relative | n/a | 0 |
| CC-gain050-mc1 | 10 | M5_he_relative | n/a | 0 |
| CC-gain100-mc1 | 10 | M5_he_relative | n/a | 0 |
| CC-ocs-mc1 | 10 | M5_he_relative | n/a | 0 |
| CC-ocs-mc1-oracle | 10 | M5_he_relative | n/a | 0 |

