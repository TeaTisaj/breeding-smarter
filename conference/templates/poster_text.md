# Breeding Smarter: A Data-Driven Matching System for Genetic Diversity in Dogs and Beyond
Tea Ćetojević Tisaj, Marija Perković · University of Zagreb, FER

## The problem
- Purebred dogs: mean genomic inbreeding {lit_genomic_f} across {lit_breeds_genotyped} breeds.
- Popular sires in all {lit_kc_breeds_popular_sires} Kennel Club breeds.
- {lit_carrier_share} of {lit_dogs_screened} dogs carry a disease variant.

## Why now
EU Regulation 2026/1818 bans close-relative matings across the EU.

## What we built
An open engine: exact inbreeding and kinship, EU, FCI and kennel-club rules, and an explained score for every candidate sire. Tested on a calibrated synthetic registry ({n_animals} dogs; {val_pass} of {val_n_checks} calibration checks pass, {val_warn} soft warnings, {val_fail} failures).

## Recorded COI hides inbreeding
2025 puppies of the small breed: recorded COI {recorded_f_2025_S}, true inbreeding {true_f_2025_S}.

## Does it work?
Ten simulated generations: the recommender cut realised inbreeding by {e1_dibd_S_S3_abs} points in the small breed and nearly removed affected puppies at tested loci, but breeders all chose the same sires. Club quotas fix this: coordinated sire planning raised Ne from {p12_ne_S_s1} (today's market) to {p12_ne_S_cc_ocs_mc1} in the small breed and from {p12_ne_M_s1} to {p12_ne_M_cc_ocs_mc1} in the medium breed; the recommender within quotas did as well. Random mating still kept the most diversity in the medium breed.

## Honesty box
All dogs are synthetic. Results are in silico. Some EU rules are not yet verified.

## Partner with us
Free pilot for kennel and breed clubs; code runs on your premises.

Refs: Bannasch 2021; Lewis 2015; Donner 2023; Meuwissen and Luo 1992; Colleau 2002.
