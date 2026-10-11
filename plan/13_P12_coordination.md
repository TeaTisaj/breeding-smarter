# P12: Coordinated sire use (contribution control)

**Goal:** add a club-level coordination layer that decides **how many litters each sire may have this season**, and let mate choice (our existing recommender) work only inside those quotas. Then test, with pre-registered success criteria, whether coordination fixes the P8 finding: per-dam recommendations cut disease and short-term COI but did not raise long-term effective population size (Ne), and random mating kept the most diversity.

**Effort:** about 3 days. **Depends on:** P2 (engine), P6 (rules), P7 (recommender), P8 (experiment runner, observed registry). Dataset v1 is reused unchanged.

**Read first:** `docs/research_coordination.md` (sources, numbers and recommendations behind every choice below), `plan/gates/P8_report.md` (the finding), `CLAUDE.md`, `plan/00_OVERVIEW.md` section 7 (conventions).

**Framing rule (unchanged from P8):** all results are in silico on synthetic populations. Every figure caption says so. Results that contradict the expected story are reported, never tuned away.

---

## 0. Why this phase exists (one paragraph for the gate report and the poster)

Long-term inbreeding is driven by **how unevenly animals contribute genes**, not by how each pair is chosen. Per-dam ranking optimises each litter in isolation; when many breeders follow the same ranking they converge on the same sires (P8: SYN_M share of eligible males used 6.6% under S3 vs 13.4% under S1; Ne 187 vs 298). The literature predicts exactly this: in a Dutch Golden Retriever simulation, mating each dam to her least-related sire cut ΔF to 0.04% per generation in years 0 to 20 but it was back at 0.39% by years 50 to 70, while excluding high-mean-kinship animals held ΔF at 0.12 to 0.14% throughout [windig-2013]. Standard remedy: **optimum contribution selection (OCS)** decides contributions at population level under a kinship budget, and **mate allocation** fills those contributions with low-coancestry pairs [meuwissen-1997; wellmann-2019; sonesson-meuwissen-2000].

---

## 1. Design decisions (fixed before implementation)

