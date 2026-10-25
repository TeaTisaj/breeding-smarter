# Experiment E11c_adoption

In-silico results on synthetic populations. Means with 95% t-intervals over replicates; generation g averages the birth cohorts of (g - 0.5, g + 0.5] generations after 2026 (4.5 years per generation).

## Rates per generation by window (early: generations 0 to 5, late: 5 to 10)

dF from realised IBD of birth cohorts, dC from realised coancestry of living animals (neutral loci); Ne = 1/(2 rate); nan Ne = non-positive rate.

| breed | strategy | adoption | R_delta_f_early | R_delta_f_late | R_ne_f_early | R_ne_f_late | R_delta_c_early | R_delta_c_late |
|---|---|---|---|---|---|---|---|---|
| SYN_M | S3q-gain010-c050 | 0.25 | 0.0429 (0.0314 to 0.0544) | 0.171 (0.157 to 0.185) | 1.43e+03 (1.04e+03 to 1.82e+03) | 302 (275 to 330) | -0.0979 (-0.104 to -0.0917) | 0.158 (0.146 to 0.171) |
| SYN_M | S3q-gain010-c050 | 0.5 | 0.0678 (0.0577 to 0.0779) | 0.13 (0.119 to 0.14) | 811 (685 to 937) | 398 (361 to 435) | -0.0773 (-0.0834 to -0.0712) | 0.115 (0.108 to 0.122) |
| SYN_M | S3q-gain010-c050 | 0.75 | 0.116 (0.109 to 0.124) | 0.13 (0.121 to 0.139) | 438 (407 to 470) | 392 (367 to 417) | -0.0438 (-0.0504 to -0.0372) | 0.12 (0.112 to 0.129) |
| SYN_M | S3q-gain010-c050 | 1 | 0.17 (0.161 to 0.18) | 0.191 (0.178 to 0.205) | 298 (280 to 315) | 267 (247 to 288) | 0.0207 (0.0119 to 0.0295) | 0.192 (0.179 to 0.205) |
| SYN_M | S3q-gain010-c050f | 0.25 | 0.0608 (0.0528 to 0.0688) | 0.163 (0.143 to 0.183) | 903 (749 to 1.06e+03) | 329 (286 to 373) | -0.0892 (-0.0957 to -0.0827) | 0.149 (0.135 to 0.163) |
| SYN_M | S3q-gain010-c050f | 0.5 | 0.0722 (0.0594 to 0.0849) | 0.13 (0.121 to 0.139) | 820 (631 to 1.01e+03) | 394 (362 to 426) | -0.0816 (-0.0907 to -0.0726) | 0.115 (0.106 to 0.124) |
| SYN_M | S3q-gain010-c050f | 0.75 | 0.112 (0.102 to 0.122) | 0.14 (0.132 to 0.148) | 463 (421 to 506) | 363 (341 to 384) | -0.0442 (-0.052 to -0.0364) | 0.123 (0.115 to 0.13) |
| SYN_M | S3q-gain010-c050f | 1 | 0.17 (0.161 to 0.18) | 0.191 (0.178 to 0.205) | 298 (280 to 315) | 267 (247 to 288) | 0.0207 (0.0119 to 0.0295) | 0.192 (0.179 to 0.205) |

Rates are in % per generation.

## SYN_M: generation 10

