# Gate report: P3 Population simulator
Date: 2026-10-10

## Acceptance checklist
- [x] Full default run (`scale = 1.0`, seed 42) completes: **8.4 s generator wall time** (10.0 s for the whole CLI; target under 10 minutes). Run `data/generated/p3-default-s42` (structure only, `--genetics null`; P4 regenerates with genetics).
- [x] `validate_run` passes on that run ("OK: 9 tables valid"; also `test_full_default_run_validates`, `test_scaled_default_validates` at scale 0.1).
- [x] All tests pass, including determinism (byte-identical Parquet in-process and across processes with different `PYTHONHASHSEED`) and save/load continuation (run to 1990, save, load, continue to 1995 equals an uninterrupted run, every animal and litter column).
- [x] Sanity plots in `reports/validation/p3_sanity/`: `registrations_per_year.png`, `litter_size_hist.png`, `offspring_per_sire.png`.
- [x] Every config value still marked `assumption: true` is listed below.

## Row counts (seed 42, scale 1.0)
| Table | Rows |
|---|---|
| registry/animals | 149,123 (SYN_L 121,007; SYN_M 24,308; SYN_S 3,808) |
| registry/litters | 23,993 (L 18,955; M 4,209; S 829) |
| registry/kennels | 72,257 (breeder kennels plus generated private owners) |
| truth/animals_truth | 275,023 (L 221,371; M 47,077; S 6,575), of which hidden: L 100,364; M 22,769; S 2,767 |
| registry/health_tests, dna_tests, ebv, truth/genotypes_truth | 0 (P4) |

Registry-era registrations track the target curve: within 6% per 5-year block for L and M and within 8% per 10-year block for S over seeds 1 to 4. Mean litter size L 6.4, M 5.5, S 4.0 (config 6.4 / 5.5 / 4.0 after the fertility fix below), share of litters with a perinatal loss about 23% (target 24.6%). Mating methods: natural 94%, foreign AI frozen 3.5%, chilled 2.3%.

## What was built
`sim/state.py` (growable struct-of-arrays `SimState`, save/load with RNG state), `sim/kennels.py` (Pareto activity, bounding-box coordinates, haversine), `sim/names.py` (syllable names, empty blocklist file `configs/names_blocklist.txt`), `sim/demography.py` (Weibull lifespans, death causes, whelping windows, eligibility), `sim/market.py` (`MarketStrategy`), `sim/reproduction.py` (year step: split, dam choice, strategy, litters, puppies, imports), `sim/registry.py` (1980 founding, imports with stub pedigrees, foreign AI stubs, population split), `sim/writer.py` (registry and truth tables), `sim/run.py` (`run_simulation`, `generate`, config snapshot, manifest, state save, validation), `sim/interfaces.py` (`GeneticsModel`, `NullGenetics`, `MatingStrategy`, `YearContext`, `SimSetup`), `sim/sanity.py`; CLI `bsm generate`; `configs/sim/tiny.yaml` (0.25 s).

