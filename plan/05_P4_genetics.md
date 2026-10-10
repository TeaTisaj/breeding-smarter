# P4: Genetics and observations

**Goal:** give the simulated animals genetics and give the registry realistic, incomplete observations of it:
1. neutral gene drop for **true identity by descent** (ground truth for inbreeding),
2. **Mendelian disease loci** with DNA testing,
3. a **polygenic hip dysplasia (HD)** trait with FCI A to E screening,
4. **EBVs** from a pedigree BLUP evaluation using only registry data, like a kennel club would compute them.

**Effort:** 1 day. **Depends on:** P3 (hooks). Task 4.6 also needs P2 (inbreeding for the A-inverse).

Module: `src/breeding_smarter/sim/genetics.py` (simulation side) and `src/breeding_smarter/evaluation/blup.py` (EBV side; create the `evaluation` subpackage).

---

## 1. Tasks

### 4.1 [MVP] `DogGenetics(GeneticsModel)` skeleton
Implements the four hooks from P3. Holds its own arrays (indexed by gid, growable): `tbv_hd`, `hd_liability`, `hd_grade_observed`, `f_true_ibd`, `disease_genotype[n, n_loci]` (int8 risk-allele count), `dna_tested[n, n_loci]` (bool), and the neutral allele store (4.2). All randomness through the passed `rng`.

### 4.2 [MVP] Neutral gene drop (true IBD)
- `n_neutral_loci = 200` unlinked loci (config; assumption). Standard error of a single animal's realised IBD is about `sqrt(F(1-F)/200)`, about 0.03 at F = 0.25, which is fine for population means and for showing individual spread.
- Base founders: allele ids `2*k` and `2*k+1` for founder `k` (same ids at every locus; loci are independent so this is valid and saves memory).
- Offspring: at each locus take one random allele from each parent (`rng.integers(0, 2, size=(n_children, n_loci))`).
- `f_true_ibd = mean over loci of (allele_from_sire == allele_from_dam)`.
- Memory: keep neutral alleles **only for living animals** (int32, shape `[n_alive, n_loci, 2]`); drop rows at death (compact once per year with an index map). Store `f_true_ibd` for everyone.

### 4.3 [MVP] Mendelian disease loci
`configs/loci/dog_mendelian.yaml`:
```yaml
loci:
  - id: PRCD_PRA     # progressive rod-cone degeneration
    gene: PRCD
    mode: recessive
    penetrance: {value: 0.95, assumption: true}
    test_available_from: {value: 2005, assumption: true}
  - id: SOD1_DM      # degenerative myelopathy, incomplete penetrance
    gene: SOD1
    mode: recessive
    penetrance: {value: 0.5, assumption: true}
    test_available_from: {value: 2009, assumption: true}
  - id: ABCB1_MDR1   # multidrug sensitivity
    gene: ABCB1
    mode: recessive
    penetrance: {value: 1.0, assumption: true, note: "phenotype = drug sensitivity"}
    test_available_from: {value: 2004, assumption: true}
  - id: DNM1_EIC     # exercise-induced collapse
    gene: DNM1
    mode: recessive
    penetrance: {value: 0.8, assumption: true}
    test_available_from: {value: 2008, assumption: true}
  - id: NOVEL_X      # fictional untested recessive, never testable
    gene: none
    mode: recessive
    penetrance: {value: 1.0, assumption: true}
    test_available_from: null
base_allele_frequency:          # in the base founders; illustrative, assumption
  SYN_L: {PRCD_PRA: 0.08, SOD1_DM: 0.25, ABCB1_MDR1: 0.0, DNM1_EIC: 0.10, NOVEL_X: 0.05}
  SYN_M: {PRCD_PRA: 0.05, SOD1_DM: 0.15, ABCB1_MDR1: 0.12, DNM1_EIC: 0.0, NOVEL_X: 0.05}
  SYN_S: {PRCD_PRA: 0.12, SOD1_DM: 0.10, ABCB1_MDR1: 0.0, DNM1_EIC: 0.0, NOVEL_X: 0.05}
```
- All frequencies are **illustrative assumptions**. The dataset card must say so. [STRETCH] task 4.8 calibrates them from the Donner 2023 Dryad data.
- `NOVEL_X` is deliberate: it lets the experiments show that managing kinship also protects against a disease nobody can test for. Keep it out of every observed table and out of the recommender; it exists only in truth.
- Founders: genotypes drawn under Hardy-Weinberg from the base frequency. Offspring: one random allele from each parent.

### 4.4 [MVP] DNA testing (observations)
Each year, for each living breeding candidate older than 12 months and each testable locus with `year >= test_available_from` that is not yet tested: test with probability `dna_test_rate(year)`, a linear ramp from 0.1 in the availability year to `dna_test_rate_2026` (breed config, assumption, for example 0.6). Imports and foreign AI sires are tested with probability 0.7 when they enter (assumption). Results are exact (lab error out of scope). Record `test_date`, a fictional `lab`.

Breeder behaviour that uses DNA results (extends `MarketStrategy` from P3, config flags):
- Known `affected` animals are not eligible for breeding with probability 0.8 (assumption).
- A pair where both are known carriers (or worse) at the same locus is resampled with probability 0.9 (assumption).
This keeps history realistic: since the 2000s breeders use DNA tests.

