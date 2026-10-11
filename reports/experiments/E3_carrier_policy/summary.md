# Experiment E3_carrier_policy

In-silico results on synthetic populations. Means with 95% t-intervals over replicates; generation g averages the birth cohorts of (g - 0.5, g + 0.5] generations after 2026 (4.5 years per generation).

## SYN_M: generation 10

| strategy | adoption | Realised inbreeding (IBD, truth) | Recorded pedigree COI | Ne from realised IBD (truth) | Gene diversity (recorded pedigree) | Neutral heterozygosity vs 2026 (truth) | Mean true HD breeding value (lower is better) | Offspring from top 20% of sires | Share of eligible males used | Mean litter size |
|---|---|---|---|---|---|---|---|---|---|---|
| S3 | 1 | 0.137 (0.133 to 0.14) | 0.0232 (0.0217 to 0.0247) | 190 (157 to 222) | 0.969 (0.968 to 0.971) | 0.992 (0.989 to 0.994) | 0.135 (0.0658 to 0.204) | 0.505 (0.482 to 0.527) | 0.0576 (0.0502 to 0.0649) | 5.53 (5.43 to 5.62) |
| S3hc | 1 | 0.137 (0.133 to 0.14) | 0.0232 (0.0217 to 0.0247) | 190 (157 to 222) | 0.969 (0.968 to 0.971) | 0.992 (0.989 to 0.994) | 0.135 (0.0658 to 0.204) | 0.505 (0.482 to 0.527) | 0.0576 (0.0502 to 0.0649) | 5.53 (5.43 to 5.62) |
| S3xc | 1 | 0.14 (0.135 to 0.145) | 0.0239 (0.0214 to 0.0263) | 163 (139 to 186) | 0.967 (0.965 to 0.969) | 0.989 (0.985 to 0.992) | 0.211 (0.164 to 0.258) | 0.509 (0.476 to 0.542) | 0.0552 (0.0448 to 0.0656) | 5.62 (5.5 to 5.74) |

### SYN_M: paired differences vs S3 (same replicate seeds)

| strategy | generation | metric | difference (95% CI) | n |
|---|---|---|---|---|
| S3hc | 5 | M1_recorded_F | 0 (0 to 0) | 10 |
| S3xc | 5 | M1_recorded_F | 0.00249 (0.000665 to 0.00432) | 10 |
| S3hc | 10 | M1_recorded_F | 0 (0 to 0) | 10 |
| S3xc | 10 | M1_recorded_F | 0.000702 (-0.00156 to 0.00296) | 10 |
| S3hc | 5 | M2_realised_ibd | 0 (0 to 0) | 10 |
| S3xc | 5 | M2_realised_ibd | -0.0012 (-0.00427 to 0.00187) | 10 |
| S3hc | 10 | M2_realised_ibd | 0 (0 to 0) | 10 |
| S3xc | 10 | M2_realised_ibd | 0.00307 (-0.00354 to 0.00969) | 10 |
| S3hc | 10 | M3_ne | 0 (0 to 0) | 10 |
| S3xc | 10 | M3_ne | -27 (-60.8 to 6.89) | 10 |
| S3hc | 5 | M5_he_relative | 0 (0 to 0) | 10 |
| S3xc | 5 | M5_he_relative | -0.000615 (-0.00291 to 0.00168) | 10 |
| S3hc | 10 | M5_he_relative | 0 (0 to 0) | 10 |
| S3xc | 10 | M5_he_relative | -0.00298 (-0.00663 to 0.000678) | 10 |

## SYN_S: generation 10

| strategy | adoption | Realised inbreeding (IBD, truth) | Recorded pedigree COI | Ne from realised IBD (truth) | Gene diversity (recorded pedigree) | Neutral heterozygosity vs 2026 (truth) | Mean true HD breeding value (lower is better) | Offspring from top 20% of sires | Share of eligible males used | Mean litter size |
|---|---|---|---|---|---|---|---|---|---|---|
| S3 | 1 | 0.497 (0.486 to 0.508) | 0.053 (0.0427 to 0.0633) | 33.4 (28.5 to 38.3) | 0.915 (0.905 to 0.924) | 0.88 (0.863 to 0.897) | 0.0638 (-0.0298 to 0.157) | 0.525 (0.472 to 0.578) | 0.105 (0.0899 to 0.12) | 3.21 (3.04 to 3.39) |
| S3hc | 1 | 0.497 (0.486 to 0.508) | 0.053 (0.0427 to 0.0633) | 33.4 (28.5 to 38.3) | 0.915 (0.905 to 0.924) | 0.88 (0.863 to 0.897) | 0.0638 (-0.0298 to 0.157) | 0.525 (0.472 to 0.578) | 0.105 (0.0899 to 0.12) | 3.21 (3.04 to 3.39) |
| S3xc | 1 | 0.497 (0.486 to 0.508) | 0.053 (0.0427 to 0.0633) | 33.4 (28.5 to 38.3) | 0.915 (0.905 to 0.924) | 0.88 (0.863 to 0.897) | 0.0638 (-0.0298 to 0.157) | 0.525 (0.472 to 0.578) | 0.105 (0.0899 to 0.12) | 3.21 (3.04 to 3.39) |

### SYN_S: paired differences vs S3 (same replicate seeds)

| strategy | generation | metric | difference (95% CI) | n |
|---|---|---|---|---|
| S3hc | 5 | M1_recorded_F | 0 (0 to 0) | 10 |
| S3xc | 5 | M1_recorded_F | 0 (0 to 0) | 10 |
| S3hc | 10 | M1_recorded_F | 0 (0 to 0) | 10 |
| S3xc | 10 | M1_recorded_F | 0 (0 to 0) | 10 |
| S3hc | 5 | M2_realised_ibd | 0 (0 to 0) | 10 |
| S3xc | 5 | M2_realised_ibd | 0 (0 to 0) | 10 |
| S3hc | 10 | M2_realised_ibd | 0 (0 to 0) | 10 |
| S3xc | 10 | M2_realised_ibd | 0 (0 to 0) | 10 |
| S3hc | 10 | M3_ne | 0 (0 to 0) | 10 |
| S3xc | 10 | M3_ne | 0 (0 to 0) | 10 |
| S3hc | 5 | M5_he_relative | 0 (0 to 0) | 10 |
| S3xc | 5 | M5_he_relative | 0 (0 to 0) | 10 |
| S3hc | 10 | M5_he_relative | 0 (0 to 0) | 10 |
| S3xc | 10 | M5_he_relative | 0 (0 to 0) | 10 |

