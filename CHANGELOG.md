# Changelog

## Unreleased
- E8 experiment (in silico): club quotas with a carrier limit (planned risk-allele
  transmission per tested locus at most 0.5 x the candidate mean) and/or gain OCS. New
  strategy ids `S3q[-gainNNN][-cBBB]`, `bsm experiment hypotheses --set e8`, figure M.
  Results: `plan/gates/E8_report.md`.
- Kennel club desk (prototype, app page 8): mating applications checked before the mating.
  - Automatic rule and club-quota checks, with three outcomes (Allowed, Needs club review,
    Blocked) and template-built explanations.
  - Stud owner confirmation, then a breeding officer queue with manual checks.
  - Quota booked on approval; mating certificate (prototype) download.
  - Season overview: counts, blocks by rule, quota per sire, compliance report (CSV).
  - See `docs/kennel_club_desk.md`.
- Rule engine: new rule type `max_caesareans`; HKS profile adds `hks_max_caesareans` and
  `hks_one_litter_12m` (unverified, source `hks-clubs-2026`). No EU caesarean rule until the
  Official Journal text confirms it.
- Mate finder: "Respect club quotas" is on by default.

## 0.1.0 (2026-10)
First public release for BioMedVetMech 2026 (Zagreb, 24 to 25 October 2026).
- Pedigree engine: Meuwissen and Luo inbreeding, Colleau kinship products, exact ancestor
  decomposition of kinship, mean kinship, Ne, founder statistics, completeness.
- Seeded synthetic registry simulator with hidden history, market, imports, gene drop,
  Mendelian loci, HD trait and registry-only BLUP.
- Calibration targets, validation report and dataset v1 (`20261011-default-s42`).
- Rule engine with EU 2026/1818, FCI, KC UK, Raad van Beheer, HKS and advisory profiles.
- Explainable mate recommender with score cards.
- Strategy experiments E1 (headline), E2 (adoption sweep) and E1b (balanced weights).
- Streamlit demo app and demo bundle.
