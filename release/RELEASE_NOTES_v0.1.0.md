# Breeding Smarter 0.1.0

Open, explainable, rule-aware mate matching for genetic diversity in dogs, with a calibrated
synthetic pedigree benchmark. **All data is synthetic; all results are in silico.**

Assets:
- `breeding-smarter-synthetic-v1.zip`: dataset v1 (registry + ground truth, Parquet and CSV,
  datasheet, data dictionary, validation report, SHA256SUMS). CC BY 4.0.
- `bundle.tar.gz`: demo bundle for the Streamlit app.

Highlights: Meuwissen and Luo inbreeding and Colleau kinship in numba (250k animals in under
a second); exact explanation of predicted COI by ancestor; EU Regulation 2026/1818, FCI, KC,
RvB and HKS rule profiles with verification status; score cards; 10-generation experiments.

Also in this release:
- **Club planner**: yearly litter quotas per sire (optimum contribution selection), optionally
  with a hips budget and a carrier limit.
- **Kennel club desk** (prototype): mating applications checked against the rules before the
  mating, with stud-owner confirmation, a breeding-officer queue and a mating certificate.
- **Experiments E1 to E10** with pre-registered criteria. In the synthetic medium breed, club
  quotas with a hips budget and a carrier limit beat a simulated status-quo market on
  diversity, hips and tested disease-allele frequency, replicated on an independent seed
  (`plan/gates/E9_report.md`, including the hypotheses that failed).

See CHANGELOG.md.
