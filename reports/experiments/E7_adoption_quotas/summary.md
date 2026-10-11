# Experiment E7_adoption_quotas

In-silico results on synthetic populations. Means with 95% t-intervals over replicates; generation g averages the birth cohorts of (g - 0.5, g + 0.5] generations after 2026 (4.5 years per generation).

## Rates per generation by window (early: generations 0 to 5, late: 5 to 10)

dF from realised IBD of birth cohorts, dC from realised coancestry of living animals (neutral loci); Ne = 1/(2 rate); nan Ne = non-positive rate.

| breed | strategy | adoption | R_delta_f_early | R_delta_f_late | R_ne_f_early | R_ne_f_late | R_delta_c_early | R_delta_c_late |
|---|---|---|---|---|---|---|---|---|
| SYN_M | S3q | 0 | 0.0576 (0.0246 to 0.0906) | 0.247 (0.212 to 0.282) | 876 (579 to 1.17e+03) | 211 (177 to 245) | -0.0326 (-0.0423 to -0.0228) | 0.233 (0.193 to 0.273) |
| SYN_M | S3q | 0.25 | 0.0565 (0.0393 to 0.0737) | 0.188 (0.156 to 0.221) | 1.15e+03 (577 to 1.72e+03) | 280 (229 to 332) | -0.0946 (-0.107 to -0.0818) | 0.162 (0.142 to 0.182) |
| SYN_M | S3q | 0.5 | 0.075 (0.0635 to 0.0864) | 0.144 (0.129 to 0.159) | 708 (547 to 870) | 355 (310 to 400) | -0.119 (-0.123 to -0.115) | 0.126 (0.106 to 0.145) |
| SYN_M | S3q | 0.75 | 0.116 (0.101 to 0.13) | 0.128 (0.0995 to 0.156) | 444 (387 to 501) | 439 (311 to 567) | -0.119 (-0.126 to -0.113) | 0.116 (0.0979 to 0.133) |
| SYN_M | S3q | 1 | 0.119 (0.106 to 0.132) | 0.152 (0.13 to 0.174) | 430 (379 to 482) | 342 (287 to 397) | -0.12 (-0.125 to -0.115) | 0.125 (0.107 to 0.144) |
| SYN_S | S3q | 0 | 2.21 (1.81 to 2.6) | 1.59 (1.37 to 1.82) | 24.1 (19.3 to 28.9) | 32.5 (27.8 to 37.3) | 1.67 (1.38 to 1.97) | 1.51 (1.32 to 1.71) |
| SYN_S | S3q | 0.25 | 1.28 (1.05 to 1.52) | 1.66 (1.32 to 1.99) | 41.2 (34.2 to 48.2) | 32.4 (26 to 38.8) | 0.946 (0.739 to 1.15) | 1.44 (1.07 to 1.81) |
| SYN_S | S3q | 0.5 | 0.895 (0.822 to 0.969) | 0.952 (0.832 to 1.07) | 56.6 (51.3 to 61.9) | 53.8 (47.7 to 59.9) | 0.607 (0.535 to 0.679) | 1 (0.864 to 1.14) |
| SYN_S | S3q | 0.75 | 0.92 (0.792 to 1.05) | 0.845 (0.762 to 0.929) | 56 (49 to 63) | 60.3 (53.7 to 66.9) | 0.464 (0.382 to 0.547) | 0.846 (0.757 to 0.934) |
| SYN_S | S3q | 1 | 1.02 (0.906 to 1.14) | 1.02 (0.835 to 1.21) | 50.1 (44.4 to 55.7) | 53.3 (38.8 to 67.8) | 0.533 (0.446 to 0.62) | 1.02 (0.815 to 1.23) |

Rates are in % per generation.

## SYN_M: generation 10

| strategy | adoption | Realised inbreeding (IBD, truth) | Recorded pedigree COI | Ne from realised IBD (truth) | Gene diversity (recorded pedigree) | Neutral heterozygosity vs 2026 (truth) | Mean true HD breeding value (lower is better) | Offspring from top 20% of sires | Share of eligible males used | Mean litter size |
|---|---|---|---|---|---|---|---|---|---|---|
| S3q | 0 | 0.137 (0.135 to 0.138) | 0.0516 (0.0497 to 0.0535) | 336 (293 to 380) | 0.945 (0.943 to 0.947) | 0.991 (0.989 to 0.993) | 0.416 (0.345 to 0.488) | 0.512 (0.499 to 0.525) | 0.133 (0.129 to 0.136) | 5.52 (5.44 to 5.6) |
| S3q | 0.25 | 0.131 (0.13 to 0.133) | 0.0418 (0.0408 to 0.0428) | 433 (381 to 485) | 0.955 (0.954 to 0.956) | 0.998 (0.997 to 0.999) | 0.438 (0.386 to 0.491) | 0.474 (0.462 to 0.486) | 0.142 (0.139 to 0.144) | 5.59 (5.46 to 5.72) |
| S3q | 0.5 | 0.128 (0.128 to 0.129) | 0.0354 (0.0342 to 0.0366) | 476 (432 to 520) | 0.961 (0.96 to 0.962) | 1 (1 to 1) | 0.375 (0.315 to 0.434) | 0.458 (0.449 to 0.467) | 0.148 (0.14 to 0.155) | 5.62 (5.53 to 5.7) |
| S3q | 0.75 | 0.127 (0.126 to 0.128) | 0.0308 (0.0298 to 0.0319) | 443 (385 to 502) | 0.965 (0.964 to 0.966) | 1 (1 to 1) | 0.373 (0.33 to 0.416) | 0.442 (0.434 to 0.451) | 0.15 (0.146 to 0.154) | 5.64 (5.49 to 5.78) |
| S3q | 1 | 0.127 (0.126 to 0.128) | 0.0282 (0.0272 to 0.0292) | 406 (363 to 449) | 0.967 (0.966 to 0.968) | 1 (1 to 1) | 0.395 (0.355 to 0.436) | 0.431 (0.425 to 0.437) | 0.152 (0.147 to 0.157) | 5.58 (5.48 to 5.69) |

