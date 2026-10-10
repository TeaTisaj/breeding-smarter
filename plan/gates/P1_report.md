# Gate report: P1 Data model, configs and schemas
Date: 2026-10-10

## Acceptance checklist
- [x] All table specs implemented (`src/breeding_smarter/schema/tables.py`, 9 tables); `docs/data_dictionary.md` generated (`bsm schema dictionary`; guarded by `test_data_dictionary_up_to_date`).
- [x] `validate_run` implemented and tested against deliberate violations (`tests/unit/test_schema.py::test_validate_catches_errors`: 13 violation types detected in one run; `test_validate_reports_missing_tables_and_schema`; all 7 fixture runs validate clean).
- [x] Config models load `dog.yaml` and the three breed files; invalid YAML, unknown keys, missing provenance and unknown source keys fail with messages naming the file and field (`tests/unit/test_config.py`).
- [x] `configs/sources.yaml` contains every key from `docs/research.md` section 9 (`test_sources_cover_research_keys`), plus `icar-999`.
- [x] Microchip convention verified (task 1.6) and documented: ICAR (the ISO 11784 registration authority) reserves code 999 for test transponders and forbids identifying animals with it, so it can never collide with a real dog. Microchips are `999` + 12 digits; validated by rule `microchip_format_999`. Source key `icar-999` (added to `docs/research.md` section 9 and `configs/sources.yaml`).
- [x] Fixture pedigrees available for P2 (`tests/fixtures/pedigrees.py`: unrelated, full_sibs, half_sibs, parent_offspring, first_cousins, repeated_full_sib, inbred_ancestor, each with expected F and kinships derived in the docstring, and a builder that writes a complete valid run folder).
- [x] Check suite passes (38 tests).

## What was built
- `schema/`: `TableSpec`/`FieldSpec`/`ForeignKey`, `validate_run` (schema, PK, FK, domains, parent sex, topological order, minimum breeding age, gestation 56 to 70 days, `n_registered`, death after birth, litter-parent consistency, synthetic ID conventions, registry-to-truth mapping, `is_hidden` consistency), data dictionary generator.
- `io/`: strict `write_table`/`read_table` (per-column Arrow conversion, never silent coercion; nullable ints read as pandas nullable dtypes; dates as datetime64), `RunPaths`, manifests with git commit, DuckDB views (`registry_animals`, ...). zstd, 128k row groups.
- `config/`: `Strict` base (extra=forbid, frozen), `Sourced[T]`, `SourcedSeries` (interpolated `(year, value)` points), `collect_assumptions` (used later for the datasheet), `config_hash`, models for species, breed and sim configs.
- Configs: `species/dog.yaml`, `breeds/syn_{large,medium,small}.yaml` (full P3 parameter table already filled), `sim/default.yaml`, `sources.yaml`.

## Deviations from the plan (and why)
- Breed and sim models already contain every P3 parameter (values from the P3 table) to avoid a second contract change in P3. P4 will add the health/genetics sections.
- Extra validation rules beyond the list: `reg_no_unique`, `microchip_unique`, `microchip_format_999`, `reg_no_synthetic_prefix`, `idx_contiguous`, `litter_parents_match`, `is_hidden_iff_idx_null`, truth topological order.
- Shared market behaviour constants (distance scale 300 km, same-kennel exclusion 0.5, prime age 2 to 8 years, off-prime factor 0.5, 5 retries) live in `configs/sim/default.yaml` under `market`, all `assumption: true`.
- Added species parameters needed by P3 (`gestation_sd_days`, `death_cause_shares`, `inbreeding_litter_slope` (source chu-2019), `attractiveness_sd`, `fertility_log_sd`), all from the P3 text and marked.
- `litter_size_mean` carries both `source: borge-2011` and `assumption: true` (the value is chosen inside the published range, not published itself).

## Numbers worth knowing
- 9 tables, 38 tests, suite runs in about 2.5 s.

## Open questions for Tea
- None blocking.

## HUMAN tasks waiting
- None new.
