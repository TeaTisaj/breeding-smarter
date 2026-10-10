# P7: Matching and explanations

**Goal:** for a given dam (bitch) and mating date, rank all permitted candidate sires by an explainable multi-factor score, and produce a score card for any pair. This is what the demo shows and what a breeder or kennel club would use.
**Effort:** 1 day. **Depends on:** P2, P6.

Module: `src/breeding_smarter/matching/`. Design inspired by the zoo Mate Suitability Index (MSI, Ballou et al. 2001; PMx, Lacy 2012), adapted to registries: rule compliance, Mendelian health risk and EBVs added.

---

## 1. Dataset context [MVP]

`matching/context.py`: `DatasetContext.load(tag="v1")` builds and caches (on disk under the run's `cache/` folder, and in memory):
- `Pedigree` (registry), `F`, `D`, `EqG`.
- Per breed: the breed sub-pedigree (breed animals plus ancestors, pruned once) to keep every O(n) pass small.
- Per (breed, reference year): reference population = living animals of breeding age on the reference date; their `MK` vector (one Colleau pass), mean and SD of MK, mean F of litters born in the last 5 years (breed reference for display).
- Health: latest HD grade per animal; DNA genotype per (animal, locus) with **hereditary clear** inference (an untested animal whose sire and dam are both tested clear is clear; one generation only, flagged as inferred).
- Allele frequency estimate per (breed, locus) from tested animals born in the last 10 years (state the testing bias in the docstring and on the score card).
- EBVs (latest), sire offspring counts per 5-year window, breed registrations per window.
- `RuleContext` from P6.

## 2. Components [MVP]

For dam `d` and each candidate sire `s` (vectorised over candidates):

| Component | Raw value | Sub-score in [0, 1] (higher is better) |
|---|---|---|
| Inbreeding | `F_off = f(s, d)` from `kinship_to_all(d)` (one Colleau pass for all candidates) | 1 if `F_off <= f_low`, 0 if `F_off >= f_high`, linear in between. Defaults `f_low = 0.03`, `f_high = 0.125` (half-sibling level), assumptions |
| Diversity | Expected MK of the litter `MK_off = (MK_s + MK_d) / 2` | `1 - Phi((MK_off - mean_MK_ref) / sd_MK_ref)` |
| Health (Mendelian) | Per locus `P_aff = t_s * t_d * penetrance`, transmission prob `t` = 0 clear, 0.5 carrier, 1 affected, `q_breed` if unknown; combined `P_any = 1 - prod(1 - P_aff)` | `1 - min(1, P_any / 0.25)` |
| Breeding value (HD) | Expected litter index `(EBV_s + EBV_d) / 2`; missing EBV = 100 with accuracy 0, flagged | `Phi((index - 100) / 10)` |
| Sire use | `ratio = offspring_5y(s) / (0.05 * breed_regs_5y)` (FCI 5% rule) | `1 - min(1, ratio)` |
| Pedigree depth | `(EqG_s + EqG_d) / 2` | `min(1, value / eqg_target)`, `eqg_target = 6` (assumption) |

Notes:
- The health component uses only tested (or inferred) loci and breed frequencies. `NOVEL_X` is never visible here.
- `Phi` is the standard normal CDF (scipy).

`configs/scoring/default.yaml`:
```yaml
weights: {inbreeding: 0.30, diversity: 0.25, health: 0.20, ebv: 0.10, sire_use: 0.10, depth: 0.05}
inbreeding: {f_low: 0.03, f_high: 0.125}
depth: {eqg_target: 6}
tiers: [{min: 80, label: Excellent}, {min: 65, label: Good}, {min: 50, label: Acceptable},
        {min: 35, label: Caution}, {min: 0, label: Not recommended}]
soft_warning_caps_tier_at: Acceptable
low_depth_warning_eqg: 3
```
All of these are **policy choices**, marked `assumption: true` with a note: "Weights express breeding priorities and should be set by the breed club." Weights must sum to 1 (validated).

`total = 100 * sum(w_k * s_k)`. Tier from thresholds; any failed SOFT rule caps the tier; failed HARD rule means the candidate is excluded (kept in an "excluded" list with reasons).

## 3. Tasks

- **7.1 [MVP]** `DatasetContext` (section 1), with a cache-key including the engine version and dataset tag.
- **7.2 [MVP]** `matching/candidates.py`: candidates = registered males of the dam's breed, alive on the mating date, of breeding age (species config), not limited registration. Option `max_distance_km` (haversine between kennels). Option `include_foreign` (default true).
- **7.3 [MVP]** `matching/components.py`: vectorised component computation (section 2). No Python loops over candidates.
- **7.4 [MVP]** `matching/score.py`: sub-scores, weights, tiers, caps.
- **7.5 [MVP]** `matching/explain.py`: `ScoreCard` (pydantic) for one pair:
  - headline: tier, score, and a one-line template summary built from the strongest positive and negative components (for example "Low predicted inbreeding (1.2% vs breed average 4.8%) and an under-used sire; HD index slightly below average.")
  - component table: raw value, breed reference, sub-score, weight, points contributed
  - inbreeding explanation: top 5 ancestors by contribution from `pair_kinship_decomposed` (P2): reg_no, name, generations back on the sire side and on the dam side, share of predicted F; plus "other ancestors: x%". Explain in the card text: "Each ancestor's share is the part of the predicted inbreeding that traces to genetic variation originating in that ancestor; shares add up to 100%."
  - depth warning if either parent's EqG is below `low_depth_warning_eqg`: "Recorded inbreeding is probably underestimated (shallow pedigree, for example an import)."
  - health matrix per tested locus: sire status, dam status (tested, inferred, unknown), P(affected puppy), P(carrier puppy)
  - rule results (badges with verified/unverified marker)
  - `to_markdown()` and `to_dict()`.
- **7.6 [MVP]** `matching/recommend.py`:
  ```python
  def recommend_sires(ctx, dam_idx, mating_date, profile="hr_full", scoring=None,
                      top_k=20, max_distance_km=None) -> Recommendation
  def score_pair(ctx, sire_idx, dam_idx, mating_date, profile="hr_full", scoring=None) -> ScoreCard
  ```
  `Recommendation` contains the ranked list (score cards built lazily for the top_k), counts (candidates, excluded by rule, with warnings), and the reference values used.
- **7.6b [MVP]** `rank_fast(ctx, dam_idx, mating_date, profile, scoring) -> (sire_idx array, score array)`: the same components and rules as `recommend_sires`, but no score cards, messages or pandas. P8 calls it thousands of times. Target under 20 ms per dam for SYN_M. Test: it returns the same order and scores as `recommend_sires`.
- **7.7 [MVP]** CLI `bsm match --dataset v1 --dam <reg_no> [--date] [--profile] [--top 10] [--explain <sire reg_no>]`.
- **7.8 [MVP]** (run once dataset v1 is frozen in P5; develop on v0 until then) Example selection script `matching/examples.py`: pick 3 demo dams from dataset v1 automatically and deterministically (one in SYN_S with few good options, one in SYN_M where the most popular sire is ranked low because of quota and kinship, one import-heavy pedigree that triggers the depth warning). Save their reg_nos to `configs/demo.yaml` for the app and slides.
- **7.9 [STRETCH]** Reverse search (stud owner looking for bitches), symmetric implementation.

## 4. Tests
- Sub-score functions: boundaries and monotonicity (lower F gives higher score; higher MK gives lower score).
- Health probabilities: clear x anything = 0; carrier x carrier = 0.25 x penetrance; affected x carrier = 0.5 x penetrance; unknown uses `q`; hereditary clear inference works and is flagged.
- Explanation: ancestor shares sum to 100% (from contributions summing to F within 1e-12) and are sorted.
- Fixture ranking: a banned half-brother is excluded; with other components equal, an unrelated sire ranks above a cousin.
- `score_pair(s, d)` equals the entry for `s` in `recommend_sires(d)`.
- Golden snapshot: top 10 for the 3 demo dams stored as JSON; any change must be intentional (update the snapshot in the same commit with a reason).
- Performance: `recommend_sires` under 2 s for a SYN_L dam (cold cache excluded), under 300 ms warm.

## 5. Acceptance checklist (gate)
- [ ] All tasks MVP done, tests pass, performance met.
- [ ] Gate report contains the three demo dams' top 5 tables and one full score card in markdown.
- [ ] Tea reviews the score card wording (it goes on the poster and in the app).
