# Breeding Smarter: A Data-Driven Matching System for Genetic Diversity in Dogs and Beyond

Tea Ćetojević Tisaj¹, TODO colleague¹
¹ University of Zagreb, Faculty of Electrical Engineering and Computing, Zagreb, Croatia

*Draft for the IFMBE Proceedings (BioMedVetMech 2026), only if a late submission is accepted. Check the length limit and formatting in the IFMBE template; numbers come from conference/numbers.json.*

## Abstract
Purebred dog populations lose genetic diversity through popular-sire use and closed studbooks, while kennel clubs mainly offer lookup tools for the inbreeding coefficient (COI) of a single dog or mating. We present an open, explainable, rule-aware mate-matching system and a calibrated synthetic benchmark. A seeded simulator generates a registry of three fictional breeds ({n_animals} registered dogs) with a hidden ground truth (realised identity by descent, true breeding values, untested genotypes); {val_pass} of {val_n_checks} calibration checks against published statistics pass, with no failures. A pedigree engine computes inbreeding (Meuwissen and Luo), kinship products (Colleau) and an exact additive explanation of a pair's predicted inbreeding by ancestor; on the synthetic data the engine agrees with neutral gene drop within {engine_max_diff_S} per birth decade. A rule engine encodes EU Regulation 2026/1818, FCI, Kennel Club, Raad van Beheer and HKS profiles with source and verification status, and a multi-factor score ranks candidate sires. In ten simulated generations, recommender-guided matings reduced realised inbreeding by {e1_dibd_S_S3_abs} percentage points in a small breed and nearly removed affected puppies at tested loci, but long-term effective population size improved only with coordinated sire use. All data and results are synthetic.

**Keywords:** dog breeding, inbreeding, kinship, mate selection, synthetic data, EU Regulation 2026/1818

## 1 Introduction
Across {lit_breeds_genotyped} breeds, mean genomic inbreeding is {lit_genomic_f} [Bannasch 2021]. Popular sires appear in all {lit_kc_breeds_popular_sires} Kennel Club breeds and the effective population size (Ne) is below 100 in {lit_ne_below_100} breeds with estimates [Lewis 2015]; {lit_carrier_share} of {lit_dogs_screened} screened dogs carry at least one disease variant [Donner 2023]. EU Regulation 2026/1818 now bans matings between close relatives. Kennel clubs provide COI lookups but no decision support that combines population diversity, health information and rules.

## 2 Related work
Kennel-club tools (Mate Select, SKK Avelsdata, Kennelliitto KoiraNet, the Raad van Beheer rule module) compute COI or check rules. Zoo software (PMx) ranks pairs by mean kinship without health or regulatory constraints. Research packages (optiSel) implement optimum contribution selection without an interface. No open tool combines multi-jurisdiction rules, mean kinship, carrier status, breeding values and per-pair explanations.

## 3 Methods
**Synthetic data.** An agent-based simulator advances one year at a time from unrelated base founders (1935) through a hidden history, a domestic/foreign split and registry founding in 1980, with a breeding market (popular-sire feedback, distance, close-relative avoidance), imports and foreign AI sires registered with short pedigrees, inbreeding depression on litter size, a neutral gene drop (2,000 loci), five recessive disease loci with DNA testing and a polygenic hip-dysplasia (HD) trait with FCI screening and registry-only BLUP. Eighteen calibration targets cite published values (litter size, sire concentration, Ne by breed size, inbreeding trends); every other parameter is listed as an assumption.

**Pedigree engine.** Inbreeding by Meuwissen and Luo; A·x products in O(n) by Colleau's method; mean kinship, gene diversity, Ne (individual increase in inbreeding and census), founder statistics and equivalent generations. The predicted inbreeding of a pair, f_sd = Σ_j ½ L_sj L_dj D_j, is split exactly over common ancestors j. Inbreeding for 250,000 animals takes {bench_inbreeding_250k_s} s.

**Rules and score.** Jurisdiction profiles in YAML give HARD (not permitted), SOFT (warning) or INFO rules, each with its source and verification flag. Permitted sires are scored as a weighted sum of six sub-scores: predicted inbreeding, litter mean kinship, Mendelian risk from tested or inferred genotypes, HD breeding value, sire use relative to the FCI 5% guideline, and pedigree depth. Weights are policy choices for breed clubs.