| # | Decision | Choice | Basis |
|---|---|---|---|
| D1 | What is coordinated | **Sire contributions only.** Which dams are mated each year stays the simulator's decision (eligibility + demand), exactly as in P8, so every strategy mates the same dams and comparisons stay clean. | P8 section 1 ("same dams for every strategy"); real kennel-club levers are stud limits [fci-strategies; kennelliitto-pevisa-2026] |
| D2 | Decision unit | One planning round per simulated year per breed: the set of dams the simulator mated this year, and all eligible sires (domestic eligible males plus eligible foreign males with a registry record, as in P8 S3/S4). Re-solved every year with the updated pedigree ("dynamic"). | [du-2025; wellmann-2019; grundy-1998] |
| D3 | Kinship used | **Recorded pedigree kinship** (what a club has) in all main arms. One diagnostic **oracle** arm uses the **true** pedigree kinship from the simulator. | [sonesson-2012] (pedigree constraint overshoots ΔF ~4x with genomic selection); research note "kinship source" |
| D4 | OCS objectives | (a) **Conservation:** minimise expected coancestry `c'Kc` of the planned matings. (b) **Gain under a ΔF budget:** maximise mean HD breeding value index of the chosen sires subject to `c'Kc ≤ C_next`. | [pong-wong-woolliams-2007; gorjanc-hickey-2018] |
| D5 | Yearly kinship budget | `C_next = 1 − (1 − C_now)(1 − ΔF)^(1/L)` with `C_now` = `c'Kc` of last year's realised matings and `L` = generation interval estimated from the observed pedigree (mean parent age at birth, last 5 years). | [du-2025] formula form, exact yearly form marked unverified in the research note; `L` method [lewis-2015] |
| D6 | ΔF ladder (gain arm only) | 1.0%, 0.5%, 0.25% per generation; SYN_M also 0.1%. 0.5% (Ne 100) is the headline default; 1% (Ne 50) the floor. | [fao-2013; frankham-2014; lewis-2015; windig-2013] |
| D7 | Infeasible budget | Solve conservation first: `C_min`. If `C_next < C_min`, use `C_eff = C_min` (i.e. the gain arm falls back to the conservation solution) and log `infeasible = true`. | [du-2025] infeasibility warning; fallback is a project choice |
| D8 | Small-cohort term | Include the Du et al. term `(1/(2N)) Σ c_i (1 − k_ii)` in the gain-arm constraint (N = expected registered newborns this year = litters × expected registered litter size). Config flag, default on. | [du-2025] (verified); Wellmann & Bennewitz dispute it [wellmann-bennewitz-2019] |
| D9 | Per-sire upper bound | Per-year cap in litters, **scaled by the sire's mean kinship (MK)**: `cap_s = clip(round(cap_base × MK_ref / MK_s), 1, cap_base)`, `cap_base = 5` litters per year. Used by the CAP arm and as an upper bound inside OCS. | per-year caps 5 to 10 gave ΔF 0.18 to 0.27% [windig-2013]; flat caps can backfire [leroy-rognon-2012]; MK scaling is a project choice |
| D10 | Age structure | In OCS, at least one litter must go to sires of each of the two youngest breeding age classes that have candidates (age in whole years on Jan 1). | [sonesson-meuwissen-2001] (optimiser picked only the oldest animals; forcing contributions from younger classes fixed it) |
| D11 | Shallow pedigrees | Linear constraint: contribution-weighted mean equivalent complete generations (EqG) of chosen sires ≥ the unweighted mean EqG of the candidate sires. Stops OCS from favouring imports only because their records are short. | optiSel `lb.equiGen` idea [wellmann-2019] |
| D12 | From contributions to whole litters | Sainte-Laguë apportionment of the year's `n_d` litters over sires, respecting caps; sires with expected litters `< 0.25` get none (stops solver noise from becoming a litter). | [du-2025] |
| D13 | Mate allocation | **MC1:** assignment problem dams × (sires replicated by quota), cost = pair kinship + `w_h` × P(affected puppy), HARD-rule pairs forbidden, at most one litter per pair, solved exactly with `scipy.optimize.linear_sum_assignment`. **Random:** random assignment respecting quotas, HARD-rule pairs avoided. | [sonesson-meuwissen-2000] (MC1); assignment formulation is standard OR |
| D14 | Product mode | **S3q, recommender within quotas:** a shared booking ledger holds each sire's remaining quota for the season; each adopting breeder sees our ranked shortlist restricted to sires with quota left and picks among the top 3 (0.5 / 0.3 / 0.2, as S3). | research note "breeder freedom" (project choice) |
| D15 | Partial adoption | Non-adopters choose first (S2 behaviour); their sire contributions are **fixed** inputs to OCS, which then sets quotas for the adopters. | [pong-wong-woolliams-2007] fixed contributions (secondary) |
| D16 | Solver | `cvxpy` with the Clarabel solver (quadratic objective / quadratic constraint, convex). Fallback if the dependency fails on our numpy: `scipy.optimize.minimize(method="trust-constr")` for the conservation QP. Cross-check against `robustocs` on small cases. | [fogg-2024]; cvxpy |

Everything above that is a number lives in `configs/coordination/default.yaml` with `source:` or `assumption: true`.

---

## 2. Notation (put this block in `coordination/__init__.py`)

- Candidates this year: sires `S` (size m), mated dams `D` (size n_d, fixed). One litter per mated dam.
- `K` = kinship matrix (A/2) among `S ∪ D` from the recorded pedigree (`pedigree.kinship_matrix`).
- Contributions: `c = (s, d)`, with `Σ s = ½`, `d_j = 1/(2 n_d)` (fixed), `s ≥ 0`. Sire i's expected litters `ℓ_i = 2 n_d s_i`.
- Expected coancestry of the planned matings: `C(c) = c' K c = s'K_SS s + 2 s'K_SD d + d'K_DD d` (convex quadratic in `s`).
- Conservation OCS: `min_s C(c)` subject to bounds and constraints D9 to D11.
- Gain OCS: `max_s m's` subject to `C(c) + τ(c) ≤ C_eff` and the same constraints, where `m_s` = standardised HD EBV index of sire s (missing EBV = breed mean, as in P7) and `τ(c)` the small-cohort term (D8).
- Bounds: `0 ≤ s_i ≤ cap_i / (2 n_d)`.
- Age classes: for each of the two youngest non-empty age classes `a`: `Σ_{i∈a} s_i ≥ 1/(2 n_d)`.
- Depth: `Σ_i s_i EqG_i ≥ ½ · mean(EqG_S)`.

