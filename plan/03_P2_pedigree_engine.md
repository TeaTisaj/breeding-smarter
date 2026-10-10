# P2: Pedigree engine

**Goal:** a correct, fast, well-tested library for inbreeding, kinship, mean kinship, diversity, Ne, founder contributions, completeness and exact inbreeding explanations. This is the scientific core. Correctness beats speed; speed must still meet the targets.
**Effort:** 1.5 days. **Depends on:** P1 (fixtures, schema). Can run in parallel with P3.

Module: `src/breeding_smarter/pedigree/`. All functions are pure (no I/O). Hot loops in numba with a pure Python twin used in tests.

---

## 1. Notation (put this block in the module docstring)

- Animals are numbered `0..n-1` in birth order; `sire[i] < i`, `dam[i] < i`, unknown parent `-1`.
- **A** is the numerator relationship matrix; `A[i,i] = 1 + F_i`; kinship `f_ij = A[i,j] / 2`.
- The inbreeding of a (possibly hypothetical) offspring of `a x b` equals `f_ab`.
- Decomposition `A = L D L'` (equivalently `A = T D T'` with `T = (I - P)^-1`, `P[i,s] = P[i,d] = 0.5`).
- **D** (Mendelian sampling variance) with the convention `F[-1] = -1` for unknown parents:
  `D_i = 0.5 - 0.25 * (F_s + F_d)`. This gives `0.5 - 0.25(F_s+F_d)` with both parents known, `0.75 - 0.25 F_known` with one known, and `1.0` with none.

References: Meuwissen and Luo 1992; Colleau 2002; Sargolzaei et al. 2005 (see `docs/research.md` section 6).

