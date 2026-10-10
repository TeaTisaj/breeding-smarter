# P0: Repository and tooling

**Goal:** an empty but production-quality Python project where `uv sync` and the check suite pass, CI runs on every push, and the plan and research notes are in the repo.
**Effort:** 0.5 day. **Depends on:** nothing.

## Tasks

### 0.1 [MVP] Create the project
- `uv init --package breeding-smarter` (or create manually), Python `>=3.12,<3.13`.
- Package name `breeding_smarter` under `src/`. Version `0.1.0`.
- Console script: `bsm = "breeding_smarter.cli:app"`.
- Runtime dependencies: `numpy`, `pandas`, `pyarrow`, `duckdb`, `scipy`, `numba`, `pydantic>=2`, `pyyaml`, `typer`, `matplotlib`, `rich`.
- Optional group `app`: `streamlit`, `plotly`, `graphviz`.
- Optional group `release`: `huggingface_hub`. Optional group `conference`: `qrcode[pil]`, `python-pptx`.
- Dev group: `pytest`, `hypothesis`, `pytest-cov`, `ruff`, `mypy`, `pandas-stubs`, `types-PyYAML`, `pre-commit`.
- Check that numba supports the resolved numpy version; pin numpy if needed and note it in the gate report.

### 0.2 [MVP] Tooling config in `pyproject.toml`
- ruff: `line-length = 100`, `target-version = "py312"`, rules `E, F, W, I, B, UP, N, SIM, RUF, NPY, PD` (relax `PD` where it fights numpy style).
- mypy: `python_version = 3.12`, `warn_unused_ignores = true`, `disallow_untyped_defs = true` for `breeding_smarter.pedigree.*`, `breeding_smarter.rules.*`, `breeding_smarter.matching.*`; `ignore_missing_imports = true` for numba, duckdb, streamlit.
- pytest: `testpaths = ["tests"]`, markers `slow` (statistical tests, benchmarks, full-size runs) and `integration`.

### 0.3 [MVP] Folder skeleton
Create the full layout from `00_OVERVIEW.md` section 6, with `__init__.py` files and a placeholder `README.md` in `configs/`, `data/` (gitignored except README), `reports/`.

### 0.4 [MVP] CLI skeleton
`src/breeding_smarter/cli.py` with typer app and these subcommands as stubs that print "not implemented yet": `generate`, `validate`, `metrics`, `match`, `experiment`, `export`. Add `--version`. Configure logging (rich handler) with `--verbose`.

### 0.5 [MVP] Repo files
- `.gitignore`: Python defaults, `.venv/`, `data/**` except `data/README.md`, `.streamlit/secrets.toml`, `*.parquet` outside `tests/fixtures/`.
- `LICENSE` Apache-2.0 (code). `LICENSE-DATA` CC BY 4.0 (dataset). Ask Tea if she prefers MIT or CC0 before finalising; default as written.
- `README.md`: title, one-paragraph description, the synthetic-data statement, quickstart (`uv sync`, `uv run bsm --help`), status badge placeholder.
- `CITATION.cff` with both authors (Tea fills colleague's name; leave a TODO).
- `.pre-commit-config.yaml`: ruff (lint and format), end-of-file fixer, trailing whitespace, check-yaml, check-added-large-files (max 1000 kB).

### 0.6 [MVP] CI
`.github/workflows/ci.yml`: on push and pull_request; ubuntu-latest; `astral-sh/setup-uv`; `uv sync --all-groups`; ruff check, ruff format --check, mypy src, `pytest -m "not slow"`. Cache uv.

### 0.7 [MVP] Plan and docs in repo
Copy `plan/`, `docs/research.md` and `CLAUDE.md` into the repo (Tea provides them). Write ADR-001 to ADR-006 from `00_OVERVIEW.md` section 4 as short files in `docs/decisions/` (context, decision, consequences; 10 to 20 lines each).

### 0.8 [MVP] Smoke test
`tests/unit/test_smoke.py`: package imports, version string, CLI `--help` exits 0 (use `typer.testing.CliRunner`).

## Acceptance checklist (gate)
- [ ] `uv sync --all-groups` works from a clean clone.
- [ ] Check suite passes (`ruff check`, `ruff format --check`, `mypy src`, `pytest -m "not slow"`).
- [ ] `uv run bsm --help` lists all six subcommands.
- [ ] numba compiles a trivial `@njit` function in a test (proves the toolchain works).
- [ ] CI workflow file present (green run if the GitHub repo exists).
- [ ] ADRs written, plan and research notes in repo, STATUS.md updated.
