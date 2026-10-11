# Why per-mating recommendations concentrate sire use, remedies, and practical issues for coordinated breeding in dog clubs

Scope note: about 25 tool calls (searches, fetches, and full-text extraction of one PDF). Several classic papers (Quinton, Smith & Goddard 1992; Belonsky & Kennedy 1988; Brisbane & Gibson 1995; Garcia-Baccino 2017 full text; Wijnrocx breeder survey) could **not** be read in full here. Anything taken from abstracts or secondary citations is labelled. Items marked **[UNVERIFIED]** come from background knowledge and were not confirmed by a source in this session.

## 1. Mechanism: why independent per-mating optimisation converges on the same sires

### Takeaway
Ranking candidates on a shared criterion (EBV, show success, or a tool's score) and picking the best one for each mating co-selects relatives. It also gives a few individuals very large long-term genetic contributions, which raises ΔF and lowers Ne even when every single mating looks good (for example, low COI). In dogs, popular sires are found in every breed and cause both diversity loss and the spread of recessive disease.

### Cited Findings
- **BLUP and truncation co-select families.** Verrier, Colleau & Foulley (1993, *Theor. Appl. Genet.* 87:446–454) used Monte Carlo simulation over 30 generations (h² = 0.10, 0.25, 0.50). In large populations, animal-model BLUP gave the greatest cumulative gain. In small populations, an index that down-weights family information (ω = 1/2) and mass selection did better. Selection with ω = 1 or 1/2 strongly affected within-replicate genetic variance and mean inbreeding, especially in small populations. Selection on within-family deviations did less damage. — [AGRIS record](https://agris.fao.org/search/en/records/65de4d760f3e94b9e5cd2b31) (abstract only)
- **Belonsky & Kennedy (1988)** is cited secondarily: truncation on BLUP EBVs raised gain per generation but also raised inbreeding per generation. Short-term gain came at a cost to long-term gain (citing Quinton et al. 1992). — secondary summary via [search result, GSE 1994 / review](https://gsejournal.biomedcentral.com/counter/pdf/10.1186/1297-9686-26-5-431.pdf). The original paper was **not retrieved**.
- Wray & Goddard (1994, *GSE* 26:431): selecting on EBV alone maximises response in the next generation, but doing so repeatedly does not necessarily maximise longer-term response. — [GSE PDF](https://gsejournal.biomedcentral.com/counter/pdf/10.1186/1297-9686-26-5-431.pdf)
- **Quinton, Smith & Goddard (1992)** could not be located; the search found only Quinton & Smith (1995, *J Anim Sci* 73:2208–2212, doi:10.2527/1995.7382208x), "Comparison of evaluation-selection systems for maximizing genetic response at the same level of inbreeding". — [JAS issue 73(8)](https://academic.oup.com/jas/issue/73/8). **[UNVERIFIED from background knowledge]**: Quinton, Smith & Goddard 1992 (*J Anim Sci* 70:1060–1067) is usually cited for this point: when compared at the *same* ΔF rather than the same number selected, BLUP's advantage over phenotypic selection shrinks or disappears, because BLUP's extra gain comes partly from family co-selection.
- **Dog evidence for concentration.** Lewis, Abhayaratne & Blott (2015), covering all 215 UK KC breeds from 1980–2014, found "The existence of popular sires was apparent in all breeds". Mean ΔF in each 5-year block from 1980–1999 exceeded 0.01 per generation, and the trend has been negative since 2000. Of 116 breeds, 68 had Ne < 100 and 29 had Ne < 50. Ne ranged from 23.8 (Manchester Terrier) to 918.8 (Borzoi) and was not associated with census size: English Springer Spaniel had about 10,886 registrations/year but Ne = 45. Mean generation interval was 3.88 years. The authors note that swapping a popular sire for a close male relative "will have limited impact". They mention negative assortative mating and optimum contribution methods but consider them unlikely to be coordinated in practice. — [Lewis et al. 2015, Canine Genet Epidemiol 2:13, doi:10.1186/s40575-015-0027-4](https://pmc.ncbi.nlm.nih.gov/articles/PMC4579366/)
- Leroy & Baumung (2011, *Anim Genet* 42:66–74) studied 10 French breeds. The effective number of sires was only 33–70% of the actual number of sires. Simulated risk of a recessive disorder spreading was 4.4 times higher under the observed (popular-sire) practice than under random mating. Close/line breeding affected only about 1–8% of dogs and was a lesser problem. — [AGRIS record](https://agris.fao.org/search/fr/records/652f9eecd5e38ff7731f7902); [Purdue summary](https://caninewelfare.centers.purdue.edu/?p=2210) (abstract-level)
- Founder effects and extensive use of popular sires "are considered to be the main reasons for the dissemination of genetic disorders" in dogs. — [Leroy & Rognon 2012, Vet J 194:343–348, doi:10.1016/j.tvjl.2012.06.025](https://www.vin.com/Proceedings/Downloads/TuftsBG2013/90649_BreedStrategies_A6_Leroy_TuftsBG2013.pdf)
- Popularity is driven by show and competition success. In Mäki's Finnish Spitz breed strategy, "the strongest factor guiding the breeding is competition" (appearance or working traits). When phenotypes become similar, "also genes become similar". Popular sires were used widely in 1950–1990. — [DogWellNet, Finnish Spitz breeding strategy](https://dogwellnet.com/content/health-and-breeding/breed-specific-programs/breed-specific-breeding-strategies/breeding-strategies-by-breed/breed-specific-breeding-strategies-to-achieve-positive-outcomes-the-finnish-spitz-as-an-example-increasing-and-maintaining-genetic-diversity-r762/)
- A Dutch golden retriever population of about 600 dams and 150 sires producing about 300 litters/year was analysed by simulation. The main driver of inbreeding was "the concentration of breeding in a few sires". — [Windig & Oldenbroek 2015, JABG doi:10.1111/jbg.12149 (AGRIS abstract)](https://agris.fao.org/search/en/records/65df97e57c7033e84bee5b68)
- Minimising parental coancestry for each mating (the per-mating COI criterion) "was not effective in the long run" in the golden retriever simulation. — [Windig & Oldenbroek 2015 abstract](https://agris.fao.org/search/en/records/65df97e57c7033e84bee5b68)

### Inferences
- The tool's behaviour in simulation is the expected outcome. Each dam's owner solves a *local* problem: low COI with that dam, high EBV, low disease risk. If one sire has high EBV and is unrelated to many dams (for example a recent import), he wins for most dams at once. COI for the current litter stays low, but the sire's long-term genetic contribution, and so ΔF in the next generation, rises. That is why per-mating COI minimisation did not help in the long run (Windig & Oldenbroek). ΔF is driven by the *variance of family contributions*, which no single-mating score sees.
- The sire-use penalty in the current tool is computed from *past* use. Breeders who query at the same time all see the same, not-yet-updated penalty. That is a classic "herding" or synchronisation failure. Any per-mating penalty needs either real-time shared booking state or a club-level allocation.
- Litter mean kinship (the offspring's mean kinship to the population) helps, but it uses the population's *current* state. It does not account for the other litters planned in the same round.

### Gaps
- I found **no published study showing that a recommendation tool or index-based mate tool (e.g. KC Mate Select, EBV publication) itself increased sire concentration in dogs**. This remains a plausible hypothesis. Possible analogues include dairy cattle after genomic selection; Sonesson et al. 2012 (section 4) is relevant there.
- Full texts of Quinton et al. 1992 and Belonsky & Kennedy 1988 were not retrieved, so their exact numbers are not quoted.
- No formal "winner-takes-all" / recommender-system literature specific to animal breeding was found in this session.

## 2. Remedies short of full OCS and what each achieves

### Takeaway
Offspring caps per sire help, but by a modest and breed-dependent amount: roughly 4–15% relative reduction in mean kinship in French breeds. They can backfire when the capped sires were genetically valuable (unrelated to the population) or when replacements are relatives. Restricting breeding to low mean-kinship animals was the most effective simple rule in Dutch golden retrievers, reducing ΔF from 0.41% to 0.12% per generation. Rotational (circle) schemes work well in group-structured populations but have no documented dog-club use. Within-family / reduced-family-weight indices and dynamic constrained selection give more gain at equal ΔF.

### Cited Findings
**Offspring caps (FCI 5% rule and fixed caps)**
- FCI recommendation: "the number of offspring per dog should not be >5% of the number of puppies registered in the breed population during a 5 year period". — [Leroy & Rognon 2012](https://www.vin.com/Proceedings/Downloads/TuftsBG2013/90649_BreedStrategies_A6_Leroy_TuftsBG2013.pdf). A forum post attributes the same rule originally to the Norwegian KC; **unverified**. — [Tapatalk forum](https://www.tapatalk.com/groups/workinghprs/popular-sire-syndrome-t3720-s20.html)
- Leroy & Rognon 2012 re-simulated 2001–2010 pedigrees of 4 French breeds (Braque Saint Germain BSG, Berger des Pyrénées BRP, Coton de Tulear COT, Epagneul Breton EPB) with caps of 25/50/100/200 offspring per reproducer, replacing over-cap parents with other animals. — [Leroy & Rognon 2012](https://www.vin.com/Proceedings/Downloads/TuftsBG2013/90649_BreedStrategies_A6_Leroy_TuftsBG2013.pdf)
  - Cap 200: "only a small proportion of matings were affected". Mean kinship (Φ) was unchanged in BSG and BRP and fell slightly in COT (0.038 to 0.036, −6%) and EPB (0.038 to 0.037, −4%).
  - Cap 50: sires were replaced for 77% of COT individuals and Φ fell from 0.038 to 0.032 (−15%). In BRP, sires were replaced for 19% and Φ fell from 0.061 to 0.055 (−10%). In BRP, cap 50 "would allow kinship rate to decrease from 0.5% to 0.2%".
  - Cap 25 in BSG (a small breed): Φ **rose** from 0.135 to 0.149 (+10%), because "The two sires used the most in 2010 show a low level of kinship with the current population". For this breed the authors recommend "more binding breeding schemes, for example minimising kinship" or outcrossing instead.
  - Recommendation for COT: a cap of about 100 affects 36% of matings (sire pathway) for about a 10% relative kinship reduction. EPB: cap 100, changing 23% of sires, gives a predicted 12% relative kinship reduction.
  - Proportion of sires changed by cap (25/50/100/200): BSG 22.8 / 2.9 / 0 / 0%; BRP 67.0 / 19.0 / 2.8 / 0.3%.
  - When replacement sires were drawn preferentially from relatives of the replaced sire, kinship rose. Breeders' non-random choice of replacements can undo a cap. Simulation assumed random replacement, "which seldom happens in real populations".
- Finnish KC lists an offspring limit of max 40 for males (counted in full litters) for at least one breed. The Swedish Bullmastiff club lists "5 % of generation". — [DogWellNet HSDD genetic diversity entries](https://dogwellnet.com/hsdd/conditions/25-populationgenetic-diversity/?breeds=97) (breed-specific; exact breed context not verified)
- "Nordic clubs have introduced maximum limits for the numbers of offspring per individual dogs as well as for the inbreeding coefficient of the litters." — [Finnish Spitz breeding strategy, DogWellNet](https://dogwellnet.com/content/health-and-breeding/breed-specific-programs/breed-specific-breeding-strategies/breeding-strategies-by-breed/breed-specific-breeding-strategies-to-achieve-positive-outcomes-the-finnish-spitz-as-an-example-increasing-and-maintaining-genetic-diversity-r762/)
- Some Swedish breeds have introduced maximum offspring numbers per male "to avoid extensive use of popular sires". — [SKK WSAVA 2006 paper, VIN](https://www.vin.com/doc/?id=3859041)
- In the Dutch golden retriever simulation, limiting litters per sire "generally decreased the generation interval… but in some instances… lead to an increase in inbreeding rates" (ΔF is per generation, so faster turnover can raise ΔF per year). — [Windig & Oldenbroek 2015](https://agris.fao.org/search/en/records/65df97e57c7033e84bee5b68)

**Mean-kinship based restriction (closest simple proxy to OCS)**
- Restricting breeding to animals with low average relatedness to the population was the most effective measure tested in Dutch golden retrievers: ΔF fell from 0.41% to 0.12% per generation. — [Windig & Oldenbroek 2015](https://agris.fao.org/search/en/records/65df97e57c7033e84bee5b68)
- Lewis et al. 2015: "Using a greater proportion of males for breeding will help mitigate the effect popular sires have on ΔF". Monitoring genetic contributions could flag over-popular sires early. — [Lewis et al. 2015](https://pmc.ncbi.nlm.nih.gov/articles/PMC4579366/)

**Within-family / reduced family weight**
- Down-weighting family information (ω = 1/2) or within-family deviations reduced inbreeding relative to full BLUP, with better long-term gain in small populations. — [Verrier et al. 1993 (abstract)](https://agris.fao.org/search/en/records/65de4d760f3e94b9e5cd2b31)
- Mendelian-sampling indices to reduce ΔF: Grundy, Villanueva & Woolliams, "The use of Mendelian indices to reduce the rate of inbreeding in selection programmes" (title only seen). — [SRUC Pure](https://pure.sruc.ac.uk/en/publications/the-use-of-mendelian-indices-to-reduce-the-rate-of-inbreeding-in-/)

**Dynamic / weighted selection (Grundy et al.)**
- Grundy, Villanueva & Woolliams (1998, *Genet Res* 72:159–168), "Dynamic selection procedures for constrained inbreeding and their consequences for pedigree development". The method details were not retrieved. — [SRUC Pure](https://pure.sruc.ac.uk/en/publications/dynamic-selection-procedures-for-constrained-inbreeding-and-their/)
- Their 2000 extension to overlapping generations reported "up to 35%" more genetic response at the same ΔF than standard truncation BLUP. — [Cambridge abstract, Animal Science 2000](https://www.cambridge.org/core/journals/animal-science/article/abs/dynamic-selection-for-maximizing-response-with-constrained-inbreeding-in-schemes-with-overlapping-generations/F14A30707DCE98C8726F1D2636BB4610)
- **[UNVERIFIED]** Brisbane & Gibson (1995) proposed selecting on EBV penalised by a multiple of the candidate's mean relationship to the selected group. Penalised-EBV schemes reduce ΔF at modest cost in gain. Original not retrieved.

**Rotational / circular mating (breeding circles)**
- In Kempisch Heideschaap sheep simulations, rotational schemes cut inbreeding to about 0.16% per year, from over 1.5% without ram exchange. A breeding circle has run for more than 30 years in Veluws Heideschaap and works in practice. These schemes need no pedigree. — [Windig et al., Animal (Cambridge abstract)](https://resolve.cambridge.org/core/journals/animal/article/abs/an-effective-rotational-mating-scheme-for-inbreeding-reduction-in-captive-populations-illustrated-by-the-rare-sheep-breed-kempisch-heideschaap/3FB5F37DEBF6CE1C93B1160255139CD0); [PMC7379314](https://pmc.ncbi.nlm.nih.gov/articles/PMC7379314); [zoo baboon circle, JZAR](https://jzar.org/jzar/article/view/585)
- Wageningen's Pointer simulation program lets users simulate sire restrictions, inbreeding limits, mean kinship and breeding circles; it was developed with the golden retriever study. — [Pointer, WUR CGN](https://genebankdata.cgn.wur.nl/software/Pointer/Pointer.html)

**Full OCS (benchmark)**
- optiSel (Wellmann) is a free R package for optimum contribution selection using pedigree or marker kinship. The docs recommend marker data and note that objectives for livestock, companion animals and zoo populations "may be quite different". — [optiSel vignette](https://ftp.fau.de/cran/web/packages/optiSel/vignettes/ocs-vignette.html); [Wellmann 2019 BMC Bioinformatics](https://link.springer.com/article/10.1186/s12859-018-2450-5)

### Inferences
- **Design implication:** a fixed cap such as the FCI 5% per 5 years is a blunt upper bound. It does not stop 20 breeders from all choosing sires #2–#5. A coordinated strategy is better framed as *allocating* a per-season budget of litters (or of "contribution") to sires, with each sire's budget scaled by his mean kinship to the breeding population (low-MK sires get more). This is effectively a discretised OCS, close to what the golden retriever study found most effective.
- Caps must not be applied blindly to genetically valuable outsiders or imports. Leroy & Rognon's BSG case shows a cap on low-MK sires *raises* kinship. Make the cap a function of mean kinship rather than a flat number.
- Count caps per generation and per year: shortening the generation interval can raise ΔF per generation (Windig & Oldenbroek).
- Replacement choice matters. When a sire is "full", the tool should steer away from his sons and brothers too, for example with a family-level cap or by counting a sire's sons' litters partly against his quota. Otherwise relatives refill the slot.

### Gaps
- No dog study was found that quantifies within-family selection, equalised family sizes, or quotas for under-represented lines.
- No quantitative comparison of weighted (penalised-EBV) selection against offspring caps in a dog-sized population was found.

## 3. Practical issues in dog clubs: breeder freedom, acceptance, voluntary vs mandatory, implementation, data

### Takeaway
Dog breeding is decentralised among many small, hobbyist breeders whose main driver is show or competition success. Clubs mostly rely on recommendations, with some binding rules in the Nordic countries (offspring caps, COI limits, registration consequences). Researchers themselves doubt that full coordination (OCS or negative assortative mating) can be achieved. Evidence on breeder attitudes is thin and mostly descriptive.

### Cited Findings
- Lewis et al. (2015) consider negative assortative mating and optimum contribution methods unlikely to be coordinated in practice in dog breeds. — [Lewis et al. 2015](https://pmc.ncbi.nlm.nih.gov/articles/PMC4579366/)
- Introducing new alleles in rare breeds depends mainly on breeders' willingness to use outside dogs. These breeds show strongly unequal sire use and few founders. — [Czech J Anim Sci 2012](https://cjas.agriculturejournals.cz/pdfs/cjs/2012/05/05.pdf)
- Finnish KC mandatory elements (PEVISA): mating parent × offspring or full siblings, or using a dog with the worst health-test grade, means the litter can only go into the EJ (non-pedigree) register. Health statements must be valid at mating. Breed-specific PEVISA rules can ban registration from affected dogs. — [Finnish KC PEVISA pages](https://kennelliitto.fi/rotukohtaisen-pevisa-ohjelman-valintamahdollisuudet); [PEVISA 2022](https://kennelliitto.fi/lomakkeet/pevisa-ja-muut-rotukohtaiset-erityisehdot-vuonna-2022)
- Breed clubs write breed-specific breeding strategies (JTO). The Finnish KC template is for breeds with ≥250 registrations in the last 5 years and asks for annual registrations, average age of breeding dogs, and mean COI over 10–15 years. — [FKC JTO template](https://www.kennelliitto.fi/sites/default/files/media/fkc_breeding_strategy_template_for_breeds_with_large_populations_0.pdf)
- Mäki warns that adding breeding criteria and recommendations risks narrowing the gene pool further by excluding potential breeding dogs. — [Finnish Spitz strategy](https://dogwellnet.com/content/health-and-breeding/breed-specific-programs/breed-specific-breeding-strategies/breeding-strategies-by-breed/breed-specific-breeding-strategies-to-achieve-positive-outcomes-the-finnish-spitz-as-an-example-increasing-and-maintaining-genetic-diversity-r762/)
- Leroy & Rognon 2012: "members of breed societies often do not know which is the best strategy to adopt". They propose breed-specific simulation of candidate policies to give tailored recommendations, and call for surveys of how breeders choose replacement sires. — [Leroy & Rognon 2012](https://www.vin.com/Proceedings/Downloads/TuftsBG2013/90649_BreedStrategies_A6_Leroy_TuftsBG2013.pdf)
- Breeder surveys:
  - Lithuania (2011, online): 83.7% aim to improve exterior, character and health. Line breeding was preferred over close breeding (30.2% vs 11.6%). Most valued genetic testing. — [Biologija 2011](https://lmaleidykla.lt/ojs/index.php/biologija/article/view/870)
  - Australia (n = 200): breed improvement is a key motivation. — [Animals 2025, 15(15):2302](https://www.mdpi.com/2076-2615/15/15/2302)
  - Australian breeders' selection of breeding stock, with emphasis on the dam. — [CQU](https://acquire.cqu.edu.au/articles/journal_contribution/Selection_of_breeding_stock_among_Australian_purebred_dog_breeders_with_particular_emphasis_on_the_dam/13389047)
  - French scent hound breeders' goals and mating practices (Leroy & Rognon). — [VIN](https://www.vin.com/doc/?id=5947812)
- Breeders without a central herd book can still be coordinated without pedigrees through rotational schemes, which have worked for 30+ years in a sheep breed. — [Windig et al.](https://resolve.cambridge.org/core/journals/animal/article/abs/an-effective-rotational-mating-scheme-for-inbreeding-reduction-in-captive-populations-illustrated-by-the-rare-sheep-breed-kempisch-heideschaap/3FB5F37DEBF6CE1C93B1160255139CD0)
- The SKK (Sweden) public Breeding Records service gives per-dog offspring counts and breed statistics, which is the data infrastructure a quota or monitoring system needs. — [SKK WSAVA paper](https://www.vin.com/doc/?id=3859041); [Breeding dogs in Sweden (SKK)](https://djurid.skk.se/globalassets/dokument/uppfodning/engelska/breeding-dogs-in-sweden-j40.pdf)
- The Finnish KC breeding database shows a popular-sire ratio (1 = no popular sires) and Ne per breed. — [DogWellNet blog 244](https://dogwellnet.com/blogs/entry/244-genetic-diversity-tools-in-the-finnish-kennel-clubs-breeding-database/)

### Inferences
- **Partial adoption:** if only a fraction of breeders follow a coordinated plan, the sires that the plan "frees up" may be taken by non-followers. Coordinated allocation should therefore be robust to a fraction of exogenous matings, for example by re-optimising each round after observed matings. This is a design inference, not from a source.
- **Acceptance levers suggested by the evidence:** keep breeder choice by offering a ranked *shortlist* per dam drawn from sires with remaining quota, rather than a single assignment. Make the cap depend on mean kinship, so valuable outsiders are rewarded rather than punished. Publish breed-level ΔF/Ne trends, as the Finnish and Swedish databases do, to show the collective benefit. Use club rules (registration consequences, as in PEVISA) only for the hard limits.
- **Booking-system idea:** a shared "reservation" ledger in which a planned mating decrements the sire's remaining contribution budget for the season fixes the simultaneity problem described in section 1. It needs only planned-mating metadata, not owner identities, which may ease data-protection concerns. GDPR applies to breeder (owner) personal data, not to dog data per se; **[UNVERIFIED]**, no source checked here.

### Gaps
- **Wijnrocx et al.** breeder attitude work could not be found. The search returned only Wijnrocx's population-genetics papers on Belgian breeds (2014 varieties; 2016 compromised diversity). — [researchportal.be](https://researchportal.be/nl/node/122511)
- No UK Kennel Club breeder survey on attitudes to sire use or mate-selection advice was retrieved. The KC Mate Select tool exists **[UNVERIFIED in this session]**, but its effect on sire use was not found.
- No source on data-protection concerns specific to kennel-club breeding tools was found.
- No evidence on voluntary vs mandatory compliance rates was found (e.g. how many litters exceed FCI 5%).
- No current (2026) Nordic offspring-cap texts were retrieved; the PEVISA documents found date from 2014–2022.

## 4. Kinship source: pedigree vs genomic, incomplete pedigrees, imports, metafounders

### Takeaway
Use the same information source for kinship control as for selection. With genomic EBVs but pedigree-based kinship control, true (genomic) ΔF was about 4× the target. Genome-wide marker kinship preserves heterozygosity better than pedigree kinship in OCS. With shallow or import pedigrees, founders are wrongly treated as unrelated. Metafounders (a generalisation of unknown parent groups that allows within- and between-group relatedness) fix this and make pedigree and genomic matrices compatible.

### Cited Findings
- Sonesson, Woolliams & Meuwissen (2012, *GSE* 44:27, doi:10.1186/1297-9686-44-27): OCS with target ΔF = 0.005 — [PMC3522025](https://pmc.ncbi.nlm.nih.gov/articles/PMC3522025/)
  - Pedigree constraint with GBLUP: ΔG = 3.08, ΔF_ped = 0.0050 but genomic ΔF_IBD = 0.0211, about 4× target.
  - Genomic constraint with GBLUP: ΔG = 1.91, ΔF_IBD = 0.0051, on target.
  - At a target of 0.010 with pedigree constraint and GBLUP, ΔF_IBD = 0.0422.
  - Truncation GBLUP gave ΔG 2.77 and ΔF_IBD 0.0209, nearly the same as OCS with a pedigree constraint.
  - Conclusion: "genomic selection has to be combined with genomic control of inbreeding."
- de Cara, Fernández, Toro & Villanueva (2011, *JABG* 128:456–464, doi:10.1111/j.1439-0388.2011.00971.x): genome-wide marker coancestry "usually performed better than using genealogical data or estimated genealogical coancestry" for maintaining expected and observed heterozygosity in OCS conservation schemes. Deciding at the offspring level kept more heterozygosity than deciding at the parent level. — [URJC repository](https://burjcdigital.urjc.es/items/051ff623-f6fd-46a6-85b1-8b4cfc2b17dc) (abstract)
- A caveat: genome-wide SNP-based conservation can still lose diversity at specific trait loci. — [Frontiers Genet 2018, Saba pigs](https://www.frontiersin.org/journals/genetics/articles/10.3389/fgene.2018.00389/pdf)
- Legarra et al. (2015, *Genetics*): metafounders are pseudo-individuals at the top of the pedigree, each representing a base population. Their self- and cross-relationship parameters (γ) are estimated from pedigree plus markers, and they make genomic and pedigree relationship matrices compatible. — [PMC4492372](https://pmc.ncbi.nlm.nih.gov/articles/PMC4492372); [HAL](https://hal.inrae.fr/hal-02639425)
- Garcia-Baccino et al. (2017, *GSE*) estimated γ for ssGBLUP. The γ track F_ST-type fixation indices, and metafounders reduced bias. — [UChile record](https://repositorioslatinoamericanos.uchile.cl/handle/2250/1891455?show=full) (abstract-level). Metafounders generalise UPGs, which treat base populations as unrelated. — [Frontiers Genet 2021 review](https://www.frontiersin.org/journals/genetics/articles/10.3389/fgene.2021.678587/pdf). A 2024 GSE paper extends γ estimation to unbalanced data and many UPGs. — [HAL 2024](https://integ04-cnspfv.archimed.fr/doc/OAI_1/oai-HAL-hal-04568877v1)
- Lewis et al. 2015 link the post-2000 decline in ΔF in UK breeds to relaxed quarantine laws and more use of non-UK dogs, i.e. imports. — [Lewis et al. 2015](https://pmc.ncbi.nlm.nih.gov/articles/PMC4579366/)

### Inferences
- Imports with 2–3-generation pedigrees appear "unrelated" in pedigree kinship. They will get very low predicted COI with every dam, which is exactly the setup in which every breeder picks the same import sire. Pedigree kinship therefore *amplifies* the herding problem. Mitigations: assign imports to a metafounder (e.g. per country or line) with γ estimated from a genotyped subset, or use genomic kinship where genotypes exist, and flag low pedigree completeness (e.g. equivalent complete generations) in the UI.
- If the tool uses genomic EBVs or genomic disease-carrier data, its kinship/OCS component should be genomic too (Sonesson et al.). Otherwise realised ΔF can be several times the target.

### Gaps
- No dog-specific study comparing pedigree vs genomic OCS was found.
- No dog-specific metafounder application was found.
- The size of the bias in dog import pedigrees is not quantified here.

## 5. Existing software for coordinated planning in dog clubs

### Takeaway
I found no turnkey club-level coordinated mating planner for dogs. The existing pieces are: simulation and decision-support tools (Pointer from Wageningen; Leroy & Rognon's breed-specific pedigree simulation), OCS engines (optiSel), and kennel-club databases with monitoring (SKK Breeding Records, Finnish KC KoiraNet popular-sire ratio and Ne).

### Cited Findings
- Pointer (WUR Centre for Genetic Resources): simulates sire restrictions, inbreeding limits, mean kinship and breeding circles. It was used for Dutch golden retrievers. — [Pointer](https://genebankdata.cgn.wur.nl/software/Pointer/Pointer.html); [Windig & Oldenbroek 2015](https://agris.fao.org/search/en/records/65df97e57c7033e84bee5b68)
- Wageningen student theses applied breed analyses and mating guidelines for Dutch clubs: Bouvier des Flandres, Wetterhoun (with the NVSW club, including outcrossing), and Schapendoes. — [Kuijpers Bouvier](https://wur.nl/en/show/talita-kuijpers-breed-analysis-of-the-dutch-bouvier-des-flandres-population-final-report.htm); [Boering Wetterhoun](https://wur.nl/nl/show/thesis-aisha-boering-inbreeding-and-outcrossing-in-the-wetterhoun.htm); [Minnema Schapendoes](https://wur.nl/nl/show/thesis-jesse-minnema-managing-inbreeding-and-relatedness-in-the-schapendoes.htm)
- optiSel: OCS with pedigree or marker kinship, aimed at local and endangered breeds. — [optiSel vignette](https://ftp.fau.de/cran/web/packages/optiSel/vignettes/ocs-vignette.html); [Wellmann EAAP 2016](https://docs.eaap.org/2016/S45_07_Wellmann.pdf)
- Finnish KC database: popular-sire ratio, Ne, and mean COI per breed. — [DogWellNet blog 244](https://dogwellnet.com/blogs/entry/244-genetic-diversity-tools-in-the-finnish-kennel-clubs-breeding-database/)
- SKK Breeding Records: offspring statistics per dog and per breed. — [SKK](https://djurid.skk.se/globalassets/dokument/uppfodning/engelska/breeding-dogs-in-sweden-j40.pdf)

### Inferences
- The gap the user's tool would fill is real: monitoring and policy simulation exist, but no tool allocates sires across a club's planned matings in a season.

### Gaps
- No evidence was found of optiSel being used operationally by a kennel club.
- No evidence was found of PMx (the zoo pedigree tool) being used for dog breeds.
- No Dutch Raad van Beheer "fokprogramma" tool details were found.
- The UK KC Mate Select and Breed Population Analyses tools are only referenced indirectly ([DogWellNet blog 52](https://dogwellnet.com/blogs/entry/52-kennel-club-breed-population-analyses-tool)); their functionality was not verified.