### SYN_M: paired differences vs S3 (same replicate seeds)

| strategy | generation | metric | difference (95% CI) | n |
|---|---|---|---|---|
| S3q | 5 | M1_recorded_F | n/a | 0 |
| S3q | 10 | M1_recorded_F | n/a | 0 |
| S3q | 5 | M2_realised_ibd | n/a | 0 |
| S3q | 10 | M2_realised_ibd | n/a | 0 |
| S3q | 10 | M3_ne | n/a | 0 |
| S3q | 5 | M5_he_relative | n/a | 0 |
| S3q | 10 | M5_he_relative | n/a | 0 |

## SYN_S: generation 10

| strategy | adoption | Realised inbreeding (IBD, truth) | Recorded pedigree COI | Ne from realised IBD (truth) | Gene diversity (recorded pedigree) | Neutral heterozygosity vs 2026 (truth) | Mean true HD breeding value (lower is better) | Offspring from top 20% of sires | Share of eligible males used | Mean litter size |
|---|---|---|---|---|---|---|---|---|---|---|
| S3q | 0 | 0.516 (0.508 to 0.524) | 0.169 (0.156 to 0.181) | 28.8 (25 to 32.6) | 0.83 (0.818 to 0.842) | 0.857 (0.842 to 0.871) | 0.0313 (-0.0528 to 0.115) | 0.563 (0.542 to 0.584) | 0.147 (0.131 to 0.164) | 3.09 (2.9 to 3.28) |
| S3q | 0.25 | 0.497 (0.487 to 0.507) | 0.129 (0.115 to 0.143) | 36 (30.7 to 41.3) | 0.866 (0.854 to 0.878) | 0.887 (0.874 to 0.901) | 0.104 (0.0119 to 0.196) | 0.546 (0.52 to 0.572) | 0.147 (0.138 to 0.156) | 3.19 (3.03 to 3.35) |
| S3q | 0.5 | 0.47 (0.466 to 0.473) | 0.109 (0.1 to 0.117) | 53.3 (49.3 to 57.2) | 0.879 (0.874 to 0.884) | 0.924 (0.918 to 0.931) | 0.0224 (-0.0971 to 0.142) | 0.502 (0.469 to 0.535) | 0.152 (0.141 to 0.164) | 3.4 (3.29 to 3.51) |
| S3q | 0.75 | 0.461 (0.457 to 0.465) | 0.0955 (0.09 to 0.101) | 58.6 (53.3 to 63.8) | 0.891 (0.887 to 0.895) | 0.935 (0.93 to 0.941) | 0.0395 (-0.0245 to 0.103) | 0.457 (0.436 to 0.478) | 0.156 (0.147 to 0.165) | 3.65 (3.41 to 3.88) |
| S3q | 1 | 0.469 (0.462 to 0.476) | 0.0754 (0.0681 to 0.0828) | 51.1 (42.6 to 59.5) | 0.909 (0.902 to 0.917) | 0.926 (0.915 to 0.936) | 0.0383 (-0.0798 to 0.156) | 0.434 (0.424 to 0.443) | 0.174 (0.164 to 0.184) | 3.54 (3.32 to 3.76) |

### SYN_S: paired differences vs S3 (same replicate seeds)

| strategy | generation | metric | difference (95% CI) | n |
|---|---|---|---|---|
| S3q | 5 | M1_recorded_F | n/a | 0 |
| S3q | 10 | M1_recorded_F | n/a | 0 |
| S3q | 5 | M2_realised_ibd | n/a | 0 |
| S3q | 10 | M2_realised_ibd | n/a | 0 |
| S3q | 10 | M3_ne | n/a | 0 |
| S3q | 5 | M5_he_relative | n/a | 0 |
| S3q | 10 | M5_he_relative | n/a | 0 |