**Experiments.** From the 2026 state we simulated ten generations under five strategies (random, status-quo market, regulated market with a 6.5% COI cap, recommender with breeders choosing among the top three, coordinated planner), with {e1_reps_S} (small breed) and {e1_reps_M} (medium breed) replicates and common random numbers; strategies see only registry data.

## 4 Results
**Validation.** {val_pass} of {val_n_checks} checks pass and {val_warn} soft targets warn. Ne of the 2016 to 2025 cohort is {ne_L}, {ne_M} and {ne_S} for the large, medium and small archetypes. Recorded pedigree COI underestimates truth: for 2025 puppies of the small breed, recorded {recorded_f_2025_S} vs true pedigree {true_f_2025_S}. The engine matches gene drop (regression slope {engine_slope_S} in the small breed).

**Case study.** For a medium-breed dam, the breed's most used candidate sire ranked last among all candidates (high predicted COI and sire use), while the top match had a predicted COI below the breed average; a half-brother was excluded by the EU close-relative ban.

**Strategies.** After ten generations in the small breed, realised inbreeding was {e1_ibd_S_S1} under the market and {e1_ibd_S_S3} with the recommender (paired difference {e1_dibd_S_S3} points, 95% CI {e1_dibd_S_S3_ci}); recorded COI fell far more ({e1_drec_S_S3} points). The recommender nearly removed affected puppies at a tested locus in the medium breed ({e1_mdr1_M_S1} vs {e1_mdr1_M_S3}) and improved the HD breeding value, but Ne did not improve ({e1_ne_S_S1} vs {e1_ne_S_S3}); random mating kept Ne at {e1_ne_S_S0}. With full adoption realised inbreeding was {e2_ibd_a100} vs {e2_ibd_a0} without the tool.

**Coordinated sire use.** We added a club planner that sets yearly litter quotas per sire by optimum contribution selection (minimum expected coancestry, mean-kinship-scaled caps of up to five litters, constraints on age classes and pedigree depth) and either allocates matings by minimum coancestry or lets breeders choose among the recommender's top three within the quotas. Against criteria fixed before running, coordinated planning raised Ne (late window, generations 5 to 10) over the market in both breeds (small: +{p12_h1_S_est}, 95% CI {p12_h1_S_ci}; medium: +{p12_h1_M_est}, {p12_h1_M_ci}) and lowered the rate of inbreeding compared with the recommender alone (small: {p12_h2_S_est} points per generation, {p12_h2_S_ci}). The recommender within quotas performed similarly (Ne {p12_ne_S_s3q} and {p12_ne_M_s3q}). Minimum-coancestry mating without quotas was the worst strategy ({p12_dflate_S_cc_none_mc1}% per generation in the small breed), so contribution control and mating method cannot be separated. Planning on true instead of recorded kinship raised Ne further (small breed +{p12_h6_S_est}, {p12_h6_S_ci}), but random mating still kept more diversity in the medium breed.

## 5 Discussion and limitations
Per-dam rankings concentrate use on the same low-kinship sires; club-level quotas from optimum contribution selection correct this in silico, while breeders keep a choice within the quotas. Acceptance by clubs and breeders is untested. Results are in silico on synthetic data; kinship is pedigree-based and underestimated for short pedigrees; HD uses a linear model on grades; disease allele frequencies are illustrative; several EU details are unverified press reports. The design is species-agnostic: species and breed parameters and rules live in configuration files.

## 6 Conclusion
Explainable, rule-aware matching is feasible and fast, and a synthetic benchmark with ground truth exposes how much recorded COI hides. We invite kennel and breed clubs to pilot the tool on real data.

**Statements.** No animals were used; all data are synthetic. Code: {link_github}; data: {link_dataset_doi}. Author contributions: TODO. Conflicts of interest: none.

## References
Bannasch D. et al. (2021) Canine Med Genet. · Lewis T.W. et al. (2015) Canine Genet Epidemiol. · Donner J. et al. (2023) PLoS Genet. · Meuwissen T.H.E., Luo Z. (1992) Genet Sel Evol. · Colleau J.J. (2002) Genet Sel Evol. · Gutiérrez J.P. et al. (2008) Genet Sel Evol. · Ballou J.D., Lacy R.C. (1995). · Lacy R.C. (2012) PMx. · Meuwissen T.H.E. (1997) J Anim Sci. · Borge K.S. et al. (2011) Theriogenology. · Regulation (EU) 2026/1818.
