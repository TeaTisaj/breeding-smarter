# Gate report: P7 Matching and explanations
Date: 2026-10-11

## Acceptance checklist
- [x] All MVP tasks done (7.1 to 7.8; 7.9 STRETCH skipped), tests pass, performance met:
  - `rank_fast`: 9.5 ms per SYN_M dam, 13.6 ms per SYN_L dam (target < 20 ms for SYN_M).
  - `recommend_sires` for a SYN_L dam on v1: cold 0.18 s (context already loaded; context load 0.22 s with cached F/D), warm 0.15 s (targets 2 s / 0.3 s; `test_recommend_performance`, slow).
  - Tests: `tests/unit/test_matching.py` (sub-score boundaries and monotonicity; health probabilities clear x anything = 0, carrier x carrier = 0.25 x penetrance, affected x carrier = 0.5 x penetrance, unknown uses q; hereditary-clear inference and flag; banned half-brother excluded; unrelated above first cousin with other components equal; ancestor shares sum to 100% and are sorted; `score_pair` = entry in `recommend_sires`; `rank_fast` = `recommend_sires` order and scores) and `tests/integration/test_matching_v1.py` (golden top-10 snapshot `tests/fixtures/golden/demo_top10.json`, demo stories hold, performance).
- [x] The three demo dams' top-5 tables and one full score card (below; also `reports/matching/demo_dams.md`). Demo dams in `configs/demo.yaml` (`bsm demo select`, deterministic).
- [ ] **[HUMAN]** Tea reviews the score card wording (it goes on the poster and in the app).

## What was built
`matching/config.py` (`ScoringConfig`, weights validated to sum to 1, tiers, `with_weights` for app sliders), `matching/context.py` (`DatasetContext`: registry tables, cached F/D/EqG, `RuleContext`, per-breed sub-pedigrees, per-(breed, year) reference mean kinship, hereditary-clear inference, allele frequencies from tested animals of the last 10 years, EBVs, owner coordinates), `matching/candidates.py`, `matching/components.py` (vectorised components and sub-scores), `matching/explain.py` (`ScoreCard` with headline template, component table, ancestor shares from the exact decomposition with generations back on both sides, depth warning, health matrix, rule badges, `to_markdown`, `to_dict`), `matching/recommend.py` (`recommend_sires`, `score_pair`, `rank_fast`), `matching/examples.py`; CLI `bsm match`, `bsm demo select`; `configs/scoring/default.yaml` (all policy values `assumption: true`; FCI share sourced).

## Deviations from the plan (and why)
1. **Demo dam 3**: imports in v1 do not have shallow recorded pedigrees (their ancestors were registered earlier through other imports and AI sires: first registration wins, as in a real registry), so no dam has EqG < 3. About 28% of foreign AI-sire records do. Dam 3 is therefore a dam whose top-ranked sire is a foreign AI sire with a shallow export pedigree (EqG 0), which triggers the depth warning for the litter.
2. **Reference population** per (breed, year) on Jan 1 of the mating year (cached in memory; one Colleau pass on the breed sub-pedigree, a few ms). F/D/EqG are cached on disk.
3. `CSR.count_before` vectorised (global searchsorted on key-encoded day numbers) to meet the `rank_fast` target.
4. Candidates include every registered male of breeding age (the registry does not record who is a stud); SYN_L dams have about 12,000 candidates.

## Known limitation worth stating (for Q&A and the poster)
Foreign AI-sire records with short pedigrees often rank at the top: their kinship to domestic dams is underestimated (unknown ancestors count as unrelated) and a missing EBV counts as the breed mean. The depth component (weight 0.05) and the depth warning only partly correct this. This is exactly the import problem the synthetic truth lets us measure; a breed club may want a larger depth weight or a penalty for missing EBVs. Not changed: weights are policy and belong to the breed club.

## Open questions for Tea
- Score card wording (headline template, "Why this COI?" text, health note): please review in `reports/matching/demo_dams.md`.
- Should missing EBVs count as 100 (current, as specified) or carry a small penalty?

## HUMAN tasks waiting
- Review score card wording.

## Demo dams on dataset v1 (mating date 2026-11-01, profile hr_full)

### Demo dam 1: Dumu od Mosa (SYN-HR-2021-001849), SYN_S

Small local breed: few good options. 349 candidate sires, 25 excluded by rules, 321 with warnings.