---

## 3. Tasks

### 12.0 [MVP] Dependency spike and decision record
- Add `cvxpy` and `clarabel` to the runtime dependencies; `uv sync --all-groups`; confirm they import with numpy 2.5 and numba 0.68 in the same environment.
- Solve a 3-sire toy problem (known answer in 12.4) with cvxpy+Clarabel and with the scipy fallback; time a 1,000-candidate random problem.
- Write `docs/decisions/ADR-007-ocs-solver.md` (context, decision, consequences).
- If cvxpy cannot be installed: implement the conservation QP with the scipy fallback only, run the gain arm only if a correct solver is available, and record the deviation.

### 12.1 [MVP] Sources and config
- Add citation keys to `docs/research.md` section 9 **and** `configs/sources.yaml` (the existing test requires both): `fao-2013`, `frankham-2014`, `windig-2013` (EAAP slides), `windig-oldenbroek-2015`, `windig-hulsegge-2021`, `kennelliitto-pevisa-2026`, `nkk-ras-2025`, `rvb-vfr-2025`, `grcn-vfr-2026`, `du-2025`, `wellmann-2019`, `wellmann-bennewitz-2019`, `pong-wong-woolliams-2007`, `sonesson-meuwissen-2000`, `sonesson-meuwissen-2001`, `sonesson-2012`, `grundy-1998`, `gorjanc-hickey-2018`, `fogg-2024`, `de-cara-2013`, `legarra-2015`, `leroy-baumung-2011`. Copy URLs/DOIs from `docs/research_coordination.md` "Sources".
- Add a short section 10 "Coordination (P12)" to `docs/research.md` listing the numbers used (ΔF ladder, caps, PEVISA range, FCI 5%), each with its key, marking unverified items exactly as the research note does.
- `configs/coordination/default.yaml` (pydantic model `CoordinationConfig`, `extra="forbid"`, every number `Sourced`):
  ```yaml
  delta_f_ladder: {value: [0.01, 0.005, 0.0025], source: fao-2013, note: "1% floor, 0.5% default (Ne 100), 0.25% Dutch 'small risk'"}
  delta_f_extra_medium: {value: [0.001], source: windig-2013, note: "SYN_M status quo is already ~0.17%"}
  delta_f_default: {value: 0.005, source: frankham-2014}
  generation_interval_window_years: {value: 5, assumption: true}
  small_cohort_term: {value: true, source: du-2025}
  cap_base_litters_per_year: {value: 5, source: windig-2013, note: "per-year caps 5-10 gave dF 0.18-0.27%"}
  cap_mk_scaling: {value: true, assumption: true, note: "flat caps can backfire (leroy-rognon-2012)"}
  min_expected_litters: {value: 0.25, source: du-2025}
  youngest_age_classes_required: {value: 2, source: sonesson-meuwissen-2001}
  depth_constraint: {value: true, source: wellmann-2019}
  health_weight_in_allocation: {value: 1.0, assumption: true, note: "cost = kinship + w x P(affected)"}
  lifetime_cap_offspring: {value: null, source: kennelliitto-pevisa-2026, note: "off by default; PEVISA range 15-120, most breeds 20-60 (sensitivity only)"}
  solver: {value: clarabel, assumption: true}
  ```
- Test: config loads; ladder values match the research note; unknown keys fail.

### 12.2 [MVP] `coordination/targets.py`
- `per_year(delta_f_gen, L) -> float` = `1 − (1 − ΔF)^(1/L)`.
- `next_budget(C_now, delta_f_gen, L) -> float` = `1 − (1 − C_now)(1 − ΔF)^(1/L)`.
- `ne_from_delta(delta) -> float` = `1/(2Δ)`.
- `estimate_generation_interval(ped, birth_year, year, window)` reusing `pedigree.population.generation_interval`.
- Docstrings carry the formulas and keys. Tests: worked example from the research note (`C_now = 0.10, ΔF = 0.005, L = 4 → 0.10113`, tolerance 1e-5); `per_year(0.005, 4) ≈ 0.00125`; round trips.