### 4.5 [MVP] Polygenic HD trait
Liability-threshold model, phenotypic variance 1 in the base population.
- `h2 = 0.35` (assumption inside the 0.25 to 0.7 range, source skk-hd-2020); `sigma_a2 = h2`, `sigma_e2 = 1 - h2`.
- Founders: `tbv ~ N(0, sigma_a2)`.
- Offspring: `tbv = 0.5 (tbv_s + tbv_d) + N(0, 0.5 * (1 - 0.5 (F_s + F_d)) * sigma_a2)` with `F` = parents' `f_true_ibd` (infinitesimal model with inbreeding-adjusted Mendelian sampling).
- Liability at screening: `tbv + N(0, sigma_e2)`.
- Grades: fixed thresholds computed once from base-population normal quantiles so that the base grade distribution matches the breed config `hd_base_distribution` (assumption, for example L: A 0.45, B 0.25, C 0.17, D 0.09, E 0.04; M: A 0.55, B 0.25, C 0.12, D 0.06, E 0.02; S: A 0.60, B 0.22, C 0.11, D 0.05, E 0.02). Selection then changes prevalence over time, as in Sweden (skk-hd-2020).
- Screening: from `hd_screening_start_year` (breed config, assumption, for example 1985), breeding candidates aged 12 to 24 months are screened with probability `hd_screening_rate` (assumption 0.7 for candidates, 0.05 for non-candidates). Record a `health_tests` row with grade, date, age in months, `official = true`.
- Eligibility: grade in breed `hd_exclude_grades` (default `[E]`, source hks-pravilnik: E/I and E/II excluded) makes the animal ineligible.

### 4.6 [MVP] EBV evaluation (pedigree BLUP), `evaluation/blup.py`
Run after the simulation on **registry data only** (registered pedigree, observed grades), once per breed, evaluation date `2026-09-30`.
- Response: grade as score `A=1, B=2, C=3, D=4, E=5` (linear model on the categorical score, the common practical approach; document the simplification).
- Model: `y = mu + birth_year_group + sex + animal + e`, birth-year groups of 5 years.
- `lambda = sigma_e2 / sigma_a2 = (1 - h2) / h2` using the true simulation `h2` (state this; a real evaluation would estimate variance components).
- A-inverse with Henderson's rules including inbreeding (uses `D` from P2): for animal i with `b = 1/D_i`, add `b` to `(i,i)`; `-b/2` to `(i,s), (s,i), (i,d), (d,i)` for each known parent; `b/4` to `(s,s), (d,d), (s,d), (d,s)` for known parents (only the pairs that exist). Build as COO then CSR.
- Solve the mixed model equations with `scipy.sparse.linalg.cg` and a Jacobi preconditioner (tolerance 1e-8, fall back to `spsolve` if it does not converge). Small fixed-effect block is fine inside the same sparse system.
- Reliability (approximation, document it): `r2_own = h2` if own record; `r2_prog = n_p / (n_p + (4 - h2) / h2)` for `n_p` progeny with records; `r2_par = 0.25 * (r2_sire + r2_dam)` from a first pass using own and progeny only; combined `r2 = 1 - (1 - r2_own)(1 - r2_prog)(1 - r2_par)`; `accuracy = sqrt(r2)`. [STRETCH] exact PEV for the small breed by direct inversion.
- Index scale: `ebv_index = 100 - 10 * ebv / sd(ebv of animals born in the last 5 years)` so higher is better (SKK convention).
- Write `registry/ebv.parquet`. CLI: `bsm ebv --run <run_id>` (also called automatically at the end of `bsm generate`).

### 4.7 [MVP] Wire up and regenerate
`bsm generate` uses `DogGenetics` by default. Produce dataset **v0** with the default config and seed 42. Fill truth columns.

### 4.8 [STRETCH] Calibrate base allele frequencies from Donner 2023
Download the CC0 Dryad data (doi:10.5061/dryad.tdz08kq3j) manually ([HUMAN] if the network blocks it), compute per-variant frequencies for a few real breeds, and choose base frequencies so that 2026 frequencies fall in observed ranges. Record what was used in `configs/loci/` with `source: donner-2023`.

---

## 2. Tests
- Gene drop: offspring of a full-sib mating of unrelated founders have mean `f_true_ibd` within 3 standard errors of 0.25 (simulate 2000 offspring; slow test).
- Mendelian loci: carrier x carrier offspring proportions 1:2:1 (chi-square p > 0.001 over 10k offspring; slow).
- Allele frequency is preserved in expectation under random mating (mean drift across 50 replicate small runs near 0).
- HD: base-population phenotypic variance in [0.9, 1.1]; regression of offspring tbv on mid-parent tbv slope in [0.95, 1.05].
- A-inverse: for random small pedigrees (n up to 80), Henderson's A-inverse equals `inv(A_dense)` (atol 1e-8). Property test.
- BLUP: on a tiny simulated breed, `corr(EBV, TBV) > corr(-grade score, TBV)` among screened animals with at least 5 screened progeny.
- DNA test results always equal the true genotype; `NOVEL_X` never appears in registry tables.
- Neutral alleles are dropped for dead animals (memory test: array rows equal living count after compaction).

## 3. Acceptance checklist (gate)
- [ ] Dataset v0 generated (default config, seed 42); `validate_run` passes.
- [ ] All tests pass (slow ones included, results in gate report).
- [ ] Gate report numbers: per breed, mean `f_true_ibd` of the 2025 cohort, allele frequencies 1980 vs 2026, carrier share 2026, HD grade distribution by decade, number of animals with EBVs, mean accuracy, `corr(EBV, TBV)` for screened candidates.
- [ ] Simulation wall time still within the P3 target (report the increase).
