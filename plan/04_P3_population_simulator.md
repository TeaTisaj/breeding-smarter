# P3: Population simulator (pedigree structure)

**Goal:** a seeded, configurable, agent-based simulator that produces realistic multi-breed pedigree structure: a hidden pre-registry history, a registry era 1980 to 2026, kennels, popular sires, imports with shallow foreign pedigrees, litters and deaths. Genetics (disease loci, HD, true IBD) plugs in through a hook in P4.
**Effort:** 1 day. **Depends on:** P1. Runs in parallel with P2.

Module: `src/breeding_smarter/sim/`.

---

## 1. Design

### 1.1 One loop for history and experiments (ADR-005)
The simulator advances **one year at a time**. Each year, for every breed and subpopulation: deaths, eligibility, choosing dams, choosing sires (through a pluggable `MatingStrategy`), litters, puppies. History generation uses `MarketStrategy` (how breeders behave today). Experiments in P8 load the end state and continue with other strategies. Therefore all simulator state must be serialisable (`SimState.save(path)` / `SimState.load(path)`).

### 1.2 Populations per breed
```
base founders (year B, unrelated, true F = 0)
        │  hidden burn-in, constant size
        ▼
   split year S ──────────────┐
        │                     │
  DOMESTIC (Croatia)     FOREIGN (rest of Europe)
  hidden until 1980      always hidden
        │ registry founded 1980: all living domestic adults registered with unknown parents
        ▼
  registry era 1980..2026  ◄── imports and foreign AI sires (registered with 3 to 5 generation stubs)
```
- `B = registry_start_year - burn_in_generations * generation_interval_years` (for example 1980 - 10 x 4.5 = 1935).
- Shared hidden ancestry means registry founders are truly related even though the registry says unrelated. This is intentional (see P1 "observed vs truth").

### 1.3 State (struct of arrays, growable buffers)
`SimState` holds numpy arrays indexed by `gid` (global birth order, all breeds and subpopulations share one counter, so `gid` order is birth order):
`breed`, `subpop` (0 domestic, 1 foreign), `sex`, `birth_year`, `birth_doy`, `sire`, `dam`, `death_year`, `lifespan`, `kennel` (owner), `breeder`, `is_breeding_candidate`, `attractiveness`, `fertility`, `litters_count`, `last_litter_year`, `offspring_count`, `registered`, `import_flag`, `litter_id`, plus per-year counters. Litters in a separate struct of arrays. Capacity doubles when full.
Litter mates get consecutive gids (required by the full-sib shortcut in P2).

### 1.4 Interfaces
```python
class GeneticsModel(Protocol):  # implemented in P4; NullGenetics here
    def init_founders(self, state, gids, rng) -> None: ...
    def make_offspring(self, state, sire, dam, child_gids, rng) -> None: ...
    def is_eligible(self, state, gids, year) -> np.ndarray: ...  # health-based eligibility
    def on_year_end(self, state, year, rng) -> None: ...  # screening, DNA testing, EBVs


class MatingStrategy(Protocol):
    name: str

    def plan_matings(
        self, dams: np.ndarray, sires: np.ndarray, ctx: "YearContext", rng: np.random.Generator
    ) -> np.ndarray: ...  # sire gid per dam, -1 = skip
```
`YearContext` gives read access to state arrays, the year, breed config, recent offspring counts per sire (5-year window), kennel coordinates, and a lazily built kinship helper (used by P8 strategies, unused by the market).

---

## 2. Tasks

### 3.1 [MVP] Configs
`configs/sim/default.yaml`:
```yaml
name: default
seed: 42
registry_start_year: 1980
end_year: 2026
generation_interval_years: {value: 4.5, assumption: true, note: "research says 4 to 5 years; confirm in P5"}
burn_in_generations: 10
breeds: [syn_large, syn_medium, syn_small]
scale: 1.0          # multiplies all population sizes; tests use 0.02
foreign:
  size_factor: 1.0  # foreign registrations per year relative to domestic 1980 level
  countries: [SI, AT, HU, IT, DE, RS, CZ, PL, SE, FI, NL]
```
Breed files (all values `assumption: true` unless a source exists; P5 tunes them):

