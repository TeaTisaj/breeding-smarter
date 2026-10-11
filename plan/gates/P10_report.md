# Gate report: P10 Release and documentation
Date: 2026-10-11

## Acceptance checklist
- [x] Release zip built, checksums written, size noted: `uv run bsm export release` ->
  `release/breeding-smarter-synthetic-v1/` (49 MB; README dataset card, datasheet, data
  dictionary, LICENSE CC BY 4.0, registry and truth tables as Parquet and gzip CSV, validation
  report and figures, config snapshot, manifest, SHA256SUMS) and
  `release/breeding-smarter-synthetic-v1.zip` (**43.3 MB**, well under the 1 GB limit, so the
  truth CSVs are kept). Also `release/zenodo_metadata.json` and `release/RELEASE_NOTES_v0.1.0.md`.
- [x] Datasheet complete (`docs/datasheet.md`, generated): motivation, composition (row counts
  per table and breed), generation process (seed, config hash, git commit, runtime from the
  manifest), calibration (the full target vs simulated table), the assumption list (generated
  from the configs, not typed), known deviations and limitations, uses and out-of-scope uses,
  distribution, maintenance. Tested in `tests/integration/test_release.py`.
- [x] Reproducibility check done and recorded (`reports/reproducibility.md`): clean clone at the
  recorded commit, fresh `uv sync`, regenerate v1: **all 9 Parquet files byte-identical**
  (2 min 17 s). Cross-platform not tested (stated).
- [x] HUMAN steps listed click by click (below and in `plan/STATUS.md`).
- [ ] No `TODO-DOI` placeholders left: **waits for the HUMAN steps.** `uv run bsm links check`
  lists the 14 remaining placeholders and exits 1; after Tea fills `conference/links.yaml`,
  `uv run bsm links fill` replaces them everywhere (tested).

## What was built
`release.py` (datasheet and dataset card renderers, release export with CSV copies,
checksums, zip and size guard, Zenodo metadata, placeholder finder and filler), CLI
`bsm export release`, `bsm links check|fill`, `conference/links.yaml`, `scripts/push_hf.py`
(Hugging Face dataset repo with YAML card metadata and per-table configs, plus the demo bundle),
final `README.md`, `CHANGELOG.md`, release notes, `reports/reproducibility.md`.

## Deviations from the plan (and why)
1. Placeholders are filled from one file (`conference/links.yaml`) by `bsm links fill` rather
   than by hand; `bsm links check` is the "script that greps for TODO-DOI and fails".
2. The Hugging Face upload also puts `bundle.tar.gz` in the dataset repo, so the Hugging Face
   Space can download it (`docs/deploy.md`, option B).
3. CSV files are gzip with a fixed mtime so SHA256SUMS are stable between exports.

## HUMAN steps (click by click)
See `plan/STATUS.md` section "Release steps (HUMAN)".

## Open questions for Tea
- Colleague's name and ORCID iDs for CITATION.cff and Zenodo.