### 12.3 [MVP] `coordination/ocs.py`
Pure functions, strict typing (add `breeding_smarter.coordination.*` to the strict mypy list and to `scripts/check.sh` / CI).
```python
@dataclass
class OCSProblem:
    K: FloatArray            # (m + n_d) square, sires first
    n_dams: int
    caps: FloatArray         # litters per sire (upper bounds), length m
    age_class: IntArray      # per sire
    eqg: FloatArray          # per sire
    merit: FloatArray | None # per sire (gain objective)
    fixed_sire_litters: FloatArray | None  # partial adoption: litters already booked by non-adopters
    n_newborn: float         # for the small-cohort term

@dataclass
class OCSResult:
    litters: FloatArray      # continuous expected litters per sire (sums to n_d)
    coancestry: float        # C(c) achieved
    objective: str           # "conservation" | "gain"
    target: float | None
    infeasible: bool
    status: str
    seconds: float

def solve_conservation(p: OCSProblem, cfg) -> OCSResult
def solve_gain(p: OCSProblem, budget: float, cfg) -> OCSResult   # falls back to conservation if infeasible (D7)
def expected_coancestry(K, sire_litters, n_dams) -> float
```
- Build `c` from litters: `s = litters / (2 n_d)`; dams `1/(2 n_d)`.
- Use `cp.quad_form` with a PSD-projected `K` (symmetrise; if the smallest eigenvalue < 0 due to round-off, add `|λ_min| + 1e-12` to the diagonal and log it).
- Constraints D9 to D11, `Σ s = ½`, fixed non-adopter litters as lower bounds equal to booked litters for those sires plus their share in the sum.
- Gain: `max m's` s.t. `C(c) + τ(c) ≤ budget`.
- Return status and timing; never raise on infeasible, return `infeasible=True`.

### 12.4 [MVP] Known-answer and property tests for OCS (write before 12.3 is finished)
`tests/unit/test_ocs.py`:
1. Two unrelated non-inbred sires, dams unrelated to both, no caps: conservation solution splits litters equally (`|ℓ1 − ℓ2| < 1e-6`).
2. Sires are full sibs of each other and a third sire unrelated: conservation puts more on the unrelated sire; exact value from the closed form of the 3×3 problem (derive in the docstring).
3. A sire who is the sire of half the dams vs an unrelated sire: unrelated sire gets those dams' share (coancestry lower).
4. Caps bind: with cap 1 and 3 dams, each of 3 sires gets exactly 1.
5. Age-class constraint forces at least one litter to the youngest class even if its sires are more related.
6. Depth constraint excludes a shallow-pedigree sire that would otherwise win.
7. Gain: with a loose budget all litters go to the highest-merit sires up to caps; with a tight budget the solution approaches the conservation solution; budget below `C_min` → `infeasible=True` and conservation result.
8. Property (hypothesis, random small pedigrees from `tests/fixtures/random_ped.py`): solution satisfies all constraints within 1e-7; `C(conservation) ≤ C(any feasible random allocation)` (sample 20 random feasible allocations); `C(equal split)` ≥ `C(conservation)`.
9. Cross-check (skip if `robustocs` not installed): conservation optimum equals `robustocs` result on 5 random problems within 1e-6.
10. `expected_coancestry` equals the brute-force mean kinship of all offspring pairs implied by the matings on a toy case.

### 12.5 [MVP] `coordination/quotas.py`, `coordination/allocation.py`, `coordination/caps.py`, `coordination/ledger.py`
- `caps.mk_scaled_caps(mk, mk_ref, cap_base) -> IntArray` (D9). Tests: boundaries, monotone in MK.
- `quotas.sainte_lague(expected, total, caps, min_expected) -> IntArray`: divisors `1, 3, 5, …`, skip sires at cap, sires with `expected < min_expected` excluded; if the sum of caps < total, raise caps by 1 for the lowest-MK sires until feasible and report `relaxed`. Tests: textbook apportionment example; sums to total; respects caps; never gives a litter below threshold; deterministic tie-breaking (lower index wins).
- `allocation.assign_mc1(K_pair, p_affected, forbidden, quotas, w_h) -> IntArray` (sire per dam, −1 if no allowed seat): `linear_sum_assignment` on dams × replicated seats; forbidden cost `1e6`; result rows with cost ≥ 1e6 → −1. Tests: brute force on 4 dams × 3 sires; quotas respected; forbidden never chosen; one litter per pair.
- `allocation.assign_random(quotas, forbidden, rng)`. Tests: quotas respected; forbidden avoided; deterministic with a seed.
- `ledger.BookingLedger(quotas)`: `available()`, `book(sire)`, `remaining(sire)`; raises if over-booked. Tests.