| Parameter | SYN_L | SYN_M | SYN_S | Source |
|---|---|---|---|---|
| size_class | large | medium | small | |
| registrations/year at 1980 and 2026 | 1200, 3500 | 300, 600 | 40, 90 | assumption |
| base founders | 400 | 120 | 25 | assumption |
| burn-in size (fraction of 1980 level) | 0.3 | 0.3 | 0.5 | assumption |
| split year | 1950 | 1955 | 1965 | assumption |
| litter size mean | 6.4 | 5.5 | 4.0 | assumption within borge-2011 range (3.5 to 7.1, overall 5.4) |
| litter size dispersion (NB size parameter) | 8 | 8 | 8 | assumption |
| perinatal loss per puppy | 0.05 | 0.05 | 0.05 | assumption tuned so about 24.6% of litters lose at least one (tonnessen-2012) |
| registration rate of live puppies | 0.95 | 0.95 | 0.95 | assumption |
| female breeding-candidate share | 0.25 | 0.25 | 0.35 | assumption (about 20% of dogs bred, calboli-2008) |
| male stud-candidate share | 0.25 | 0.25 | 0.35 | assumption |
| popular sire alpha | 1.0 | 1.0 | 0.8 | tuned in P5 against sire concentration targets |
| attractiveness weight beta | 1.5 | 1.5 | 1.0 | tuned in P5 |
| import rate (share of new breeding animals imported) | 0.03 | 0.05 | 0.10 | assumption |
| foreign AI sire share | 0.05 | 0.08 | 0.15 | assumption |
| import pedigree depth (generations recorded) | 4 | 4 | 3 | pde-2011 says 3 to 5 |
| close-mating avoidance probability | 0.95 | 0.95 | 0.90 | assumption |
| max litters per dam (lifetime) | 6 | 6 | 6 | assumption |
| min months between litters | 10 | 10 | 10 | assumption |
| caesarean rate | 0.10 | 0.10 | 0.15 | assumption |
| expected Ne range (target for P5) | 200 to 900 | 80 to 150 | 25 to 50 | lewis-2015 distribution |

`registrations_per_year` is a list of `(year, value)` points interpolated linearly (allows a peak and decline later).

### 3.2 [MVP] `sim/state.py`
`SimState` with growable arrays, `add_animals(n, **fields) -> gids`, `alive_mask(year)`, `age(year)`, `save(path)`/`load(path)` (npz plus JSON metadata), and `to_tables(...)` (see 3.8).

### 3.3 [MVP] `sim/kennels.py`
- Per breed: `n_breeder_kennels` (assumption: registrations_2026 / 15, at least 5) with activity weights from a Pareto distribution (few large kennels, many small). Domestic kennels get coordinates inside Croatia's bounding box (approximately lat 42.4 to 46.6, lon 13.5 to 19.4; jitter and reject points outside a simple polygon is not needed, the bounding box is fine for a POC). Foreign kennels get country codes and coordinates inside each country's rough bounding box (hardcode a small dict, mark as approximate).
- Private owners: pool of owner records created lazily when puppies are sold (one owner per 1 to 2 dogs).
- Kennel names: syllable generator; ensure uniqueness; never use real affixes (keep a blocklist file empty but present for future).

### 3.4 [MVP] `sim/demography.py`
- Lifespan at birth: Weibull(shape, scale) from species config; `death_year = birth_year + floor(lifespan)`; death cause sampled (`age` mostly; `disease`, `accident`, `unknown` small shares, assumption).
- Breeding candidates: at birth, females are candidates with the configured share, males likewise; candidates move to a breeder kennel (weighted by kennel activity), others to private owners.
- Eligibility each year: alive, age within species/breed window, candidate, `GeneticsModel.is_eligible`, and for females: litters below max, enough months since last litter.

### 3.5 [MVP] `sim/market.py`: `MarketStrategy` (status quo behaviour)
For each dam (vectorised where possible):
1. With probability `foreign_ai_sire_share`, choose from foreign eligible males (weights as below, no distance factor). Mating method `ai_frozen` or `ai_chilled`.
2. Otherwise choose among domestic eligible males with weight
   `w_j = exp(beta * attractiveness_j) * (1 + offspring_last_5y_j) ** alpha * exp(-dist_km(dam_kennel, sire_kennel) / 300) * age_factor_j`
   where `age_factor` is 1 between 2 and 8 years and 0.5 outside (assumption). Exclude males owned by the same kennel with probability 0.5 (assumption: breeders often use outside studs).
3. Close-mating avoidance: if the chosen pair is parent-offspring, full or half siblings, or grandparent-grandchild (fast check with parent and grandparent arrays), resample with probability `close_mating_avoidance` (max 5 retries).
Return the sire per dam. This strategy creates popular sires through the `(1 + offspring)^alpha` rich-get-richer term and heritable attractiveness (see 3.6).

