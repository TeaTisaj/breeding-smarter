# Gate report: P6 Rule engine
Date: 2026-10-11

## Acceptance checklist
- [x] All 14 rule types implemented (`rules/types/__init__.py`: same_breed, alive_at_mating, registration_type, relationship_ban, min_age, max_age, min_interval_between_litters, max_litters_in_window, max_lifetime_litters, health_grade_exclusion, affected_exclusion, carrier_pairing, offspring_coi_threshold, sire_quota) and all profiles (`configs/rules/`: eu_2026_1818, fci, kc_uk, rvb_nl, hks_hr, eu_platform_guide, plus base_checks, dna_health and the composites hr_full, uk_full, nl_full). Loader rejects unknown rule types, unknown relationships, missing or unknown sources, missing params and include cycles (`test_loader_rejects_bad_yaml`).
- [x] Tests pass (19 in `tests/unit/test_rules.py`): one test per rule type with pass and fail cases on fixture pedigrees, including every banned relationship and first cousins passing the EU ban; derogation (local breed + granted -> SOFT, non-local unaffected, not granted unaffected); `check_many` equals `check_one` element-wise (5 dams x 40 sires x 14 rules on a 20k pedigree); hr_full contains the expected ids once; status aggregation; every profile loads. Performance: one dam vs 2000 sires in under 200 ms (`test_evaluate_candidates_performance`).
- [x] `bsm check` demo on dataset v1 (dam Muvi od Kokano, SYN-HR-2021-002462, SYN_M, mating 2026-11-01, profile hr_full):

| Sire | Status | Failed rules (message) |
|---|---|---|
| Sana od Verito (SYN-HR-2016-000056) | **PERMITTED** | none; predicted COI 2.7% (breed recent litters 3.3%) |
| Nove od Verito (SYN-HR-2016-000226) | **PERMITTED_WITH_WARNINGS** | `guide_coi_6_5` (SOFT): "Predicted COI of the litter 9.0% > threshold 6.5%."; INFO: above breed average 3.3% |
| Mili od Kokano (SYN-HR-2023-004157) | **NOT_PERMITTED** | `eu_close_relatives` (HARD, unverified): "Banned relationship: half siblings (common parent(s): Rize od Samape (SYN-HR-2020-000735))."; also COI 16.2% > 6.5% |

  Full tables: `uv run bsm check --dam SYN-HR-2021-002462 --sire <reg_no>` (each prints all 14 rules with source and verified flag).
- [x] `docs/rules_verification.md` and `docs/rules_catalogue.md` generated (`bsm rules docs`; freshness test). HUMAN verification task listed in STATUS.md.

## What was built
`rules/models.py` (RuleSpec, ProfileSpec, Profile, Severity, Status), `rules/loader.py` (composition with includes, dedup by id, cycle detection, validation), `rules/context.py` (`RuleContext`: arrays by idx, sorted CSR date arrays for litters per dam/sire, offspring per sire, registrations per breed, litter F per breed; cached kinship rows), `rules/types/` (vectorised implementations and messages naming relatives by name and reg_no), `rules/engine.py` (`evaluate_candidates`, `evaluate_pair`, derogation, status aggregation, `ComplianceResult`), `rules/docs.py`; CLI `bsm check`, `bsm rules docs`; dataset tags (`io/datasets.py`).

## Deviations from the plan (and why)
1. **Two extra profiles.** `base_checks` (same breed, alive at mating; the plan lists these types but no profile) and `dna_health` (carrier pairing and affected parent as SOFT, `verified: false`, source fci-strategies with a note that the wording is unverified). I first put the DNA rules in `eu_platform_guide` but moved them out so the guide is not credited with rules it may not contain. Composites: hr_full = base_checks + eu_2026_1818 + fci + hks_hr + eu_platform_guide + dna_health; uk_full = base_checks + kc_uk + eu_platform_guide + dna_health (UK is not EU or FCI); nl_full = base_checks + eu_2026_1818 + fci + rvb_nl + eu_platform_guide + dna_health.
2. `guide_coi_breed_mean` (INFO) cites `kc-coi` (KC advice style) rather than eu-platform-guide.
3. `health_grade_exclusion` with `missing: warn` marks a soft warning even when the rule is HARD (the plan's "allow|warn|block"); hks_hr uses `missing: allow`.
4. Rules use tested DNA results only (no hereditary-clear inference); the recommender (P7) adds inference for scoring.
5. `alive_at_mating` takes the mating method; frozen semen of a dead sire is exempt when `frozen_semen_exempt: true`.
6. No HKS litter-interval rule (task note: only if the Pravilnik states one; listed in the verification checklist).

## Numbers worth knowing
- hr_full: 14 rules, 9 of them unverified-or-sourced-from-press items flagged in the app (`verified: false`: eu_close_relatives, eu_dam_min_age, eu_dam_litter_frequency, hks_dam_min_age, hks_dam_max_age, dna_carrier_pairing, dna_affected_parent).
- `evaluate_candidates` for one SYN_M dam vs all males: about 10 ms; 2000 sires < 200 ms in the test.

## Open questions for Tea
- None blocking. The EU minimum dam age (18 months) and 3 litters in 24 months come from a press report and are HARD but unverified: keep them HARD in the demo (with the badge) or downgrade to SOFT until verified?

## HUMAN tasks waiting
- Verify EU 2026/1818 (articles, application date, ages, litter limits) and the HKS Pravilnik using `docs/rules_verification.md`, then flip `verified` and run `bsm rules docs`.
