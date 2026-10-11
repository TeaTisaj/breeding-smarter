# Recommended targets for rate of inbreeding (ΔF) and effective population size (Ne) in managed animal populations, with emphasis on dog breeds

Verification status: claims marked **[verified]** were read directly from the primary document text in this session. Claims marked **[secondary]** come from a summary page or search snippet. Claims marked **[unverified]** come from background knowledge and were not confirmed against a source here.

## What do FAO guidelines say (Ne >= 50 / ΔF <= 1%, risk categories)?

### Takeaway
FAO (2013) *In vivo conservation of animal genetic resources* sets Ne = 50, i.e. ΔF ≤ 1% per generation, as the minimum acceptable level ("at least ... short and medium term"). It recommends ΔF ≤ 1% for breeds at high risk. For commercial (not-at-risk) breeds under selection it says "general consensus" puts the maximum acceptable ΔF at about 2%. Its risk categories map numbers of breeding males to ΔF bands: >3% critical, 1–3% endangered, 0.5–1% vulnerable. FAO classes the dog as a "high reproductive capacity" species.

### Cited Findings
- **[verified]** "In general, 50 has been established as an acceptable Ne, at least to guarantee the survival of the population in the short and medium term. Consequently, the desired ΔF per generation should not exceed 1 percent (ΔF = 1/[2×50])." The same passage says 25 males + 25 females, 20 males + 34 females, or 14 males + 116 females all give Ne = 50 under random contributions. It adds: "the population sizes described here are minimum sizes. Larger numbers of animals are always to be preferred" (Section 6, "Minimum effective population size", p. ~140 of PDF). — [FAO 2013, In vivo conservation of animal genetic resources, Animal Production and Health Guidelines No. 14](https://www.fao.org/4/i3327e/i3327e.pdf)
- **[verified]** "The acceptable rate of inbreeding per generation (ΔF) will depend on the status of the population and the characteristic of the species. For breeds at high risk of extinction, ΔF ≤ 1 percent is recommended, assuming this is possible. In the case of populations that are not in the critical or endangered categories, restrictions can be relaxed and a larger ∆F can be justified if it occurs as a result of intense and accurate selection. In commercial breeds, there is a general consensus that the maximum acceptable ∆F is about 2 percent, but the figure may vary between species." It also suggests: "One option is to predict the expected gain for a range of ∆F and choose the compromise solution that best meets both objectives." (Section 7, Task 1 Action 2, p. 171) — [FAO 2013](https://www.fao.org/4/i3327e/i3327e.pdf)
- **[verified]** Risk-status categories, assigned on the least favourable parameter:
  - **Critical:** ≤100 breeding females (300 for low-reproductive-capacity species), or "total number of breeding males is less than or equal to five (i.e. ΔF is 3 percent or greater)".
  - **Endangered:** 100–1,000 breeding females (300–3,000), or breeding males "less than or equal to 20 and greater than five (i.e. ΔF is between 1 and 3 percent)".
  - **Vulnerable:** 1,000–2,000 breeding females (3,000–6,000), or breeding males "between 20 and 35 (i.e. the ΔF is between 0.5 and 1 percent)".
  - **Not at risk:** none of the above.
  - Male thresholds (i.e. the ΔF criterion) "are the same for all species".
  — [FAO 2013, Section 2, pp. 44–46](https://www.fao.org/4/i3327e/i3327e.pdf)
- **[verified]** Table 2 of FAO 2013 lists **Dog** under "High reproductive capacity" species, so the lower female and population thresholds apply to dogs. — [FAO 2013, Table 2](https://www.fao.org/4/i3327e/i3327e.pdf)
- **[verified]** FAO calls optimum contributions "the most powerful way of dealing with genetic gain and inbreeding at the same time (Meuwissen, 1997)". It describes the objective Σ cᵢvᵢ − ΣΣ cᵢcⱼfᵢⱼ and says "In practice, the term regarding ∆F is treated as a restriction, and the algorithm searches for the solution ... with the highest response to selection but not exceeding the desired value for ∆F." It also says implementation needs "several generations (at least four) of complete pedigree information" (Section 7 Option 5, Box 51, pp. 175–176). — [FAO 2013](https://www.fao.org/4/i3327e/i3327e.pdf)
- **[verified]** For choosing numbers of parents, FAO gives ∆F = 3/(32 N_M) + 1/(32 N_F) (Gowe et al., 1959). — [FAO 2013, p. 173](https://www.fao.org/4/i3327e/i3327e.pdf)
- **[secondary]** UK JNCC states that FAO recommends a minimum Ne of at least 50 "to reduce the rate of inbreeding to less than 1%". — [JNCC UKBI Animal genetic resources indicator](https://www.jncc.gov.uk/our-work/ukbi-animal-genetic-resources)
- **[secondary]** A Wageningen thesis supervised by Windig and Oldenbroek cites the older FAO (2007) system: ≤5 breeding males is critical (NeS ≈ 20) and ≤20 breeding males is endangered (NeS ≈ 80). — [Doekes 2016, WUR MSc thesis, Markiesje & Stabyhoun](https://edepot.wur.nl/403077)

### Inferences
- The FAO hierarchy yields three anchors: ΔF ≤ 0.5% per generation (not at risk on the male criterion), ≤ 1% (minimum acceptable, Ne 50), and ~2% (upper bound tolerated in intensely selected commercial lines). A dog-breed simulator aiming at sustainability should not set a constraint above 1% per generation.

### Gaps
- I could not retrieve the FAO 1998 *Secondary guidelines ... management of small populations at risk* text, so its exact wording is not quoted. Background knowledge **[unverified]**: it also uses Ne ≥ 50 / ΔF ≤ 1% as the minimum.
- I did not consult the FAO 2011 *Molecular genetic characterization* guideline or the 2023 *Genomic characterization* guideline for Ne thresholds.

## The 50/500 rule (Franklin 1980) and Frankham et al. 2014 revision

### Takeaway
The 50/500 rule comes from Franklin 1980 and Soulé 1980. Ne = 50 is meant to avoid short-term inbreeding depression (ΔF = 1%), and Ne = 500 to retain long-term evolutionary potential. Frankham, Bradshaw & Brook (2014) argue both should be at least doubled, to 100/1000 (ΔF ≤ 0.5% per generation for the short-term criterion). Franklin, Allendorf & Jamieson (2014) dispute the revision.

### Cited Findings
- **[verified]** Frankham et al.'s reply to Franklin et al.: the thresholds "required to avoid inbreeding depression in the short-term and loss of evolutionary potential in perpetuity (Franklin, 1980), need to be increased to 100 and 1000, respectively". "Empirical data (post-1980) indicate that Ne = 50 is insufficient to prevent inbreeding depression, and our revised recommendation of at least Ne = 100 was based on a combination of theory and empirical evidence." They also say "our recommendations are conservative, as available evidence indicates that more than a doubling of Ne may be justified." — [Frankham, Bradshaw & Brook 2014, "50/500 rules need upward revision to 100/1000 – Response to Franklin et al.", Biol. Conserv., doi:10.1016/j.biocon.2014.05.006](https://doi.org/10.1016/j.biocon.2014.05.006)
- **[verified, citation]** Original paper: Frankham, R., Bradshaw, C.J.A., Brook, B.W. (2014). "Genetics in conservation management: revised recommendations for the 50/500 rules, Red List criteria and population viability analyses." *Biol. Conserv.* 170, 56–63. Counter-view: Franklin, Allendorf & Jamieson (2014), "The 50/500 rule is still valid – reply to Frankham et al." — [reference list in the reply letter](https://doi.org/10.1016/j.biocon.2014.05.006); [Macquarie repository](https://researchers.mq.edu.au/en/publications/genetics-in-conservation-management-revised-recommendations-for-t/)
- **[secondary]** Caballero et al. (2017): "the minimum Ne is 50, which corresponds to a rate of increase in inbreeding of 1% per generation (Soulé, 1980; Franklin, 1980)". Because of the arbitrariness of this rule, Frankham et al. (2014) proposed a more specific definition based on a maximum 10% decline in fitness over five generations. — [Caballero, Bravo & Wang 2017, Inbreeding load and purging (PDF)](https://fenix.ciencias.ulisboa.pt/downloadFile/1688987299228272/Caballero%20et%20al%202017%20_%20Inbreeding%20load%20and%20purging,%20implications%20for%20the%20short-term%20survival%20and%20the%20conservation%20management%20of%20small%20populations.pdf)
- **[verified]** The UK Kennel Club / Lewis et al. framing used for dogs: "The rate of loss of genetic diversity within a breed or population increases dramatically when Ne <100" and "a population with Ne <50 is considered to be at high risk of the detrimental effects of inbreeding". The paper treats ΔF = 0.01 per generation as the recommended maximum. — [Lewis, Abhayaratne & Blott 2015, Canine Genet. Epidemiol. 2:13](https://pmc.ncbi.nlm.nih.gov/articles/PMC4579366/)

### Inferences
- Under the Frankham revision, the short-term goal becomes Ne ≥ 100, i.e. ΔF ≤ 0.5% per generation. This coincides with the FAO "not at risk" male-number boundary and the Dutch dog "moderate risk" boundary (next section), so 0.5% per generation is a well-supported conservative constraint.
- Ne = 500/1000 (ΔF 0.1%/0.05%) is a long-term evolutionary-potential criterion. It is rarely used as an operational OCS constraint in livestock or dogs.

### Gaps
- I could not access the full text of the main Frankham et al. 2014 paper (paywalled; the fetched PDF was the reply letter). The "10% fitness decline over 5 generations" definition is therefore cited via Caballero et al. 2017.
- Meuwissen (2009), "Genetic management of small populations: a review", *Acta Agric. Scand. A* 59(2):71: I confirmed only the citation. I could not access the text, so I cannot quote its ΔF recommendations. Background knowledge **[unverified]**: Nordic and Meuwissen/Woolliams-school recommendations typically cite ΔF 0.5–1% per generation as an acceptable range for selected livestock breeds. I found no primary text in this session confirming this.
- I found no ICAR "guidelines for breeding programmes" document giving a numeric ΔF target.

## Dog-specific guidance (FKC, FCI, Kennel Club UK, Dutch work, Leroy, Lewis)

### Takeaway
- **Finnish Kennel Club (FKC):** requires intervention (crosses or importing dogs) when a breed's Ne over the last 3–4 generations is ≤ 50 based on inbreeding rate, or ≤ 200 based on numbers of breeding dogs. I could not confirm the 100 threshold as an FKC rule.
- **Kennel Club UK / Lewis et al. 2015:** Ne < 100 is a concern, Ne < 50 is high risk, and ΔF = 1%/generation is the maximum.
- **Dutch Windig & Oldenbroek "traffic light":** >1% unacceptable, 0.5–1% high risk, 0.25–0.5% moderate, <0.25% small. Ne 100 (ΔF ≤ 0.5%) is the long-term minimum.
- **FCI:** no ΔF number; it uses a popular-sire cap (≤ 5% of puppies registered in 5 years).

### Cited Findings
- **[secondary, quoted text of FKC strategy]** FKC General Breeding Strategy: "If a breed's average effective population size over the last 3–4 generations, taking overseas populations into account, has been 50 or less when calculated on the basis of inbreeding rate, or 200 or less when calculated using a formula based on the number of breeding dogs, the genetic variation of the breed should be increased through breed crosses and/or the introduction of native breed dogs." The linked strategy is the "General Breeding Strategy 2018–2022". The same page says "Tens of breeds have a limit in the number of offspring registered for individual (male) dogs." — [DogWellNet blog, K. Mäki, 15 May 2022](https://dogwellnet.com/blogs/entry/243-kennel-clubs-and-responsible-breeding-examples-from-finland/)
- **[secondary]** FKC breeding database note: Ne should be calculated per generation, because "the per year -figure doesn't tell you the right thing". — [DogWellNet blog 244, Genetic diversity tools in the FKC breeding database](https://dogwellnet.com/blogs/entry/244-genetic-diversity-tools-in-the-finnish-kennel-clubs-breeding-database/)
- **[secondary]** Finnish Spitz example: the FKC set a maximum litter COI of 6.25% (7 generations). Pedigree-based realized Ne = 168, versus LD-based genomic Ne = 57. — [DogWellNet, Finnish Spitz breed strategy](https://dogwellnet.com/content/health-and-breeding/breed-specific-programs/breed-specific-breeding-strategies/breeding-strategies-by-breed/breed-specific-breeding-strategies-to-achieve-positive-outcomes-the-finnish-spitz-as-an-example-increasing-and-maintaining-genetic-diversity-r762/)
- **[verified]** FCI International Breeding Strategies:
  - "Mating between siblings, mother to son or father to daughter should never be performed. As a general recommendation no dog should have more offspring than equivalent to 5% of the number of puppies registered in the breed population during a five-year period."
  - Breed size should be considered at the international level.
  - "As a general rule, a breeding programme should not exclude more than 50% of the breed; the breeding stock should be selected from the best half of the breed population."
  - The document gives no numeric ΔF or Ne target.
  — [FCI International Breeding Strategies (fci.be)](http://www.fci.be/medias/FCI-REG-STR-ELE-en-9312.pdf) (text read from a local copy; URL **[unverified]** as the exact current link)
- **[verified]** Lewis et al. 2015 (all 215 UK KC breeds, 1980–2014):
  - Ne < 100 means rapid loss of diversity; Ne < 50 is high risk; ΔF 0.01/generation is the maximum.
  - Of 116 breeds with a calculable Ne, 68 (~59%) had Ne < 100 and 29 (~25%) had Ne < 50. Ne ranged from 23.8 (Manchester Terrier) to 918.8 (Borzoi).
  - Mean generation interval was 3.88 years (range 3.06–5.04).
  - Since 2000, ΔF has generally declined towards sustainable levels.
  - Recommendation: "Breeders should guard against the over-use of sires as a strategy to maintain sustainable ΔF in the breed."
  — [Lewis et al. 2015, PMC4579366](https://pmc.ncbi.nlm.nih.gov/articles/PMC4579366/)
- **[verified]** Dutch "traffic light" table (Windig, v.d. Kraats & Oldenbroek, EAAP 2013, "Inbreeding in the Golden Retriever"):

  | Inbreeding rate | Risk assessment | Ne |
  |---|---|---|
  | >1% | Extinction by accumulation of genetic defects possible | <50 |
  | 0.5–1% | Genetic defects likely to occur | 50–100 |
  | 0.25–0.5% | Possibility of genetic defects | 100–200 |
  | <0.25% | Small chance of genetic defects | >200 |

  In the Golden Retriever, ΔF went from 0.82% (1985–94) to 0.27% (2003–12), with sire age 4.2–4.6 years. Simulated ΔF was 0.41% at a generation interval of 3.6 years. Halving the top-5 sires' share (25% → 12.5%) cut ΔF to 0.26%, whereas doubling the number of males (150 → 300) only cut it to 0.39%. — [Windig et al., EAAP 2013 slides](https://docs.eaap.org/2013/S51b_04.pdf)
- **[verified]** The same table is translated in a WUR thesis from Oldenbroek & Windig (2012). It adds the minimum number of stud dogs: >1% "unacceptably high" (<25 stud dogs), 0.5–1% "high" (25–50), 0.25–0.5% "moderate" (50–100), <0.25% "small" (>100). It also says "a Ne of 100 (ΔF of < 0.5%) is here considered as the minimum to prevent a high frequency of inherited disorders on the long term". — [Doekes 2016, WUR thesis](https://edepot.wur.nl/403077)
- **[secondary]** Windig & Oldenbroek 2015 (Golden Retriever, J. Anim. Breed. Genet.): limiting breeding to dogs with low mean kinship to the population reduced ΔF from 0.41% to 0.12% per generation in simulation. — [DogWellNet summary](https://dogwellnet.com/content/research/peer-reviewed-research/genetic-management-of-dutch-golden-retriever-dogs-with-a-simulation-tool-r271/)
- **[secondary]** A WUR study on the Dutch Shepherd refers to a "0.5% increase per generation" safe limit. — [WUR edepot 583996](https://edepot.wur.nl/583996)
- **[verified, abstract only]** Leroy (2011), "Genetic diversity, inbreeding and breeding practices in dogs: results from pedigree analyses", *Vet. J.* 189(2):177–182, doi:10.1016/j.tvjl.2011.06.016. It identifies popular-sire overuse as "the most problematic breeding practice" and suggests limiting litters/offspring per breeding animal. The abstract gives no numeric thresholds. — [AGRIS record](https://agris.fao.org/search/en/records/652f9efed5e38ff7731f7a43)
- **[secondary]** Leroy et al. (2013), "Methods to estimate effective population size using pedigree data: Examples in dog, sheep, cattle and horse", GSE (140 populations, 60 dog breeds). Ne based on identity-by-descent averaged 93–203 across methods. Demographic estimates were far higher (356–4425), so the method strongly affects comparisons against thresholds. — [PMC3599586](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3599586/)
- **[secondary]** The WUR thesis cites Leroy et al. 2013 for "Effective population size thresholds of 50 and 500 ... on respectively the short and long run". — [Doekes 2016](https://edepot.wur.nl/403077)

### Inferences
- Dog-specific guidance converges on these bands:
  - **ΔF ≤ 1%/generation (Ne ≥ 50):** absolute minimum (FKC trigger for intervention, KC UK "high risk" boundary, Dutch "unacceptable" boundary).
  - **ΔF ≤ 0.5%/generation (Ne ≥ 100):** the recommended target (KC UK, Dutch long-term minimum, Frankham revision).
  - **ΔF ≤ 0.25% (Ne ≥ 200):** the "low risk" aspiration.
- Dutch simulations suggest that limiting top-sire share is more effective than adding sires. This supports OCS-style contribution control.
- The Ne estimation method matters: FKC uses 50 for inbreeding-rate Ne but 200 for demographic Ne. Compare a simulator's ΔF-based Ne against the 50/100 numbers, not the 200 number.

### Gaps
- I could not fetch the FKC General Breeding Strategy PDF itself (kennelliitto.fi URLs returned 404), so the 50/200 text is quoted via DogWellNet.
- No primary source found for an FKC "100" threshold.
- SKK (Swedish Kennel Club) breed-specific breeding strategy (RAS) Ne guidance was not checked.
- I did not find an official Kennel Club UK policy document setting a numeric ΔF target. The KC thresholds are quoted via Lewis et al. 2015, whose authors are KC staff.

## Conversions: per generation ↔ per year, Ne ↔ ΔF, kinship targets for OCS

### Takeaway
- **Ne and ΔF:** Ne = 1/(2ΔF).
- **Per year:** per-year ΔF ≈ per-generation ΔF ÷ generation interval L. Dogs have L ≈ 3.6–4.5 years (UK mean 3.88).
- **OCS constraint:** the kinship target recursion C_{t+1} = C_t + ΔF(1 − C_t) is the standard way to set the bound. I did not verify it against a primary source this session.

### Cited Findings
- **[verified]** FAO: "we can convert ΔF per generation to a yearly rate by dividing ΔF by the average generation interval (in years)". Example: "a pig population (generation interval of two years) with ΔF of 1 percent will accumulate 15 percent inbreeding in 30 years, while in the same time period a cattle population (generation interval of six years) will accumulate 5 percent". FAO generation intervals: avian ≥1 y, pigs 1–2, sheep/goats 4, cattle 6, horses 8 (dogs not listed). — [FAO 2013, pp. 49–50](https://www.fao.org/4/i3327e/i3327e.pdf)
- **[verified]** FAO: ΔF = 1/(2×Ne). Also: "if the generation interval ... is longer, the same ∆F per generation has to be divided among more years, diminishing the loss of genetic diversity per year". — [FAO 2013](https://www.fao.org/4/i3327e/i3327e.pdf)
- **[verified]** Lewis et al. 2015 method:
  - Annual ΔF is the regression coefficient of ln(1 − F_t) on year of birth.
  - Per-generation ΔF = annual rate × mean generation interval L.
  - Ne = (2ΔF)⁻¹.
  - Mean L = 3.88 y (range 3.06–5.04).
  — [Lewis et al. 2015](https://pmc.ncbi.nlm.nih.gov/articles/PMC4579366/)
- **[verified]** Dog generation intervals observed:
  - Golden Retriever: 3.6–3.8 y (simulated), father age 4.2–4.6 y. — [Windig et al. 2013](https://docs.eaap.org/2013/S51b_04.pdf)
  - Markiesje: 3.4 y; Stabyhoun: 4.4 y. — [Doekes 2016](https://edepot.wur.nl/403077)
- **[verified]** FAO describes the OCS constraint form: maximise Σcᵢvᵢ subject to the contribution-weighted coancestry (ΣΣcᵢcⱼfᵢⱼ) not exceeding the value implied by the desired ΔF. — [FAO 2013, Box 51](https://www.fao.org/4/i3327e/i3327e.pdf)
- **[unverified, standard theory]** The kinship bound for generation t+1 is set as C_{t+1} = C_t + ΔF(1 − C_t), equivalently 1 − C_{t+1} = (1 − C_t)(1 − ΔF), following Meuwissen (1997, GSE 29:139) and Grundy, Villanueva & Woolliams. With overlapping generations and yearly selection rounds (e.g., the optiSel R package), the per-round bound is commonly C_next = 1 − (1 − C_now)(1 − 1/(2Ne))^(1/L). I could not open the optiSel vignette (404) to quote it. Related Woolliams work: [Woolliams & Pong-Wong 2007 GSE (SDP for OCS)](https://doaj.org/article/5eee59df20db4ae5b6e28602a0a9755a); [Woolliams, Nirea & Meuwissen, WCGALP 2014](https://asas.confex.com/asas/WCGALP14/webprogram/Paper10467.html).

### Inferences (worked numbers; arithmetic, not sourced)
- ΔF 1%/gen ↔ Ne 50; 0.5% ↔ Ne 100; 0.25% ↔ Ne 200; 0.1% ↔ Ne 500.
- Per year with L = 4 y: 1%/gen ≈ 0.25%/y (exact: 1 − 0.99^(1/4) = 0.2509%); 0.5%/gen ≈ 0.125%/y; 0.25%/gen ≈ 0.0626%/y.
- With L = 3.88 y: 1%/gen ≈ 0.258%/y; 0.5%/gen ≈ 0.129%/y.
- Over 30 years at L = 4 (7.5 generations): ΔF 1% gives ≈ 7.3% accumulated inbreeding (1 − 0.99^7.5); 0.5% gives ≈ 3.7%.
- Example kinship target: if current mean kinship is 0.10 and ΔF = 0.5%/gen, the next-generation target is 0.10 + 0.005 × 0.90 = 0.1045. In a yearly step with L = 4, the target is 1 − 0.90 × 0.995^(0.25) ≈ 0.10113.

### Gaps
- No primary source quoted here for the C_{t+1} recursion or the optiSel per-year formula. Verify against Meuwissen 1997 or the optiSel documentation before citing.

## Values used for balancing genetic gain against diversity; very small or highly inbred populations

### Takeaway
FAO recommends choosing ΔF by predicting gain across a range of ΔF values and taking a compromise. It sets ≤ 1% for at-risk breeds and allows up to ~2% for commercial breeds. Dog-oriented guidance points to 0.5% per generation as the sustainable target. For breeds already below Ne 50, both FAO and FKC recommend first enlarging Ne: more breeding animals, longer generation intervals, cryopreserved semen, or crosses and imports (FKC).

### Cited Findings
- **[verified]** FAO, at-risk vs commercial ΔF (≤1% vs ~2%), plus the advice to "predict the expected gain for a range of ∆F and choose the compromise solution". — [FAO 2013, p. 171](https://www.fao.org/4/i3327e/i3327e.pdf)
- **[verified]** FAO for critical populations: raise Ne "as rapidly as possible" to at least 50. "When the Ne of a population drops significantly lower than 50, it may reach a level where it cannot ..." [recover]. FAO actions include equalising contributions, using more males, and prolonging the generation interval, including with cryopreserved material. — [FAO 2013, Section 6](https://www.fao.org/4/i3327e/i3327e.pdf)
- **[verified]** In the FAO example (Moreno et al. 2011), weighted selection at the same selection intensity (1.235) nearly doubled Ne, from 19.8 to 31.5, compared with truncation selection. — [FAO 2013, Box 50](https://www.fao.org/4/i3327e/i3327e.pdf)
- **[secondary]** FKC: breeds at or below Ne 50 (inbreeding-based) or 200 (demographic) should use crosses or native-dog introductions. — [DogWellNet 243](https://dogwellnet.com/blogs/entry/243-kennel-clubs-and-responsible-breeding-examples-from-finland/)
- **[secondary]** Fernández, Meuwissen, Toro & Mäki-Tanila (2011, *Animal*), "Management of genetic diversity in small farm animal populations": the "Optimum Contribution" approach is the best among the methods compared. — [Luke Jukuri record](https://jukuri.luke.fi/items/312b5c52-6b4a-4d18-a602-5290ebf48c61/full)
- **[secondary]** Leroy & Rognon (2012, Vet. J. 194:343–348): limiting offspring per breeding animal improves genetic diversity in four dog breeds. — [VIN PDF](https://www.vin.com/Proceedings/Downloads/TuftsBG2013/90649_BreedStrategies_A6_Leroy_TuftsBG2013.pdf)

### Inferences
- Recommended simulator settings, all traceable to the sources above:
  - **Default:** ΔF = 0.5% per generation (Ne 100). This is backed by Frankham et al. 2014, the KC UK Ne < 100 concern, the Dutch 0.5% boundary, and the FAO "vulnerable/not at risk" male boundary.
  - **Ceiling:** ΔF = 1% per generation (Ne 50), the FAO minimum and the FKC/KC "high risk" boundary.
  - **Sensitivity scenarios:** 0.25% (Ne 200) and 1%.
- For breeds already below Ne 50, a tight ΔF constraint (≤ 0.5%) mainly rations the remaining diversity. Guidance says the population also needs new genetic input (crosses or imports), which OCS alone cannot supply.

### Gaps
- I found no published OCS study specific to dog breeds that reports gain at several ΔF levels.
- I did not verify, with a primary source, the Meuwissen/Woolliams statement that 0.5–1%/generation is the livestock standard (see Gaps in the 50/500 section).
