#!/usr/bin/env bash
# Full check suite (CLAUDE.md). Usage: scripts/check.sh
set -euo pipefail
unset VIRTUAL_ENV
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest -m "not slow" -q "$@"
