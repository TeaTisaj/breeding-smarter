# ADR-005: The simulator and the experiments share one engine

Status: accepted (2026-10-10)

## Context
Experiments must start from exactly the dataset we publish, and behave like the history that produced it.

## Decision
History generation and future experiments are the same year loop with a different MatingStrategy; the end-of-history SimState is saved and reloaded.

## Consequences
- Experiments start from the published state by construction.
- All simulator state must be serialisable (SimState.save/load).
- Strategies are plug-ins behind one Protocol.
