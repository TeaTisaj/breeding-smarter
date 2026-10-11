# Mating and contribution strategies in dog breeds and other small closed populations: simulation evidence

Scope note: I retrieved full text (or full slide/abstract text) for Windig et al. 2013 EAAP (golden retriever slides), Sonesson & Meuwissen 2001, Windig et al. 2018/2019 (breeding circle), Windig & Hulsegge 2021 (Retriever/Pointer), Windig & Doekes 2018 (abstract) and the Bergsma 2022 MSc thesis (summary). Everything else comes from abstracts or search snippets and is marked as such. Findings that rest on my background knowledge and that I could not verify in this session are listed only under Inferences or Gaps, labelled "unverified".

## 1. Dog-specific studies: which strategies were compared and what they found

### Takeaway
The best quantified dog study (Dutch golden retriever, Windig & Oldenbroek 2015) found something very close to what your simulator found. Mating each dam to her least related sire cut ΔF almost to zero for about 20 years. After that it gave no long-term benefit: ΔF was 0.39% versus 0.40% for no restriction in years 50–70. Excluding animals with above-average mean kinship (MK) was the measure that lasted, at 0.12–0.14% throughout. Limiting popular sires, and especially capping litters per sire per year, also helped. Lifetime caps sometimes backfired because they shortened the generation interval.

