# P1: Data model, configs and schemas

**Goal:** define the data contract (table schemas, IDs, file layout) and the config system before any simulator or engine code. The simulator (P3, P4) writes this format; everything else reads it.
**Effort:** 0.5 day. **Depends on:** P0.

## Key idea: observed vs truth

The simulator runs one population that includes animals nobody recorded (a hidden burn-in history before 1980, and the foreign ancestors of imported dogs). Every simulated animal has a global id `gid`. Only animals a kennel club would have registered appear in the **registry** tables, renumbered with a contiguous `idx`. Parent links of registry animals point only to registered parents; a parent that was not registered becomes unknown.

This mirrors reality (Mate Select treats the oldest recorded ancestors as unrelated founders, see `docs/research.md` 2.3) and lets us measure how much recorded-pedigree F underestimates true F. That is a result worth showing on the poster.

## Run folder layout

```
data/generated/<run_id>/
├── manifest.json
├── config_snapshot/            # exact YAML used, copied
├── registry/                   # what a kennel club knows (published as the main dataset)
│   ├── breeds.parquet
│   ├── kennels.parquet
│   ├── animals.parquet
│   ├── litters.parquet
│   ├── health_tests.parquet
│   ├── dna_tests.parquet
│   └── ebv.parquet
├── truth/                      # ground truth for benchmarking (published, clearly separated)
│   ├── animals_truth.parquet   # every simulated animal including hidden ones
│   └── genotypes_truth.parquet # disease loci genotypes of every animal
├── state/                      # end-of-history simulator state (P3), used by P8 experiments; not published
└── cache/                      # derived engine outputs (F, D, EqG, MK); safe to delete, rebuilt on demand
```

`run_id` format: `<YYYYMMDD>-<config name>-s<seed>`, for example `20261013-default-s42`.

## Table schemas

Types are Arrow types. "NN" means not null. Every table has a field-level description in code (used to generate `docs/data_dictionary.md`).

### registry/breeds
| Field | Type | Notes |
|---|---|---|
| breed_id | string NN, PK | `SYN_L`, `SYN_M`, `SYN_S` |
| display_name | string NN | `Synthetic Breed L` |
| species | string NN | `dog` |
| size_class | string NN | `toy`, `small`, `medium`, `large`, `giant` |
| studbook | string NN | `HR` for all synthetic breeds (Croatian registry setting) |
| is_local_breed | bool NN | true for the small archetype (relevant to the EU local-breed derogation) |
| archetype_description | string NN | one sentence |

### registry/kennels
Holds breeders and private owners (one table keeps the model simple).
| Field | Type | Notes |
|---|---|---|
| kennel_id | int32 NN, PK | |
| name | string NN | generated affix, for example `od Zlatne Ravnice` style but syllable-generated, never a real kennel |
| kind | string NN | `breeder` or `private_owner` |
| country | string NN | ISO 3166-1 alpha-2 |
| lat, lon | float64 NN | synthetic points inside the country bounding box (jittered) |
| registered_year | int16 NN | |

### registry/animals
| Field | Type | Notes |
|---|---|---|
| idx | int64 NN, PK | contiguous, birth order; `sire_idx < idx` and `dam_idx < idx` always |
| reg_no | string NN, unique | `SYN-HR-<birth year>-<6-digit seq>`; imports `SYN-FOREIGN-<country>-<seq>` stored in `original_reg_no`, and they get a local `reg_no` |
| name | string NN | generated: kennel affix plus call name |
| species | string NN | |
| breed_id | string NN, FK breeds | |
| sex | string NN | `M` or `F` |
| birth_date | date32 NN | |
| sire_idx | int64 nullable, FK animals | null if unknown or not registered |
| dam_idx | int64 nullable, FK animals | |
| litter_id | int64 nullable, FK litters | null for founders and imports |
| breeder_id | int32 nullable, FK kennels | |
| owner_id | int32 NN, FK kennels | current owner |
| country_of_birth | string NN | |
| studbook | string NN | `HR`, `HUR` (domestic animal with an unknown parent or grandparent) or `FOREIGN` (ancestor of an import or foreign AI sire, registered only as a pedigree record) |
| import_flag | bool NN | |
| original_reg_no | string nullable | imports only |
| microchip | string NN | 15 digits, prefix `999` (see task 1.6) |
| coat_colour | string NN | from breed config list |
| registration_type | string NN | `full` or `limited` |
| death_date | date32 nullable | |
| death_cause | string nullable | `age`, `disease`, `accident`, `unknown` |
| titles_count | int16 NN | show or working titles, 0 for most |

