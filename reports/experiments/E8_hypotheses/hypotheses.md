# E8 pre-registered criteria (in-silico results on synthetic populations)

Pre-registration: `plan/14_E8_health_gain_quotas.md`. Generation 10 (Ne: late window, generations 5 to 10); paired by replicate (same seeds); 95% t-intervals. Frequencies and affected shares are sums over tested loci, shown in %. HD: lower is better.

| id | breed | quantity | estimate | lo | hi | n | pass |
|---|---|---|---|---|---|---|---|
| H8a | SYN_M | Ne late: S3q-gain010-c050 - S1 | 71.3 | 16.8 | 126 | 20 | yes |
| H8b | SYN_M | true HD breeding value (gen 10): S3q-gain010-c050 - S1 | -1.18 | -1.23 | -1.13 | 20 | yes |
| H8c | SYN_M | tested risk-allele freq, sum (gen 10): S3q-gain010-c050 - S1 | -8.881 | -10.865 | -6.897 | 20 | yes |
| H8 | SYN_M | diversity, health and hips at once (H8a and H8b and H8c) | n/a | n/a | n/a | 0 | yes |
| H8d | SYN_M | affected share at tested loci (gen 10): S3q-gain010-c050 - S1 | -0.414 | -0.565 | -0.262 | 20 |  |
| H8-arm | SYN_M | Ne late: S3q - S1 | 113 | 59.5 | 167 | 20 |  |
| H8-arm | SYN_M | HD (gen 10): S3q - S1 | -0.00848 | -0.053 | 0.036 | 20 |  |
| H8-arm | SYN_M | freq (gen 10): S3q - S1 | 9.156 | 6.289 | 12.024 | 20 |  |
| H8-arm | SYN_M | Ne late: S3q-gain010 - S1 | 72 | 22.3 | 122 | 20 |  |
| H8-arm | SYN_M | HD (gen 10): S3q-gain010 - S1 | -1.21 | -1.28 | -1.14 | 20 |  |
| H8-arm | SYN_M | freq (gen 10): S3q-gain010 - S1 | 12.453 | 9.722 | 15.184 | 20 |  |
| H8-arm | SYN_M | Ne late: S3q-c050 - S1 | 97.5 | 39.9 | 155 | 20 |  |
| H8-arm | SYN_M | HD (gen 10): S3q-c050 - S1 | 0.00221 | -0.0421 | 0.0465 | 20 |  |
| H8-arm | SYN_M | freq (gen 10): S3q-c050 - S1 | -6.954 | -9.275 | -4.634 | 20 |  |
| H8e | SYN_M | carrier-limit effect on freq (mean over planners) | -18.722 | -20.427 | -17.017 | 20 |  |
| H8e | SYN_M | carrier-limit effect on Ne late (mean over planners) | -8.15 | -36.2 | 19.9 | 20 |  |
| H8e | SYN_M | gain-OCS effect on HD (mean over carrier levels) | -1.19 | -1.24 | -1.15 | 20 |  |
| H8e | SYN_M | gain-OCS effect on Ne late (mean over carrier levels) | -33.7 | -59.2 | -8.16 | 20 |  |
| H8f | SYN_S | Ne late: S3q-gain025 - S1 | 44.1 | 26.8 | 61.3 | 10 |  |
| H8f | SYN_S | HD (gen 10): S3q-gain025 - S1 | -0.653 | -0.837 | -0.469 | 10 |  |
| H8f | SYN_S | Ne late: S3q-gain025 - S3q | 21.9 | -1.91 | 45.8 | 10 |  |
| H8f | SYN_S | HD (gen 10): S3q-gain025 - S3q | -0.729 | -0.897 | -0.562 | 10 |  |

## Planner diagnostics

| breed | strategy | seasons | infeasible | carrier relaxed | overflow (dams) | solver s median | p95 |
|---|---|---|---|---|---|---|---|
| SYN_M | S3q | 900 | 0 | n/a | 0 | 3.03 | 3.72 |
| SYN_M | S3q-c050 | 900 | 0 | 0 of 900 | 2 | 3.06 | 3.70 |
| SYN_M | S3q-gain010 | 900 | 0 | n/a | 29 | 10.11 | 12.93 |
| SYN_M | S3q-gain010-c050 | 900 | 0 | 0 of 900 | 31 | 9.82 | 12.81 |
| SYN_S | S3q | 450 | 0 | n/a | 2 | 0.06 | 0.13 |
| SYN_S | S3q-gain025 | 450 | 0 | n/a | 54 | 0.53 | 1.05 |
