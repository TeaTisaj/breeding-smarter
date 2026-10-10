# Research notes (source of truth for numbers)

Condensed from the deep-research report of 2026-10-10. Every number used in configs must cite a key from section 9 or be marked `assumption: true`. Items marked **UNVERIFIED** must not be presented as fact.

---

## 1. Conference
- BioMedVetMech 2026, 3rd European Congress on Biomedical and Veterinary Engineering, Zagreb, **24 to 25 October 2026** [bmvm-site].
- Abstract deadline has passed (site says 10 July on one page, 10 August on another). Full paper deadline **15 October 2026**. Proceedings: IFMBE Proceedings (Springer) [bmvm-submission].
- Poster: max **90 x 120 cm**, about **300 words** including references, official BioMedVetMech template, self-printed, mount at least 1 hour before the session, presenter stands by the poster. Best-poster award (double-blind) [bmvm-submission].
- Animal-use ethics statement is required when reporting animal experiments. We state that all data is synthetic.
- Contact: info@orthoing.com.

## 2. Regulation and rules

### 2.1 EU Regulation 2026/1818 (welfare and traceability of dogs and cats)
- Published in the Official Journal on 10 August 2026 [eurlex-2026-1818; consilium-2026].
- Prohibits breeding between **parents and offspring, siblings, half-siblings, grandparents and grandchildren**. Derogation possible for **local breeds with a limited gene pool** (competent authority) [eurlex-2026-1818; ep-2026].
- **UNVERIFIED** (press only, check OJ text): maximum 3 litters in 2 years per bitch, bitch at least 18 months old, transition periods (4 years for breeders/sellers, 15 years for owners of never-traded pets), the "2036" date in EUR-Lex metadata [euroweekly-2026; catster-2026].

### 2.2 FCI
- FCI is a federation; national clubs keep studbooks and issue pedigrees. Limited registration is a tool against matador breeding [fci-strategies].
- Guideline: no dog should have more offspring than **5% of puppies registered in the breed in a 5-year period** [fci-strategies].
- Breeding programmes should not exclude more than **50% of the breed** [fci-strategies].
- The 5% rule is non-binding in large breeds (1,366 puppies in the Epagneul Breton) and too strict in tiny breeds [leroy-rognon-2012].
- For EBV-based selection, the EBV of the combination should be better than the breed average [fci-strategies].

### 2.3 Kennel Club UK
- Does not register puppies from mother/son, father/daughter or brother/sister matings [kc-coi].
- Mate Select (since May 2011): individual COI, breed average COI, predicted COI of hypothetical matings, using all generations on file. Breed averages recalculated each June [kc-coi; vettimes-coi].
- Known weakness: founders and the earliest recorded ancestors of imports (often only 3 to 5 generations) are treated as COI 0 and unrelated, so COI is underestimated in import-heavy breeds [pde-2011].

### 2.4 Raad van Beheer (Netherlands)
- VFR template: a bitch may not be mated by her grandfather, father, brother, son or grandson; such litters are not entered in the NHSB [rvb-vfr].
- Breed clubs can add half-sibling bans, repeat-combination limits, lifetime stud limits (example: 25 matings) [rvb-vfr].
- Since December 2023: breed "foknormen" plus a software module that automatically checks whether a sire x dam combination meets the norms [rvb-foknormen].

### 2.5 HKS (Croatia)
- Studbooks: HR (Hrvatska rodovna knjiga) and HUR (conditional register) [hks-pravilnik].
- Only members of HKS clubs may breed; breeder is the owner of the bitch at mating; dogs must pass a breeding examination (uzgojni pregled) [hks-pravilnik].
- HD findings E/I or E/II exclude a dog from a breeding licence [hks-pravilnik].
- Hunting breeds: bitches may breed from 12 months (small breeds) or 15 months (others) up to 8 years [hks-pravilnik].
- Mating certificate contains sire and dam names and registration numbers, sire owner's name and address [hks-pravilnik].
- Stated breeding goal: preservation and, if possible, expansion of the breed's genetic diversity [hks-pravilnik].
- **UNVERIFIED for non-hunting breeds**: exact age windows. Check the current Pravilnik.

### 2.6 Finland (Kennelliitto)
- Breeding database (KoiraNet) is openly browsable: pedigree, inbreeding over different generation depths, health, BLUP indices, breed statistics [fkc-db].
- General Breeding Strategy: if Ne over the last 3 to 4 generations is **50 or less (inbreeding-based)** or **200 or less (based on number of breeding dogs)**, diversity should be increased (crosses or native dogs) [fkc-strategy].
- Breed programmes (PEVISA) can limit offspring per male [fkc-strategy].