### 3.6 [MVP] `sim/reproduction.py`
Per year and subpopulation:
1. Target number of litters: `target_regs(year) * scale / (litter_mean * (1 - perinatal_loss) * registration_rate)`. In hidden mode use the burn-in size.
2. Choose dams from eligible females without replacement, weights `fertility * kennel_activity`. If there are too few eligible dams, use all and log a warning (report count in the manifest).
3. Sires from the strategy.
4. Litter size: `n_born ~ NegBin(mean = litter_mean * fertility_dam * (1 - id_slope * F_dam), size = dispersion)`, minimum 1, where `id_slope` = 10 per unit of the dam's F (about one puppy fewer per 10% COI, chu-2019, assumption that it transfers) and `F_dam` is the dam's true IBD from P4 (0 with `NullGenetics`).
5. `n_born_alive ~ Binomial(n_born, 1 - perinatal_loss)`; registered `~ Binomial(n_born_alive, registration_rate)` in the registry era (all alive in hidden mode). Only puppies that are registered (or alive, in hidden mode) become animals; the others exist only as litter counts.
6. Dates: whelp day-of-year uniform; mating date = whelp date - gestation (63 +/- 2 days).
7. Puppy attributes: sex Bernoulli(0.5); `attractiveness = 0.5 (a_s + a_d) + N(0, 0.5 * sigma_a^2)` with `sigma_a = 1` (heritable, so sons of popular sires tend to become popular, as observed); `fertility ~ LogNormal(0, 0.15)`.
8. Call `GeneticsModel.make_offspring`.
9. Mating method (`natural` unless foreign AI), caesarean flag.

### 3.7 [MVP] `sim/registry.py`: registry founding and imports
- **Registry founding (1980):** every living domestic animal of breeding age becomes registered with unknown parents (`studbook = HR`, founders). Younger living animals are registered too, with parents linked if the parents are registered.
- **Imports:** each year, `import_rate * new_domestic_candidates` foreign animals (young adults, alive, eligible) move to domestic breeder kennels. The import and its ancestors up to `import_pedigree_depth` generations are registered; ancestors registered this way get `studbook = FOREIGN` and keep their true parents only if those parents are also inside the depth window (deeper parents become unknown). The import itself gets `import_flag = true` and an `original_reg_no`.
- **Foreign AI sires:** the same stub registration for the sire.
- Animals registered with unknown parents after 1980 (imports' oldest ancestors) are what makes recorded F lower than true F.

### 3.8 [MVP] `sim/writer.py`
`to_tables(state) -> dict[str, DataFrame]`:
- Registered animals sorted by gid get `idx = 0..m-1`. Parent idx = mapped idx if the parent is registered, otherwise null.
- `reg_no`: `SYN-HR-<year>-<seq>` per birth year; foreign stubs `SYN-FOREIGN-<country>-<seq>` (both in `reg_no`; for imports `original_reg_no` holds the foreign number and `reg_no` the local one).
- `studbook`: `HR` for full domestic ancestry recorded for 3 generations, `HUR` for domestic animals with any unknown parent or grandparent, `FOREIGN` for stub ancestors.
- Names, colours (uniform over the breed list, assumption), microchip (`999` plus 12 random digits, unique), titles (`Poisson(0.05 * exp(attractiveness))`), registration type (`limited` for 30% of non-candidates, assumption).
- Truth table rows for all animals (`is_hidden = not registered`).
- Litters table for registered litters only.

### 3.9 [MVP] `sim/run.py` and CLI
`run_simulation(config, seed, genetics=NullGenetics(), strategy=MarketStrategy()) -> SimState`; `bsm generate --config configs/sim/default.yaml --seed 42 [--scale 0.1] [--out data/generated]` writes tables, manifest (including warnings and wall time), **saves the end-of-history `SimState` (including the genetics model's arrays and the RNG state) to `state/`** (P8 continues from it), and runs `validate_run`. Progress bar per decade.

### 3.10 [MVP] Tiny config for tests
`configs/sim/tiny.yaml`: one breed, scale 0.02, burn-in 3 generations, end year 1995. Must run in under 5 seconds.

---

## 3. Tests
- Determinism: two runs with the same seed produce identical Parquet bytes (compare file hashes); different seeds differ.
- `validate_run` passes on the tiny run and on a scaled default run (`scale = 0.1`, marked slow).
- Topology: every registered animal's parents (if any) have smaller idx; litter mates have consecutive idx.
- Registrations per year within 10% of the target curve in the registry era (scaled run).
- Mean litter size per breed within 0.3 of config mean (allowing for dam fertility and the F effect).
- No parent-offspring or full-sibling matings above the expected leak rate (`1 - avoidance` times the base rate).
- Imports: each import has at most `import_pedigree_depth` generations of recorded ancestry.
- Save/load: `SimState.load(SimState.save(x))` continues identically for 2 more years as an uninterrupted run (needed by P8).

## 4. Acceptance checklist (gate)
- [ ] Full default run (`scale = 1.0`, seed 42) completes; wall time and row counts per table and breed in the gate report (target under 10 minutes; if slower, profile and report).
- [ ] `validate_run` passes on that run.
- [ ] All tests pass, including determinism and save/load continuation.
- [ ] Quick sanity plots in `reports/validation/p3_sanity/`: registrations per year per breed, litter size histogram, offspring-per-sire distribution (log scale).
- [ ] Gate report lists every config value still marked `assumption: true`.
