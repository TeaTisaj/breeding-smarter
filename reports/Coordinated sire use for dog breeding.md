# Allocate sire contributions before ranking any mates

Breeding Smarter should implement coordinated sire use in two layers. First, a yearly **optimum contribution selection (OCS)** step decides how many litters each living dog may parent this season, under a kinship budget set from a target rate of inbreeding (ΔF). Second, a **mate-allocation** step fills those quotas with low-coancestry pairs, and the existing per-dam recommender only ranks sires inside the quotas. The project's P8 failure is the expected one. Per-dam ranking optimises each litter's inbreeding coefficient (COI), but long-term ΔF depends on how unevenly animals contribute genes to later generations, and no per-mating score can see that. The best-documented dog study, a simulation of Dutch Golden Retrievers, found the same pattern: mating each dam to her least-related sire cut ΔF to 0.04% in years 0–20, but by years 50–70 it was back at 0.39%. Excluding animals with above-average mean kinship (MK) held ΔF at 0.12–0.14% throughout ([Windig et al. 2013](https://docs.eaap.org/2013/S51b_04.pdf)). For targets, sources agree on **ΔF ≤ 0.5% per generation (Ne ≥ 100)** as the sustainable default and 1% (Ne 50) as the floor. With dog generation intervals of about 3.9–4.5 years, that is about **0.11–0.13% per year**. Real kennel-club caps are lifetime offspring limits of roughly 15–120, and the FCI 5% rule rarely binds. Simulations show flat caps give only modest gains (about 4–15% less kinship) and can backfire. The next experiment should therefore treat contribution control as the main factor and mate allocation as a second factor, cross the two, and judge them on true identity-by-descent (IBD) ΔF rather than recorded COI.

**Evidence labels.** The labels follow the research notes. **[verified]** means the claim was read in the primary text, or its bibliographic data was confirmed through Crossref. **[secondary]** means it comes from an abstract, a search summary or a secondary write-up. **[unverified]** means background knowledge that was not confirmed in a source. **[project choice]** marks a design decision proposed for Breeding Smarter that no source prescribes.

## Per-dam ranking fails because ΔF depends on contribution variance

The P8 runs show the herding failure clearly. In SYN_M, the recommender (S3) used only 6.6% of eligible males and the capacity-limited planner (S4) only 4.6%, against 13.4% under the status quo. Ne fell from 298 (S1) to 187 (S3) and 106 (S4), while random mating (S0) reached about 2,660. In SYN_S, no strategy improved on the status quo's Ne of about 35, and random mating gave 87.5 (project P8 gate report). Raising the sire-use weight from 0.10 to 0.25 widened sire use to 8.7%, but Ne still stayed below the status quo. The literature predicts this. Ranking on a shared criterion co-selects relatives and gives a few individuals large long-term contributions. Truncation selection on BLUP EBVs raised inbreeding, especially in small populations, and down-weighting family information reduced it **[secondary]** ([Verrier et al. 1993](https://agris.fao.org/search/en/records/65de4d760f3e94b9e5cd2b31)). Selecting on EBV alone maximises next-generation response, but repeating that every generation does not maximise longer-term response **[verified]** ([Wray & Goddard 1994](https://gsejournal.biomedcentral.com/counter/pdf/10.1186/1297-9686-26-5-431.pdf)). In the Golden Retriever simulation, minimising parental coancestry for each mating "was not effective in the long run" **[secondary]**. The authors' explanation was that "using a small number of (or a single) unrelated fathers decreases inbreeding of offspring, but increases their relatedness" **[verified, slides]** ([Windig & Oldenbroek 2015](https://doi.org/10.1111/jbg.12149); [slides](https://docs.eaap.org/2013/S51b_04.pdf)). The authors of the Pointer simulator add that inbreeding limits "are often promoted, but not very effective in the long run" because "inbreeding is not heritable, and kinships may still increase" **[verified]** ([Windig & Hulsegge 2021](https://doi.org/10.3390/ani11051332)).

Three features of the project make the failure worse. First, the sire-use penalty is computed from past use, so dams queried in the same round all see the same stale penalty. S3's within-year updating (P8 deviation 2) softens this but does not remove it. Second, the tool ranks on recorded pedigree kinship. Imports with shallow pedigrees look unrelated to every dam, so they win everywhere. Wellmann warns that candidates with few equivalent complete generations "can appear artificially unrelated and be overfavored" **[verified]** ([Wellmann 2019](https://doi.org/10.1186/s12859-018-2450-5)). P8 measured the same distortion: recorded COI fell about 8 times more than true IBD in SYN_S. Third, the S4 capacity came from the FCI 5%-in-5-years rule, and that rule is loose in all but tiny breeds. Leroy & Rognon found the FCI threshold above every reproducer's actual output in three of four French breeds **[verified]** ([Leroy & Rognon 2012](https://doi.org/10.1016/j.tvjl.2012.06.025)). Random mating did well in P8 for a clear reason: it spreads contributions evenly. Contribution equalisation is the textbook route to higher Ne (Wright 1938; Gowe et al. 1959, **[unverified]** in this session). FAO's formula ΔF = 3/(32N_M) + 1/(32N_F) **[verified]** ([FAO 2013](https://www.fao.org/4/i3327e/i3327e.pdf)) shows the same point: the number and evenness of sires dominates ΔF.

The remedies that work all control contributions, not pairings. In the Golden Retriever simulation, MK-based exclusion cut ΔF from 0.41% to 0.12% per generation **[secondary abstract, verified slides]**. Halving the top-5 sires' share of litters from 25% to 12.5% cut ΔF to 0.26%, while doubling the number of breeding males from 150 to 300 only reached 0.39% **[verified, slides]** ([Windig et al. 2013](https://docs.eaap.org/2013/S51b_04.pdf)). Zoo practice ranks breeders by low MK. In Drosophila, MK management kept significantly more gene and allelic diversity than maximum avoidance of inbreeding or random choice **[secondary]** ([Montgomery et al. 1997](https://czaw.org/resources/minimizing-kinship-in-captive-breeding-programs/)). FAO calls optimum contributions "the most powerful way of dealing with genetic gain and inbreeding at the same time" **[verified]** ([FAO 2013](https://www.fao.org/4/i3327e/i3327e.pdf)). A review of small farm populations ranked OCS best among the methods compared **[secondary]** ([Fernández et al. 2011](https://jukuri.luke.fi/items/312b5c52-6b4a-4d18-a602-5290ebf48c61/full)). MK selection is effectively OCS without a gain term, because it decides who breeds and how often **[project inference]**.

## OCS is a small convex problem solvable in Python

**The standard formulation.** Choose contributions c ≥ 0 with Σc = ½ within each sex, so that 2c_i is the share of offspring with parent i. Maximise c′EBV subject to c′Kc ≤ C_{t+1}, where K = A/2 is the kinship matrix and the target is C_{t+1} = C_t + ΔF(1 − C_t). This contribution definition is in [Wellmann 2019](https://doi.org/10.1186/s12859-018-2450-5) **[verified]**. The target form is the one Du et al. implement, with a 1% per generation default taken from FAO **[verified]** ([Du, Bernstein & Hoppe 2025](https://arxiv.org/abs/2504.12895)). The full matrix form with sex-incidence constraints and per-animal upper bounds is standard **[unverified]**. The original is [Meuwissen 1997](https://doi.org/10.2527/1997.754934x) **[verified bibliographically, text not read]**.

**The conservation variant.** For conservation, drop the EBV objective and minimise c′Kc. Both "maximise gain at a preset ΔF" and "minimise inbreeding regardless of gain" are standard problem types **[secondary]** ([Pong-Wong & Woolliams 2007](https://doi.org/10.1186/1297-9686-39-1-3)). AlphaMate supports both, plus minimising the inbreeding of individual matings **[secondary]** ([Gorjanc & Hickey 2018](https://doi.org/10.1093/bioinformatics/bty375)). Health goals stay convex as linear constraints. For example, Σc_i·p_carrier,i ≤ b, or "mean HD EBV no worse than now" **[project inference]**.

**A correction term for small cohorts.** Du et al. derive the exact expected kinship of the next generation. It carries an extra term (1/(2N))Σc_I(1 − k_II) that Meuwissen 1997 "apparently overlooks" **[verified]** ([Du et al. 2025](https://arxiv.org/abs/2504.12895)). For a few hundred puppies the term is about 0.001. That is small, but not negligible against a yearly budget of about 0.0011. Wellmann & Bennewitz argue for omitting or modifying it because it rewards inbred parents, and Du et al. call that argument "unclear" **[verified, via Du et al.]** ([Wellmann & Bennewitz 2019](https://doi.org/10.3389/fgene.2019.00667)). A related implementation hazard: the factor ½ must appear exactly once. Mixing A and K conventions is a classic bug **[project inference]**.

**Overlapping generations and yearly decisions.** Dogs breed across many years, so the decision variable is each year's newborn cohort. Living animals are weighted by age × sex class, with older animals weighted less. The per-generation rate is divided by the generation interval L **[verified]** ([Du et al. 2025](https://arxiv.org/abs/2504.12895); [Wellmann 2019](https://doi.org/10.1186/s12859-018-2450-5)). optiSel's agecont() estimates these class weights from parents' ages at birth **[verified]**. Without them, optiSel assumes discrete generations. Du et al. warn that the optimum is only optimal if the survival assumptions hold, which matters most for long-lived mammals **[verified]**. The original overlapping-generation derivations are [Meuwissen & Sonesson 1998](https://doi.org/10.2527/1998.76102575x) and [Grundy, Villanueva & Woolliams 2000](https://doi.org/10.1017/s1357729800051717). The second reports "up to 35%" more response than truncation BLUP at equal ΔF **[secondary]**. Neither full text was read.

One overlapping-generation pitfall applies directly. Sonesson & Meuwissen's optimiser picked only the oldest animals, which split the population into age-class sublines and raised ΔF by 18–52%. Requiring at least one sire and one dam from the second-oldest class fixed it **[verified]** ([Sonesson & Meuwissen 2001](https://doi.org/10.1017/S0016672301005079)). Re-optimising every year with the updated pedigree and survivors follows the "dynamic" selection of [Grundy et al. 1998](https://doi.org/10.1017/s0016672398003474) **[verified bibliographically; method details secondary]**.

**Solvers.** The gain problem is a second-order cone program (SOCP) and the conservation problem is a convex QP. Meuwissen's Lagrangian method is fast but sometimes sub-optimal: in Pong-Wong & Woolliams' examples its expected gain was 1.5–9% below the semidefinite-programming (SDP) optimum **[secondary]** ([Pong-Wong & Woolliams 2007](https://doi.org/10.1186/1297-9686-39-1-3)). In optiSel, the cone solvers cccp/cccp2 were fastest and correct for linear and quadratic objectives. Its kinship computation handled 32,698 individuals, and an 11,000-animal optimisation took about 3 minutes **[verified]** ([Wellmann 2019](https://doi.org/10.1186/s12859-018-2450-5)). optiSel was **archived on CRAN on 2026-09-17** **[verified]** ([CRAN](https://cran.r-project.org/web/packages/optiSel/index.html)), so it is a validation tool, not a dependency.

Two Python routes exist. The only verified Python OCS package is **robustocs** 0.2.1 (MIT licence, HiGHS or Gurobi back end), which covers standard and robust OCS **[verified]** ([Fogg et al. 2024](https://arxiv.org/abs/2412.02888); [PyPI](https://pypi.org/project/robustocs/)). AlphaMate (Fortran, evolutionary algorithm) optimises contributions and pairings together **[secondary]**. The straightforward stack is cvxpy with Clarabel. It uses `cp.quad_form(c, K) <= C`, or a Cholesky factor of K for a norm constraint, plus linear sex-sum and bound constraints. It should solve at dog-breed scale in under a second **[project inference; no verified benchmark]** ([CVXPY](https://arxiv.org/pdf/1603.00943)).

**Turning contributions into matings.** The literature works in two stages, and Python handles each well.

1. *Integer quotas.* Convert c to whole numbers of litters per parent. optiSel's noffspring() uses n_i ≈ 2c_i·N with floor-plus-remainder rounding **[verified]**. Du et al. recommend Webster/Sainte-Laguë apportionment. It is unbiased and avoids Hamilton's paradoxes, and they suggest making the "first seat" harder to win so that solver noise of about 1e-7 never becomes a real litter. They reject D'Hondt because it enlarges large sib groups **[verified]** ([Du et al. 2025](https://arxiv.org/abs/2504.12895)).
2. *Mate allocation.* Fill the quotas with a transportation problem that minimises Σx_ij·k_ij. Each dam gets her quota, each sire his, at most one litter per pair, and forbidden pairs are fixed at zero. The constraint matrix is totally unimodular, so scipy's HiGHS linprog returns integers **[project inference, standard OR]**. optiSel's matings() minimises offspring-weighted parental kinship in the same spirit **[verified]**.

Minimum-coancestry mating with at most one offspring per pair (MC1) raised genetic response about 22% over random mating at ΔF = 1% with 100 candidates, and 5–6% under looser settings **[secondary]** ([Sonesson & Meuwissen 2000](https://doi.org/10.1186/1297-9686-32-3-231)). With overlapping generations at 0.25% per year it gave 18% **[secondary]** ([Sonesson & Meuwissen 2002](https://doi.org/10.1186/1297-9686-34-1-23)). Practical restrictions imposed during optimisation keep most of OCS's long-term gain **[verified title only]** ([Henryon et al. 2015](https://doi.org/10.1186/s12711-015-0107-7)).

## The standard target is ΔF 0.5% per generation, or about 0.12% per year

**What the guidelines say.**

- **FAO** sets Ne = 50 (ΔF ≤ 1% per generation) as the minimum "to guarantee the survival of the population in the short and medium term". It recommends ΔF ≤ 1% for at-risk breeds, tolerates about 2% for selected commercial breeds, and advises choosing ΔF by predicting gain over a range of values **[verified]**. Its male-number risk bands are ΔF ≥ 3% critical, 1–3% endangered and 0.5–1% vulnerable, and it lists the dog as a high-reproductive-capacity species **[verified]** ([FAO 2013](https://www.fao.org/4/i3327e/i3327e.pdf)).
- **Frankham, Bradshaw & Brook** argue the 50/500 rule should rise to at least 100/1000, because "Ne = 50 is insufficient to prevent inbreeding depression" **[verified]** ([Frankham et al. 2014 reply](https://doi.org/10.1016/j.biocon.2014.05.006)). Franklin, Allendorf & Jamieson dispute this.
- **Dog-specific guidance converges on the same bands.** Lewis et al. (Kennel Club staff) treat Ne < 100 as rapid diversity loss, Ne < 50 as high risk, and 1% per generation as the maximum. Across 116 UK breeds, 68 had Ne < 100 and 29 had Ne < 50, and mean L was 3.88 years **[verified]** ([Lewis et al. 2015](https://doi.org/10.1186/s40575-015-0027-4)). The Dutch "traffic light" of Oldenbroek & Windig grades ΔF > 1% unacceptable, 0.5–1% high risk, 0.25–0.5% moderate and < 0.25% small. It calls Ne 100 the long-term minimum **[verified]** ([Windig et al. 2013](https://docs.eaap.org/2013/S51b_04.pdf); [Doekes 2016](https://edepot.wur.nl/403077)). The Finnish Kennel Club triggers crosses or imports when inbreeding-based Ne over 3–4 generations is ≤ 50, or demographic Ne is ≤ 200 **[secondary]** ([DogWellNet, Mäki 2022](https://dogwellnet.com/blogs/entry/243-kennel-clubs-and-responsible-breeding-examples-from-finland/)).
- **The estimator matters.** Pedigree IBD-based Ne in 60 dog breeds averaged 93–203 across methods, while demographic estimates ran 356–4,425 **[secondary]** ([Leroy et al. 2013](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3599586/)). The project's realised-IBD Ne should be compared against the 50/100 thresholds, not the demographic 200.

**Conversions.** Ne = 1/(2ΔF), and the per-year rate ≈ ΔF/L **[verified]** ([FAO 2013](https://www.fao.org/4/i3327e/i3327e.pdf); [Lewis et al. 2015](https://doi.org/10.1186/s40575-015-0027-4)). The exact yearly kinship bound used below, C_next = 1 − (1 − C_now)(1 − ΔF)^(1/L), is standard but **[unverified]** against a primary text. The arithmetic below is the project's own.

| ΔF per generation | Ne | Per year, L = 3.88 | Per year, L = 4.0 | Per year, L = 4.5 | Status in sources |
|---|---|---|---|---|---|
| 1.0% | 50 | 0.259% | 0.251% | 0.223% | Floor (FAO, KC, FKC) |
| 0.5% | 100 | 0.129% | 0.125% | 0.111% | Recommended default (Frankham, KC, Dutch) |
| 0.25% | 200 | 0.065% | 0.063% | 0.056% | Dutch "small risk" aspiration |
| 0.1% | 500 | 0.026% | 0.025% | 0.022% | Long-term evolutionary criterion, rarely operational |

Worked example: with current mean kinship 0.10, ΔF = 0.5% and L = 4, one yearly step allows kinship up to 1 − 0.90 × 0.995^0.25 ≈ 0.10113.

**Applying the targets to the two synthetic breeds** **[project inference]**. In SYN_S, true IBD went from about 0.43 to 0.508 over 10 generations, which implies a realised ΔF of about 1.5% per generation (Ne ≈ 35). That is below FAO's floor, so a 0.5% bound may be infeasible. Du et al. warn that OCS "may fail to find an optimum solution if k*_{t+1} is chosen too small" **[verified]**. SYN_M's status quo already gives Ne ≈ 298 (ΔF ≈ 0.17%), so a 0.5% bound would not bind there. Each breed therefore needs a target ladder relative to its own feasible minimum, not one universal number.

## Real sire caps are blunt, and simulation shows modest gains

**What clubs actually do.**

- **FCI** recommends, without binding force, that "no dog should have more offspring than equivalent to 5% of the number of puppies registered in the breed population during a five-year period". A programme "should not exclude more than 50% of the breed" **[verified]** ([FCI Breeding Strategies 2010](https://www.fci.be/medias/ELE-STR-en-941.pdf)). Enforcement is uncommon, and no evidence exists on uptake **[secondary]** ([CGE 2025](https://link.springer.com/10.1186/s40575-025-00142-1)).
- **Finland (PEVISA)** has binding caps. A litter is not registered once a parent exceeds the breed cap, although the litter that crosses the cap is still registered in full. Pre-existing litters count toward the cap. In the 2026 programmes caps range from 15 (Volpino italiano) through 20–60 for most breeds to 90 (English Cocker Spaniel) and 120 (Finnish Hound). Some are age-graded (Havanese: 25 while the male is under four years old), one combines puppies and litters (Central Asian Shepherd: 30 puppies and 4 litters), and several pair the cap with a 6.25% litter COI limit **[verified]** ([Kennelliitto PEVISA 2026](https://kennelliitto.fi/pevisa-ja-rotukohtaiset-erityisehdot)).
- **Norway (NKK)** recommends 5% of five-year registrations, or 2% for large breeds, applied to both sexes **[secondary]** ([NEKF RAS guide 2025](https://elghundforbundet.no/wp-content/uploads/2025/09/NEKFs-RAS-veileder.pdf)).
- **Sweden (SKK)** found only general anti-overuse policy, a five-litter limit for bitches, and breed-level advice such as 25 puppies before age five and 50 for life in the Finnish Lapphund **[secondary]** ([SKK R42](https://www.skk.se/globalassets/globala-filer/regler/registreringsregler-r42-2025.pdf); [SRFL](https://finsklapphund.nu/wp-content/uploads/2024/02/Utvardering-RAS-SRFL-Avelskommitte-2023-1.pdf)).
- **Netherlands.** The Raad van Beheer's model breeding regulation leaves a stud cap optional **[verified]** ([VFR guide 2025](https://www.houdenvanhonden.nl/globalassets/regelgeving/format-vfr/leeswijzer-vfr-maart-2025.pdf)). Clubs that adopt one set binding caps: the Golden Retriever club allows 12 matings a year and cut its lifetime cap from 80 to 40 from August 2026; the Hovawart club allows 1 a year and 3 lifetime **[secondary]** ([GRCN](https://www.goldenretrieverclub.nl/images/GRCN_VFR_DEF_versie_2_-_goedgekeurd_11042026_ingediend_23062026_pdf_1_augustus2026.pdf); [HCN](https://hovawartclub-site.e-captain.nl/bestanden/hcn-verenigings-fok-reglement-versie-1-feb-2026.pdf)).
- **UK, US and Germany.** The UK Kennel Club caps bitches at four litters but has no stud cap **[secondary]** ([MRCVS](https://www.mrcvs.co.uk/en/news-story.php?id=6344)). The AKC only requires a DNA profile for frequently used sires **[secondary]** ([AKC](https://www.akc.org/breeder-programs/dna/dna-resource-center/frequently-used-sires-requirement/)). In Germany the caps are set by breed clubs.

**Evidence on the popular sire effect.**

- Popular sires appeared in every UK breed, and Ne was unrelated to census size: the English Springer Spaniel has about 10,886 registrations a year but Ne 45 **[verified]** ([Lewis et al. 2015](https://doi.org/10.1186/s40575-015-0027-4)).
- In ten French breeds the effective number of sires was 33–70% of the actual number. Popular-sire use raised the simulated risk of spreading a recessive disorder about 4.4-fold over random mating **[secondary]** ([Leroy & Baumung 2011](https://agris.fao.org/search/fr/records/652f9eecd5e38ff7731f7902)).
- Calibrating the Pointer simulator showed that leaving out the top 2–5 sires makes simulations underestimate inbreeding **[verified]** ([Windig & Hulsegge 2021](https://doi.org/10.3390/ani11051332)).

**How well caps work.** No ex-post evaluation of a real cap exists. In simulation, Leroy & Rognon found that a cap of 200 offspring barely bound, while a cap of 50 cut kinship by 10–15% (Coton de Tulear 0.038 → 0.032). In the Berger des Pyrénées it lowered the kinship rate from 0.5% to 0.2% per generation. A cap of 25 in the tiny Braque Saint Germain **raised** kinship by 10%, because the capped sires were the least related to the population **[verified]** ([Leroy & Rognon 2012](https://doi.org/10.1016/j.tvjl.2012.06.025)). In the Golden Retriever simulation, per-year caps beat lifetime caps (10 litters per sire per year gave ΔF 0.27%; 5 per year gave 0.18%). Lifetime caps of 5 or fewer shortened the generation interval to 2.4–2.6 years, and a 20-per-year cap gave 0.45%, worse than no cap **[verified, slides]** ([Windig et al. 2013](https://docs.eaap.org/2013/S51b_04.pdf)). Two lessons follow for the project **[project inference]**: a cap must depend on the sire's mean kinship rather than being flat, and a cap needs relatedness-aware replacement so that sons and brothers do not refill the slot.

## Small-population studies rank contribution control above mating design

| Strategy | Key finding | Source (label) |
|---|---|---|
| Random vs minimum-coancestry (MC) mating, unselected | MC lowers the level of F, but asymptotic ΔF is the same (e.g. 0.0043 vs 0.0046 per year with 10 newborns) | [Sonesson & Meuwissen 2001](https://doi.org/10.1017/S0016672301005079) (verified) |
| Per-dam least-related sire (dogs) | ΔF 0.04% in years 0–20, 0.39% in years 50–70 (no restriction: 0.41/0.40%) | [Windig et al. 2013](https://docs.eaap.org/2013/S51b_04.pdf) (verified slides) |
| Exclude animals with above-average MK (dogs) | ΔF 0.12% in years 0–20, 0.14% in years 50–70 | same (verified slides); [Windig & Oldenbroek 2015](https://doi.org/10.1111/jbg.12149) (secondary) |
| Lowest-MK, least-related mating, sire limits (small dog population, 100 years) | All three reduced ΔF and disease fixation, MK most effective; excluding carriers caused near-universal extinction | [Bergsma 2022 MSc](https://edepot.wur.nl/575638) (secondary, not peer-reviewed) |
| OCS + MC1 mating, selected populations | +22% gain vs random mating at ΔF 1%; +18% at 0.25% per year | [Sonesson & Meuwissen 2000](https://doi.org/10.1186/1297-9686-32-3-231), [2002](https://doi.org/10.1186/1297-9686-34-1-23) (secondary) |
| Compensatory mating vs MC | Compensatory mating about 0.30 more effective at low ΔF; combining both best | [Caballero et al. 1996](https://portalinvestigacion.uniovi.es/documentos/5e78c51c2999521b3d11bc06) (secondary) |
| Rotational mating vs OC | Rotation comparable to OC; OC + rotation of males gave the lowest ΔF; OC preferable with full pedigree | [Mucha & Komen 2016](https://research.wur.nl/en/publications/rates-of-inbreeding-and-genetic-adaptation-for-populations-manage/) (secondary) |
| Breeding circles | Sheep: ΔF from > 1.5% per year to about 0.16% per year; Veluws circle realised 0.29–0.41% per generation vs 0.12–0.18% in theory (dominant rams plus selection: 0.67%); in Pointer, a circle had higher inbreeding than one random-mating group for 78 years | [Windig & Kaal 2008](https://doi.org/10.1017/S1751731108003029) (secondary; co-author listing uncertain); [Windig et al. 2019](https://doi.org/10.1111/jbg.12371) (verified); [Windig & Hulsegge 2021](https://doi.org/10.3390/ani11051332) (verified) |
| Outcrossing a closed breed | ΔF 2.1% → 1.8% with one outcross litter; more than 8 of 14 yearly litters needed to get below 1%; a 5% outcross chance per litter gave −0.2% | [Windig & Doekes 2018](https://europepmc.org/search?query=DOI:10.1111/jbg.12330) (secondary) |

The pattern is consistent. Mating design changes F at a given coancestry level, but it does not change the rate at which coancestry accumulates. Contribution control does change that rate. MC mating adds a real but secondary benefit under selection, mainly by preventing full-sib families and spreading ancestors. This argues for a factorial experiment and for reporting ΔC (the rate of change of mean coancestry) next to ΔF. A further caution comes from de Cara et al.: OC keeps deleterious recessives at low heterozygous frequencies rather than purging them, and deliberate inbred matings "never led to higher fitness" **[secondary]** ([de Cara et al. 2013](https://doi.org/10.1038/hdy.2012.119)). Disease incidence, allele frequency and allele loss should therefore be reported separately. The project's E3 result, where excluding carriers sharply cut risk-allele frequency at a small Ne cost in SYN_M, fits that framing.

## Breeder freedom, partial adoption and kinship source decide real-world success

**Breeder freedom and adoption.**

- Lewis et al. doubt that OCS or negative assortative mating can be coordinated in dog breeds at all **[verified]** ([Lewis et al. 2015](https://doi.org/10.1186/s40575-015-0027-4)).
- FCI deliberately prefers "education of breeders" over strict rules **[verified]** ([FCI](https://www.fci.be/medias/ELE-STR-en-941.pdf)).
- Mäki warns that piling on criteria can itself narrow the gene pool **[secondary]** ([DogWellNet Finnish Spitz](https://dogwellnet.com/content/health-and-breeding/breed-specific-programs/breed-specific-breeding-strategies/breeding-strategies-by-breed/breed-specific-breeding-strategies-to-achieve-positive-outcomes-the-finnish-spitz-as-an-example-increasing-and-maintaining-genetic-diversity-r762/)).
- No study measures compliance with voluntary versus mandatory plans, and none shows that a mate-recommendation tool itself increases sire concentration in dogs. P8 is, as far as these notes go, novel evidence on that point.

The project's design answers follow **[project choice]**:

- Keep breeder choice by showing each dam a ranked shortlist drawn only from sires with remaining quota, instead of a single assignment.
- Keep a shared booking ledger, so a planned mating immediately reduces the sire's remaining quota. This removes the stale-penalty problem.
- Re-solve OCS each round after observed matings, so that non-adopters' choices are treated as fixed contributions. Pong-Wong & Woolliams' formulation supports candidates with fixed contributions **[secondary]**.

E2 found true-IBD benefits only from about 50% adoption, so partial adoption must be tested with the new planner rather than assumed.

**Kinship source.** This is the largest technical risk.

- With genomic EBVs but a pedigree kinship constraint, realised genomic ΔF was 0.0211 against a 0.005 target, about four times too high. A genomic constraint hit the target **[verified]** ([Sonesson, Woolliams & Meuwissen 2012](https://doi.org/10.1186/1297-9686-44-27)).
- Marker coancestry generally kept more heterozygosity than pedigree coancestry in conservation OCS **[secondary]** ([de Cara et al. 2011](https://doi.org/10.1111/j.1439-0388.2011.00971.x)).
- Metafounders are pseudo-ancestors whose self- and cross-relatedness (γ) are estimated from markers. They make pedigree and genomic matrices compatible, generalise unknown-parent groups, and suit imports grouped by country or line **[secondary]** ([Legarra et al. 2015](https://pmc.ncbi.nlm.nih.gov/articles/PMC4492372)).
- Imports reduced UK ΔF after 2000 **[verified]** ([Lewis et al. 2015](https://doi.org/10.1186/s40575-015-0027-4)). That makes imports valuable, but only if their relatedness is not underestimated.

No dog-specific pedigree-vs-genomic OCS study or metafounder application was found. In the simulator, true kinship is available, so the gap between OCS on recorded kinship and OCS on true kinship can be measured directly. That measurement is itself a publishable result **[project inference]**.

## Recommendations for the next experiment

**Implementation choices.**

| Choice | Recommendation | Basis |
|---|---|---|
| Decision unit and timing | Yearly OCS on all living, fertile animals; decision = this year's litters; re-solve every year | Du et al. 2025 and Wellmann 2019 (verified); Grundy et al. 1998 dynamic selection (secondary) |
| Constraint | Age-weighted mean kinship of the population after adding the newborn cohort ≤ C_next = 1 − (1 − C_now)(1 − ΔF)^(1/L); include the Du et al. small-cohort term, or reserve budget for it | Du et al. 2025 (verified); exact yearly formula (unverified); budget reservation (project choice) |
| L | Estimate from the simulated pedigree each run (project docs assume 4–5 years; UK mean 3.88) | Lewis et al. 2015 (verified) |
| Objectives | (a) conservation: min c′Kc; (b) gain: max of the recommender's merit score subject to the ΔF bound, with health entered as linear constraints | Pong-Wong & Woolliams 2007, AlphaMate (secondary); linear health constraints (project choice) |
| Solver | cvxpy + Clarabel; cross-check selection against robustocs; optionally validate one scenario against archived optiSel | Fogg et al. 2024, CRAN archive (verified); runtimes (unverified) |
| Infeasibility | Solve min c′Kc first; if the ΔF target is below that minimum, use the minimum plus a stated fraction of the gap, and log it | Du et al. infeasibility warning (verified); fallback (project choice) |
| Quotas | Drop c < 0.25/(2·L_tot); Sainte-Laguë apportionment to whole litters per sire; dams ≤ 1 litter per year | Du et al. 2025 (verified); thresholds (project choice) |
| Mate allocation | Transportation LP (scipy HiGHS) minimising Σ pair kinship, with carrier × carrier and HARD-rule pairs set to zero and at most 1 litter per pair; the recommender then ranks within the allocation or shortlist | Sonesson & Meuwissen 2000 MC1 (secondary); LP formulation (project inference) |
| Age structure | Require contributions from at least the two youngest breeding age classes, so the solver cannot select only the oldest animals | Sonesson & Meuwissen 2001 (verified) |
| Imports and shallow pedigrees | Add a minimum equivalent-complete-generations constraint (optiSel lb.equiGen style) or metafounder groups for foreign stubs | Wellmann 2019, Legarra et al. 2015 (verified/secondary) |
| Hard upper bounds | Per-sire per-year litter bound, scaled by the sire's MK rather than flat, plus lifetime bounds in the Finnish 20–60 offspring range | PEVISA (verified); Leroy & Rognon, Windig (verified); MK scaling (project choice) |

**Strategies to compare.** Use a factorial design: contribution control {none, MK exclusion, MK-scaled per-year sire cap, OCS} × mate allocation {random, MC1 LP}. Run it against the existing anchors S0 (random), S1 (status quo) and S3 (recommender). Add two OCS arms for diagnosis: an **oracle** arm that optimises on true kinship, and a **recorded** arm that optimises on recorded kinship. Run partial adoption at 25%, 50%, 75% and 100% with the OCS planner. A breeding circle is a low-priority extra; if included, use a horizon long enough to pass the roughly 78-year crossover reported for Pointer.

Some expectations are drawn from the literature, not guaranteed. OCS (min c′Kc) on true kinship should at least match S0's Ne, because equal contributions are a feasible point of the problem; this is a project inference. The literature predicts that MC1 adds little to ΔF but lowers F and affected-genotype incidence.

**Parameters.**

- ΔF ladder: 1.0%, 0.5% and 0.25% per generation, plus unconstrained min-kinship. For SYN_M, add 0.1%, because the status quo already sits near 0.17%.
- Report ΔF and ΔC per year and per generation, the generation interval, the share of eligible males used, the top-5 sire share, the variance of contributions, realised-IBD Ne, recorded COI, and disease incidence and allele frequency.
- Use two time windows: generations 0–5 and the last 5 of at least 10 generations. Extending to 15–25 generations (50–100 years) follows the literature's horizons (Sonesson & Meuwissen 2001; Bergsma 2022).
- Keep the E1 replicate count and common random numbers.

For the record, the source anchors behind these parameters are: Ne 100 is the KC, Dutch and Frankham target **[verified]**; the FAO floor is Ne 50 **[verified]**; the Golden Retriever per-year caps of 5–10 litters per sire gave ΔF 0.18–0.27% **[verified slides]**; and the Finnish lifetime caps are 15–120 **[verified]**.

## Conclusion

The P8 result is not a defect of the recommender's weights. It follows structurally from optimising each litter in isolation, and the dog and conservation literature predicted it. Diversity is lost through who contributes and how much, not through who is paired with whom. A tool that wants to raise Ne must therefore own a population-level budget, the yearly contribution vector, and let breeder choice and per-dam ranking work inside it. Doing so is also technically cheap: a small convex program plus an integer transportation problem, both solvable in Python in seconds.

The more consequential open question is the kinship matrix, not the optimiser. In P8, recorded kinship overstated gains about eightfold, and genomic studies show pedigree-constrained OCS overshooting its ΔF target fourfold. So the oracle-versus-recorded OCS comparison is likely the most informative single contrast in the next experiment. Its result will tell the project whether the next investment should be coordination (quotas and a booking ledger) or better relationship information (metafounders and genotypes for imports). No published dog OCS study, and no evaluation of a real-world sire cap, exists to settle this. The simulator is well placed to supply that evidence.

## Sources

**OCS methods and software**
- Meuwissen 1997, J Anim Sci 75:934–940. https://doi.org/10.2527/1997.754934x
- Meuwissen & Sonesson 1998, J Anim Sci 76:2575–2583. https://doi.org/10.2527/1998.76102575x
- Grundy, Villanueva & Woolliams 1998, Genet Res. https://doi.org/10.1017/s0016672398003474
- Grundy, Villanueva & Woolliams 2000, Anim Sci. https://doi.org/10.1017/s1357729800051717
- Pong-Wong & Woolliams 2007, GSE 39:3–25. https://doi.org/10.1186/1297-9686-39-1-3
- Sonesson & Meuwissen 2000, GSE 32:231–248. https://doi.org/10.1186/1297-9686-32-3-231
- Sonesson & Meuwissen 2001, Genet Res 77:285–292. https://doi.org/10.1017/S0016672301005079
- Sonesson & Meuwissen 2002, GSE 34:23–39. https://doi.org/10.1186/1297-9686-34-1-23
- Sonesson, Woolliams & Meuwissen 2012, GSE 44:27. https://doi.org/10.1186/1297-9686-44-27
- Henryon et al. 2015, GSE 47:21. https://doi.org/10.1186/s12711-015-0107-7
- Woolliams et al. 2015, J Anim Breed Genet 132:89–99 (not read). https://doi.org/10.1111/jbg.12148
- Gorjanc & Hickey 2018, AlphaMate, Bioinformatics 34:3408–3411. https://doi.org/10.1093/bioinformatics/bty375
- Wellmann 2019, optiSel, BMC Bioinformatics 20:25. https://doi.org/10.1186/s12859-018-2450-5
- Wellmann & Bennewitz 2019, Front Genet 10:667. https://doi.org/10.3389/fgene.2019.00667
- Du, Bernstein & Hoppe 2025, arXiv:2504.12895. https://arxiv.org/abs/2504.12895
- Fogg et al. 2024, robust OCS, arXiv:2412.02888. https://arxiv.org/abs/2412.02888 ; https://pypi.org/project/robustocs/
- optiSel CRAN status (archived 2026-09-17). https://cran.r-project.org/web/packages/optiSel/index.html
- CVXPY. https://arxiv.org/pdf/1603.00943

**Targets**
- FAO 2013, In vivo conservation of animal genetic resources. https://www.fao.org/4/i3327e/i3327e.pdf
- Frankham, Bradshaw & Brook 2014 (reply). https://doi.org/10.1016/j.biocon.2014.05.006
- Lewis, Abhayaratne & Blott 2015, Canine Genet Epidemiol 2:13. https://doi.org/10.1186/s40575-015-0027-4
- Leroy et al. 2013, Ne estimation methods. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3599586/
- Doekes 2016, WUR thesis. https://edepot.wur.nl/403077
- DogWellNet (FKC strategy, Mäki 2022). https://dogwellnet.com/blogs/entry/243-kennel-clubs-and-responsible-breeding-examples-from-finland/

**Sire limits and popular sires**
- FCI International Breeding Strategies. https://www.fci.be/medias/ELE-STR-en-941.pdf
- Kennelliitto PEVISA 2026. https://kennelliitto.fi/pevisa-ja-rotukohtaiset-erityisehdot
- NEKF RAS guide 2025. https://elghundforbundet.no/wp-content/uploads/2025/09/NEKFs-RAS-veileder.pdf
- SKK R42 2025. https://www.skk.se/globalassets/globala-filer/regler/registreringsregler-r42-2025.pdf
- Dutch VFR guide 2025. https://www.houdenvanhonden.nl/globalassets/regelgeving/format-vfr/leeswijzer-vfr-maart-2025.pdf
- GRCN VFR 2026. https://www.goldenretrieverclub.nl/images/GRCN_VFR_DEF_versie_2_-_goedgekeurd_11042026_ingediend_23062026_pdf_1_augustus2026.pdf
- AKC Frequently Used Sires. https://www.akc.org/breeder-programs/dna/dna-resource-center/frequently-used-sires-requirement/
- Leroy & Rognon 2012, Vet J 194:343–348. https://doi.org/10.1016/j.tvjl.2012.06.025
- Leroy & Baumung 2011, Anim Genet 42:66–74. https://agris.fao.org/search/fr/records/652f9eecd5e38ff7731f7902
- CGE 2025 on FCI uptake. https://link.springer.com/10.1186/s40575-025-00142-1

**Strategy comparisons**
- Windig, van der Kraats & Oldenbroek 2013, EAAP slides. https://docs.eaap.org/2013/S51b_04.pdf
- Windig & Oldenbroek 2015, J Anim Breed Genet 132:428–440. https://doi.org/10.1111/jbg.12149
- Windig & Doekes 2018. https://europepmc.org/search?query=DOI:10.1111/jbg.12330
- Windig & Hulsegge 2021, Animals 11:1332. https://doi.org/10.3390/ani11051332
- Windig, Verweij & Oldenbroek 2019, J Anim Breed Genet 136:51–62. https://doi.org/10.1111/jbg.12371
- Windig & Kaal 2008, Animal 2:1733–1741. https://doi.org/10.1017/S1751731108003029
- Mucha & Komen 2016. https://research.wur.nl/en/publications/rates-of-inbreeding-and-genetic-adaptation-for-populations-manage/
- Caballero, Santiago & Toro 1996. https://portalinvestigacion.uniovi.es/documentos/5e78c51c2999521b3d11bc06
- Bergsma 2022, WUR MSc. https://edepot.wur.nl/575638
- Montgomery et al. 1997. https://czaw.org/resources/minimizing-kinship-in-captive-breeding-programs/
- de Cara et al. 2013, Heredity. https://doi.org/10.1038/hdy.2012.119
- Fernández et al. 2011. https://jukuri.luke.fi/items/312b5c52-6b4a-4d18-a602-5290ebf48c61/full
- Verrier, Colleau & Foulley 1993. https://agris.fao.org/search/en/records/65de4d760f3e94b9e5cd2b31
- Wray & Goddard 1994. https://gsejournal.biomedcentral.com/counter/pdf/10.1186/1297-9686-26-5-431.pdf

**Kinship source**
- de Cara et al. 2011, J Anim Breed Genet 128:456–464. https://doi.org/10.1111/j.1439-0388.2011.00971.x
- Legarra et al. 2015, metafounders. https://pmc.ncbi.nlm.nih.gov/articles/PMC4492372
