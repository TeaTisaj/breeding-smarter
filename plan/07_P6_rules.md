# P6: Rule engine

**Goal:** decide, for any sire x dam pair on a given mating date, whether the mating is permitted under a chosen set of rules (jurisdiction profiles), with a clear message and source for every rule. Rules live in YAML; the engine never hard-codes a regulation.
**Effort:** 0.5 day. **Depends on:** P2 (relationships, F). Uses dataset v1 tables.

Module: `src/breeding_smarter/rules/`.

---

## 1. Concepts

- **Rule:** one check with a `type` (implemented in code), `params`, `severity` (`HARD` = not permitted, `SOFT` = warning, `INFO` = shown only), `source` (key from `configs/sources.yaml`), `verified` (bool), `article` (string or null), `note`.
- **Profile:** a named list of rules, can `include` other profiles. Profiles: `eu_2026_1818`, `fci`, `kc_uk`, `rvb_nl`, `hks_hr`, `eu_platform_guide`, and composites `hr_full` (= eu_2026_1818 + fci + hks_hr + eu_platform_guide, the default for the demo), `uk_full`, `nl_full`.
- **Outcome:** `ComplianceResult` with overall status `PERMITTED`, `PERMITTED_WITH_WARNINGS` or `NOT_PERMITTED`, and a list of `RuleResult(rule_id, profile, severity, passed, message, value, threshold, source, verified, article)`.

## 2. Rule types to implement [MVP]

| type | params | Logic |
|---|---|---|
| `same_breed` | | sire and dam breed equal (crossbreeding programmes are out of scope) |
| `alive_at_mating` | | both alive on the mating date (frozen semen: sire may be dead if `mating_method = ai_frozen`; accept a flag) |
| `registration_type` | `disallowed: [limited]` | neither parent has limited registration (fci-strategies) |
| `relationship_ban` | `relationships: [...]` | uses `pedigree.relationships.relationship()`; message names the relationship and the linking ancestor(s) by reg_no |
| `min_age` / `max_age` | `sex`, `months` or `years` | age on mating date |
| `min_interval_between_litters` | `months` | dam's last whelp date to this mating date |
| `max_litters_in_window` | `max`, `window_months` | dam's litters in the window including the proposed one |
| `max_lifetime_litters` | `max`, `sex` | dam lifetime litters, or sire lifetime litters (RvB stud limit example) |
| `health_grade_exclusion` | `test_type`, `exclude: [E]`, `missing: allow\|warn\|block` | latest official result |
| `affected_exclusion` | `loci: all_tested` | parent known affected at a tested locus |
| `carrier_pairing` | `loci: all_tested` | both parents known carrier or affected at the same locus; severity set per profile |
| `offspring_coi_threshold` | `threshold` or `relative_to_breed_mean: true` | `f(sire, dam)` from P2 vs threshold |
| `sire_quota` | `share`, `window_years` | sire's offspring registered in the window (plus expected litter size) vs `share` x breed registrations in the window |

Every rule implements:
```python
class Rule(Protocol):
    id: str

    def check_many(
        self, ctx: RuleContext, dam: int, sires: np.ndarray, mating_date: date
    ) -> RuleBatchResult: ...  # vectorised over candidate sires
```
`check_one` is a thin wrapper. `RuleContext` is built once per dataset: pedigree arrays, F, D, latest health and DNA results as arrays indexed by idx, litters per dam and sire as sorted arrays, breed registrations per year, breed config (including `is_local_breed`). No pandas inside `check_many`.

## 3. Profiles (YAML) [MVP]