| Rank | Sire | Tier | Score | Pred. COI | P(affected) | HD index | Sire use | Warnings |
|---|---|---|---|---|---|---|---|---|
| 1 | Lovi of Liko (SYN-FOREIGN-HU-001296) | Excellent | 85.3 | 4.6% | 0.0% affected | 97 (missing EBV counted as 100) | 1 pups (5%) | 0 |
| 2 | Repe of Bemudu (SYN-FOREIGN-PL-000590) | Excellent | 80.4 | 5.7% | 0.0% affected | 97 (missing EBV counted as 100) | 1 pups (5%) | 0 |
| 3 | Tari vom Beka (SYN-FOREIGN-AT-000030) | Good | 74.0 | 6.3% | 0.0% affected | 97 (missing EBV counted as 100) | 3 pups (14%) | 0 |
| 4 | Neko od Mosa (SYN-HR-2015-003545) | Acceptable | 69.8 | 7.0% | 0.0% affected | 102 | 0 pups (0%) | 1 |
| 5 | Mila od Mosa (SYN-HR-2017-003294) | Acceptable | 69.8 | 7.0% | 0.0% affected | 102 | 0 pups (0%) | 1 |

### Demo dam 2: Romo od Samape (SYN-HR-2021-000783), SYN_M

The most popular sire is not on top: sire quota and kinship. 2110 candidate sires, 36 excluded by rules, 154 with warnings.

| Rank | Sire | Tier | Score | Pred. COI | P(affected) | HD index | Sire use | Warnings |
|---|---|---|---|---|---|---|---|---|
| 1 | Duma del Karo (SYN-FOREIGN-IT-000932) | Excellent | 90.4 | 1.7% | 0.0% affected | 95 (missing EBV counted as 100) | 1 pups (1%) | 0 |
| 2 | Sipe van Benoda (SYN-HR-2021-002135) | Excellent | 90.2 | 2.1% | 0.0% affected | 101 | 0 pups (0%) | 0 |
| 3 | Rosa of Zolata (SYN-HR-2019-003633) | Excellent | 89.6 | 1.9% | 0.0% affected | 106 | 10 pups (7%) | 0 |
| 4 | Toze of Zolata (SYN-HR-2024-000551) | Excellent | 89.5 | 1.9% | 0.0% affected | 96 | 0 pups (0%) | 0 |
| 5 | Muna od Kokano (SYN-HR-2016-002204) | Excellent | 89.3 | 2.1% | 0.0% affected | 99 | 0 pups (0%) | 0 |

Most used candidate sire Gine od Kokano (SYN-HR-2017-001831): rank 2074 of 2074, score 35.7 (Caution); Low Mendelian disease risk and a deep recorded pedigree; high predicted inbreeding (10.9% vs breed average 3.3%).

### Demo dam 3: Solu od Loveze (SYN-HR-2020-002485), SYN_L

Top match is a foreign AI sire with a shallow recorded pedigree: the litter's recorded COI is probably underestimated. 12118 candidate sires, 152 excluded by rules, 141 with warnings.

| Rank | Sire | Tier | Score | Pred. COI | P(affected) | HD index | Sire use | Warnings |
|---|---|---|---|---|---|---|---|---|
| 1 | Zema of Zoda (SYN-FOREIGN-FI-001774) | Excellent | 96.6 | 0.0% | 0.0% affected | 106 (missing EBV counted as 100) | 0 pups (0%) | 1 |
| 2 | Vene of Mavene (SYN-FOREIGN-HU-001355) | Excellent | 96.2 | 0.2% | 0.0% affected | 106 (missing EBV counted as 100) | 0 pups (0%) | 0 |
| 3 | Mika of Zoda (SYN-FOREIGN-FI-001855) | Excellent | 96.1 | 0.3% | 0.0% affected | 106 (missing EBV counted as 100) | 1 pups (0%) | 0 |
| 4 | Gito od Kasoba (SYN-FOREIGN-RS-001417) | Excellent | 96.0 | 0.3% | 0.0% affected | 106 (missing EBV counted as 100) | 1 pups (0%) | 0 |
| 5 | Sima od Kasoma (SYN-HR-2019-000764) | Excellent | 95.7 | 0.4% | 0.0% affected | 113 | 0 pups (0%) | 0 |

