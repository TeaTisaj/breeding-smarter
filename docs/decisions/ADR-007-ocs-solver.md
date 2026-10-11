# ADR-007: cvxpy with Clarabel for optimum contribution selection

Status: accepted (2026-10-11)

## Context
P12 needs a yearly optimum contribution selection (OCS) for each experiment breed: a convex quadratic program (conservation: minimise `c'Kc`) or a linear objective with one convex quadratic constraint (gain under a kinship budget), with up to about 1,000 candidate sires, solved 45 times per simulated replicate. optiSel (R) was archived on CRAN on 2026-09-17; robustocs 0.2.1 depends on `gurobipy`, a commercial solver that needs a licence for anything but small problems [fogg-2024].

## Decision
Use `cvxpy` (1.9.3) with the open-source interior-point solver Clarabel (0.11) as runtime dependencies. The spike (12.0) confirmed they install and import next to numpy 2.5.3 and numba 0.68.0, and solve a dense 1,000-candidate conservation problem in 0.7 s. The kinship block is symmetrised and, if round-off makes it slightly indefinite, its diagonal is lifted by `|lambda_min| + 1e-12` before `cp.psd_wrap`. SCS is the fallback solver if Clarabel raises.

Correctness is checked by known-answer tests (closed form of a 3-sire problem) and by cross-checking the conservation optimum against scipy's SLSQP on random problems. robustocs is not installed (Gurobi licence); its cross-check test is skipped when it is missing.

## Consequences
- Pure Python, open-source solver chain; the gain arm (quadratic constraint) works as a second-order cone program.
- Adds about 10 packages to the environment (cvxpy, clarabel, scs, osqp, highspy and their dependencies).
- No validation against optiSel or robustocs; the independent check is SLSQP plus closed-form cases.