### 12.6 [MVP] `coordination/planner.py`: one planning round
```python
def plan_season(ctx: DatasetContext, breed: str, day: int, dams: IntArray, sires: IntArray,
                cfg: CoordinationConfig, control: str, mating: str,
                K_override: FloatArray | None = None, delta_f: float | None = None,
                fixed_sire_litters: dict[int, int] | None = None,
                C_now: float | None = None, L: float | None = None,
                rng: np.random.Generator | None = None) -> SeasonPlan
```
- `control ∈ {"none", "mkx", "cap", "ocs", "ocs_gain"}`; `mating ∈ {"random", "mc1"}`.
  - **none:** quotas unlimited (each sire may take every dam). `none × random` is S0; `none × mc1` is per-dam minimum coancestry (the P8 failure mode in its purest form).
  - **mkx:** sires with MK above the mean MK of the candidate sires are excluded; quotas unlimited among the rest [windig-2013] (applied to sires only, D1).
  - **cap:** MK-scaled per-year caps (D9), no optimisation.
  - **ocs:** conservation OCS with caps, age and depth constraints → Sainte-Laguë quotas.
  - **ocs_gain:** gain OCS with `C_eff` from D5 to D7.
- `SeasonPlan`: sire quotas, assignment (sire per dam), diagnostics (C_now, budget, achieved C, infeasible, relaxed caps, solver seconds, number of sires with quota).
- Uses `RuleContext` / `exp_pairing` HARD rules for `forbidden`; P(affected) from `matching.components.transmission` (tested loci only, as P7).
- Tests: each control × mating on a fixture context returns a valid plan; `none × mc1` reproduces "each dam gets her least-kin allowed sire"; plans are deterministic for a fixed rng.

### 12.7 [MVP] Truth-side tracking for metrics and the oracle arm (`experiments/truth_kinship.py`)
- `TrueKinship`: incremental F and D of the **true** pedigree of the experiment breed (state sire/dam, gid order) with `inbreeding_extend` each year; `kinship_matrix(gids)` for the oracle arm.
- `realised_coancestry(neutral_alleles)`: mean over loci of `Σ_a p_a²` among living domestic animals (equals 1 − expected heterozygosity, so it reuses the P8 He computation).
- Tests: incremental equals full recompute (as the P8 observed-registry test); `realised_coancestry` = 1 − He on a toy array.