### registry/litters
| Field | Type | Notes |
|---|---|---|
| litter_id | int64 NN, PK | |
| breed_id | string NN | |
| sire_idx, dam_idx | int64 NN | both parents of a registered litter are registered |
| mating_date | date32 NN | about 63 days before whelping |
| whelp_date | date32 NN | |
| n_born | int16 NN | |
| n_born_alive | int16 NN | |
| n_registered | int16 NN | puppies in `animals` with this litter_id |
| mating_method | string NN | `natural`, `ai_fresh`, `ai_chilled`, `ai_frozen` |
| caesarean | bool NN | |
| breeder_id | int32 NN | |

### registry/health_tests
| Field | Type | Notes |
|---|---|---|
| test_id | int64 NN, PK | |
| idx | int64 NN, FK animals | |
| test_type | string NN | `HD` in MVP (`ED` is STRETCH) |
| scheme | string NN | `FCI` |
| result | string NN | `A`, `B`, `C`, `D`, `E` |
| test_date | date32 NN | |
| age_months | int16 NN | |
| official | bool NN | |

### registry/dna_tests
| Field | Type | Notes |
|---|---|---|
| idx | int64 NN | |
| locus_id | string NN, FK loci config | |
| genotype | string NN | `clear`, `carrier`, `affected` |
| test_date | date32 NN | |
| lab | string NN | fictional lab name |
PK is (idx, locus_id).

### registry/ebv
| Field | Type | Notes |
|---|---|---|
| idx | int64 NN | |
| trait | string NN | `HD` |
| ebv_index | float64 NN | breed index scale: mean 100, SD 10, **higher is better** (SKK convention) |
| accuracy | float64 NN | 0 to 1 |
| evaluation_date | date32 NN | |
PK is (idx, trait, evaluation_date). MVP keeps only the latest evaluation.

### truth/animals_truth
| Field | Type | Notes |
|---|---|---|
| gid | int64 NN, PK | global simulation id, birth order |
| idx | int64 nullable | registry idx if registered |
| breed_id | string NN | |
| sex | string NN | |
| birth_year | int16 NN | |
| true_sire_gid, true_dam_gid | int64 nullable | null only for base-generation animals |
| is_hidden | bool NN | true if the animal is not in the registry (`idx` is null): burn-in history, unrecorded foreign animals |
| f_true_ibd | float64 NN | realised identity by descent from neutral gene drop (P4) |
| f_true_pedigree | float64 NN | pedigree F computed on the full true pedigree (P5 fills it) |
| tbv_hd | float64 NN | true breeding value, liability scale |
| hd_liability | float64 nullable | phenotype liability, null if never screened |
| attractiveness | float64 NN | latent show/marketing value driving popular sire choice |
| fertility | float64 NN | latent, scales litter size and mating probability |

### truth/genotypes_truth
| Field | Type | Notes |
|---|---|---|
| gid | int64 NN | |
| locus_id | string NN | |
| n_risk_alleles | int8 NN | 0, 1 or 2 |

## Tasks

### 1.1 [MVP] Schema module `src/breeding_smarter/schema/`
- `tables.py`: one `TableSpec` per table (name, pyarrow schema, primary key, foreign keys, field descriptions). Single source of truth.
- `validate.py`: `validate_run(run_dir) -> ValidationResult` with checks:
  - schema match (names, types, nullability)
  - primary key uniqueness, foreign key integrity
  - `sire.sex == "M"`, `dam.sex == "F"`
  - `sire_idx < idx` and `dam_idx < idx` (topological order)
  - parent born at least `min_breeding_age` before offspring (from species config)
  - `whelp_date - mating_date` within 56 to 70 days
  - `n_registered` equals the count of animals with that litter_id
  - `death_date >= birth_date`
  - categorical fields inside their allowed domains
  - every registry animal maps to exactly one truth row (`truth.idx`)
  Return all failures (not just the first), each with table, rule, count and up to 5 example rows.
- `dictionary.py`: generate `docs/data_dictionary.md` from `TableSpec`s. CLI: `bsm schema dictionary`.

