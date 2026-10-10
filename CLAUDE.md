# CLAUDE.md: Working rules for Claude Code on Breeding Smarter

You are implementing a proof of concept for a conference (BioMedVetMech 2026, Zagreb, 24 to 25 October 2026). The plan is in `plan/`. Domain facts are in `docs/research.md`. Read `plan/00_OVERVIEW.md` before anything else.

## How to work

1. **One phase at a time.** Only work on the phase Tea names (for example "Start P2"). Read that phase file completely before writing code.
2. **Plan mode first.** At the start of each phase, propose a short file-level plan (files to create or change, order, tests) and wait for approval.
3. **Order inside a phase:** tests with known answers first (where the phase file says so), then implementation, then run the full check suite.
4. **MVP before STRETCH.** Never start a `[STRETCH]` task while an `[MVP]` task in any started phase is open. Never do `[HUMAN]` tasks; prepare material for them and list them in the gate report.
5. **Do not invent numbers.** Every biological, regulatory or calibration number comes from `docs/research.md` (cite its key in the YAML `source` field) or is marked `assumption: true`. If you need a number that is not there, stop and ask.
6. **Do not change the data contract silently.** Schemas from P1 are the contract between the simulator and the engine. Any change needs: updated schema, regenerated `docs/data_dictionary.md`, a note in the gate report.
7. **Never claim the data is real.** Every user-facing surface (README, app, figures, dataset card) says the animals are synthetic.
8. **Ask instead of guessing** when the plan is ambiguous or seems wrong. Point to the exact line in the plan.

## Check suite (must pass before any gate)

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest -m "not slow"
```
Phases that add slow tests (statistical, benchmarks) also run `uv run pytest -m slow` and report results.

## Definition of done for a task
- Code, tests and docstrings written; public functions have type hints and a docstring with formulas or references where relevant.
- Check suite passes.
- Any new config value has `source` or `assumption: true`.
- `plan/STATUS.md` updated (task ticked).

## Gate report template (write at the end of every phase, then stop)

Save as `plan/gates/PX_report.md` and print a summary in the chat:

```markdown
# Gate report: PX <name>
Date:
## Acceptance checklist
- [x] item (evidence: test name / command output / file)
- [ ] item (why not, what is needed)
## What was built
## Deviations from the plan (and why)
## Numbers worth knowing (runtimes, row counts, key metric values)
## Open questions for Tea
## HUMAN tasks waiting
```

Do not start the next phase until Tea says so.

## Commands you will use
- `uv sync` (install), `uv run bsm --help` (CLI), `uv run streamlit run app/Home.py` (demo, from P9).

## Style
- Python 3.12, ruff formatting, line length 100.
- Pure functions in `pedigree/`, `rules/`, `matching/` (no I/O inside). I/O lives in `io/` and `cli.py`.
- Randomness only through an explicit `np.random.Generator` argument.
- Prefer numpy arrays over pandas inside hot loops; pandas at the edges.
- Commit messages: conventional commits, one logical change per commit.