## Deviations from the plan (and why)
1. **Whelping windows instead of whole-year eligibility.** Each dam and sire gets an earliest and latest whelping time in the year (minimum breeding age and minimum litter interval at any possible mating date, i.e. whelp minus up to 70 days, and maximum breeding age). The whelping date is sampled inside the pair's window. Whole-year rules made dams skip every other year.
2. **Demand-driven recruitment (assumption).** When eligible dams are fewer than the target litters, breeders acquire eligible non-candidate females; when fewer than 3 sires are eligible, males likewise. Counted in `state.meta` (seed 42: 6 SYN_M females). Without it small populations went extinct.
3. **Hidden domestic population ramps up before 1980 (assumption).** It grows linearly from `burn_in_size_fraction` to the full 1980 level over the last 2 generation intervals before registry founding. Without it the registry could not reach the 1980 registration target (1985 to 1989 registrations were 27% low for SYN_M).
4. **Fertility normalised among mated dams.** Dams are chosen with fertility weights, which inflated litters (SYN_L 6.8 vs 6.4). The configured litter mean is now the mean of the year's mated non-inbred dams.
5. **Registration test granularity.** "Within 10% of the target curve" is tested on the full-scale run, per 5-year block for L and M and per 10-year block for S (S has 40 to 90 registrations a year; 5-year sums carry about 8% sampling noise). At scale 0.1 per-block sums are too noisy for a 10% test, and SYN_S can go extinct at that scale for some seeds; the scale-0.1 run is used only for `validate_run`.
6. **Close-mating test** uses counters recorded by the market (registry era): close pairs among first-choice sires vs after avoidance; asserts final <= base x ((1 - p) + p x base) x 1.5. Base 29% in the tiny run, final about 9.5%.
7. **Determinism bug found and fixed:** set iteration order in kennel creation depended on `PYTHONHASHSEED`; a cross-process test now guards it.
8. **`GeneticsModel` protocol extended** with `pair_avoid` (carrier pairing resampling, P4), `on_import` and `state_arrays`/`load_arrays` (state serialisation). `make_offspring` takes per-child parent arrays. Realised IBD lives in `SimState.animals.f_true` so the litter-size inbreeding effect works with any genetics model.
9. Registry-writing constants (`limited_registration_share 0.3`, `titles_rate 0.05`, `dogs_per_private_owner 1.5`, `min_founders 10`) moved into `configs/sim/*.yaml` under `registry`, all `assumption: true`. Other code constants (assumptions, documented at their definition): founders born 1 to 6 years before the start, imports aged 1 to 4 years, kennels = registrations/15 (at least 5), Pareto shape 1.5, minimum 3 sires, ramp 2 generations.
10. Imports' recorded pedigree may exceed `import_pedigree_depth` when an ancestor was already registered earlier (shared foreign ancestry); the test checks that any deeper record comes through an ancestor registered before the import (first registration wins).

## Known issue for P5
- **Sire concentration is far too extreme** (`offspring_per_sire.png`): the top SYN_L sire has about 12,000 registered offspring. The rich-get-richer term with `popular_sire_alpha = 1` plus a 10-year breeding career runs away. P5 tunes alpha and beta against T05 and T06.

## Numbers worth knowing
- Default run: 275k simulated animals 1935 to 2026, 8.4 s. Tiny run: 0.25 s.
- 103 fast tests (9 s); slow simulator tests 3 (14 s).

## Assumptions still marked `assumption: true` (full list)
sim: generation_interval 4.5; foreign size_factor 1.0; market distance 300 km, same-kennel exclusion 0.5, prime age 2 to 8, off-prime factor 0.5, 5 retries; registry limited share 0.3, titles 0.05, 1.5 dogs per owner, min founders 10.
species: gestation 63 (sd 2); male min age 12 months, male max age 12 years; Weibull(4.0, 12.5); sex ratio 0.5; death causes 0.80/0.12/0.05/0.03; attractiveness sd 1.0; fertility log-sd 0.15.
per breed (L / M / S): registrations (1200 to 3500 / 300 to 600 / 40 to 90); base founders 400/120/25; burn-in fraction 0.3/0.3/0.5; split year 1950/1955/1965; litter mean 6.4/5.5/4.0 (inside borge-2011 range); dispersion 8; perinatal loss 0.05; registration rate 0.95; caesarean 0.10/0.10/0.15; max 6 litters; 10 months between litters; candidate shares 0.25/0.25/0.35; popular_sire_alpha 1.0/1.0/0.8; attractiveness beta 1.5/1.5/1.0; import rate 0.03/0.05/0.10; foreign AI share 0.05/0.08/0.15; AI frozen share 0.6; close-mating avoidance 0.95/0.95/0.90.

## Open questions for Tea
- None blocking.

## HUMAN tasks waiting
- None new.
