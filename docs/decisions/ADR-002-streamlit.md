# ADR-002: Streamlit for the demo

Status: accepted (2026-10-10)

## Context
We need an interactive, deployable demo that a vet understands in two minutes, written by the same people who write the engine.

## Decision
Use a Streamlit multipage app that only calls package functions (no science in the app).

## Consequences
- Fastest path to an all-Python, deployable demo.
- Limited layout control and scaling; a Django REST API plus React front end is the production path.
- All logic stays testable in the package.
