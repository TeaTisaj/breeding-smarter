# Reproducibility check (P10 task 10.4)

Date: 2026-10-11. Machine: macOS (arm64), Python 3.12.3, uv 0.11.13.

1. `git clone` of the repository into a fresh folder, `git checkout 6c2d30af31fb3c1078e0a4932f8fb60aa3d23903`
   (the commit recorded for dataset v1 in `configs/datasets.yaml`).
2. Fresh environment: `uv sync --all-groups` (new `.venv`).
3. `uv run bsm generate --run-id 20261011-default-s42` (default config, seed 42), then
   `uv run bsm validate --run 20261011-default-s42` (fills `f_true_pedigree`, 39 PASS, 8 WARN, 0 FAIL).
4. SHA-256 of every Parquet file compared with the frozen v1 run.

Result: **all 9 tables byte-identical.** Wall time 2 min 17 s for steps 2 and 3 (including
the environment install).

| File | SHA-256 (first 16 hex) |
|---|---|
| registry/animals.parquet | 356eba2a0c8944af |
| registry/breeds.parquet | 4b87d1e8d57b0c36 |
| registry/dna_tests.parquet | 5cfc098878d58402 |
| registry/ebv.parquet | ab8f0cebdc5b999d |
| registry/health_tests.parquet | 0911dda1affa9c7c |
| registry/kennels.parquet | dc352bc0dd43142f |
| registry/litters.parquet | 8215ca9f928a6515 |
| truth/animals_truth.parquet | a13cc2c06e635d3a |
| truth/genotypes_truth.parquet | 729188be59bf24b8 |

Not tested: another operating system or CPU architecture. Floating-point results of numpy and
numba can differ across platforms; if hashes differ there, compare table contents
(`pandas.testing.assert_frame_equal` with a tolerance) rather than bytes. Determinism within a
platform, including across Python hash seeds, is covered by `tests/integration/test_sim.py`.
