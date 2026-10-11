# Slide outline (10 to 12 minutes)

Numbers come from `conference/numbers.json` (rebuild with `conference/build_numbers.py`).

## 1. Title
**On slide:** Breeding Smarter: a data-driven matching system for genetic diversity in dogs and beyond. Tea Ćetojević Tisaj, TODO colleague, FER Zagreb.
**Figure:** none (FER logo).
**Notes:** Good morning. I will show you an open tool that helps breeders and kennel clubs choose mates that protect a breed's genetic diversity, the synthetic data we built to test it honestly, and what ten simulated generations say about whether it works. Everything you will see is synthetic: no real dog appears in this talk.

## 2. The problem in three numbers
**On slide:** Genomic inbreeding {lit_genomic_f} across {lit_breeds_genotyped} breeds. Popular sires in all {lit_kc_breeds_popular_sires} KC breeds. {lit_carrier_share} carry a risk variant.
**Figure:** three large numbers.
**Notes:** Bannasch and colleagues genotyped {lit_dogs_genotyped} dogs: mean genomic inbreeding is about a quarter, like mating half siblings every time. Lewis found popular sires in every Kennel Club breed, and Ne below 100 in {lit_ne_below_100} breeds. Donner screened {lit_dogs_screened} dogs: more than half carry at least one disease variant. The tools exist to measure this; what is missing is help to decide.

## 3. Why now
**On slide:** EU Regulation 2026/1818: no parent-offspring, sibling, half-sibling or grandparent matings. Kennel-club rules add more.
**Figure:** timeline: published {lit_eu_reg_published}.
**Notes:** The new EU regulation on dog and cat welfare bans matings between close relatives across the Union, with a derogation for local breeds. FCI, the Kennel Club and the Raad van Beheer have their own rules. Breeders will need tools that check compliance automatically and still leave room for good choices. Some press-reported details, such as litter limits, we have not yet verified in the official text.

## 4. The gap: lookup tools vs decision tools
**On slide:** Today: what is this dog's COI? Needed: which mate best protects this breed, and why?
**Figure:** tools table (Mate Select, Avelsdata, KoiraNet, RvB module, PMx, optiSel).
**Notes:** Existing tools answer lookup questions: the COI of a dog or of a hypothetical mating. Zoo software such as PMx ranks pairs by mean kinship but ignores health and kennel-club rules. Research packages such as optiSel are powerful but have no interface. No open tool combines rules, population-level diversity, carrier status and breeding values in one explained recommendation.

## 5. Our approach
**On slide:** Synthetic registry, pedigree engine, rules, explained score, simulated futures.
**Figure:** pipeline diagram (`conference/poster/pipeline.svg`).
**Notes:** We built five pieces. A simulator that creates a realistic registry with a hidden ground truth. A pedigree engine that computes inbreeding, kinship and diversity exactly and fast: {bench_inbreeding_250k_s} seconds for 250,000 dogs. A rule engine with jurisdiction profiles. A score that explains itself. And an experiment runner that lets us test strategies over ten generations.

## 6. Synthetic data you can trust?
**On slide:** {n_animals} synthetic dogs, three breeds, calibrated to published statistics: {val_pass} of {val_n_checks} checks pass, {val_fail} fail.
**Figure:** P5 figure 4 (recorded vs true COI).
**Notes:** We cannot use real registries yet, so we calibrated a synthetic one to published litter sizes, sire concentration and effective population sizes, and we kept the truth that no registry has. This figure shows why that matters: in the small breed, recorded COI of 2025 puppies is {recorded_f_2025_S}, true inbreeding is {true_f_2025_S}, because the recorded pedigree starts in 1980 and imports carry short pedigrees.

## 7. The engine and the explanation
**On slide:** Every score explained: which ancestors cause the predicted COI, which rules apply, which disease risks remain.
**Figure:** score card image (`conference/poster/scorecard.png`).
**Notes:** For a planned litter we compute the predicted inbreeding and split it exactly into the share each ancestor causes: the shares add up to 100 percent. The card adds litter diversity, Mendelian risk from DNA tests, the hip-dysplasia breeding value, how heavily the sire has been used under the FCI five percent rule, and every rule with its source and verification status.