### Full score card (demo dam 2, top match)

#### Score card: Duma del Karo (SYN-FOREIGN-IT-000932) x Romo od Samape (SYN-HR-2021-000783)

*Synthetic data. Breed SYN_M, mating date 2026-11-01.*

**Excellent** (90/100, rules: PERMITTED). Low predicted inbreeding (1.7% vs breed average 3.3%) and the litter adds genetic diversity (low mean kinship); HD index below average (95).

| Component | Raw value | Breed reference | Sub-score | Weight | Points |
|---|---|---|---|---|---|
| Predicted inbreeding (COI) | 1.7% | 3.3% (recent litters) | 1.00 | 0.30 | 30.0 |
| Litter diversity (mean kinship) | 3.06% | 3.52% (mean MK) | 0.90 | 0.25 | 22.5 |
| Mendelian health risk | 0.0% affected | tested loci, breed frequencies | 1.00 | 0.20 | 20.0 |
| HD breeding value | 95 (missing EBV counted as 100) | 100 (breed mean) | 0.29 | 0.10 | 2.9 |
| Sire use (FCI 5% rule) | 1 pups (1%) | 100% = FCI 5% in 5 years | 0.99 | 0.10 | 9.9 |
| Pedigree depth (EqG) | 9.3 | target 6 generations | 1.00 | 0.05 | 5.0 |

### Why this COI? (1.7%)

| Ancestor | Generations back (sire side / dam side) | Share |
|---|---|---|
| Rilu of Zolata (SYN-FOREIGN-SE-000105) | 9 / 9 | 13.3% |
| Zepe of Zolata (SYN-FOREIGN-SE-000798) | 4 / 5 | 10.8% |
| Mata od Kokano (SYN-FOREIGN-NL-000011) | 11 / 11 | 4.1% |
| Kana van Benoda (SYN-FOREIGN-NL-000046) | 10 / 10 | 3.6% |
| Vera of Zolata (SYN-FOREIGN-SE-000058) | 10 / 10 | 3.3% |
| other ancestors | | 64.9% |

Each ancestor's share is the part of the predicted inbreeding that traces to genetic variation originating in that ancestor; shares add up to 100%.

### Health (tested loci)

| Locus | Sire | Dam | P(affected puppy) | P(carrier puppy) |
|---|---|---|---|---|
| ABCB1_MDR1 | clear (tested) | clear (inferred) | 0.0% | 0.0% |
| DNM1_EIC | clear (tested) | clear (inferred) | 0.0% | 0.0% |
| PRCD_PRA | clear (tested) | clear (inferred) | 0.0% | 0.0% |
| SOD1_DM | clear (tested) | unknown | 0.0% | 24.2% |

Allele frequencies for untested parents are estimated from tested animals born in the last 10 years; who gets tested biases them. Only tested loci are shown; untestable variants cannot be scored.

### Rules

- PASS `base_same_breed` (HARD): Sire and dam are of the same breed.
- PASS `base_alive` (HARD): Both parents alive on the mating date.
- PASS `eu_close_relatives` (HARD) [unverified]: No banned close relationship.
- PASS `eu_dam_min_age` (HARD) [unverified]: Dam age 66.5 months >= minimum 18 months.
- PASS `eu_dam_litter_frequency` (HARD) [unverified]: 1 litter(s) in 24 months including this one <= 3.
- PASS `fci_registration_type` (HARD): Both parents have full registration.
- PASS `fci_sire_quota` (SOFT): Sire offspring in 5 years incl. this litter 6 <= 5% of breed registrations (147).
- PASS `hks_hd_exclusion` (HARD): HD: sire none, dam none.
- PASS `hks_dam_min_age` (HARD) [unverified]: Dam age 66.5 months >= minimum 15 months.
- PASS `hks_dam_max_age` (HARD) [unverified]: Dam age 66.5 months <= maximum 96 months.
- PASS `guide_coi_6_5` (SOFT): Predicted COI of the litter 1.7% <= threshold 6.5%.
- PASS `guide_coi_breed_mean` (INFO): Predicted COI of the litter 1.7% <= breed average of recent litters 3.3%.
- PASS `dna_carrier_pairing` (SOFT) [unverified]: No known carrier x carrier combination.
- PASS `dna_affected_parent` (SOFT) [unverified]: No parent known affected at a tested locus.

