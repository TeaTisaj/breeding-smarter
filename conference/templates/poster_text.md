# Breeding Smarter: A Data-Driven Matching System for Genetic Diversity in Dogs and Beyond
Tea Ćetojević Tisaj, Marija Perković · University of Zagreb, FER

## The problem
- Purebred dogs: mean genomic inbreeding {lit_genomic_f} across {lit_breeds_genotyped} breeds.
- Popular sires in all {lit_kc_breeds_popular_sires} Kennel Club breeds.
- {lit_carrier_share} of {lit_dogs_screened} dogs carry a disease variant.

## Why now
EU Regulation 2026/1818 bans close-relative matings. Clubs must check every mating, but today they have lookup tools, not decision tools.

## One engine, three tools for a kennel club
- **Breeders: Mate finder.** Every candidate sire ranked and explained: inbreeding, breed diversity, DNA risk, hips, sire use, rules.
- **Breeding officer: Kennel club desk.** Mating applications checked against EU, FCI and club rules before the mating.
- **Breeding committee: Club planner.** Yearly litter quotas per sire: the club sets an inbreeding budget and sees what it buys.

## Recorded COI hides inbreeding
Small breed, 2025 puppies: recorded COI {recorded_f_2025_S}, true inbreeding {true_f_2025_S}.

## Does it work?
Ten simulated generations on a calibrated synthetic registry ({n_animals} dogs), with criteria fixed before every run. Club quotas with a hips budget (inbreeding rise at most 0.1% per generation) and a carrier limit beat today's market on all three at once in the medium breed: Ne {e9_rep_ne_est} ({e9_rep_ne_ci}), hip breeding value {e9_rep_hd_est}, disease-allele frequency {e9_freq_cut_vs_s1} lower. Replicated on an independent seed. At the lowest budget, diversity stayed at the level of plain quotas while hips and disease alleles still improved.

## Honesty box
All dogs are synthetic; results are in silico. The carrier limit works when most breeders take part. Some EU rules are not yet verified.

## Partner with us
Free pilot for kennel and breed clubs: one breed, your data stays on your servers. Scan for the live demo and code.

Refs: Bannasch 2021; Lewis 2015; Donner 2023; Meuwissen and Luo 1992; Meuwissen 1997.