| strategy | adoption | Realised inbreeding (IBD, truth) | Recorded pedigree COI | Ne from realised IBD (truth) | Gene diversity (recorded pedigree) | Neutral heterozygosity vs 2026 (truth) | Mean true HD breeding value (lower is better) | Offspring from top 20% of sires | Share of eligible males used | Mean litter size |
|---|---|---|---|---|---|---|---|---|---|---|
| S3q-gain010-c050 | 0.25 | 0.131 (0.13 to 0.132) | 0.0423 (0.0416 to 0.043) | 459 (422 to 495) | 0.955 (0.954 to 0.955) | 0.998 (0.997 to 0.998) | 0.192 (0.15 to 0.234) | 0.489 (0.478 to 0.501) | 0.131 (0.127 to 0.134) | 5.61 (5.51 to 5.72) |
| S3q-gain010-c050 | 0.5 | 0.129 (0.128 to 0.129) | 0.0403 (0.0397 to 0.0408) | 503 (475 to 531) | 0.956 (0.955 to 0.956) | 0.999 (0.999 to 1) | -0.206 (-0.25 to -0.161) | 0.498 (0.482 to 0.514) | 0.131 (0.126 to 0.137) | 5.66 (5.61 to 5.72) |
| S3q-gain010-c050 | 0.75 | 0.129 (0.128 to 0.129) | 0.0394 (0.039 to 0.0398) | 406 (390 to 423) | 0.955 (0.955 to 0.956) | 0.998 (0.997 to 0.998) | -0.493 (-0.534 to -0.452) | 0.5 (0.492 to 0.508) | 0.13 (0.127 to 0.133) | 5.64 (5.58 to 5.7) |
| S3q-gain010-c050 | 1 | 0.132 (0.131 to 0.132) | 0.0427 (0.0422 to 0.0431) | 276 (266 to 286) | 0.95 (0.949 to 0.95) | 0.992 (0.991 to 0.992) | -0.808 (-0.85 to -0.767) | 0.541 (0.526 to 0.557) | 0.0991 (0.0941 to 0.104) | 5.63 (5.56 to 5.71) |
| S3q-gain010-c050f | 0.25 | 0.131 (0.13 to 0.131) | 0.0432 (0.0425 to 0.0439) | 466 (426 to 506) | 0.954 (0.953 to 0.954) | 0.998 (0.997 to 0.999) | 0.156 (0.116 to 0.195) | 0.49 (0.479 to 0.501) | 0.132 (0.129 to 0.135) | 5.61 (5.54 to 5.69) |
| S3q-gain010-c050f | 0.5 | 0.128 (0.128 to 0.129) | 0.0397 (0.039 to 0.0404) | 493 (462 to 523) | 0.956 (0.956 to 0.957) | 1 (0.999 to 1) | -0.207 (-0.246 to -0.168) | 0.488 (0.48 to 0.495) | 0.134 (0.129 to 0.138) | 5.63 (5.55 to 5.72) |
| S3q-gain010-c050f | 0.75 | 0.129 (0.129 to 0.129) | 0.0393 (0.0389 to 0.0398) | 400 (389 to 411) | 0.956 (0.955 to 0.956) | 0.998 (0.997 to 0.998) | -0.489 (-0.537 to -0.442) | 0.504 (0.49 to 0.517) | 0.128 (0.125 to 0.132) | 5.6 (5.53 to 5.67) |
| S3q-gain010-c050f | 1 | 0.132 (0.131 to 0.132) | 0.0427 (0.0422 to 0.0431) | 276 (266 to 286) | 0.95 (0.949 to 0.95) | 0.992 (0.991 to 0.992) | -0.808 (-0.85 to -0.767) | 0.541 (0.526 to 0.557) | 0.0991 (0.0941 to 0.104) | 5.63 (5.56 to 5.71) |

### SYN_M: paired differences vs S3 (same replicate seeds)

| strategy | generation | metric | difference (95% CI) | n |
|---|---|---|---|---|
| S3q-gain010-c050 | 5 | M1_recorded_F | n/a | 0 |
| S3q-gain010-c050f | 5 | M1_recorded_F | n/a | 0 |
| S3q-gain010-c050 | 10 | M1_recorded_F | n/a | 0 |
| S3q-gain010-c050f | 10 | M1_recorded_F | n/a | 0 |
| S3q-gain010-c050 | 5 | M2_realised_ibd | n/a | 0 |
| S3q-gain010-c050f | 5 | M2_realised_ibd | n/a | 0 |
| S3q-gain010-c050 | 10 | M2_realised_ibd | n/a | 0 |
| S3q-gain010-c050f | 10 | M2_realised_ibd | n/a | 0 |
| S3q-gain010-c050 | 10 | M3_ne | n/a | 0 |
| S3q-gain010-c050f | 10 | M3_ne | n/a | 0 |
| S3q-gain010-c050 | 5 | M5_he_relative | n/a | 0 |
| S3q-gain010-c050f | 5 | M5_he_relative | n/a | 0 |
| S3q-gain010-c050 | 10 | M5_he_relative | n/a | 0 |
| S3q-gain010-c050f | 10 | M5_he_relative | n/a | 0 |

