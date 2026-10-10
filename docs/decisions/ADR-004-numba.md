# ADR-004: numba for the hot loops

Status: accepted (2026-10-10)

## Context
Meuwissen and Luo inbreeding and Colleau kinship products over about 250k animals are too slow in pure Python.

## Decision
Implement hot loops with numba @njit on numpy arrays; keep plain-Python twins for tests.

## Consequences
- Large speed-up without a C extension or build step.
- numba constrains the numpy version; pinned via the resolver.
- Twins give an independent oracle in property tests.
