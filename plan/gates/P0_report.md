# Gate report: P0 Repository and tooling
Date: 2026-10-10

## Acceptance checklist
- [x] `uv sync --all-groups` works from a clean checkout (evidence: `uv sync --all-groups --python 3.12` resolved and installed; `.venv` created from scratch).
- [x] Check suite passes (evidence: `scripts/check.sh`: ruff check, ruff format --check, mypy src "no issues found", pytest 4 passed).
- [x] `uv run bsm --help` lists all six subcommands (generate, validate, metrics, match, experiment, export; also `tests/unit/test_smoke.py::test_cli_help_lists_subcommands`).
- [x] numba compiles a trivial `@njit` function (`test_smoke.py::test_numba_toolchain`).
- [x] CI workflow present (`.github/workflows/ci.yml`). No GitHub repo yet, so no green run (HUMAN, P10).
- [x] ADRs written (`docs/decisions/ADR-001` to `ADR-006`), plan and research notes in repo, STATUS.md updated.

## What was built
- `pyproject.toml` (hatchling, Python >=3.12,<3.13, `bsm` script, optional groups app/release/conference, dev group), ruff/mypy/pytest config.
- Full folder skeleton from `00_OVERVIEW.md` section 6, plus `src/breeding_smarter/evaluation/` (P4) and `tests/benchmarks/` (P2).
- Typer CLI with six stub commands, `--version`, `--verbose` (rich logging).
- `.gitignore`, `LICENSE` (Apache-2.0, official text), `LICENSE-DATA` (CC BY 4.0 legal code), `README.md`, `CITATION.cff`, `.pre-commit-config.yaml`, CI workflow.
- `scripts/check.sh` runs the full check suite (unsets a stray `VIRTUAL_ENV` from pyenv that makes uv print warnings).

## Deviations from the plan (and why)
- Repo root is the project folder itself; the bundle's `CLAUDE.md`, `plan/`, `docs/` were moved up from `breeding-smarter-plan/` (as `HOW_TO_USE.md` intends). Duplicate top-level `00_OVERVIEW.md` (byte-identical) removed.
- Dev group includes `breeding-smarter[app,release,conference]` so `uv sync --all-groups` also installs the optional extras (needed for app tests and conference scripts in CI).
- Ruff ignores N802/N803/N806 so math-style names from the plan (`A_times`, `F`, `D`) are allowed, and PD011.
- Licences kept at the plan defaults (Apache-2.0 / CC BY 4.0) per GOAL.md decision.

## Numbers worth knowing
- Resolved numpy 2.5.3 with numba 0.68.0 (compatible, no pin needed). Python 3.12.3.

## Open questions for Tea
- Colleague's name for CITATION.cff and pyproject authors (`TODO colleague`).

## HUMAN tasks waiting
- Email organisers (slot, late paper). Create GitHub repo (then CI runs).