### 2.7 Sweden (SKK)
- Avelsdata publishes pedigree, COI, health results and BLUP EBVs for HD and ED (since 2012), updated weekly, 44 breeds as of 2020 [skk-hd-2020].
- HD graded A to E (FCI). 60 years of screening reduced HD to about one third in predisposed breeds [skk-hd-2020].

### 2.8 EU Animal Welfare Platform guide
- Cites a recommendation that a combined COI above **6.5%** should be avoided [eu-platform-guide].

### 2.9 Not verified in this research pass
AKC and VDH rules, KC UK EBV programme details, per-mutation allele frequencies, features of commercial tools (Breedmate, ZooEasy, Pedigree Database Online, PawPeds, Breedera), named researchers at Zagreb faculties.

## 3. Genetic diversity facts
- 227 breeds, 49,378 dogs genotyped: mean genomic inbreeding **F_adj = 0.249**; only 12 breeds had F < 0.10; higher-F breeds had higher morbidity [bannasch-2021].
- Golden Retrievers: each 10% increase in genomic COI associated with about one fewer puppy per litter [chu-2019].
- All 215 KC breeds (1980 to 2014): popular sires in every breed; rate of inbreeding peaked in the 1980s to 1990s then declined [lewis-2015].
- Ne estimable for 116 breeds: **68 below 100**, **29 below 50**, range **23.8 (Manchester Terrier) to 918.8 (Borzoi)** [lewis-2015].
- Historical sire concentration: about 40% of puppies from 20% of sires (terriers, 1915) [haynes-1915 via ICB].
- About 20% of dogs have recorded offspring (10 KC breeds; secondary summary of [calboli-2008], not checked against primary text). Inbreeding-based Ne of 40 to 80 for most of those breeds [calboli-2008].
- Samoyed: 1.7% of males born in 2015 were bred from [kc-demography-2025].
- 1,054,293 dogs screened for 250 variants: **57% carried at least one copy** of a risk variant [donner-2023].
- HD heritability reported between **0.25 and 0.7** depending on population and measurement [skk-hd-2020 and refs therein].

## 4. Calibration parameters
| Parameter | Value | Status | Key |
|---|---|---|---|
| Mean litter size (all breeds) | 5.4 | verified | borge-2011 |
| Litter size range by size | about 3.5 (miniature) to about 7.1 (giant) | verified | borge-2011 |
| Litters with at least one perinatal loss | 24.6% | verified | tonnessen-2012 |
| Mean litter size at 8 days | 4.97 | verified | tonnessen-2012 |
| Sire concentration | heavy-tailed; top 20% of sires produce about 40% of puppies (historical) | verified (old source) | haynes-1915 |
| Share of dogs ever bred | about 20% | secondary | calboli-2008 |
| Generation interval | 4 to 5 years | **assumption** (confirm per breed from lewis-2015 Additional file 1) | |
| Ne archetypes | small about 25 to 50, medium about 80 to 150, large about 200 to 900 | derived from distribution in lewis-2015 | lewis-2015 |
| Genomic F median | about 0.25 | verified, genomic not pedigree | bannasch-2021 |
| Disease allele frequencies | from Donner 2023 Dryad data | open data, CC0 by Dryad policy | donner-2023 |
| HD heritability | 0.25 to 0.7 | verified range | skk-hd-2020 |
| Missing data rates | 10 to 30% missing health tests, 2 to 5% unknown sire in old cohorts | **assumption** | |

## 5. Existing tools (gap analysis)
| Tool | Does | Gap |
|---|---|---|
| KC Mate Select | COI lookups and hypothetical matings | No ranking or optimisation, founders unrelated, UK only |
| SKK Avelsdata | COI, health stats, HD/ED EBVs | Lookup only |
| FKC KoiraNet | Open pedigrees, COI by depth, BLUP, breed stats | No pair optimisation |
| RvB foknormen module | Automatic rule check of a combination | Compliance only |
| PMx, SPARKS, PopLink, ZIMS (zoos) | Mean kinship, Mate Suitability Index, gene diversity | Not for registries; no health or EBV scoring |
| optiSel, ENDOG, R pedigree packages | OCS, kinship, population parameters | Research tools, no UI, R only |
| Embark, Wisdom Panel | Genomic COI, carrier status | Proprietary, individual level |

## 6. Methods (with references)
- Wright's inbreeding coefficient and path method [wright-1922].
- Meuwissen and Luo algorithm for F via A = LDL' [meuwissen-luo-1992].
- Colleau's indirect method for products A x without forming A; modified by Sargolzaei, Iwaisaki and Colleau (1.2 to 143 times faster) [colleau-2002; sargolzaei-2005].
- Mean kinship and Mate Suitability Index (PMx, MateRx) [ballou-2001; lacy-2012].
- Ne from individual increase in inbreeding [gutierrez-2008]; census Ne = 4 Nm Nf / (Nm + Nf).
- Effective number of founders fe = 1 / sum(p_k^2) [lacy-1989]; founder genome equivalents fg = 1 / (2 * mean kinship) [lacy-1995 / ballou-lacy-1995].
- Optimum contribution selection [meuwissen-1997]; optiSel R package v2.1.0 [optisel].
- AlphaSimR v2.1.0 (CRAN, May 2026) can gene-drop through a given pedigree [alphasimr].

