# P12 pre-registered criteria (in-silico results on synthetic populations)

Late window = generations 5 to 10; paired by replicate (same seeds); 95% t-intervals. dF rows are in % per generation. H3 lists range over controls (lo) and over matings (hi). H5 lists oracle Ne (lo) and S0 Ne (hi), each 1/(2 mean dF late).

| id | breed | quantity | estimate | lo | hi | n | pass |
|---|---|---|---|---|---|---|---|
| H1 | SYN_S | Ne late: CC-ocs-mc1 - S1 (paired) | 20.9 | 13.5 | 28.3 | 20 | yes |
| H1-support | SYN_S | dF late: CC-ocs-mc1 - S1 (paired) | -0.592 | -0.791 | -0.394 | 20 |  |
| H2 | SYN_S | dF late: CC-ocs-mc1 - S3 (paired) | -0.631 | -0.900 | -0.363 | 20 | yes |
| H3 | SYN_S | range of late dF over controls minus over matings | -0.183 | 0.712 | 0.895 | 0 | no |
| H5 | SYN_S | Ne(1/2 mean dF late): oracle / S0 | 2.97 | 221 | 74.4 | 0 | yes |
| H6 | SYN_S | Ne late: oracle - recorded (paired) | 178 | 145 | 210 | 20 |  |
| H6-support | SYN_S | dF late: oracle - recorded (paired) | -0.700 | -0.807 | -0.593 | 20 |  |
| H1 | SYN_M | Ne late: CC-ocs-mc1 - S1 (paired) | 83.5 | 16 | 151 | 10 | yes |
| H1-support | SYN_M | dF late: CC-ocs-mc1 - S1 (paired) | -0.089 | -0.161 | -0.017 | 10 |  |
| H2 | SYN_M | dF late: CC-ocs-mc1 - S3 (paired) | -0.122 | -0.212 | -0.031 | 10 | yes |
| H3 | SYN_M | range of late dF over controls minus over matings | -0.203 | 0.336 | 0.539 | 0 | no |
| H4a | SYN_M | affected share at tested loci (gen 10): S3q - S1 | 0.111 | -0.182 | 0.405 | 10 | no |
| H4b | SYN_M | Ne late: S3q - S1 (paired) | 136 | 72.7 | 200 | 10 | yes |
| H5 | SYN_M | Ne(1/2 mean dF late): oracle / S0 | 0.8 | 763 | 953 | 0 | no |
| H6 | SYN_M | Ne late: oracle - recorded (paired) | 497 | 377 | 618 | 10 |  |
| H6-support | SYN_M | dF late: oracle - recorded (paired) | -0.111 | -0.134 | -0.088 | 10 |  |

## Planner diagnostics

| experiment | breed | strategy | seasons | infeasible | solver s median | p95 | max |
|---|---|---|---|---|---|---|---|
| E5_coordination | SYN_M | CC-ocs-mc1 | 450 | 0 | 1.52 | 2.80 | 4.51 |
| E5_coordination | SYN_M | CC-ocs-rand | 450 | 0 | 1.22 | 1.64 | 2.53 |
| E5_coordination | SYN_M | S3q | 450 | 0 | 1.43 | 2.00 | 3.01 |
| E5_coordination | SYN_S | CC-ocs-mc1 | 900 | 0 | 0.06 | 0.08 | 0.20 |
| E5_coordination | SYN_S | CC-ocs-rand | 900 | 0 | 0.05 | 0.08 | 0.31 |
| E5_coordination | SYN_S | S3q | 900 | 0 | 0.06 | 0.08 | 0.18 |
| E6_budget_and_kinship | SYN_M | CC-gain010-mc1 | 450 | 0 | 4.12 | 5.33 | 6.22 |
| E6_budget_and_kinship | SYN_M | CC-gain025-mc1 | 450 | 0 | 4.28 | 5.58 | 6.83 |
| E6_budget_and_kinship | SYN_M | CC-gain050-mc1 | 450 | 0 | 4.50 | 6.18 | 7.41 |
| E6_budget_and_kinship | SYN_M | CC-gain100-mc1 | 450 | 0 | 4.85 | 6.62 | 9.14 |
| E6_budget_and_kinship | SYN_M | CC-ocs-mc1 | 450 | 0 | 1.28 | 1.73 | 3.01 |
| E6_budget_and_kinship | SYN_M | CC-ocs-mc1-oracle | 450 | 0 | 1.26 | 1.59 | 1.94 |
| E6_budget_and_kinship | SYN_S | CC-gain025-mc1 | 900 | 0 | 0.17 | 0.30 | 0.69 |
| E6_budget_and_kinship | SYN_S | CC-gain050-mc1 | 900 | 0 | 0.17 | 0.28 | 0.37 |
| E6_budget_and_kinship | SYN_S | CC-gain100-mc1 | 900 | 0 | 0.18 | 0.30 | 0.70 |
| E6_budget_and_kinship | SYN_S | CC-ocs-mc1 | 900 | 0 | 0.05 | 0.07 | 0.21 |
| E6_budget_and_kinship | SYN_S | CC-ocs-mc1-oracle | 900 | 0 | 0.06 | 0.08 | 0.21 |
| E7_adoption_quotas | SYN_M | S3q (adoption 0.25) | 450 | 0 | 1.23 | 1.74 | 2.12 |
| E7_adoption_quotas | SYN_M | S3q (adoption 0.5) | 450 | 0 | 1.23 | 1.64 | 2.24 |
| E7_adoption_quotas | SYN_M | S3q (adoption 0.75) | 450 | 0 | 1.22 | 1.54 | 2.05 |
| E7_adoption_quotas | SYN_M | S3q | 450 | 0 | 1.14 | 1.48 | 1.86 |
| E7_adoption_quotas | SYN_S | S3q (adoption 0.25) | 450 | 0 | 0.05 | 0.17 | 0.53 |
| E7_adoption_quotas | SYN_S | S3q (adoption 0.5) | 450 | 0 | 0.05 | 0.15 | 0.36 |
| E7_adoption_quotas | SYN_S | S3q (adoption 0.75) | 450 | 0 | 0.05 | 0.07 | 0.22 |
| E7_adoption_quotas | SYN_S | S3q | 450 | 0 | 0.05 | 0.08 | 0.17 |
