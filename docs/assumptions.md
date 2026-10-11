# Assumptions

Generated from the YAML configs (`bsm docs assumptions`). Every value below is marked
`assumption: true`: it is a modelling or policy choice, not a published number.
Values with a `source` are cited in `configs/sources.yaml` and not listed here.

| Config | Parameter | Value | Note |
|---|---|---|---|
| sim | generation_interval_years | 4.5 | research says 4 to 5 years; confirm in P5 |
| sim | foreign.size_factor | 1.0 | foreign registrations per year relative to the domestic 1980 level |
| sim | market.distance_scale_km | 300.0 | exp(-distance / 300 km) weight, P3 task 3.5 |
| sim | market.same_kennel_exclusion_prob | 0.5 | breeders often use outside studs |
| sim | market.prime_age_years | (2.0, 8.0) |  |
| sim | market.off_prime_age_factor | 0.5 |  |
| sim | market.max_resample_retries | 5 |  |
| sim | registry.limited_registration_share | 0.3 | share of non-candidates with limited registration (P3 task 3.8) |
| sim | registry.titles_rate | 0.05 | titles ~ Poisson(0.05 exp(attractiveness)) |
| sim | registry.dogs_per_private_owner | 1.5 | one owner per 1 to 2 dogs |
| sim | registry.min_founders | 10 | lower bound on scaled base founders |
| species | gestation_days | 63 | textbook mean, range 56-70 |
| species | gestation_sd_days | 2.0 | P3 task 3.6: 63 +/- 2 days |
| species | min_breeding_age_months.male | 12.0 |  |
| species | max_breeding_age_years.male | 12.0 |  |
| species | lifespan_weibull | {'shape': 4.0, 'scale_years': 12.5} |  |
| species | sex_ratio_male | 0.5 |  |
| species | death_cause_shares | {'age': 0.8, 'disease': 0.12, 'accident': 0.05, 'unknown': 0.03} | P3 task 3.4: mostly age, small shares otherwise |
| species | attractiveness_sd | 1.0 | P3 task 3.6, sigma_a = 1 |
| species | fertility_log_sd | 0.15 | P3 task 3.6, LogNormal(0, 0.15) |
| genetics | n_neutral_loci | 2000 | plan suggested 200; raised in P5 (200 -> 1000 -> 2000) so that realised IBD of the small, highly inbred breed is precise enough for T12/T13 (noise scales with 1/sqrt(loci)) |
| genetics | hd_heritability | 0.35 | chosen inside the reported 0.25 to 0.7 |
| genetics | hd_screening_age_months | (12, 24) |  |
| genetics | dna_test_min_age_months | 12 |  |
| genetics | dna_test_rate_initial | 0.1 | test rate in the year a test becomes available |
| genetics | dna_test_rate_ramp_end_year | 2026 |  |
| genetics | import_dna_test_prob | 0.7 | imports and foreign AI sires tested on entry |
| genetics | affected_exclusion_prob | 0.8 | known affected animals not bred |
| genetics | carrier_pair_resample_prob | 0.9 | known carrier x carrier pairs resampled |
| genetics | ebv_birth_year_group_years | 5 |  |
| genetics | ebv_index_sd_window_years | 5 | index SD from animals born in the last 5 years |
| loci | loci[0].penetrance | 0.95 |  |
| loci | loci[0].test_available_from | 2005 |  |
| loci | loci[1].penetrance | 0.5 |  |
| loci | loci[1].test_available_from | 2009 |  |
| loci | loci[2].penetrance | 1.0 | phenotype = drug sensitivity |
| loci | loci[2].test_available_from | 2004 |  |
| loci | loci[3].penetrance | 0.8 |  |
| loci | loci[3].test_available_from | 2008 |  |
| loci | loci[4].penetrance | 1.0 |  |
| loci | base_allele_frequency | {'SYN_L': {'PRCD_PRA': 0.08, 'SOD1_DM': 0.25, 'ABCB1_MDR1': 0.0, 'DNM1_EIC': 0.1, 'NOVEL_X': 0.05}, 'SYN_M': {'PRCD_PRA': 0.05, 'SOD1_DM': 0.15, 'ABCB1_MDR1': 0.12, 'DNM1_EIC': 0.0, 'NOVEL_X': 0.05}, 'SYN_S': {'PRCD_PRA': 0.12, 'SOD1_DM': 0.1, 'ABCB1_MDR1': 0.0, 'DNM1_EIC': 0.0, 'NOVEL_X': 0.05}} | risk-allele frequencies in the base founders; illustrative (P4 task 4.3) |
| scoring | weights | {'inbreeding': 0.3, 'diversity': 0.25, 'health': 0.2, 'ebv': 0.1, 'sire_use': 0.1, 'depth': 0.05} | Weights express breeding priorities and should be set by the breed club. |
| scoring | inbreeding.f_low | 0.03 | sub-score 1 at or below this predicted COI |
| scoring | inbreeding.f_high | 0.125 | sub-score 0 at or above (half-sibling level) |
| scoring | health.p_any_zero_score | 0.25 | P(affected puppy) giving sub-score 0 |
| scoring | ebv.index_mean | 100.0 | SKK-style index scale |
| scoring | ebv.index_sd | 10.0 |  |
| scoring | depth.eqg_target | 6.0 | equivalent generations giving sub-score 1 |
| scoring | tiers | [(80.0, 'Excellent'), (65.0, 'Good'), (50.0, 'Acceptable'), (35.0, 'Caution'), (0.0, 'Not recommended')] |  |
| scoring | soft_warning_caps_tier_at | Acceptable |  |
| scoring | low_depth_warning_eqg | 3.0 | warn when either parent's EqG is below |
| scoring | allele_frequency_window_years | 10 |  |
| breed syn_large | population.registrations_per_year | [(1980, 1200.0), (2026, 3500.0)] | (year, registrations) points, linear interpolation; P3 table |
| breed syn_large | population.founders_base_generation | 400 |  |
| breed syn_large | population.burn_in_size_fraction | 0.3 | hidden burn-in size as a fraction of the 1980 level |
| breed syn_large | population.split_year | 1950 | domestic and foreign subpopulations split |
| breed syn_large | reproduction.litter_size_mean | 6.4 | chosen inside the borge-2011 range 3.5 to 7.1 (overall mean 5.4) |
| breed syn_large | reproduction.litter_size_dispersion | 8.0 | negative binomial size parameter |
| breed syn_large | reproduction.perinatal_loss_rate | 0.05 | per puppy; tuned so about 24.6% of litters lose at least one (tonnessen-2012) |
| breed syn_large | reproduction.registration_rate | 0.95 | share of live puppies registered |
| breed syn_large | reproduction.caesarean_rate | 0.1 |  |
| breed syn_large | reproduction.max_litters_per_dam | 6 | lifetime |
| breed syn_large | reproduction.min_months_between_litters | 10 |  |
| breed syn_large | market.female_candidate_share | 0.25 | about 20% of dogs bred (calboli-2008, secondary) |
| breed syn_large | market.male_candidate_share | 0.25 |  |
| breed syn_large | market.popular_sire_alpha | [(1935, 0.2), (1999, 0.6), (2000, 0.2), (2026, 0.2)] | tuned in P5, see reports/validation/calibration_grid.csv; higher before 2000 (T10) |
| breed syn_large | market.attractiveness_beta | 0.6 | tuned in P5, see reports/validation/calibration_grid.csv |
| breed syn_large | market.import_rate | 0.03 | share of new breeding animals imported |
| breed syn_large | market.foreign_ai_sire_share | 0.05 |  |
| breed syn_large | market.ai_frozen_share | 0.6 | share of foreign AI matings with frozen (vs chilled) semen |
| breed syn_large | market.close_mating_avoidance | 0.95 |  |
| breed syn_large | health.hd_screening_start_year | 1985 |  |
| breed syn_large | health.hd_screening_rate_candidates | 0.7 |  |
| breed syn_large | health.hd_screening_rate_others | 0.05 |  |
| breed syn_large | health.hd_base_distribution | {'A': 0.45, 'B': 0.25, 'C': 0.17, 'D': 0.09, 'E': 0.04} | base-population FCI grade shares |
| breed syn_large | health.dna_test_rate_2026 | 0.6 |  |
| breed syn_medium | population.registrations_per_year | [(1980, 300.0), (2026, 600.0)] | (year, registrations) points, linear interpolation; P3 table |
| breed syn_medium | population.founders_base_generation | 120 |  |
| breed syn_medium | population.burn_in_size_fraction | 0.3 | hidden burn-in size as a fraction of the 1980 level |
| breed syn_medium | population.split_year | 1955 | domestic and foreign subpopulations split |
| breed syn_medium | reproduction.litter_size_mean | 5.5 | chosen inside the borge-2011 range 3.5 to 7.1 (overall mean 5.4) |
| breed syn_medium | reproduction.litter_size_dispersion | 8.0 | negative binomial size parameter |
| breed syn_medium | reproduction.perinatal_loss_rate | 0.05 | per puppy; tuned so about 24.6% of litters lose at least one (tonnessen-2012) |
| breed syn_medium | reproduction.registration_rate | 0.95 | share of live puppies registered |
| breed syn_medium | reproduction.caesarean_rate | 0.1 |  |
| breed syn_medium | reproduction.max_litters_per_dam | 6 | lifetime |
| breed syn_medium | reproduction.min_months_between_litters | 10 |  |
| breed syn_medium | market.female_candidate_share | 0.25 | about 20% of dogs bred (calboli-2008, secondary) |
| breed syn_medium | market.male_candidate_share | 0.25 |  |
| breed syn_medium | market.popular_sire_alpha | [(1935, 0.3), (1999, 0.8), (2000, 0.4), (2026, 0.4)] | tuned in P5, see reports/validation/calibration_grid.csv; higher before 2000 (T10) |
| breed syn_medium | market.attractiveness_beta | 0.65 | tuned in P5: between 0.6 (Ne 130-146) and 0.7 (Ne 76-125) of reports/validation/calibration_grid_medium_round2.csv, to centre Ne in 80-150 |
| breed syn_medium | market.import_rate | 0.05 | share of new breeding animals imported |
| breed syn_medium | market.foreign_ai_sire_share | 0.08 |  |
| breed syn_medium | market.ai_frozen_share | 0.6 | share of foreign AI matings with frozen (vs chilled) semen |
| breed syn_medium | market.close_mating_avoidance | 0.95 |  |
| breed syn_medium | health.hd_screening_start_year | 1985 |  |
| breed syn_medium | health.hd_screening_rate_candidates | 0.7 |  |
| breed syn_medium | health.hd_screening_rate_others | 0.05 |  |
| breed syn_medium | health.hd_base_distribution | {'A': 0.55, 'B': 0.25, 'C': 0.12, 'D': 0.06, 'E': 0.02} | base-population FCI grade shares |
| breed syn_medium | health.dna_test_rate_2026 | 0.6 |  |
| breed syn_small | population.registrations_per_year | [(1980, 40.0), (2026, 90.0)] | (year, registrations) points, linear interpolation; P3 table |
| breed syn_small | population.founders_base_generation | 25 |  |
| breed syn_small | population.burn_in_size_fraction | 0.5 | hidden burn-in size as a fraction of the 1980 level |
| breed syn_small | population.split_year | 1965 | domestic and foreign subpopulations split |
| breed syn_small | reproduction.litter_size_mean | 4.0 | chosen inside the borge-2011 range 3.5 to 7.1 (overall mean 5.4) |
| breed syn_small | reproduction.litter_size_dispersion | 8.0 | negative binomial size parameter |
| breed syn_small | reproduction.perinatal_loss_rate | 0.05 | per puppy; tuned so about 24.6% of litters lose at least one (tonnessen-2012) |
| breed syn_small | reproduction.registration_rate | 0.95 | share of live puppies registered |
| breed syn_small | reproduction.caesarean_rate | 0.15 |  |
| breed syn_small | reproduction.max_litters_per_dam | 6 | lifetime |
| breed syn_small | reproduction.min_months_between_litters | 10 |  |
| breed syn_small | market.female_candidate_share | 0.35 | about 20% of dogs bred (calboli-2008, secondary) |
| breed syn_small | market.male_candidate_share | 0.35 |  |
| breed syn_small | market.popular_sire_alpha | [(1935, 0.6), (1999, 1.2), (2000, 0.6), (2026, 0.6)] | tuned in P5, see reports/validation/calibration_grid_small_round2.csv; higher before 2000 (T10) |
| breed syn_small | market.attractiveness_beta | 0.8 | tuned in P5, see reports/validation/calibration_grid_small_round2.csv |
| breed syn_small | market.import_rate | 0.1 | share of new breeding animals imported |
| breed syn_small | market.foreign_ai_sire_share | 0.15 |  |
| breed syn_small | market.ai_frozen_share | 0.6 | share of foreign AI matings with frozen (vs chilled) semen |
| breed syn_small | market.close_mating_avoidance | 0.9 |  |
| breed syn_small | health.hd_screening_start_year | 1985 |  |
| breed syn_small | health.hd_screening_rate_candidates | 0.7 |  |
| breed syn_small | health.hd_screening_rate_others | 0.05 |  |
| breed syn_small | health.hd_base_distribution | {'A': 0.6, 'B': 0.22, 'C': 0.11, 'D': 0.05, 'E': 0.02} | base-population FCI grade shares |
| breed syn_small | health.dna_test_rate_2026 | 0.6 |  |
