# P10: Release and documentation

**Goal:** make the code and dataset public, citable and reproducible before the congress, so the QR code on the poster points to something real.
**Effort:** 1 day. **Depends on:** P5 (dataset v1), P8 (results), ideally P9.

---

## 1. Tasks

### 10.1 [MVP] Release package
`bsm export release --dataset v1` writes `release/breeding-smarter-synthetic-v1/`:
```
README.md                  # short dataset card (same text as the Hugging Face card)
datasheet.md               # full datasheet (10.2)
data_dictionary.md
LICENSE (CC BY 4.0)
registry/*.parquet  and  registry_csv/*.csv.gz
truth/*.parquet     and  truth_csv/*.csv.gz
validation/validation_report.md, targets_vs_simulated.csv, figures/
config_snapshot/
manifest.json
SHA256SUMS
```
Plus `breeding-smarter-synthetic-v1.zip`. Check the size; if over 1 GB, drop CSV copies of the truth tables.

### 10.2 [MVP] Datasheet (`docs/datasheet.md`), following "Datasheets for Datasets" (Gebru et al.)
Sections and required content:
- **Motivation:** why (no open real pedigree data, see `docs/research.md` section 7), who made it, funding (none).
- **Composition:** breeds, animals per table, years, what one row is, observed vs truth split, explicit statement **"All animals are synthetic. Any resemblance to real dogs, kennels or registration numbers is accidental."**, ID conventions (`SYN-`, microchip prefix).
- **Generation process:** simulator summary (hidden history, market, imports, genetics, observations, BLUP), seed, config hash, git commit, runtime.
- **Calibration:** the `targets_vs_simulated` table with sources, and the complete list of parameters marked `assumption: true`.
- **Known deviations and limitations:** for example: linear model on HD grades, simplified registration, no parentage errors, illustrative allele frequencies, no linkage between loci, one mating per dam per year at most, AI and import processes stylised.
- **Uses:** intended (benchmarking pedigree and kinship algorithms, testing matching and compliance tools, teaching, prototyping); **out of scope** (decisions about real animals, estimates of real breed parameters, any claim about real breeds).
- **Distribution:** licence CC BY 4.0, DOI, Hugging Face mirror, citation.
- **Maintenance:** contact, versioning (v1 frozen; future versions get new DOIs).

### 10.3 [MVP] README (repo)
Sections: title and one-line pitch; synthetic-data notice; what is in the repo (engine, simulator, rules, recommender, app); quickstart (`uv sync`, `bsm generate --config configs/sim/tiny.yaml`, `bsm validate`, `bsm match`, run the app); headline figure (Fig A) with caption; dataset links (DOI, Hugging Face); how to cite; licence (code Apache-2.0, data CC BY 4.0); roadmap (from `00_OVERVIEW.md` section 9); "Partner with us" with contact; acknowledgements (FER).

### 10.4 [MVP] Reproducibility check
On a clean clone in a fresh environment: `uv sync`, regenerate v1 with the recorded config and seed, compare `SHA256SUMS` of the Parquet files. Record result and runtime in `reports/reproducibility.md`. If hashes differ, find the cause (library versions, platform) and either fix it or document the platform requirement and compare table contents instead of bytes.

### 10.5 [HUMAN, prepared by Claude Code] GitHub
Claude Code prepares: final README, CITATION.cff, CHANGELOG (`0.1.0`), release notes text. Tea creates or makes public the repo `breeding-smarter`, enables GitHub Actions, creates release `v0.1.0` and uploads the zip as a release asset.

### 10.6 [HUMAN, prepared by Claude Code] Zenodo
- Code: enable the Zenodo GitHub integration before creating the release, so `v0.1.0` gets a DOI automatically.
- Dataset: separate Zenodo record (type "Dataset"), upload the zip; Claude Code prepares `release/zenodo_metadata.json` (title, authors with affiliations, description from the datasheet, keywords, licence `cc-by-4.0`, related identifiers linking to the code DOI and the GitHub repo). **Reserve the DOI first** so it can be printed on the poster before publishing.

### 10.7 [MVP] Hugging Face dataset mirror (Tea provides the token)
Script `scripts/push_hf.py` using `huggingface_hub`: creates the dataset repo, uploads Parquet files and the dataset card with YAML metadata (`license: cc-by-4.0`, `tags: [synthetic, pedigree, dogs, animal-genetics, inbreeding]`, `configs` for registry tables, `pretty_name`). First in the cut list if time is short.

### 10.8 [MVP] Update links everywhere
DOIs and URLs into README, datasheet, CITATION.cff, app About page, `conference/` materials. A test or script greps for `TODO-DOI` placeholders and fails if any remain.

## 2. Acceptance checklist (gate)
- [ ] Release zip built, checksums written, size noted.
- [ ] Datasheet complete (every section filled, assumptions list generated, not hand-typed).
- [ ] Reproducibility check done and recorded.
- [ ] HUMAN steps listed with exact click-by-click instructions in the gate report.
- [ ] No `TODO-DOI` placeholders left after Tea completes the HUMAN steps.
