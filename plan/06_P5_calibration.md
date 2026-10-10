# P5: Calibration and validation

**Goal:** prove the synthetic data is realistic enough to be useful, with a reproducible "target vs simulated" report, and prove the engine is right against ground truth. Freeze **dataset v1**, the version used in every later phase and published in P10.
**Effort:** 1 day. **Depends on:** P2 and P4.

Module: `src/breeding_smarter/calibration/`.

This is the phase that answers the first question any vet or geneticist will ask: "Why should I believe your fake data?" The report it produces goes straight into the paper, poster and dataset card.

---

## 1. Tasks

### 5.1 [MVP] Targets file `configs/calibration/targets.yaml`
Each target: `id`, `description`, `metric` (function name in `calibration/metrics.py`), `scope` (breed or all), `cohort`, `target` (value or range), `tolerance`, `source` or `assumption`, `kind` (`hard`: must pass; `soft`: warn only; `report`: no target, shown for context).

| id | Metric | Target | Kind | Source |
|---|---|---|---|---|
| T01 | Mean litter size per breed (registry era) | configured mean +/- 0.3, all breeds inside 3.5 to 7.1 | hard | borge-2011 |
| T02 | Share of litters with at least one perinatal loss | 24.6% +/- 5 percentage points | soft | tonnessen-2012 |
| T03 | Share of registered dogs (born 2005 to 2015) with recorded offspring | 10% to 30% | soft | calboli-2008 (secondary) |
| T04 | Share of registered males (born 2005 to 2015) that sired a litter | 2% to 20% | soft | kc-demography-2025 (one breed, weak) |
| T05 | Share of puppies (2016 to 2025) sired by the top 20% of active sires | at least 40% | soft (the source is historical) | haynes-1915 |
| T06 | At least one sire above the FCI 5%-in-5-years threshold (2016 to 2025) | true for SYN_M and SYN_S; report for SYN_L | soft | lewis-2015, leroy-rognon-2012 |
| T07 | Ne by individual increase in inbreeding, 2016 to 2025 cohort | L 200 to 900, M 80 to 150, S 25 to 50 | hard | lewis-2015 |
| T08 | Ne census (breeding animals), same cohort | report, plus FKC flag if at most 200 | report | fkc-strategy |
| T09 | Generation interval | 4 to 5 years | soft | assumption |
| T10 | Rate of inbreeding per generation higher in 1985 to 1995 than in 2010 to 2020 | true | soft | lewis-2015 |
| T11 | Recorded pedigree F < true pedigree F for the 2025 cohort | true for every breed | hard | pde-2011 (founder effect) |
| T12 | Engine vs gene drop: mean `f_true_ibd` minus mean F on the full true pedigree, per birth decade | absolute difference under 0.01 | hard | internal validation |
| T13 | Regression of `f_true_ibd` on true pedigree F (all animals born after 1980) | slope 0.9 to 1.1, intercept within +/- 0.01 | hard | internal validation |
| T14 | HD: share of D and E grades decreases after screening starts (first 5 screening years vs 2021 to 2025) | true | soft | skk-hd-2020 |
| T15 | EBV quality: `corr(EBV, TBV)` vs mean reported accuracy for screened candidates | within 0.1 | soft | internal validation |
| T16 | Imports and missingness: share of HUR animals, share of imports, share of unknown parents per decade | report | report | assumption |
| T17 | Mean genomic-style F (`f_true_ibd`) of the 2025 cohort | report next to the published median of about 0.25, with a note that the bases differ | report | bannasch-2021 |

T10 needs time-varying market behaviour: make `popular_sire_alpha` a list of `(year, value)` points in the breed config (for example higher before 2000) and interpolate, like registrations. Mark the points as assumptions tuned to T10.

### 5.2 [MVP] `calibration/metrics.py`
One pure function per metric, input = loaded run tables (+ cached F/D from P2) and parameters; output = value(s) plus the data behind them (for plotting). Reuse `pedigree/population.py` wherever possible; no duplicated formulas.

### 5.3 [MVP] Fill `f_true_pedigree`
Compute F with the P2 engine on the **full true pedigree** (`Pedigree.from_truth`) and write it into `truth/animals_truth.parquet` (`bsm validate` does this when the column is empty, and stores engine version in the manifest).

### 5.4 [MVP] `calibration/report.py` and `bsm validate --run <id>`
Produces `reports/validation/<run_id>/`:
- `validation_report.md`: summary (counts of PASS, WARN, FAIL), the target table with simulated values and status, then one short section per target with its figure. Starts with the sentence: "All animals in this dataset are synthetic."
- `targets_vs_simulated.csv` (the same table, machine-readable; reused by the dataset card and the paper).
- Figures (matplotlib, 300 dpi PNG plus SVG, consistent style module `calibration/plotstyle.py` reused in P8 and P11):
  1. registrations per year per breed
  2. litter size distribution per breed vs target mean
  3. offspring per sire (log-log rank plot) and Lorenz curve per breed
  4. mean F per birth year: recorded pedigree F, true pedigree F, realised IBD (three lines per breed). **This is a key poster figure**: it shows the underestimation of recorded COI.
  5. scatter `f_true_ibd` vs true pedigree F with the 1:1 line
  6. Ne per breed vs target band
  7. HD grade shares per 5-year period
  8. carrier frequency per locus 1980 vs 2026
- `bsm validate` exits with code 1 if any `hard` target fails (so CI can use it on the tiny run with relaxed targets file `targets_tiny.yaml`).

### 5.5 [MVP] Calibration loop `bsm calibrate`
- `configs/calibration/grid.yaml`: per breed, small grids over `popular_sire_alpha` points, `attractiveness beta`, candidate shares, `close_mating_avoidance`. At most about 30 combinations per breed.
- Run each combination per breed separately (`--breeds`), at scale 0.25 for SYN_L and 1.0 for SYN_M and SYN_S, 2 seeds each; score = number of failed hard targets, then summed normalised distance to soft targets.
- Output a ranked table `reports/validation/calibration_grid.csv`. **Do not auto-edit configs**: print the best combination and let Tea approve, then write the values into the breed YAML with `note: "tuned in P5, see calibration_grid.csv"`.
- Keep it simple. If the default values already pass all hard targets, skip the grid and say so in the gate report.

### 5.6 [MVP] Freeze dataset v1
- Generate the final run (`seed 42`, default config). Run `bsm validate`. All hard targets pass.
- Tag the run id in `configs/datasets.yaml` as `v1` (`run_id`, config hash, git commit). Later phases load data by dataset tag, never by hard-coded run id.
- Sensitivity runs (seeds 1, 2, 3): report the spread of T05, T07, T11 values across seeds in the gate report (shows results are not a lucky seed).

## 2. Tests
- Each metric function on a tiny hand-made dataset with a known answer (for example the Gini of `[1,1,1,1]` is 0; top-20% share of `[10,1,1,1,1]` is 10/14).
- `bsm validate` on the tiny run produces all files and the right exit code with `targets_tiny.yaml`.
- Report generation is deterministic (same run, same markdown).

## 3. Acceptance checklist (gate)
- [ ] Dataset v1 frozen and tagged; all hard targets pass; soft-target warnings explained in the gate report.
- [ ] T12 and T13 pass (this is the main correctness evidence for the engine).
- [ ] Validation report and figures generated; Tea has looked at figure 4.
- [ ] Seed sensitivity table in the gate report.
- [ ] All remaining `assumption: true` values listed, so the dataset card can list them.
