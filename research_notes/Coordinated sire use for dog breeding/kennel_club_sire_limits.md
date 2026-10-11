# Kennel-club and breed-club limits on sire use (popular sire effect), and the evidence behind them

Research date: 2026-10-11. "Verified (primary)" means I read the primary document's text myself. "Via search summary" means the figure came from a search-engine digest of the primary document, which I did not open. Treat those as needing a re-check before they are hard-coded.

## 1. FCI International Breeding Strategies (5% rule, 50% rule)

### Takeaway
The FCI recommends, without binding force, that no dog have more offspring than 5% of the puppies registered in the breed over a five-year period. It also says a breeding programme should not exclude more than 50% of the breed. The Breeding Commission approved the text on 23 May 2009, and the General Committee approved it in Madrid in February 2010.

### Cited Findings
- Exact wording of point 3 (verified, primary): "To preserve, or preferably extend, the genetic diversity of the breed, matador breeding and heavy inbreeding should be avoided. Mating between siblings, mother to son or father to daughter should never be performed. As a general recommendation no dog should have more offspring than equivalent to 5% of the number of puppies registered in the breed population during a five-year period. The size of the breed population should be looked upon not only on national but also on international level, especially in breeds with few individuals." — [FCI International Breeding Strategies (PDF)](https://www.fci.be/medias/ELE-STR-en-941.pdf)
- Point 8 (verified): "As a general rule, a breeding programme should not exclude more than 50% of the breed; the breeding stock should be selected from the best half of the breed population." — [FCI](https://www.fci.be/medias/ELE-STR-en-941.pdf)
- Point 4.1 (verified): "As a general rule the estimated breeding value for a combination should be better than the average for the breed." — [FCI](https://www.fci.be/medias/ELE-STR-en-941.pdf)
- Introduction (verified): "Education of breeders is to be recommended rather than strict breeding regulations and stringent demands in breeding programmes, which can easily result in reduced genetic diversity…" The document is therefore advisory by design. — [FCI](https://www.fci.be/medias/ELE-STR-en-941.pdf)
- Dates (verified): "These strategies were approved by the FCI Breeding Commission in Naples, May 23rd 2009. The document was approved by the FCI General Committee in Madrid, February 2010." The PDF is labelled "2010 cir 29 Breeding Strategies-annex" (FCI circular 29/2010). Leroy & Rognon 2012 cite it at the old URL http://www.fci.be/uploaded_files/29-2010-annex-en.pdf. — [FCI](https://www.fci.be/medias/ELE-STR-en-941.pdf)
- A 2025 Canine Genetics and Epidemiology article notes that, although the FCI has 98 member countries, enforcement of the recommendation is uncommon and no evidence exists on how well it has been integrated into practice (via search summary). — [s40575-025-00142-1](https://link.springer.com/10.1186/s40575-025-00142-1)

### Inferences
- A simulator can implement the rule as: cap per dog = 0.05 × (sum of puppies registered in the breed over the last five years). FCI wording says "no dog", so it applies to both sexes. In practice it bites on males.
- The cap scales with population size, so it binds only in small breeds. For large breeds it is essentially non-binding (see Leroy & Rognon below: 1,366 puppies for the Epagneul Breton).

### Gaps
- I found no FCI document later than 2010 that revises the 5% figure. The FCI International Breeding Rules may contain related text, but I did not check them.

## 2. Finnish Kennel Club (Kennelliitto): PEVISA offspring caps (binding)

### Takeaway
In Finland, offspring limits are binding registration conditions. Under a breed's PEVISA programme, a litter is not registered if a parent has already exceeded the breed's maximum number of registered offspring. The caps are lifetime numbers set breed by breed, and the 2026 programmes range from 15 to 120 offspring.

### Cited Findings
- Definition (verified, 2026 PEVISA document): "Jälkeläismäärä tarkoittaa koiralle rekisteröitävien jälkeläisten enimmäismäärää. Viimeinen, rajan ylittävä pentue rekisteröidään kuitenkin kokonaisuudessaan. Lisäksi voidaan ilmoittaa, jos ehto koskee vain toista sukupuolta tai jos enimmäismäärä on porrastettu koiran iän perusteella." In English: the offspring number is the maximum number of offspring registered to a dog, but the last litter that crosses the limit is registered in full. A cap may apply to one sex only, or be graded by the dog's age. — [Kennelliitto, PEVISA-ohjelmat ja rotukohtaiset erityisehdot 2026](https://kennelliitto.fi/pevisa-ja-rotukohtaiset-erityisehdot)
- Retroactive counting (verified): "Jälkeläisten määrää rajoittavassa ehdossa huomioidaan kuitenkin myös ennen ehdon voimaantuloa rekisteröidyt pentueet." Litters registered before a condition came into force still count toward the cap. — [same](https://kennelliitto.fi/pevisa-ja-rotukohtaiset-erityisehdot)
- PEVISA guidance (via search summary): breeding bans on population-genetic grounds mean a litter is not registered if either parent has produced more offspring than the breed programme allows. — [PEVISA-ohje](https://www.kennelliitto.fi/sites/default/files/media/pevisa-ohje_0_0_0_0_0_0.pdf)
- Foreign males (verified): standing exemptions typically allow registration of "narttu 1, uros 2 pentuetta" (bitch 1 litter, male 2 litters) without PEVISA test results. At least one breed (Barbet) states explicitly that the offspring cap also applies to foreign dogs. — [same](https://kennelliitto.fi/pevisa-ja-rotukohtaiset-erityisehdot)
- Offspring caps in the 2026 document (verified from the table's "Jälkeläismäärä" column; programme end dates in brackets). Lifetime registered offspring per dog, both sexes unless stated:
  - Abruzzese maremmano (Maremma Sheepdog): 20 (31.12.2029)
  - Amerikankettukoira (American Foxhound): 45 (2026)
  - Bernhardinkoirat (St Bernards): 30 (2029)
  - Berninpaimenkoira (Bernese Mountain Dog): 60 (2026)
  - Bourbonnaisinseisoja (Braque du Bourbonnais): 21 (2028)
  - Bretoni (Brittany): 36 (2026)
  - Broholminkoira (Broholmer): 25 (2028)
  - Chow chow: 50 (2028). Table position suggests Chow chow; check.
  - Cockerspanieli (English Cocker Spaniel): 90 (2030)
  - Estrelanvuoristokoirat (Estrela Mountain Dogs): 25 (2030)
  - Havannankoira (Havanese): "25 kun ♂ alle 4-v." (25 while the male is under four years old; an age-graded cap) (2028)
  - Keskiaasiankoira (Central Asian Shepherd): "30 pentua ja 4 pentuetta" (30 puppies and 4 litters) (2027)
  - Lagotto romagnolo: 34 (2027)
  - Lancashirenkarjakoira (Lancashire Heeler): 20 (2029)
  - Lyhytkarvainen saksanseisoja (German Shorthaired Pointer): 55 (2026)
  - Lyhytkarvainen unkarinvizsla (Hungarian Vizsla, short-haired): 21 (2026)
  - Plottinajokoira (Plott Hound): 45 (2029)
  - Pointteri (Pointer): 20 (2030)
  - Punainen irlanninsetteri (Irish Red Setter): 40 (2028)
  - Pyreneittenmastiffi (Pyrenean Mastiff): 20 (2026)
  - Rottweiler: 60 (2026)
  - Stabijhoun: 21 (2026)
  - Suomenajokoira (Finnish Hound): 120 (2029)
  - Valkoinenpaimenkoira (White Swiss Shepherd): 45 (2030). Breed name inferred from position.
  - Venäjänajokoira (Russian Hound): 25 (2030), with litter inbreeding capped at 6.25% (5 generations)
  - Volpino italiano: 15 (2027)
  - Two further entries could not be matched to a breed because of PDF page breaks: one with a cap of 30 that also requires litter inbreeding of at most 6.25% over seven generations and a minimum age of 24 months (2029), and one with a cap of 40 and a 6.25% inbreeding limit (2026). The second is the breed listed just before Suursnautseri.
  - All from — [Kennelliitto PEVISA 2026](https://kennelliitto.fi/pevisa-ja-rotukohtaiset-erityisehdot)
- Several Finnish programmes pair the offspring cap with a binding litter inbreeding cap ("Pentueen sukusiitosaste max 6,25 %", computed over 5 or 7 generations). — [same](https://kennelliitto.fi/pevisa-ja-rotukohtaiset-erityisehdot)
- DogWellNet's account of Finnish practice (Leroy 2015): limits on litters per reproducer "is applied in Finland" through the national PEVISA programmes. — [Leroy, DogWellNet blog](https://dogwellnet.com/blogs/entry/33-limiting-popular-sire-phenomenon/)

### Inferences
- These Finnish caps are the best real-world parameter set for a simulator. They are absolute lifetime counts of registered offspring, mostly 20–60, with 90–120 for numerically large breeds. One variant is graded by age (Havanese, 25 before age 4), and another has a dual puppy-and-litter cap (Central Asian Shepherd, 30 pups and 4 litters). They are enforced at registration, and the litter that crosses the cap is still registered.
- Rough estimate: a cap of 20–60 offspring is about 4–12 litters at 5 pups per litter.

### Gaps
- Most breed JTOs (jalostuksen tavoiteohjelma) give the cap's rationale as a share of a generation's registrations (often a "1/2 × 5%"-type logic). I did not open any individual JTO to confirm the derivation.
- I could not confirm Mäki's 2010 sire-use statistics (see section 7).

## 3. Sweden (SKK), Norway (NKK), Denmark (DKK)

### Takeaway
NKK's breeding strategy carries the 5% per five-year recommendation, tightened to 2% for numerically large breeds and applied to both sexes. It is advisory, though NKK has allowed breed clubs to apply for hard registration caps (for example, the Gordon Setter at 100). For SKK I found only general "avoid overuse" policy language plus breed-club RAS recommendations. I found no national numeric sire cap.

### Cited Findings
- NKK (via a secondary guidance document): "NKKs anbefaling er at en hund ikke bør ha flere avkom enn tilsvarende 5 % av antall registrerte hunder i rasepopulasjonen i en 5 års-periode." For numerically large breeds, no dog should have more offspring than about 2%. The "5/2 % anbefalingen gjelder både for tisper og hannhunder" (applies to bitches and males alike). The method is to sum registered puppies over the last five years and take 5% or 2%. For small breeds, consider including the population in partner countries such as the Nordic region. — [NEKF RAS-veileder 2025 (Norske Elghundklubbers Forbund)](https://elghundforbundet.no/wp-content/uploads/2025/09/NEKFs-RAS-veileder.pdf)
- NKK (2013, via search summary): Norsk Gordonsetter Klub cited the 5% rule, adopted a cap of 100 registered puppies per male, and NKK's board (HS) decided on 5 September 2013 to let breed clubs apply for such maximum limits. This is an old source and current status is unverified. — [NKK Sunnhetsutvalget årsrapport 2013](https://nkk2023.stage22.coretrek.no/getfile.php/13320876-1700141852/Dokumenter/Om%20NKK/Organisasjonen/Sunnhetsutvalget/Sunnhetsutvalget%20DIV/2013%20SU%20%C3%85rsrapport.pdf)
- NKK's Sunnhetsutvalg issued a statement on point 4.2 of NKK's avlsstrategi. I did not read its content. — [NKK SU statement](https://www.nkk.no/getfile.php/132967322-1712214419/Dokumenter/Om%20NKK/Organisasjonen/Sunnhetsutvalget/Sunnhetsutvalget%20DIV/Uttalelse%20fra%20Sunnhetsutvalget%20ang%C3%A5ende%20NKKs%20avlsstrategi%20punkt%204.2.pdf)
- SKK (via search summary): the RAS system was adopted by Kennelfullmäktige in 2001, and each RAS is revised every five years. SKK's avelspolicy says breeders should avoid overuse of individual dogs or groups of closely related dogs. SKK's binding basic rules limit a bitch to five litters, require a vet check before mating a bitch over seven, and ban mating a bitch over ten. These limits apply to bitches, not males. — [SKK registreringsregler R42 2025](https://www.skk.se/globalassets/globala-filer/regler/registreringsregler-r42-2025.pdf)
- SKK breed example, Finnish Lapphund (Suomenlapinkoira) RAS recommendation (via search summary): a male should sire at most 25 puppies before age five, so his progeny can be evaluated, and at most 50 puppies in his lifetime. This is advisory. — [SRFL RAS evaluation 2023](https://finsklapphund.nu/wp-content/uploads/2024/02/Utvardering-RAS-SRFL-Avelskommitte-2023-1.pdf)

### Inferences
- The Nordic convention is 5% of five-year registrations, or 2% for large breeds, applied to both sexes. Clubs often convert it into age-graded absolute caps (for example, 25 before age 5 and 50 lifetime).

### Gaps
- I could not read SKK's avelspolicy text verbatim (the PDF fetch failed), so whether SKK itself states the 5% figure is unverified.
- I did not find the current primary NKK avlsstrategi text.
- I found nothing on the Danish Kennel Club (DKK). It is not covered.

## 4. Netherlands: Raad van Beheer framework and breed-club VFR caps

### Takeaway
The Raad van Beheer's model breed-club breeding regulation (VFR, March 2025 format) makes a maximum number of matings per male an optional clause for each breed club. It does not set a national stud cap. Breed clubs that adopt one set binding lifetime caps that range from 3 matings (Hovawart) to 40–80 (Golden Retriever).

### Cited Findings
- Guide to the VFR format (verified, primary; March 2025): "2.5 de rasvereniging kan hier kiezen om een maximaal aantal dekking voor een reu in te voeren. (keuze)" (the breed club may choose to set a maximum number of matings for a male; optional). It adds that a maximum for matings abroad is possible, but "de controleerbaarheid hiervan is echter laag" (hard to verify). The same guide states: "2.2 dezelfde combinatie is maximaal vijf keer toegestaan (keuze om minder dan vijf in te vullen)" (the same pairing is allowed at most five times). — [Houden van Honden, Leeswijzer VFR maart 2025](https://www.houdenvanhonden.nl/globalassets/regelgeving/format-vfr/leeswijzer-vfr-maart-2025.pdf)
- Golden Retriever Club Nederland (GRCN), VFR version approved 11 December 2025 (via search summary): at most 12 successful matings in the Netherlands per calendar year, and at most 80 successful matings in the male's lifetime. A later GRCN version (approved 11 April 2026, effective 1 August 2026) sets the lifetime total at 40. A "successful mating" is one that produces at least one live pup registered in the NHSB, and AI counts the same as a natural mating. — [GRCN VFR Dec 2025](https://www.goldenretrieverclub.nl/images/GRCN_VFR_DEF_versie_-_goedgekeurd_11122025_ingediend_20260129_PDF.pdf); [GRCN VFR v2 Aug 2026](https://www.goldenretrieverclub.nl/images/GRCN_VFR_DEF_versie_2_-_goedgekeurd_11042026_ingediend_23062026_pdf_1_augustus2026.pdf)
- Hovawart Club Nederland (Feb 2026, via search summary): at most 1 successful mating per calendar year and at most 3 in the male's lifetime in the Netherlands. — [HCN VFR 2026](https://hovawartclub-site.e-captain.nl/bestanden/hcn-verenigings-fok-reglement-versie-1-feb-2026.pdf)
- Hollandse Smoushond club (version 2025-09-08, via search summary): at most 3 successful matings per calendar year and at most 4 lifetime in the Netherlands, OR at most 15 live pups. — [VFR HSC](https://smoushond.nl/cddata/0171/files/1770106918_VFR_HSC_20120121_versie20250908_OUD_NIEUW.pdf)
- Dutch simulation of the Golden Retriever (Windig & Oldenbroek 2015, J Anim Breed Genet, DOI 10.1111/jbg.12149): the population had about 600 dams and 150 sires producing 300 litters a year, and the five most popular sires sired about 25% of each year's litters. Caps on litters per sire generally shortened the generation interval, because sires were replaced sooner, and "in some instances, this lead to an increase in inbreeding rates because the next generations were more related." The most effective measure was restricting breeding to animals with low average relatedness to the population, which cut ΔF per generation from 0.41% to 0.12%. Minimising parental co-ancestry was not effective in the long run. — [AGRIS record](https://agris.fao.org/search/en/records/65df97e57c7033e84bee5b68); [DogWellNet summary](https://dogwellnet.com/content/research/peer-reviewed-research/genetic-management-of-dutch-golden-retriever-dogs-with-a-simulation-tool-r271/)
- Leroy's reading of the same study: "the best strategies were related to the limitation of the use of popular sire", and it "was more efficient to consider a fixed number of litters per year than per reproductive life". — [Leroy, DogWellNet blog 2015](https://dogwellnet.com/blogs/entry/33-limiting-popular-sire-phenomenon/)

### Inferences
- The GRCN reduction from 80 to 40 lifetime matings within one year suggests Dutch clubs are tightening caps. The annual cap (12 per year) together with a lifetime cap matches Windig & Oldenbroek's finding that per-year caps work better than lifetime caps alone.

### Gaps
- I found no Raad van Beheer KR clause setting a general national stud cap. The task's suggested figure of "25 matings" was not confirmed for any national rule.
- I did not verify the 2023+ "foknormen" (Dutch breeding norms) content on sire use.
- I did not find a "Windig & Doekes 2018" paper on sire limits. The closest Dutch evidence is Windig & Oldenbroek 2015, plus a 2023 WUR MSc report on the Bouvier des Flandres (Kuijpers, supervised by Windig) whose conclusions I did not see: [WUR](https://wur.nl/en/show/talita-kuijpers-breed-analysis-of-the-dutch-bouvier-des-flandres-population-final-report.htm).

## 5. UK Kennel Club, German VDH, Croatian HKS, American Kennel Club

### Takeaway
None of these organisations has a national numeric cap on sire use that I could verify. The UK Kennel Club caps bitches at four litters, and the AKC only requires DNA profiling of frequently used sires. In Germany, caps are set by individual breed clubs.

### Cited Findings
- UK Kennel Club (via search summary): from 1 January 2012 the KC stopped registering more than four litters from one bitch in her lifetime, while the legal limit was six. A 2011 Parliament petition asked for limits on stud use, but this did not become policy. — [MRCVS](https://www.mrcvs.co.uk/en/news-story.php?id=6344); [Petition 56733](https://petition.parliament.uk/archived/petitions/56733)
- AKC (via search summary of the AKC page): a sire must have an AKC DNA Profile once he has produced 7 or more litters in his lifetime, or more than 3 litters in a calendar year, for litters whelped on or after 1 July 2000. This is a parentage and identity requirement, not a limit. — [AKC Frequently Used Sires Requirement](https://www.akc.org/breeder-programs/dna/dna-resource-center/frequently-used-sires-requirement/)
- Germany: the VDH Zuchtordnung is a framework, and breed clubs set the caps. Example (via search summary): Verein Deutsch-Wachtelhund (2018 rules) allows at most three breeding tags (Deckscheine) per stud per year, with tags 1 and 4 at least 365 days apart. Before tags 6–9 are issued, ten of the stud's offspring must be X-rayed and evaluated. — [VDW Zuchtbestimmungen](https://wachtelhund.de/wp-content/uploads/2024/04/ZuchtbestimmungenaktuellHV2018.pdf)

### Inferences
- The English-speaking registries rely on information tools (published sire statistics and coefficient-of-inbreeding (COI) calculators) rather than hard sire caps.

### Gaps
- I did not verify KC Mate Select or Breed Watch wording on popular sires, nor any current KC stud-dog guidance.
- I found nothing on HKS (Croatia). Not covered.
- I did not retrieve DRC (German Retriever Club) stud limits; the ZO PDF returned 404.

## 6. Evidence: Leroy & Rognon 2012 (simulated sire caps under the FCI rule)

### Takeaway
In four French breeds, the FCI 5% threshold would not bind in three of them, because no reproducer exceeded it, and was impractical in the fourth. Breed-specific absolute caps of 50–100 offspring cut kinship by roughly 10–15%. A very tight cap (25) raised kinship in one small breed, because the dogs being removed were the least related ones.

### Cited Findings
All verified from the primary text: Leroy G., Rognon X. (2012) "Assessing the impact of breeding strategies on inherited disorders and genetic diversity in dogs", The Veterinary Journal 194: 343–348. DOI: [10.1016/j.tvjl.2012.06.025](https://doi.org/10.1016/j.tvjl.2012.06.025). PDF: [VIN copy](https://www.vin.com/Proceedings/Downloads/TuftsBG2013/90649_BreedStrategies_A6_Leroy_TuftsBG2013.pdf)
- Design: once a reproducer exceeded the cap, it could not reproduce again. Caps tested were 50, 100 and 200 offspring for all breeds, plus 25 for the Braque Saint Germain (BSG) and Berger des Pyrénées (BRP). Reproducers were replaced at random.
- Table 1, with the FCI threshold equal to 5% of dogs produced in 2006–2010:

  | Breed | Dogs, 2006–2010 | FCI threshold | Mean offspring/sire (max) | Mean offspring/dam (max) | Generation interval | F | Mean kinship |
  |---|---|---|---|---|---|---|---|
  | Braque Saint Germain | 283 | 14 | 14.8 (62) | 7.6 (30) | 4.69 | 0.073 | 0.103 |
  | Berger des Pyrénées | 3,630 | 182 | 13.2 (82) | 7.4 (40) | 4.77 | 0.091 | 0.054 |
  | Coton de Tulear | 10,784 | 539 | 27.4 (233) | 9.8 (39) | 4.37 | 0.061 | 0.039 |
  | Epagneul Breton | 27,325 | 1,366 | 18.6 (297) | 9.6 (54) | 4.88 | 0.056 | 0.036 |

- Cap of 200: affected few matings. Kinship changed by −6% in Coton de Tulear and −4% in Epagneul Breton, with no change in BSG or BRP.
- Cap of 50: sires were replaced for 77% of Coton de Tulear individuals, and kinship fell from 0.038 to 0.032 (−15%). For BRP, 19% of sires were replaced and kinship fell from 0.061 to 0.055 (−10%). In BRP, "a threshold of 50 would allow kinship rate to decrease from 0.5% to 0.2%" per generation.
- Cap of 25 in BSG: "unexpected increase of U from 0.135 to 0.149 in 2010 (+10%)", because "the two sires used the most in 2010 show a low level of kinship with the current population".
- Recommendations: Coton de Tulear, a threshold of about 100 (36% of matings affected through the sire pathway, kinship −10%). Epagneul Breton, 100 (23% of sires changed, kinship −12%). BSG: caps will not help; instead increase the number of reproducers, minimise kinship, or outcross.
- On the FCI rule: "the FCI recommendations… are not applicable for the BRP, COT and EPB… since the maximum number of puppies produced by all reproducers in the period from 2006 to 2010 was less than the recommended threshold… the FCI recommendation would be difficult to implement for the BSG breed, since sires currently produce more offspring on average than the recommended threshold."
- Benchmark cited: acceptable inbreeding or kinship rate per generation should not exceed 0.5–1% (Bijma 2000).

### Inferences
- For the simulator, a sire cap should be paired with relatedness-aware replacement. Random or naive replacement under a tight cap can raise kinship when the capped sires are the population's outcross sires.

### Gaps
- None for this paper. The key figures were read from the primary text.

## 7. Other evidence on popular sires (Leroy & Baumung 2011, Calboli 2008, Lewis 2015, Mäki, Oliehoek & Bijma)

### Takeaway
Popular-sire use is pervasive and is the main driver of inbreeding rates in UK breeds. Simulations show it spreads recessive disorders about 4.4 times more than random mating.

### Cited Findings
- Leroy & Baumung 2011, Animal Genetics 42(1): 66–74, "Mating practices and the dissemination of genetic disorders in domestic animals, based on the example of dog breeding" (via search summary of the abstract). In ten French breeds, the effective number of sires was 33–70% of the actual number of sires. The risk of disseminating a recessive disorder under popular-sire use was 4.4 times that under random mating. Line breeding and close breeding tended to decrease dissemination risk. Between about 1% and 8% of dogs were inbred after two generations. — [AGRIS](https://agris.fao.org/search/fr/records/652f9eecd5e38ff7731f7902); [Purdue summary](https://caninewelfare.centers.purdue.edu/?p=2210)
- Lewis, Abhayaratne & Blott 2015, Canine Genet Epidemiol 2:13, DOI [10.1186/s40575-015-0027-4](https://doi.org/10.1186/s40575-015-0027-4), covering all 215 KC breeds from 1980 to 2014 (verified from PMC):
  - "Popular sires" were present in all breeds with sufficient data. The authors measured the percentage of registrations from the top 50/25/10/5% of sires, but the main text gives no per-breed percentages.
  - Mean ΔF across breeds in 1980–1999 far exceeded the recommended maximum of 0.01 per generation, and has declined since 2000.
  - Of 116 breeds with an estimable Ne, Ne ranged from 23.8 (Manchester Terrier) to 918.8 (Borzoi); 68 breeds had Ne below 100 and 29 below 50. Ne was not correlated with census size (English Springer Spaniel: about 10,886 registrations a year, Ne 45).
  - The authors write that "breeders should guard against the over-use of sires", and that replacing a popular sire with a close male relative has limited effect. — [PMC4579366](https://pmc.ncbi.nlm.nih.gov/articles/PMC4579366/)
- Calboli et al. 2008, Genetics 179: 593–601, DOI [10.1534/genetics.107.084954](https://doi.org/10.1534/genetics.107.084954) (abstract via search summary). Ten UK KC breeds; inbreeding Ne was 40–80 in all but two breeds; more than 90% of unique genetic variants were lost over six generations in all but three breeds. — [Purdue summary](https://caninewelfare.centers.purdue.edu/resource/population-structure-and-inbreeding-from-pedigree-analysis-of-purebred-dogs)
  - Unverified secondary figures (Wikipedia, citing Calboli): 5% of Labrador males and 10% of Golden Retriever males each sired more than 100 offspring, and one English Springer Spaniel sired 2,538. — [Wikipedia: Popular sire effect](https://en.wikipedia.org/wiki/Popular_sire_effect)
- Leroy's 2015 DogWellNet blog worked example (FCI threshold vs. reality): for the Braque Saint Germain, the FCI threshold of 14 puppies equals about 2–3 litters. — [DogWellNet](https://dogwellnet.com/blogs/entry/33-limiting-popular-sire-phenomenon/)
- Mäki et al. (Animal Science, Cambridge; the record shows a 2016 online date, so the year may not be 2010) studied 289,569 dogs in six Finnish breeds. Observed mean F exceeded expected F in every breed, so breeders did not actively avoid inbreeding. Inbreeding trends fell from the early 1980s in Golden Retriever, Labrador, Rough Collie and Rottweiler, but not in the Finnish Hound and German Shepherd (via search summary). — [Cambridge](https://www.cambridge.org/core/journals/animal-science/article/abs/population-structure-inbreeding-trend-and-their-association-with-hip-and-elbow-dysplasia-in-dogs/88F322D78BC2C06A2460BE62AE1D6DEB)

### Inferences
- Plausible simulator defaults from the literature:
  - the top five sires produce about 25% of litters in a medium-sized breed (Dutch Golden Retriever);
  - the effective number of sires is 33–70% of the actual number of sires;
  - the maximum offspring per sire is 5–10 times the mean (Table 1 of Leroy & Rognon).

### Gaps
- I did not retrieve Oliehoek & Bijma (optimal contribution and mean-kinship work, e.g. Oliehoek et al. 2009). They are not covered here.
- I did not retrieve Mäki 2010 sire-offspring statistics.
- I found no Windig & Doekes 2018 paper on sire limits.

## 8. How effective are sire limits in practice?

### Takeaway
No ex-post evaluation of real-world sire caps was found. The evidence is entirely simulation-based, and it is conditional: moderate caps (about 50–100 offspring, or per-year litter caps) reduce kinship by about 10–15%. Fixed-percentage rules like FCI's 5% rarely bind, and tight caps can backfire without relatedness-aware replacement. Selecting on low mean kinship to the population is more effective.

### Cited Findings
- The 2025 CGE paper notes no evidence exists on how well the FCI recommendation has been integrated into practice. — [s40575-025-00142-1](https://link.springer.com/10.1186/s40575-025-00142-1)
- The ΔF decline in UK breeds after 2000 is attributed partly to more imports after the 2000 Pet Passport relaxation, not to sire caps (the KC has none). — [Lewis et al. 2015](https://pmc.ncbi.nlm.nih.gov/articles/PMC4579366/)
- Simulation results: Leroy & Rognon 2012 (section 6) and Windig & Oldenbroek 2015 (section 4).

### Inferences
- The Finnish PEVISA caps (in force with programme end dates through 2030) are the natural real-world experiment. A before-and-after Ne/ΔF analysis in Finnish breeds would be the evaluation to look for. None was found.

### Gaps
- No published evaluation of Finnish, Dutch or Nordic sire caps on realised ΔF was found within this search budget.
