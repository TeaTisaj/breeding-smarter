# ADR-006: Observed vs truth separation

Status: accepted (2026-10-10)

## Context
A synthetic dataset is only useful as a benchmark if what a kennel club would know is separated from what only the simulator knows.

## Decision
Registry tables hold only observable data; truth tables (true breeding values, realised IBD, untested genotypes, hidden animals) are separate files. The engine never reads truth except in validation and experiment metrics.

## Consequences
- We can measure how much recorded COI underestimates true inbreeding.
- Strategies are honest: they see only observed data.
- Two ID spaces (idx for registry, gid for truth) must be mapped carefully.