### 1.2 [MVP] IO module `src/breeding_smarter/io/`
- `write_table(df, spec, path)` and `read_table(path, spec)` enforcing the Arrow schema (cast or fail, never silently coerce).
- `RunPaths` dataclass that resolves all paths for a run_id.
- `write_manifest(...)` and `read_manifest(...)`.
- `duckdb_connect(run_dir)` that registers every Parquet file as a view (`registry_animals`, `truth_animals_truth` and so on).
- Zstd compression, row groups of 128k rows.

### 1.3 [MVP] Config framework `src/breeding_smarter/config/`
- Pydantic v2 models with `model_config = ConfigDict(extra="forbid")` so typos in YAML fail loudly.
- A reusable `Sourced[T]` pattern: every biological or regulatory number is written in YAML as `{value: ..., source: <key>}` or `{value: ..., assumption: true, note: "..."}`. A validator checks that `source` keys exist in a registry of keys (parse the table in `docs/research.md` section 9 or keep a `configs/sources.yaml` list; choose `configs/sources.yaml`, simpler and testable).
- `load_config(path) -> Model`, with `${...}` free YAML (no templating).
- `config_hash(model) -> str` (sha256 of canonical JSON) for manifests.

### 1.4 [MVP] Species and breed YAML (structure now, values tuned in P3 and P5)

`configs/species/dog.yaml` (example; values from `docs/research.md`):
```yaml
species: dog
gestation_days: {value: 63, assumption: true, note: "textbook mean, range 56-70"}
min_breeding_age_months:
  female: {value: 15, source: hks-pravilnik, note: "HKS hunting breeds, non-small"}
  male: {value: 12, assumption: true}
max_breeding_age_years:
  female: {value: 8, source: hks-pravilnik}
  male: {value: 12, assumption: true}
lifespan_weibull: {shape: 4.0, scale_years: 12.5, assumption: true}
sex_ratio_male: {value: 0.5, assumption: true}
```

`configs/breeds/syn_medium.yaml` (shape only; P3 fills numbers):
```yaml
breed_id: SYN_M
display_name: Synthetic Breed M
size_class: medium
is_local_breed: false
archetype_description: "Medium-sized breed with moderate population and strong popular-sire use."
population:
  registrations_per_year: [[1980, ...], [2026, ...]]   # (year, value) points, linear interpolation
  founders_base_generation: ...
  burn_in_generations: ...
reproduction:
  litter_size_mean: {value: ..., source: borge-2011}
  litter_size_dispersion: ...
  perinatal_loss_rate: ...
market:
  popular_sire_alpha: ...
  share_of_males_used: ...
  import_rate: ...
  ai_frozen_share: ...
health_programme:
  hd_screening_start_year: ...
  hd_screening_rate: ...
coat_colours: [...]
```

### 1.5 [MVP] Fixture builder for tests
`tests/fixtures/pedigrees.py`: small hand-built pedigrees as pandas DataFrames in registry format (used by P2 tests): unrelated founders, full-sib mating, half-sib mating, parent-offspring, first cousins, three generations of full-sib mating, inbred common ancestor. Each fixture carries its expected F values (computed by hand in the docstring, see P2 task 2.2).

### 1.6 [MVP] Verify the synthetic-ID conventions
Check (web search allowed) that ISO 11784 manufacturer/country code `999` is reserved for test transponders. If confirmed, use it and cite the source in `configs/sources.yaml`. If not confirmed, use a clearly non-ISO format `SYN` plus 12 digits and note it.

## Tests
- `test_schema_roundtrip`: write and read each table with a tiny DataFrame; types preserved.
- `test_validate_catches_errors`: build a fixture with one of each violation; `validate_run` reports all of them.
- `test_config_forbids_extra_keys`, `test_config_requires_source_or_assumption`.
- `test_data_dictionary_up_to_date`: regenerating the dictionary produces no diff (CI guard against silent contract changes).

## Acceptance checklist (gate)
- [ ] All table specs implemented; `docs/data_dictionary.md` generated.
- [ ] `validate_run` implemented and tested against deliberate violations.
- [ ] Config models load `dog.yaml` and a stub breed file; invalid YAML fails with a clear message.
- [ ] `configs/sources.yaml` contains every key from `docs/research.md` section 9.
- [ ] Microchip convention verified (task 1.6) and documented.
- [ ] Fixture pedigrees available for P2.
- [ ] Check suite passes.
