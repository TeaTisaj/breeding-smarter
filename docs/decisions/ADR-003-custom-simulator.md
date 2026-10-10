# ADR-003: Custom Python simulator, not AlphaSimR

Status: accepted (2026-10-10)

## Context
We need a breeding market (popular sires, kennels, imports, rule-compliant matings) and pluggable mating strategies, and the whole stack is Python.

## Decision
Write our own seeded, agent-based, year-step simulator in Python with numpy.

## Consequences
- Full control over market behaviour and observation processes.
- We own correctness: covered by statistical tests and engine-vs-gene-drop validation.
- Pedigrees can be exported to AlphaSimR later for genome-level work.