## 7. Open datasets
| Dataset | Content | Access | Use |
|---|---|---|---|
| Donner 2023, Dryad doi:10.5061/dryad.tdz08kq3j | 250 variants x 1,054,293 dogs, no pedigree | CC0 by Dryad policy | Allele frequency priors (STRETCH import) |
| optiSel ExamplePed | Real cattle pedigree subset | GPL-2 (do not redistribute under permissive licence) | Optional cross-check only |
| Real dog pedigrees (SKK, KC, FKC) | | Not open | Partnership targets |

## 8. Potential partners
University of Zagreb Faculty of Veterinary Medicine and Faculty of Agriculture (find names), HKS breed-club breeding leaders (especially Croatian native breeds), SKK, Kennelliitto (Katariina Mäki), Kennel Club UK (Tom Lewis), IPFD/DogWellNet, Grégoire Leroy, UC Davis (Danika Bannasch), Wisdom Panel (Jonas Donner), Raad van Beheer, FVE/FECAVA.

## 9. Citation keys
| Key | Reference |
|---|---|
| bmvm-site | biomedvetmech.com (home, leadership, schedule pages) |
| bmvm-submission | biomedvetmech.com/paper-submission |
| eurlex-2026-1818 | eur-lex.europa.eu/eli/reg/2026/1818 |
| consilium-2026 | Council press release, 22 May 2026 |
| ep-2026 | European Parliament press release 20260423IPR41833 |
| euroweekly-2026 | Euro Weekly News, 2 May 2026 (secondary) |
| catster-2026 | Catster (secondary) |
| fci-strategies | FCI International Breeding Strategies |
| leroy-rognon-2012 | Leroy G, Rognon X (2012), popular sire and FCI 5% rule |
| kc-coi | Kennel Club UK COI pages / Mate Select |
| vettimes-coi | Vet Times, breed average COI update |
| pde-2011 | Pedigree Dogs Exposed blog, May 2011, Mate Select critique |
| rvb-vfr | Raad van Beheer VFR template (via breed club sites) |
| rvb-foknormen | houdenvanhonden.nl, foknormen news |
| hks-pravilnik | HKS Pravilnik o uzgoju i upisu pasa / Pravilnik o stručnom radu |
| fkc-db | kennelliitto.fi breeding database pages |
| fkc-strategy | FKC General Breeding Strategy and JTO template |
| skk-hd-2020 | Swedish experiences from 60 years of HD screening (2020) |
| eu-platform-guide | EU Platform on Animal Welfare, dog breeding guide |
| bannasch-2021 | Bannasch et al. 2021, Canine Med Genet |
| chu-2019 | Chu et al. 2019, Mammalian Genome |
| lewis-2015 | Lewis et al. 2015, Canine Genet Epidemiol |
| haynes-1915 | Haynes 1915, J Heredity (via Institute of Canine Biology) |
| calboli-2008 | Calboli et al. 2008, Genetics |
| kc-demography-2025 | KC demography study 2025, Canine Med Genet |
| donner-2023 | Donner et al. 2023, PLoS Genetics, Dryad data |
| borge-2011 | Borge et al. 2011, Theriogenology |
| tonnessen-2012 | Tønnessen et al., canine perinatal mortality (NKK cohort) |
| wright-1922 | Wright 1922, Am Nat |
| meuwissen-luo-1992 | Meuwissen and Luo 1992, Genet Sel Evol |
| colleau-2002 | Colleau 2002, Genet Sel Evol |
| sargolzaei-2005 | Sargolzaei, Iwaisaki, Colleau 2005, J Anim Breed Genet |
| ballou-2001 | Ballou, Earnhardt, Thompson 2001 (MSI) |
| lacy-2012 | Lacy 2012, PMx |
| gutierrez-2008 | Gutiérrez et al. 2008/2009, individual increase in inbreeding |
| lacy-1989 | Lacy 1989, founder equivalents |
| lacy-1995 | Lacy 1995 / Ballou and Lacy 1995, founder genome equivalents |
| meuwissen-1997 | Meuwissen 1997, optimum contribution selection |
| optisel | optiSel on CRAN, v2.1.0 |
| alphasimr | AlphaSimR on CRAN, v2.1.0 |

Full URLs are in the original research report (`docs/research_report_full.md` if Tea adds it).