### 12.8 [MVP] Strategies and runner wiring (`experiments/strategies.py`, `experiments/runner.py`)
- `Coordinated(control, mating, kinship="recorded"|"true", delta_f=None)`: implements `plan_matings` by calling `plan_season` once per year with the year's dams and candidate sires (gid ↔ idx through `ObservedRegistry`); foreign sires without a record are excluded (as P8 S3/S4). Keeps `C_now` from its previous year's plan (first year: `C(c)` of the 2026 cohort's realised matings).
- `RecommenderWithQuotas` (**S3q**): runs the OCS round (control `ocs`, mating none) to get quotas, opens a `BookingLedger`, then for each adopting dam in random order calls `rank_fast(..., candidates=sires with quota left)` and picks among the top 3 (0.5/0.3/0.2); books the choice. Non-adopters (`adoption < 1`) first follow S2 and their sire choices enter OCS as `fixed_sire_litters` (D15).
- Strategy ids (used in configs and file names): `CC-none-rand`, `CC-none-mc1`, `CC-mkx-rand`, `CC-mkx-mc1`, `CC-cap-rand`, `CC-cap-mc1`, `CC-ocs-rand`, `CC-ocs-mc1`, `CC-ocs-mc1-oracle`, `CC-gain100-mc1`, `CC-gain050-mc1`, `CC-gain025-mc1`, `CC-gain010-mc1` (ΔF × 10⁴), `S3q`.
- `ContractChecker` (P8 debug wrapper) extended: no HARD-rule violations, sire quotas never exceeded, every chosen sire eligible.
- Per-year diagnostics written alongside metrics: `D1_budget`, `D2_achieved_C`, `D3_infeasible`, `D4_n_sires_with_quota`, `D5_solver_seconds`, `D6_relaxed_caps`.
- Colours and labels for the new ids in `calibration/plotstyle.py` and `experiments/figures.py` (colour-blind safe; contribution-control families share a hue, mating method distinguished by line style).

### 12.9 [MVP] New metrics (`experiments/metrics.py`)
- **M12** realised mean coancestry `C_t` (truth, neutral loci) and per-year `ΔC_t = (C_t − C_{t−1})/(1 − C_{t−1})`; Ne from ΔC per generation.
- **M13** generation interval of the cohort (mean parent age at birth, both sexes).
- **M14** top-5 sires' share of litters (5-year window) and coefficient of variation of litters per sire (this year).
- **M15** recorded mean coancestry of the reference population (observed, existing MK machinery).
- Summary (`experiments/summary.py`): rates estimated in two windows, **early** (generations 1 to 5) and **late** (generations 6 to 10), by regression of `−log(1 − x)` on generation for x = realised IBD (ΔF) and x = realised coancestry (ΔC); paired differences vs `S1` **and** vs `S3`.

### 12.10 [MVP] Experiments
Seeds are the E1 seed (`20261024`) so that replicate r of every arm starts from the same random stream as E1 (common random numbers, also with the E1 anchors). Generations 10; replicates SYN_S 20, SYN_M 10 (as E1).

- **E5_coordination** (`configs/experiments/coordination.yaml`): factorial contribution control {none, mkx, cap, ocs} × mating {random, mc1} (8 arms) + anchors S1, S3 + product arm S3q. Breeds SYN_S and SYN_M.
- **E6_budget_and_kinship** (`configs/experiments/budget.yaml`): `CC-gain100/050/025-mc1` (SYN_M also `CC-gain010-mc1`) + `CC-ocs-mc1` + `CC-ocs-mc1-oracle`. Breeds SYN_S and SYN_M. Answers: what does each ΔF budget cost in HD genetic gain, and how much does recorded vs true kinship matter.
- **E7_adoption_quotas** (`configs/experiments/adoption_quotas.yaml`): `S3q` at adoption 0, 0.25, 0.5, 0.75, 1.0 (0 equals S2). Breeds SYN_S and SYN_M, 10 replicates.
- **Runtime planning (as P8 task 8.7):** run one replicate of `CC-ocs-mc1` and `S3q` per breed first, extrapolate, report. If E5 + E6 + E7 would exceed 6 hours on this machine with 5 workers, reduce replicates (never generations, never arms) in this order: E7 to 6, E6 to 6, E5 SYN_S to 10. Record the reduction.
- Long runs go to the background; work on 12.11 to 12.13 meanwhile.

### 12.11 [MVP] Figures (`experiments/figures.py`), all with the in-silico caption, PNG 300 dpi + SVG + poster variant
- **Fig G (headline P12):** realised inbreeding over generations, panels per breed: S0, S1, S3, `CC-ocs-mc1`, `S3q`.
- **Fig H (factorial):** late-window ΔF (and Ne) per contribution control, two markers per control (random vs MC1), with 95% intervals: shows which factor matters.
- **Fig I (budget trade-off):** HD genetic gain (generation 1 → 10) vs realised ΔF for the gain ladder, conservation and anchors.
- **Fig J (kinship source):** recorded vs true-kinship OCS: Ne and recorded-vs-true COI gap.
- **Fig K (adoption):** late-window ΔF vs adoption share for S3q, both breeds, with the P8 E2 S3 curve for comparison.
- **Fig L (sire use):** share of eligible males used and top-5 sire share per arm.

### 12.12 [MVP] Product integration
- **Package API:** `coordination.planner.plan_season` usable on the real `DatasetContext` (v1 or bundle) for a given breed, date and list of planned dams.
- **CLI:** `bsm coordinate --dataset v1 --breed SYN_M --date 2027-03-01 [--dams <file|auto>] [--delta-f 0.005] [--mode ocs|cap]` prints the sire quota table (sire, MK, EqG, cap, quota) and the suggested allocation; `--dams auto` = living females aged 2 to 6 with no litter in the previous 10 months (documented).
- **App:** new page `7_Club_planner.py`: breed, date, ΔF slider (ladder values), mode (cap / OCS); shows the quota table and a bar chart of litters per sire vs status quo concentration; caption "Club-level planning: quotas decide how often each sire is used; breeders choose within them." Mate finder gets a toggle "Respect club quotas" that runs `plan_season` for auto dams and hides sires with no quota left, showing "quota left" as a column.
- App smoke tests extended to page 7 and the toggle (AppTest on the tiny bundle).

### 12.13 [MVP] Documentation
- `docs/coordination.md`: method (sections 0 to 2 of this plan in plain language), parameter table with keys, limitations (pedigree kinship, sire-only control, unverified yearly formula).
- README: short "Coordination" paragraph and Fig G once results exist.
- `docs/assumptions.md` regenerated (`bsm docs assumptions`); rule docs regenerated if profiles change.
- `configs/datasets.yaml` untouched (v1 is reused, not regenerated).

### 12.14 [MVP-conditional] Conference materials
Only after the P12 gate numbers exist **and** not later than 20 October (poster print is 21 October):
- Extend `conference/build_numbers.py` with E5 to E7 values (keys prefixed `p12_`).
- Update templates: poster text "Does it work?" block (stay ≤ 300 words; the build fails otherwise), slides 9 to 11, Q&A (new questions: "So does coordination fix it?", "Would clubs accept quotas?"), partner one-pager, paper draft results paragraph.
- Regenerate figures (Fig G poster variant replaces or joins Fig A, decided by the pre-registered outcome below), rebuild `poster_draft.pptx`, rebuild the demo bundle with E5 to E7.
- If the gate is not reached by 20 October: materials keep the P8 story and say "coordinated planning is being evaluated"; no partial numbers on the poster.

### 12.15 [STRETCH] Not before every MVP item above is done
- 20-generation horizon rerun of E5 (late window = generations 11 to 20) [sonesson-meuwissen-2001; bergsma-2022 horizons].
- Lifetime caps (PEVISA-style, 40 offspring) as a sensitivity arm.
- Dam contributions in OCS (both sexes), knowingly breaking the "same dams" design; reported separately.
- Metafounders for foreign stub groups [legarra-2015].
- Breeding-circle arm (needs ≥ 78-year horizon to be fair [windig-hulsegge-2021]).

---

## 4. Pre-registered success criteria (written before any P12 experiment runs)

These are fixed now and copied verbatim into the gate report. They decide the headline wording, not whether results are reported (everything is reported). All comparisons are paired by replicate, 95% t-intervals, late window (generations 6 to 10) unless stated.

| id | Criterion | Arms | Breeds |
|---|---|---|---|
| H1 | Coordination raises Ne above today's market: Ne(`CC-ocs-mc1`) − Ne(`S1`) > 0 (CI lower bound > 0) | E5 | SYN_S and SYN_M |
| H2 | Coordination beats the per-dam recommender on long-term inbreeding: ΔF(`CC-ocs-mc1`) − ΔF(`S3`) < 0 (CI upper bound < 0) | E5 | SYN_S and SYN_M |
| H3 | Contribution control matters more than mating method: the late-window ΔF range across the four controls (averaged over mating) is larger than the range across the two mating methods (averaged over control) | E5 | SYN_S and SYN_M |
| H4 | The product mode keeps the P8 benefits while fixing diversity: `S3q` has affected-genotype share at tested loci ≤ `S1` and Ne ≥ `S1` (CI lower bound of the difference > 0) | E5 | SYN_M (SYN_S has no segregating tested locus in v1) |
| H5 | Diagnostic: OCS on true kinship reaches at least S0's Ne (point estimate ≥ 0.9 × S0) | E6 | SYN_S and SYN_M |
| H6 | Kinship source: Ne(`CC-ocs-mc1-oracle`) − Ne(`CC-ocs-mc1`) is reported with CI; no pass/fail | E6 | both |

Interpretation rules:
- H1 and H2 pass in both breeds → headline "Coordinated planning fixes long-term diversity" (with numbers).
- Mixed → headline states exactly which breed/criterion passed.
- H5 fails → treat as a likely bug: check that equal contributions are feasible and that `C(conservation) ≤ C(equal split)` on the logged problems before reporting; if no bug is found, report it as a result.
- No criterion is changed after results exist. Additional analyses are labelled "additional (not pre-registered)".

---

## 5. Tests (all MVP, must pass before the gate)
- Unit: 12.2, 12.4, 12.5, 12.6 tests above; config test (12.1); `test_sources_cover_research_keys` still passes with the new keys.
- Integration (tiny run, `tests/integration/test_experiments.py` extended): every new strategy id passes `ContractChecker` (`debug=True`) for 1 generation; S3q never books beyond quota; determinism (same seed → identical tables) for `CC-ocs-mc1` and `S3q`; `TrueKinship` incremental = full recompute.
- Performance: one `plan_season` with `ocs` for a SYN_M year (≈ 150 dams, ≈ 800 candidate sires) under 2 s; `rank_fast` with quotas unchanged in speed (< 20 ms/dam).
- App: AppTest smoke for page 7 and the mate finder toggle.
- Full check suite: `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy src`, strict mypy for `pedigree`, `rules`, `matching`, **`coordination`**, `uv run pytest -m "not slow"`; plus `uv run pytest -m slow`.

## 6. Acceptance checklist (gate)
- [ ] ADR-007 written; solver decision recorded; dependency works in a clean `uv sync`.
- [ ] All new citation keys in `docs/research.md` and `configs/sources.yaml`; every new config number sourced or `assumption: true`.
- [ ] OCS known-answer and property tests pass (≥ 200 hypothesis examples for the constraint property).
- [ ] E5, E6, E7 complete with planned replicates (or the documented reduction); runtime reported.
- [ ] Figures G to L generated; `summary.md` per experiment.
- [ ] Gate report states H1 to H6 outcomes in plain words with numbers from `summary.csv` / paired CSVs (nothing typed by hand), plus the infeasibility count per breed and the solver-time distribution.
- [ ] CLI `bsm coordinate` demo output for SYN_M on v1 pasted in the gate report.
- [ ] App page 7 and quota toggle working on the v1 bundle (AppTest), bundle rebuilt.
- [ ] Conference materials updated per 12.14, or explicitly marked "not updated (deadline)".
- [ ] `plan/STATUS.md` updated; commit messages without co-author trailers; push to `origin` (GitHub) at the gate.

## 7. Timeline (fits before the 21 October print deadline)
| Day | Work |
|---|---|
| Sun 12 Oct | 12.0 to 12.5 (dependency, config, targets, OCS with tests, quotas, allocation) |
| Mon 13 Oct | 12.6 to 12.9 (planner, truth tracking, strategies, metrics); runtime planning; launch E5 to E7 in background |
| Tue 14 Oct | 12.11 figures, 12.12 CLI and app page, 12.13 docs; read results; gate report |
| Wed 15 Oct | Paper deadline: paper draft updated only if the gate is done (12.14); otherwise P8 version |
| by Mon 20 Oct | 12.14 conference materials updated and poster rebuilt |

## 8. Risks
| Risk | Mitigation |
|---|---|
| cvxpy/Clarabel incompatible with numpy 2.5 | scipy fallback for the conservation QP (12.0); gain arm only with a verified solver |
| Budget infeasible every year in SYN_S (already ΔF ≈ 1.5%) | D7 fallback logged; report the infeasibility count; the conservation arm is the main SYN_S result |
| Recorded kinship over-uses shallow foreign records | D11 depth constraint; oracle arm (E6) quantifies the remaining gap |
| Coordination shortens the generation interval (as lifetime caps did in [windig-2013]) | M13 tracked; reported |
| Results do not support the hypotheses | Reported as is (section 4 rules); the poster keeps the honest P8 + P12 story |
| Scope creep (app, poster) eats the time | 12.12 app work is minimal; 12.14 has a hard date; STRETCH list is explicit |