### Cited Findings
**Windig & Oldenbroek 2015, J Anim Breed Genet 132:428–440, DOI [10.1111/jbg.12149](https://doi.org/10.1111/jbg.12149)** (abstract via [AGRIS](https://agris.fao.org/search/en/records/65df97e57c7033e84bee5b68) / [DogWellNet](https://dogwellnet.com/content/research/peer-reviewed-research/genetic-management-of-dutch-golden-retriever-dogs-with-a-simulation-tool-r271/)). Detailed numbers come from the preceding EAAP 2013 talk by Windig, van der Kraats & Oldenbroek, "Inbreeding in the Golden Retriever" ([slides PDF](https://docs.eaap.org/2013/S51b_04.pdf)). The slide values match the paper's abstract (0.41% falling to 0.12%), but the published tables may differ slightly.
- Population: about 600 dams, 150 sires and 300 litters per year. The "5 most popular sires sire approximately 25% of the litters in a year" — [AGRIS abstract](https://agris.fao.org/search/en/records/65df97e57c7033e84bee5b68)
- Simulation set-up (slides): standard population based on 2005–2011; litter size 6.7 (range 2–13); parent age 4.5 years; "5 'top' dogs sire 75 nests"; "50% of top dogs replaced by sons"; inbreeding and relatedness start at 0; "Simulated for 20 years", "10 replicates". ΔF for the standard population was 0.41% — [EAAP 2013 slides](https://docs.eaap.org/2013/S51b_04.pdf)
- Population structure (ΔF, generation interval) — [slides](https://docs.eaap.org/2013/S51b_04.pdf):
  - Standard: 0.41%, 3.6
  - 300 instead of 150 breeding males: 0.39%, 3.6
  - Top 5 sires at 12.5% instead of 25% of litters: 0.26%, 3.7
  - The slides conclude that "Limiting contribution of top dogs more effective than increasing number of breeding males"
- Sire restrictions (ΔF and generation interval, per-year cap vs lifetime cap) — [slides](https://docs.eaap.org/2013/S51b_04.pdf):
  - No restriction: 0.41%
  - 20 litters per sire: per year 0.45%
  - 10 litters per sire: per year 0.27% (3.8); lifetime 0.42% (3.6)
  - 5 litters per sire: per year 0.18%; lifetime 0.26% (generation interval 2.6)
  - 2 litters per sire: per year 0.16%; lifetime 0.13% (2.4)
  - 1 litter per sire: per year 0.19%; lifetime 0.12% (2.5)
  - The slides conclude "Restricting nests/father/year more effective"
- Relatedness restrictions — [slides](https://docs.eaap.org/2013/S51b_04.pdf):
  - "Minimise f Parents" (each female mated to the least related male): ΔF 0.04% in years 0–20, but 0.39% in years 50–70 (generation interval 4.2 and 4.6)
  - "Breed wide f above average excluded" (animals with above-average MK excluded from breeding): 0.12% in years 0–20 and 0.14% in years 50–70
  - No restriction: 0.41% and 0.40%
  - The explanation on the slide: "Using a small number of (or a single) unrelated fathers decreases inbreeding of offspring, but increases their relatedness"
- Paper abstract: restricting breeding to animals with low average relatedness "decreased the rate of inbreeding per generation from 0.41 to 0.12%". Minimising parental co-ancestry did not help in the long run but reduced variation in inbreeding rates. Lifetime litter caps shortened generation intervals and could increase inbreeding — [AGRIS](https://agris.fao.org/search/en/records/65df97e57c7033e84bee5b68)
- A secondary summary attributes a ΔF of 0.17% to removing popular sires and equalising offspring per sire. This comes from a search snippet that cites the Institute of Canine Biology, not the paper, so treat it as unverified — [ICB blog](https://www.instituteofcaninebiology.org/blog/how-to-develop-effective-strategies-for-the-genetic-management-of-your-breed)

**Windig & Doekes 2018, "Limits to genetic rescue by outcross in pedigree dogs", J Anim Breed Genet, DOI 10.1111/jbg.12330** (abstract via [Europe PMC](https://europepmc.org/search?query=DOI:10.1111/jbg.12330))
- Saarloos wolfdog-like population, about 14 litters per year. "The inbreeding rate estimated for a 25-year period of 2.1% per generation ... reduced to 1.8% when a single litter was produced by an outcross without backcrosses. To reduce the inbreeding rate below 1%, more than eight of the 14 litters born yearly in the recipient breed had to be outcrossed."
- With two outcross litters plus one generation of backcross, ΔF was 2.0% per generation. "When each newborn litter during 25 years had a 5% chance of being produced by an outcross, the inbreeding rate reduced to −0.2%."
- 80 years of natural selection were simulated before the outcross. Introducing a new lethal allele "occurred rarely"; slightly detrimental and neutral alleles came in more often.
- Conclusion: outcrossing "may help to buy time in which the population structure can be changed so that the effective population size increases."

**Windig & Hulsegge 2021, "Retriever and Pointer: Software to Evaluate Inbreeding and Genetic Management in Captive Populations", Animals 11:1332, DOI [10.3390/ani11051332](https://doi.org/10.3390/ani11051332)** ([PMC8151292](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8151292/))
- Pointer is a stochastic simulator with options for sire restrictions, inbreeding limits, MK restrictions and breeding circles, plus optional allelic diversity and disease loci (lethality, effects on fertility or survival, selection against carriers). It was "originally devised for dogs" — [PMC8151292](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8151292/)
- Validation lesson: "Most crucial parameter proved to be the contribution of dominant males. Without incorporating the contribution of the top 2 to 5 most popular sires, simulations generally underestimated inbreeding rates." — same source
- The authors state that inbreeding limits, or bans on mating animals with common ancestors in the past x generations, are "often promoted, but not very effective in the long run. The explanation is that inbreeding is not heritable, and kinships may still increase despite these measures" — same source
- Rotational example: 1 group of 24 males and 144 females versus 12 groups of 2 males and 12 females, simulated for 1000 years with 50 replicates. Breeding circle inbreeding was "higher ... than for a single large group with random mating for the first 78 years, and higher than Falconers scheme and MAI up to about year 180". Rotational breeding was "always much lower than for isolated groups" — same source

**Bergsma 2022, MSc thesis, Wageningen (supervisor J. Windig), "Simulating genetic management strategies & genetic defects in dogs"** ([edepot.wur.nl/575638](https://edepot.wur.nl/575638))
- Used Pointer on a small population modelled on the Saarloos wolfdog around 1990 (15 males, 20 females, 11 litters per year, 2 champion sires siring 50%) and on a medium population, over 100 years. Four strategies: excluding carriers, mating least related animals, breeding animals with the lowest MK, and limiting litters per sire.
- Results: "Excluding carriers ... resulted in swift extinction of almost all populations." The other three "all successfully reduced inbreeding levels and rate of inbreeding, lowered the amount of fixed deleterious alleles, and helped prevent the fixation of disease alleles ... Focusing on mean kinship was most effective. When the effective population size is increased, some disease alleles may take longer to eliminate, but they linger at low frequencies in a heterozygous state" — [thesis](https://edepot.wur.nl/575638)
- Quantitative tables were not extracted. This is an MSc thesis, not peer-reviewed. It cites "Lewis & Windig 2016" as the source of its strategy set; I did not identify that reference.

**Leroy & Baumung 2011, "Mating practices and the dissemination of genetic disorders in domestic animals, based on the example of dog breeding", Animal Genetics 42(1):66–74** (abstract via [AGRIS](https://agris.fao.org/search/fr/records/652f9eecd5e38ff7731f7902) / [BOKU](https://forschung.boku.ac.at/de/publications/74701))
- Used genealogies from ten French breeds (n = 80,785). The effective number of sires was 33%–70% of the actual number. Popular-sire use multiplied the risk of spreading a recessive disorder by about 4.4 relative to random mating. Line breeding and close breeding were associated with lower dissemination risk (a purging and exposure effect). These figures come from a search summary of the abstract, so verify the 4.4 figure against the paper — [AGRIS](https://agris.fao.org/search/fr/records/652f9eecd5e38ff7731f7902)

**Selection on hip and elbow dysplasia (dogs)**
- Mäki et al. simulated breeding schemes for hip dysplasia, elbow dysplasia, behaviour and appearance in a population modelled on Finnish Rottweilers (Animal Welfare). The realised genetic response for HD and ED in 1989–1998 was only about 0.03 genetic SD — [Cambridge record](https://resolve.cambridge.org/core/journals/animal-welfare/article/effect-of-breeding-schemes-on-the-genetic-response-of-canine-hip-dysplasia-elbow-dysplasia-behaviour-traits-and-appearance/CF8EECC49177EE7AFC4E5E62E179BE7B) (abstract only; inbreeding results not retrieved).
- Malm, Fikse, Sørensen & Strandberg (EAAP 2011) compared phenotypic truncation selection, BLUP truncation selection and OCS based on BLUP for categorical HD scores, with 300 and 3000 dogs born per year — [EAAP 2011 abstract](https://docs.eaap.org/2011/S48_Malm.pdf). I did not retrieve the numeric results. The search summary says the companion paper concludes that efficient selection against HD is possible with BLUP plus OCS.
- In Labrador retrievers, genomic selection gave about 1.15 times the response of phenotypic selection under the BVA/KC hip scheme, and testing all littermates gave more than three times the response — [PMC4166706](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4166706/) (from the search summary).
- In Border Collies (13,339 records), ancestral inbreeding was associated with lower HD values, which is interpreted as purging — [PMC7601391](https://pmc.ncbi.nlm.nih.gov/articles/PMC7601391)

### Inferences
- Your simulator's result matches the golden retriever result: per-dam minimum-kinship mate choice gives a big short-term drop in offspring inbreeding (ΔF 0.04% in years 0–20), but ΔF returns to baseline (0.39%) once kinship builds up. The mechanism Windig names is that the "least related" sire is often the same few sires, so contributions become more concentrated and population-wide kinship rises. This matches your finding that Ne does not rise.
- The dog literature points to controlling contributions as the lever: MK-based exclusion, caps on sire use, and equalised family sizes. Avoiding inbreeding in each mating is not enough. In the cited work, random mating combined with contribution control beats minimum-kinship mating with uncontrolled contributions over the long run.
- Lifetime litter caps can raise ΔF by shortening the generation interval. Report ΔF both per year and per generation, and track generation interval.

### Gaps
- I found no peer-reviewed study of formal OCS (for example optiSel, EVA or GENCONT) applied operationally by a kennel club. I also found no dog OCS simulation with full numeric results apart from Malm et al., whose numbers I could not retrieve. No Wellmann dog or horse OCS paper was found in this session.
- No Mäki, Kettunen, Oliehoek or Nicholas study comparing mating strategies was retrieved with numbers. Oliehoek's work on mean-kinship and founder-based management in dogs (e.g. Kooiker/Dutch breeds) exists to my knowledge, but I did not verify it here.
- The full tables of Windig & Oldenbroek 2015 (paper version) were not accessed. Values above are from the conference slides.

## 2. Small populations and conservation: minimum-coancestry mating vs random mating vs OCS, family-size equalisation and rotational schemes

### Takeaway
The theory and simulation literature is consistent. Minimum-coancestry (MC) mating lowers the level of inbreeding (Wright's FIS < 0) and delays its rise by about two generations. In unselected populations whose contributions are already optimised, it leaves the asymptotic ΔF essentially unchanged. In selected populations it helps somewhat by reducing the variance of family contributions, and the benefit is largest when the population is small or evaluated by BLUP. Rotational schemes and breeding circles achieve low ΔF without pedigrees, roughly matching OC. Combining OC with male rotation gave the lowest ΔF.

### Cited Findings
**Sonesson & Meuwissen 2001, Genet Res 77:285–292, DOI [10.1017/S0016672301005079](https://doi.org/10.1017/S0016672301005079)** ([PDF](https://www.cambridge.org/core/services/aop-cambridge-core/content/view/A7DF3B134973BF5C210BAEBBDD285590/S0016672301005079a.pdf/minimization-of-rate-of-inbreeding-for-small-populations-with-overlapping-generations.pdf))
- "Minimum coancestry mating resulted in lower levels of inbreeding than random mating, but ∆F was approximately the same."
- Design: 100 years, 100 replicates, ΔF averaged over years 96–100, 6, 10 or 20 newborns per year, overlapping generations.
- Per-year ΔF, random (RAND) vs minimum-coancestry (MC) mating, 70% survival:
  - 6 newborns per year: 0.0077 vs 0.0083
  - 10 newborns per year: 0.0043 vs 0.0046
  - 20 newborns per year: 0.0021 vs 0.0022
- Under MC, α (Wright's FIS) was more negative: for 6 animals, −0.074 vs −0.108. The variance of long-term contributions was "somewhat lower ... but these differences where not large enough to affect predicted rates of inbreeding".
- Their optimised-contribution method chose only the oldest animals, which made the population split into age-class sublines and raised inbreeding. Requiring at least one sire and one dam from the second-oldest class fixed this and gave an "L times lower ∆F". "For schemes where the oldest animals were selected, ∆F increased by 18–52%."

**Sonesson & Meuwissen 2000, "Mating schemes for optimum contribution selection with constrained rates of inbreeding", Genet Sel Evol 32:231–248, DOI [10.1051/gse:2000116](https://www.gse-journal.org/10.1051/gse:2000116)** (abstract via search snippet; the page returned 403)
- MC and MC1 (at most one offspring per pair) "delayed inbreeding by about two generations" compared with random mating. With ΔF constrained to 1.0% and 100 candidates, genetic response was 22% higher for MC1 and MVRO than for random mating. With looser constraints or more candidates the gain was 5–6%.

**Sonesson & Meuwissen 2002, Genet Sel Evol 34:23–39, DOI [10.1051/gse:2001002](https://www.gse-journal.org/10.1051/gse:2001002)** (abstract via search snippet)
- Overlapping generations, ΔF restricted to 0.25% per year, 256 animals born per year, h² = 0.25: MC1 increased genetic gain by 18% over random mating. The gain was larger in small schemes and under tighter restrictions.

**Kahsay et al. 2012, Genet Sel Evol** ([DOAJ](https://doaj.org/article/2b07480527ae44ba9c1511d61e6bb428)), abstract via search snippet
- Non-random mating had little effect under genomic evaluation. MC "remains an efficient mating design when BLUP is used for genetic evaluation or when the size of the population is small."

**Caballero, Santiago & Toro 1996, "Systems of mating to reduce inbreeding in selected populations", Animal Science 62:431–442, DOI 10.1017/S1357729800014971** (abstract via [Univ. Oviedo record](https://portalinvestigacion.uniovi.es/documentos/5e78c51c2999521b3d11bc06))
- Compensatory mating (largest selected families mated to the smallest) was "proportionately about 0.30 more effective than minimum coancestry matings" when ΔF was low (phenotypic selection or large N). MC was better under high ΔF (BLUP or small N). Combining compensatory and MC mating gave the largest reductions. The mechanism is a reduced cumulative effect of selection plus deviation from Hardy–Weinberg proportions. A version for overlapping generations reduced ΔF by about 0.50 more than with discrete generations.
- The search summary says Fernández et al. (2003, Genetics) found that minimising global coancestry gives equal or lower inbreeding in the short and medium term. One hierarchical design gave lower asymptotic ΔF. This is unverified.

**Breeding circles and rotational mating (livestock and zoo)**
- Windig & Kaal 2008, Animal 2:1733–1741, DOI [10.1017/S1751731108003029](https://resolve.cambridge.org/core/journals/animal/article/abs/an-effective-rotational-mating-scheme-for-inbreeding-reduction-in-captive-populations-illustrated-by-the-rare-sheep-breed-kempisch-heideschaap/3FB5F37DEBF6CE1C93B1160255139CD0) (Kempisch Heideschaap sheep). Without ram exchange, ΔF was above 1.5% per year. A breeding circle and maximum avoidance of inbreeding both reduced ΔF "to on average 0.16% per year". MAI was more variable than the circle. One secondary source lists a different co-author, so check the citation.
- Windig, Verweij & Oldenbroek 2019 (online 2018), J Anim Breed Genet 136:51–62, DOI [10.1111/jbg.12371](https://pmc.ncbi.nlm.nih.gov/articles/PMC7379314) (Veluws Heideschaap, a circle running for more than 30 years):
  - Theoretical ΔF per generation started at 0.29–0.47% within flocks and converged to 0.18%. Simulations with overlapping generations converged to 0.12%.
  - Realised ΔF from a 12K SNP chip was 0.29–0.41%. Adding selection to the simulation gave 0.35%, dominant rams gave 0.38%, and both together gave 0.67%.
  - For comparison, expected ΔF under isolated random mating within single flocks was 0.94–1.90% (from the paper's Table 1).
  - The introduction states: "In the long run, the most effective strategy is to minimize mean kinship of the population rather than kinship of mating pairs only (Frankham, Briscoe, & Ballou, 2002)."
- Mucha & Komen 2016, J Anim Breed Genet 133(4):323–332 ([WUR record](https://research.wur.nl/en/publications/rates-of-inbreeding-and-genetic-adaptation-for-populations-manage/)), abstract:
  - Herd structures simulated: 3×20, 6×40 and 20×60.
  - Rotational mating (RM) moved 10%, 20% or 50% of males in a circle. "RM was efficient in restriction of inbreeding and produced results comparable with OC. However, RM can result in genetic adaptation ... when 20% or less males are selected for rotation and selection of animals is not random. Lowest rates of inbreeding were obtained by combining OC with rotation of males." "When full pedigree is available, OC management is preferable."
- Kappelhof & Windig 2021 (Hamadryas baboons in 14 European zoos), [JZAR](https://jzar.org/jzar/article/view/585): ΔF per generation was 1.93% without exchange and 0.64–1.47% with a breeding circle. Genetic diversity was "almost the same".

### Inferences
- Splitting into subpopulations with a fixed donor–recipient circle trades higher early inbreeding for lower long-term ΔF. In Pointer, inbreeding under the circle exceeded that of one random-mating group for about 78 years. The time horizon decides which strategy "wins", so dog experiments need horizons of at least 50–100 years (about 12–25 dog generations at L ≈ 4 years).
- In real circles, dominant males (popular sires) and selection roughly doubled realised ΔF over theory (0.67% vs 0.12–0.18%). Any mating scheme still has to control the number of offspring per sire.

### Gaps
- The classic results that equalising family sizes roughly doubles Ne (Wright 1938; Gowe, Robertson & Latter 1959) and the MC theory papers (Caballero & Toro 2000 and 2002, Genet Res; Fernández, Toro & Caballero 2003/2004) were not fetched here. They are unverified in this session but well established in textbooks.
- I did not retrieve exact numbers from Caballero et al. 1996 (long-term behaviour of MC under selection), nor from Fernández et al. 2003 or 2004 on subdivided populations ("Management of genetic diversity of subdivided populations").

## 3. Zoo practice: mean-kinship breeding vs pairwise minimum kinship

### Takeaway
Zoo management (PMx, Ballou & Lacy) ranks breeders by low MK and pairs them to avoid close inbreeding. The direct experimental test, Montgomery et al. 1997 in Drosophila, found that MK retained significantly more gene diversity and allelic diversity than maximum avoidance of inbreeding or random choice, with no difference in fitness. Quantitative zoo comparisons of MK against pairwise minimum kinship are scarce in what I retrieved.

### Cited Findings
- Montgomery, Ballou, Nurthen, England, Briscoe & Frankham 1997, "Minimizing kinship in captive breeding programs", Zoo Biology 16:377–389 ([CZAW summary](https://czaw.org/resources/minimizing-kinship-in-captive-breeding-programs/)). Drosophila lines were started with unequal founder representation. MK retained significantly more gene diversity and allelic diversity, measured at 6 microsatellite and 7 allozyme loci, than MAI or RAND. Reproductive fitness did not differ significantly. The authors concluded that MK is "currently the best available method" — [CZAW](https://czaw.org/resources/minimizing-kinship-in-captive-breeding-programs/) (summary; exact percentages not retrieved)
- Rudnick & Lacy 2008, Conservation Genetics: the long-term benefit of knowing founder relationships was "generally small". MK strategies "probably often produce near optimal results" under standard founder assumptions — [PDF](https://responsibleherpetoculture.foundation/wp-content/uploads/2021/09/the-impact-of-assumptions-about-founder-relationships-on-the-effectiveness-of-captive-breeding-strategies.pdf) (via search summary)
- Lacy, Ballou, Starfield, Thompson & Thomas 1995, "Pedigree analysis for population management", in Population Management for Survival and Recovery — [Smithsonian repository](https://repository.si.edu/handle/10088/4315) (record only)
- Kappelhof & Windig (2021) cite Mucha & Komen in noting that MK management also requires control over offspring numbers per individual — [JZAR](https://jzar.org/jzar/article/view/585)

### Inferences
- MK selection is a practical heuristic approximation of OCS without a genetic-gain term, since minimising average coancestry of the next generation is equivalent to optimising contributions. Its edge over pairwise minimum kinship comes from choosing who breeds and how often, not from who is paired with whom.

### Gaps
- I did not obtain exact numeric results from Montgomery et al. 1997 (gene diversity retained per treatment) or from Ballou & Lacy 1995 (founder importance coefficients vs MK).

## 4. Interaction with purging, recessive disease and selection on breeding values

### Takeaway
Managing for diversity (MK, OCS or MC) keeps deleterious recessives at low heterozygous frequencies rather than purging them. Deliberate inbred matings did not improve fitness in de Cara et al. 2013. Excluding carriers in small dog populations led to extinction in Bergsma 2022. Popular sires are the main route by which recessive disease spreads. With selection, MC mating and OCS let you get more genetic gain at a fixed ΔF.

### Cited Findings
- de Cara, Villanueva, Toro & Fernández 2013, Heredity, DOI 10.1038/hdy.2012.119 ([Nature](https://www.nature.com/articles/hdy2012119); [PMC3656637](https://pmc.ncbi.nlm.nih.gov/articles/PMC3656637)), via search summary:
  - Combining optimal contributions with inbred matings: inbred matings "never led to higher fitness in the scenarios analysed" and usually kept diversity lower than random or MC matings.
  - OC alone maintains deleterious mutations. Results "depend strongly on the mutational model ..., the population size during management and the reproductive rate."
- Bergsma 2022: excluding carriers led to near-universal extinction. MK, least-related mating and sire limits all lowered disease allele frequencies and fixation, with MK best — [thesis](https://edepot.wur.nl/575638)
- Leroy & Baumung 2011: popular sires raised the risk of recessive disorder dissemination about 4.4 times compared with random mating — [AGRIS](https://agris.fao.org/search/fr/records/652f9eecd5e38ff7731f7902)
- Windig & Doekes 2018: outcrossing rarely introduces new lethals because prior selection had purged them from the donor population — [Europe PMC](https://europepmc.org/search?query=DOI:10.1111/jbg.12330)
- Sonesson & Meuwissen 2000 and 2002: MC mating under OCS gave 18–22% more genetic gain at constrained ΔF in small schemes — [GSE 2000](https://www.gse-journal.org/10.1051/gse:2000116), [GSE 2002](https://www.gse-journal.org/10.1051/gse:2001002)
- Malm et al. 2011: OCS with BLUP was evaluated for hip dysplasia in dogs (numbers not retrieved) — [EAAP](https://docs.eaap.org/2011/S48_Malm.pdf)

### Inferences
- A strategy can win on ΔF and Ne yet lose on short-term disease incidence, because MC lowers the homozygosity of recessives in the current generation. Your experiment should therefore report disease-affected incidence (homozygotes) separately from allele frequency and from number of alleles lost or fixed.

### Gaps
- I found no dog simulation that combines BLUP selection for HD with OCS or MK management and reports ΔF and gain trade-offs with numbers (Malm et al. would be the closest; full text not retrieved).

## 5. Outcome measures and time horizons used (for experiment design)

### Takeaway
Typical designs run 20–100 years (and up to 1000 for asymptotics) with 10–100 replicates. They report ΔF per year and per generation separately for early and late windows, and alongside it the generation interval, Ne, kinship, α (FIS), variance of contributions, and allele loss and fixation.

### Cited Findings
- Golden retriever study: 20 years and 10 replicates for the main runs, with a long-term window of years 50–70. Outputs were ΔF and the age of parents — [slides](https://docs.eaap.org/2013/S51b_04.pdf)
- Sonesson & Meuwissen 2001: 100 years and 100 replicates. ΔF and ΔC were averaged over years 96–100. They also reported α, the variance of long-term contributions (S²c), predicted ΔF, generation interval L and number selected — [Genet Res](https://doi.org/10.1017/S0016672301005079)
- Pointer: 1000 years and 50 replicates for rotational comparisons. Outputs include inbreeding and kinship (with and without self-kinship), ΔF per period, Ne, top-sire contributions, generation interval, allele frequencies, and years to fixation or loss — [PMC8151292](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8151292/)
- Bergsma 2022: 100 years. Outputs include disease allele frequencies, numbers of eliminated and fixed alleles, F, ΔF, population size and survival — [thesis](https://edepot.wur.nl/575638)
- Breeding circle paper: ΔF was compared across theory, simulation and SNP data (marker-based and heterozygosity-based) — [PMC7379314](https://pmc.ncbi.nlm.nih.gov/articles/PMC7379314)

### Inferences (design suggestions)
- **Report ΔF in two ways.** Report ΔC, the rate of change of mean coancestry, as well as ΔF. ΔC (equivalent to MK) measures the gene diversity that is truly lost. Mating designs change F at a given level of coancestry through α, but not the coancestry itself. Compute Ne from ΔC, and also from the variance of contributions (sire-use concentration).
- **Use at least two time windows,** for example 0–20 and 50–100 years. Strategies swap ranks over time: minimum-kinship mating is best early and no better than baseline late; circles are worse early and better late.
- **Compare a factorial of strategies:** {random, per-dam minimum kinship} × {no contribution control, sire caps per year, MK exclusion or OCS}. This separates the effect of mate allocation from the effect of contribution control. Add a combined arm (OCS plus minimum-kinship mating), which the literature finds best: Mucha & Komen 2016; Sonesson & Meuwissen 2000.
- **Model popular sires explicitly.** Validation in Windig & Hulsegge 2021 shows they dominate realised ΔF.
- **Track generation interval.** Lifetime litter caps change it.
- **Use 10–100 replicates.** Report the variance in ΔF too, since MAI and circles differ in variability (Windig & Kaal 2008).
- **Include recessive loci of varying severity.** Report incidence of affected animals, allele frequency, and loss or fixation counts.

### Gaps
- No dog study reported genetic gain for a breeding goal alongside ΔF under mating strategies with retrievable numbers.