## 8. Live demo
**On slide:** Demo: mate finder (video as fallback).
**Figure:** live app or recording.
**Notes:** Follow `conference/demo_script.md`: breed overview with the ground-truth toggle, the mate finder for demo dam 2 where the most popular sire ends up near the bottom, the excluded half-brother, and the score card of the top match. If the network fails, switch to the local app, then to the video.

## 9. Results: realised inbreeding, and the fix
**On slide:** Recommender alone: less disease, short-term COI down, Ne not up. With club quotas: Ne {p12_ne_S_s1} to {p12_ne_S_cc_ocs_mc1} (small breed), {p12_ne_M_s1} to {p12_ne_M_cc_ocs_mc1} (medium).
**Figure:** Fig G (`reports/experiments/E5_coordination/figures/figG_coordination_poster.png`).
**Notes:** We simulated ten generations, {e1_reps_S} replicates for the small breed. The recommender lowered realised inbreeding by {e1_dibd_S_S3_abs} points (95 percent interval {e1_dibd_S_S3_ci}) and nearly removed affected puppies at tested loci, but breeders who follow a ranking all choose the same few sires, so Ne did not improve. We then added a club planner: once a season it decides how many litters each sire may have (optimum contribution selection), and breeders choose within those quotas. With criteria fixed before running, coordinated planning raised Ne over today's market in both breeds (small breed by {p12_h1_S_est}, interval {p12_h1_S_ci}; medium breed by {p12_h1_M_est}, interval {p12_h1_M_ci}) and beat the recommender alone on the long-term rate of inbreeding. Honest caveat: random mating still kept more diversity in the medium breed.

## 10. Adoption and trade-offs
**On slide:** With quotas, half of the breeders is enough for most of the gain; HD improves strongly.
**Figure:** Fig K (adoption with quotas) and Fig H (which factor matters).
**Notes:** Without quotas, the adoption sweep barely moved true inbreeding: {e2_ibd_a0} without the tool, {e2_ibd_a100} with everybody using it. With quotas, the rate of inbreeding in the small breed fell from {p12_e7_df_S_a0}% per generation with no adopters to {p12_e7_df_S_a50}% with half of the breeders adopting. A surprise: minimum-kinship mating without quotas is the worst option of all ({p12_dflate_S_cc_none_mc1}% per generation in the small breed), because every dam goes to the same few least-related sires. In the medium breed the recommender improved the true hip-dysplasia breeding value from {e1_tbv_M_S1} to {e1_tbv_M_S3} and cut affected puppies at the MDR1 locus from {e1_mdr1_M_S1} to {e1_mdr1_M_S3}. Recorded COI looks far better than the truth: optimising the records is not the same as optimising the dogs.

## 11. Limitations, said plainly
**On slide:** Synthetic data. Pedigree, not genomic, kinship. Policy weights. Some rules unverified. Quotas only tested in silico.
**Figure:** none.
**Notes:** Everything is synthetic and in silico. Kinship comes from pedigrees, which underestimate inbreeding when pedigrees are short; genomic data would help. The weights are policy and belong to breed clubs. Several EU details come from press reports. And our main lesson: a per-dam ranking alone does not protect long-term diversity; coordinating how often each sire is used does, in our model. Planning on true kinship would do even better (Ne higher by {p12_h6_S_est} in the small breed), which is why genomic data matters. Whether clubs and breeders accept quotas is untested.

## 12. Call for partners
**On slide:** Free pilot: diversity report, EU 2026/1818 check, mate recommendations. Code runs on your premises.
**Figure:** QR codes (demo, dataset DOI, contact).
**Notes:** We are looking for kennel clubs, breed clubs and researchers with real pedigree, health and DNA data. A pilot is free: a diversity report for one breed, a compliance check and mate recommendations. The code can run inside your club, so no data leaves it. Scan the codes for the demo, the open dataset and our contact. Thank you.