`docs/reference/algorithm_check.py` is a plain-Python prototype of the algorithms in this file (Meuwissen and Luo, Colleau, virtual-offspring kinship, ancestor decomposition, Henderson's A-inverse, EqG, founder contributions with phantom parents), checked against the dense oracle on 40 random pedigrees while writing this plan: all agree to floating-point precision. Use it as a reference and as a starting point for the test oracle, not as production code.

---

## 2. Tasks

### 2.1 [MVP] `pedigree/core.py`: the `Pedigree` container
```python
@dataclass(frozen=True)
class Pedigree:
    sire: np.ndarray  # int64, -1 unknown
    dam: np.ndarray  # int64, -1 unknown
    sex: np.ndarray  # int8, 0 = female, 1 = male
    birth_year: np.ndarray  # int16
    breed: np.ndarray  # int16 codes
    ids: np.ndarray  # original idx or gid (int64), for mapping back
    breed_codes: tuple[str, ...]
```
- `Pedigree.from_registry(animals_df)` and `Pedigree.from_truth(animals_truth_df)` (truth uses `true_sire_gid`, `true_dam_gid`).
- `validate()`: topological order, sex of parents, no self-parenting. Raise `PedigreeError` with offending rows.
- `prune(keep: np.ndarray) -> tuple[Pedigree, np.ndarray]`: keep the given animals plus all their ancestors, renumber preserving order, return the old-to-new index map. Implement with a backward sweep marking ancestors (O(n)).
- `with_phantom_parents() -> Pedigree`: for animals with exactly one known parent, insert a unique phantom founder for the missing one (needed so founder contributions sum to 1). Phantom rows get `ids = -1`. Insert phantoms before their child to keep topological order (rebuild arrays; O(n)).
- `offspring_index()`: CSR-style arrays of children per animal (used in relationships and explanations).

### 2.2 [MVP] Known-answer tests first: `tests/unit/test_pedigree_known.py`
Use the fixtures from P1 task 1.5. Expected values (derive each in the test docstring):

| Fixture | Mating | Expected F of offspring |
|---|---|---|
| unrelated | A x B | 0 |
| full_sibs | children of A x B mated together | 0.25 |
| half_sibs | children of A x B and A x D mated | 0.125 |
| parent_offspring | A x (daughter of A) | 0.25 |
| first_cousins | children of two full sibs mated | 0.0625 |
| repeated_full_sib | 3 generations of full-sib mating | 0.25, 0.375, 0.5 (recurrence F_t = 1/4 (1 + 2 F_{t-1} + F_{t-2})) |
| inbred_ancestor | half sibs through sire S with F_S = 0.25 | (1/2)^3 (1 + 0.25) = 0.15625 |

Also: `f(A, A) = 0.5` for a non-inbred founder; `f(S, S) = 0.625` for S with F = 0.25; `f(parent, offspring) = 0.25` for non-inbred unrelated parents; `f(full sibs) = 0.25`; `f(half sibs) = 0.125`.

### 2.3 [MVP] `pedigree/reference.py`: dense tabular method (test oracle only)
`relationship_matrix_dense(ped) -> np.ndarray` for `n <= 3000`:
```
for i in 0..n-1:
    s, d = sire[i], dam[i]
    for j in 0..i-1:
        A[i,j] = A[j,i] = 0.5 * ((A[j,s] if s>=0 else 0) + (A[j,d] if d>=0 else 0))
    A[i,i] = 1 + (0.5 * A[s,d] if s>=0 and d>=0 else 0)
```
Never used outside tests and the benchmark baseline.

### 2.4 [MVP] `pedigree/inbreeding.py`: Meuwissen and Luo
`inbreeding(ped) -> tuple[F: np.ndarray, D: np.ndarray]`

Algorithm (numba `@njit`), animals processed in order:
```
F_ext[-1] := -1  (store F with an offset so index -1 maps to the sentinel)
for i in 0..n-1:
    s, d = sire[i], dam[i]
    D[i] = 0.5 - 0.25 * (F(s) + F(d))          # sentinel handles unknown parents
    if s < 0 or d < 0:  F[i] = 0; continue     # one unknown parent: no common ancestor recorded
    if i > 0 and s == sire[i-1] and d == dam[i-1]:  F[i] = F[i-1]; continue   # full-sib shortcut
    # compute row i of L restricted to ancestors, accumulate sum L_ij^2 D_j
    Lval[i] = 1; push i on max-heap
    acc = 0
    while heap not empty:
        j = pop max (also pop and skip duplicates of j)
        acc += Lval[j]^2 * D[j]
        if sire[j] >= 0: Lval[sire[j]] += 0.5 * Lval[j]; push sire[j]
        if dam[j]  >= 0: Lval[dam[j]]  += 0.5 * Lval[j]; push dam[j]
    F[i] = acc - 1
    reset Lval for every touched index (keep a touched list; do not reallocate)
```
Why it is correct: ancestors have smaller indices than descendants, so popping the largest index first guarantees all contributions to `Lval[j]` arrive before `j` is processed. `D[i]` of the animal itself is included through `j = i`.

Implementation notes:
- Use a numba-compatible binary max-heap on a preallocated int64 array (write a tiny `heap_push`/`heap_pop`; do not rely on `heapq` with typed lists). Deduplicate with a `in_heap` boolean array instead of skipping duplicates.
- The full-sib shortcut needs offspring of the same litter to be adjacent; the simulator guarantees it (litter mates get consecutive indices). It is an optimisation only; a test runs with the shortcut disabled and compares.
- Provide `inbreeding_py(ped)` (same algorithm, plain Python, dict-based) for tests.
- Provide `inbreeding_extend(ped, F, D, start) -> (F, D)`: computes F and D only for animals with index `>= start`, reusing the given values for older animals. The loop above is naturally incremental. P8 uses this every simulated year. Test: extending in several chunks equals one full computation.

### 2.5 [MVP] L-rows and pair kinship
- `l_row(ped, D, i) -> tuple[anc: np.ndarray, L: np.ndarray]` returns the non-zero entries of row `i` of L (ancestors of `i` plus `i` itself, with `L_ii = 1`). Same traversal as 2.4.
- `l_row_virtual(ped, D, F, a, b)`: row of a hypothetical offspring of `a x b`.
- `pair_kinship(ped, F, D, a, b) -> float` = F of the virtual offspring of `a x b` = `sum_j Lx_j^2 D_j - 1` with `D_x = 0.5 - 0.25 (F_a + F_b)`. Handle `a == b` (returns `(1 + F_a)/2`).
- `pair_kinship_decomposed(ped, F, D, a, b) -> dict[int, float]`: contributions `c_j = 0.5 * L_aj * L_bj * D_j` over ancestors `j` common to the rows of `a` and `b` (including `a` or `b` themselves if one is an ancestor of the other). The sum equals `f_ab` exactly (identity `A = L D L'`). This powers the explanation in P7.

### 2.6 [MVP] `pedigree/kinship.py`: Colleau indirect method
`A_times(ped, D, x) -> y` computes `y = A x` in O(n) without forming A:
```
u = x.copy()                                # step 1: u = T' x  (youngest to oldest)
for i in n-1 .. 0:
    if sire[i] >= 0: u[sire[i]] += 0.5 * u[i]
    if dam[i]  >= 0: u[dam[i]]  += 0.5 * u[i]
w = D * u                                   # step 2
y = zeros(n)                                # step 3: y = T w  (oldest to youngest)
for i in 0 .. n-1:
    y[i] = w[i] + 0.5 * ((y[sire[i]] if sire[i] >= 0 else 0) + (y[dam[i]] if dam[i] >= 0 else 0))
```
Built on it:
- `kinship_to_all(ped, D, a) -> np.ndarray` = `0.5 * A_times(e_a)`: kinship of `a` with every animal (one dam vs all candidate sires in one O(n) pass).
- `mean_kinship(ped, D, ref_mask) -> np.ndarray` = `0.5 * A_times(ref_mask / ref_mask.sum())`: MK of every animal to the reference population (self-kinship included, PMx convention; document it).
- `kinship_matrix(ped, D, members) -> np.ndarray` for small sets (K up to about 2000): prune to the ancestors of `members` first, then K calls of `A_times`.
- `contributions(ped_with_phantoms, ref_mask) -> np.ndarray`: step 1 only, `u = T' x` with `x = ref/N`; for founders `u_k` is the expected genetic contribution `p_k` to the reference population.

### 2.7 [MVP] `pedigree/completeness.py`
- `equivalent_generations(ped) -> np.ndarray`: `EqG_i = sum over known parents p of 0.5 * (1 + EqG_p)` (O(n), forward pass). Equals the sum over all known ancestors of `(1/2)^generations`, counting each path.
- `max_generations`, `complete_generations` (both parents known recursively): `complete_i = 1 + min(complete_s, complete_d)` if both known else 0; `max_i = 1 + max(...)` if any known else 0.
- `completeness_index(ped, depth=5)` (MacCluer style, optional, [STRETCH]).

### 2.8 [MVP] `pedigree/population.py`: population metrics
For a breed and a reference cohort (default: animals born in the last generation interval before a given year):
- `generation_interval(ped, ref_mask)`: mean age of parents (years) at birth of reference animals, all four pathways pooled; also report the sire and dam pathways separately.
- `ne_individual_delta_f(F, eqg, ref_mask)`: `dF_i = 1 - (1 - F_i)^(1/(t_i - 1))` for `t_i = EqG_i > 1`; `Ne = 1 / (2 * mean dF)` (Gutiérrez et al.). Report n used and how many were excluded.
- `ne_census(ped, ref_mask)`: `Nm`, `Nf` = distinct sires and dams of the reference cohort; `Ne = 4 Nm Nf / (Nm + Nf)`. Label it "census (breeding animals)".
- `gene_diversity(mk, ref_mask)`: `GD = 1 - mean(MK over ref)`.
- `founder_stats(ped, ref_mask)`: number of founders contributing, `fe = 1 / sum(p_k^2)`, `fg = 1 / (2 * mean kinship of ref)`, top 10 founders by contribution, check `sum p_k == 1` (tolerance 1e-9).
- `sire_usage(ped, window_years, year)`: offspring per sire in the window, share of the top sire, top-20% share, Gini coefficient, share of males of breeding age that sired at least one litter, FCI 5%-rule ratio (offspring of each sire / 5% of breed registrations in the window).
- `population_report(...) -> PopulationReport` (pydantic model) combining all of the above plus mean F of the cohort, mean MK, mean EqG.
- [STRETCH] effective number of ancestors `fa` (Boichard et al. 1997).

### 2.9 [MVP] `pedigree/relationships.py`
Exact relationship classification used by the rule engine (P6), based on the recorded pedigree only:
- `relationship(ped, a, b) -> set[Relationship]` with members: `SELF`, `PARENT_OFFSPRING`, `FULL_SIBLINGS`, `HALF_SIBLINGS`, `GRANDPARENT_GRANDCHILD`, `AUNT_UNCLE_NIECE_NEPHEW` (informational), `NONE_DETECTED`.
- Half siblings: exactly one known parent in common. Full siblings: both known parents in common.
- Grandparent: `a` in the set of known grandparents of `b` or vice versa.
- Also return `generations_to_nearest_common_ancestor(a, b, max_depth=6)` via bidirectional BFS on parents.

### 2.10 [MVP] CLI and caching
- `bsm metrics --run <run_id> [--breed SYN_M] [--year 2026]` computes F and D for the run once, caches them to `data/generated/<run_id>/cache/pedigree_F_D.parquet` (keyed by run_id and engine version), and prints the population report as a table (rich). `--json` option for machine output.

### 2.11 [MVP] Benchmarks
`tests/benchmarks/test_speed.py` marked `slow`: random realistic pedigrees (use the simulator later; for now a synthetic generator with overlapping generations, 10k, 50k, 250k animals). Record times in `reports/benchmarks/engine.md`.
Targets on a laptop: `inbreeding` for 250k animals under 60 s; `A_times` under 1 s; `kinship_to_all` under 1 s; `pair_kinship` under 10 ms.

---

## 3. Tests (all MVP)

Unit (known answers): section 2.2.

Property tests (`hypothesis`, `tests/property/test_pedigree_props.py`), random valid pedigrees with n up to 150, overlapping generations, 0 to 30% unknown parents:
1. `inbreeding(ped)[0] == diag(A_dense) - 1` (atol 1e-12).
2. `A_times(ped, D, x) == A_dense @ x` for random x.
3. `pair_kinship(a, b) == A_dense[a, b] / 2 == sum(pair_kinship_decomposed(a, b).values())`.
4. Shortcut on and off give identical F.
5. Pruning invariance: F, and kinships among kept animals, are unchanged after `prune`.
6. Founder contributions are non-negative and sum to 1 after `with_phantom_parents`.
7. `equivalent_generations` equals brute-force path enumeration for n up to 40.
8. `mean_kinship` equals the mean of the corresponding rows of `A_dense / 2`.
9. `numba` and pure Python versions agree.

Edge cases: empty pedigree, single animal, all founders, an animal with only a dam, a sire used across many generations (deep loops).

---

## 4. Acceptance checklist (gate)
- [ ] All known-answer tests pass.
- [ ] All property tests pass with at least 200 examples each.
- [ ] Benchmarks recorded and targets met (or documented deviation with a plan).
- [ ] Every public function has a docstring with formula and reference.
- [ ] `bsm metrics` works on a run folder written from the P1 fixture pedigrees (the simulator may not exist yet).
- [ ] mypy strict passes for `pedigree/`.
