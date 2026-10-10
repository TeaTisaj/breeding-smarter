# Gate report: P2 Pedigree engine
Date: 2026-10-10

## Acceptance checklist
- [x] All known-answer tests pass (`tests/unit/test_pedigree_known.py`, 35 tests: every fixture's F under numba, pure Python and the dense oracle; kinship identities f(A,A)=0.5, f(S,S)=0.625, parent-offspring 0.25, full sibs 0.25, half sibs 0.125; full-sib recurrence 0.25, 0.375, 0.5; inbred ancestor 0.15625; D convention; edge cases).
- [x] All property tests pass with at least 200 examples each (`tests/property/test_pedigree_props.py`, 10 properties, `max_examples=200`, n up to 150, 0 to 30% unknown parents): F = diag(A) - 1; A x (1-D and 2-D); pair kinship = A/2 = sum of decomposition; kinship_to_all; shortcut on/off identical; pruning invariance (F, D, kinship matrix); founder contributions non-negative and sum to 1 with phantoms (and phantoms do not change F); EqG = brute-force path enumeration (n up to 40); mean kinship = dense; numba = Python; `inbreeding_extend` in chunks = full run.
- [x] Benchmarks recorded and targets met (`reports/benchmarks/engine.md`): 250k animals: inbreeding 0.39 s (target 60 s), A_times 0.002 s (1 s), kinship_to_all 0.002 s (1 s), pair_kinship 0.20 ms (10 ms).
- [x] Every public function has a docstring with formula and reference (module docstring of `core.py` holds the notation block).
- [x] `bsm metrics` works on a run folder written from the P1 fixture pedigrees (`tests/integration/test_cli_metrics.py`, JSON and table output, cache file written).
- [x] mypy strict passes for `pedigree/` (`mypy --strict src/breeding_smarter/pedigree`: no issues; now part of `scripts/check.sh` and CI).

## What was built
- `pedigree/core.py`: `Pedigree` (from_arrays, from_registry, from_truth, validate, prune, subset_arrays, ancestors_mask, with_phantom_parents, offspring_index, breed_mask).
- `pedigree/_kernels.py`: numba kernels (array max-heap with `in_heap` dedup, L-row traversal, Meuwissen and Luo with full-sib shortcut and incremental start, Colleau T' and T passes for 1-D and 2-D, EqG, generation depths, ancestor marking).
- `pedigree/inbreeding.py`: `inbreeding`, `inbreeding_extend`, `inbreeding_py`, `l_row`, `l_row_virtual`, `pair_kinship`, `pair_kinship_decomposed`.
- `pedigree/kinship.py`: `A_times`, `kinship_to_all`, `mean_kinship` (self-kinship included, PMx), `kinship_matrix` (pruned, multi-column), `contributions`.
- `pedigree/completeness.py`, `pedigree/relationships.py` (`relationship`, `nearest_common_ancestor`, `generations_to_nearest_common_ancestor`, and vectorised `close_relative_flags` for P3/P6), `pedigree/population.py` (generation interval, Ne by individual dF and census, gene diversity, founder stats fe/fg, Gini, top-20% share, sire usage with FCI 5% ratio, `population_report`).
- `pedigree/reference.py`: dense tabular A and brute-force EqG (test oracles).
- `io/cache.py`: `resolve_run`, F/D/EqG cache keyed by run id, engine version and pedigree kind (registry or truth). CLI `bsm metrics --run ... [--breed] [--year] [--json]`.

## Deviations from the plan (and why)
- Cache file is `cache/pedigree_F_D_<kind>.parquet` (+ JSON key) so the truth pedigree (P5) can be cached next to the registry one.
- `close_relative_flags` (vectorised relationship flags for one dam vs many sires) added to `relationships.py`; tested equal to `relationship` element-wise. P3 market and P6 rules use it.
- `sire_usage` approximates "males of breeding age" by birth year (1 to 12 years old), ignoring deaths, because the registry pedigree has no death dates; documented in the docstring.
- `top_share` uses `max(1, round(0.2 n))` units for "top 20%".
- Ruff ignores B008 (typer idiom), N812, N815 (math names).

## Numbers worth knowing
- 94 fast tests in about 7 s. Benchmark pedigree is shallower than the real simulated truth pedigree; P3/P5 will report the time of F on the full truth pedigree (about 400k animals with 10 hidden burn-in generations).

## Open questions for Tea
- None.

## HUMAN tasks waiting
- None new.