`configs/rules/eu_2026_1818.yaml`:
```yaml
profile: eu_2026_1818
title: "EU Regulation 2026/1818 (welfare and traceability of dogs and cats)"
in_application_from: null      # [HUMAN] fill from the OJ text
local_breed_derogation_granted: false   # derogation needs a competent-authority decision
rules:
  - id: eu_close_relatives
    type: relationship_ban
    params: {relationships: [PARENT_OFFSPRING, FULL_SIBLINGS, HALF_SIBLINGS, GRANDPARENT_GRANDCHILD]}
    severity: HARD
    derogation: local_breed          # downgraded to SOFT if breed is local AND derogation granted
    source: eurlex-2026-1818
    article: null                    # [HUMAN] fill
    verified: false                  # set true once the article is checked in the OJ text
  - id: eu_dam_min_age
    type: min_age
    params: {sex: F, months: 18}
    severity: HARD
    source: euroweekly-2026
    verified: false                  # press report only
  - id: eu_dam_litter_frequency
    type: max_litters_in_window
    params: {max: 3, window_months: 24}
    severity: HARD
    source: euroweekly-2026
    verified: false                  # press report only
```
`fci.yaml`: `registration_type` (HARD, verified), `sire_quota` 5% / 5 years (SOFT, verified, note that it is a guideline and non-binding in large breeds, leroy-rognon-2012).
`kc_uk.yaml`: `relationship_ban [PARENT_OFFSPRING, FULL_SIBLINGS]` (HARD, verified, kc-coi).
`rvb_nl.yaml`: `relationship_ban [PARENT_OFFSPRING, FULL_SIBLINGS, GRANDPARENT_GRANDCHILD]` (HARD; the template's "brother" is read as full brother; note that some breed VFRs also ban half siblings) and an example `max_lifetime_litters {sex: M, max: 25}` as SOFT with note "example from one breed VFR".
`hks_hr.yaml`: `health_grade_exclusion HD [E]` (HARD, verified), `min_age F 15 months` and `max_age F 8 years` (HARD, `verified: false` for non-hunting breeds: the source covers hunting breeds), `min_interval_between_litters` only if the Pravilnik states one ([HUMAN] check; leave out otherwise).
`eu_platform_guide.yaml`: `offspring_coi_threshold 0.065` (SOFT, source eu-platform-guide) and `offspring_coi_threshold relative_to_breed_mean` (INFO, KC advice style).

Loader validation: unknown rule type, unknown relationship name, missing source, include cycles: all fail loudly.

## 4. Tasks
- **6.1 [MVP]** Rule models and loader (`rules/models.py`, `rules/loader.py`), profile composition with `include`, deduplication by rule id (a rule included twice is evaluated once).
- **6.2 [MVP]** `RuleContext` builder from dataset tables (`rules/context.py`), cached per dataset.
- **6.3 [MVP]** Rule implementations (`rules/types/*.py`), one file per family (pedigree, age and litters, health, quota).
- **6.4 [MVP]** `evaluate_pair` and `evaluate_candidates` (`rules/engine.py`), derogation handling, status aggregation, human-readable messages that name relatives by `reg_no` and name.
- **6.5 [MVP]** CLI `bsm check --dataset v1 --sire <reg_no> --dam <reg_no> [--date YYYY-MM-DD] [--profile hr_full]` printing a rich table.
- **6.6 [HUMAN]** Verification checklist `docs/rules_verification.md` (Claude Code generates it from the YAML: every rule with `verified: false`, what to check, where). Tea fills article numbers, ages, litter limits and the application date from the EUR-Lex text and the HKS Pravilnik, then flips `verified`.
- **6.7 [MVP]** `docs/rules_catalogue.md` generated from the YAML (rule, profile, severity, source, verified): used in the paper appendix and app.

## 5. Tests
- One unit test per rule type with pass and fail cases on fixture pedigrees (including every relationship in the ban list, and a pair that is related only beyond the banned degrees, for example first cousins: must pass `relationship_ban`).
- Derogation: local breed plus granted flag downgrades HARD to SOFT; non-local breed unaffected.
- `check_many` equals `check_one` applied element-wise (property test on random dams and candidates from the tiny run).
- Composite profile `hr_full` contains the expected rule ids, each once.
- Status aggregation: any failed HARD gives `NOT_PERMITTED`; only SOFT failures give `PERMITTED_WITH_WARNINGS`.
- Performance: `evaluate_candidates` for one dam vs 2000 candidate sires under 200 ms.

## 6. Acceptance checklist (gate)
- [ ] All rule types and profiles implemented; loader rejects bad YAML.
- [ ] Tests pass; performance target met.
- [ ] `bsm check` demo on 3 example pairs from dataset v1 (one permitted, one with warnings, one not permitted) pasted in the gate report.
- [ ] `docs/rules_verification.md` and `docs/rules_catalogue.md` generated; HUMAN verification task listed.
