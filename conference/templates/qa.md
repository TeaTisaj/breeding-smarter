# Q&A preparation

Short answers backed by our files. Numbers from `conference/numbers.json`.

**1. Why synthetic data? Isn't that circular?**
No open dog registry with pedigree, health and DNA data exists, so methods cannot be compared openly. Synthetic data lets us publish everything and, crucially, keep a ground truth no registry has. It is not circular because the simulator and the recommender are separate: the simulator was calibrated to published statistics before any experiment, and the experiments measure truth (realised inbreeding) that the recommender never sees. (Files: `plan/gates/P5_report.md`, `docs/datasheet.md`.)

**2. How do you know the simulated population is realistic?**
{val_n_targets} calibration targets from published studies (litter sizes, sire concentration, Ne per breed size, inbreeding trends, HD trends): {val_pass} of {val_n_checks} checks pass, {val_warn} warn, {val_fail} fail; hard targets all pass, also across four seeds. Every parameter is cited or marked as an assumption. (`reports/validation/`, `docs/assumptions.md`.)

**3. How is this different from Mate Select or KoiraNet?**
They are lookup tools: COI of a dog or a hypothetical mating. We rank all candidate sires, combine population diversity (mean kinship), DNA-based risk, breeding values, sire use and rules in one explained score, and show which ancestors cause the predicted COI.

**4. Pedigree COI vs genomic COI (Embark, Wisdom Panel)?**
Genomic COI measures realised inbreeding and is better for individuals. Pedigree COI is free and available for every dog, but underestimates inbreeding when pedigrees are short: in our small breed, recorded {recorded_f_2025_S} vs true {true_f_2025_S}. The engine is designed to accept a genomic kinship matrix later.

**5. Who sets the score weights?**
The breed club. Weights are breeding priorities, not science; the app shows sliders and says so. Our defaults are documented assumptions.

**6. What about the EU regulation's application dates and the local-breed derogation?**
Close-relative bans are encoded as HARD rules with the local-breed derogation as a switch. Application dates and some details (minimum dam age, litter limits) come from press reports and are marked unverified until we check the Official Journal text (`docs/rules_verification.md`).

**7. Does excluding carriers help or hurt?**
Excluding all carriers lowers a tested disease faster but removes breeding animals, which costs diversity and can raise untestable variants. Our score penalises carrier x carrier pairs instead. In the medium breed the recommender cut affected puppies at MDR1 from {e1_mdr1_M_S1} to {e1_mdr1_M_S3}; the untestable variant stayed at {e1_novelx_range} affected under every strategy. A dedicated ablation (E3) follows.

**8. How do you handle imports with short pedigrees?**
We show an EqG depth component and a warning ("recorded inbreeding is probably underestimated"). Our data shows imports and foreign AI sires look unrelated on paper; that is the main reason recorded COI underestimates truth.

**9. Data privacy and ownership for kennel clubs?**
The code is open and can run on the club's own servers; nothing has to leave the club. A future service would be multi-tenant with each club owning its data.

**10. Does it work for horses or cats?**
Everything species-specific (gestation, ages, litter sizes, rules) is in configuration files, so the engine is species-agnostic. Horses and cats need validated profiles from partners; that is post-conference work.

**11. What would a pilot with a kennel club look like, and what does it cost?**
Free for the first partners: we import one breed's pedigree, health and DNA data, deliver a diversity report and a compliance check, and run the recommender with the breed club's own weights. Two to three months.

**12. What are the biggest limitations?**
Synthetic data; pedigree-based kinship; a linear model on HD grades; illustrative disease allele frequencies; policy weights; unverified rule details; and our own finding that per-dam ranking alone does not protect long-term diversity.

**13. Why HD as a linear model on grades?**
It is the common practical approach (the score A=1 to E=5); threshold models are more accurate. Our BLUP still beats the phenotype in tests; correlation with true breeding values is reported in the validation.

**14. How fast is it on a national registry?**
Inbreeding for 250,000 dogs in {bench_inbreeding_250k_s} s; one pair's predicted COI in {bench_pair_ms} ms; a full ranking with explanations in well under a second.

**15. What is next (thesis, startup, partners)?**
Real-data pilots with breed clubs, genomic kinship import, genomic kinship for the club planner (planning on true kinship raised Ne further in our model), and a production backend.

**16. Your own results say random mating keeps more diversity. Why use the tool?**
Random mating spreads use over many sires, which is exactly what protects Ne ({e1_ne_S_S0} vs {e1_ne_S_S1} under today's market in the small breed). Breeders will not mate randomly. With club quotas the tool comes close in the small breed (Ne {p12_ne_S_cc_ocs_mc1} vs {p12_ne_S_s0} random) while keeping rule compliance, disease and hip improvement; in the medium breed random mating is still clearly ahead ({p12_ne_M_s0} vs {p12_ne_M_cc_ocs_mc1}).

**17. So does coordination fix it?**
In our model, yes against today's market and against the recommender alone. We fixed the success criteria before running: coordinated planning raised Ne over the market in both breeds (small {p12_h1_S_est}, 95% interval {p12_h1_S_ci}; medium {p12_h1_M_est}, {p12_h1_M_ci}) and lowered the long-term rate of inbreeding compared with the recommender alone. Two pre-registered expectations failed: mating method mattered as much as contribution control (minimum-kinship mating without quotas was the worst strategy), and in the medium breed planning on true kinship did not reach random mating. All in silico.

**18. Would clubs accept quotas?**
Untested, and we say so. Clubs already cap sires (Finland: 15 to 120 offspring per male; the Dutch Golden Retriever club: 12 matings a year), and the FCI recommends 5% of five-year registrations. Our quotas are softer than a fixed cap: breeders still choose among sires with quota left, and with half of the breeders taking part most of the gain remained in our simulation.

**17. Is the simulator's breeding market realistic?**
It reproduces popular-sire concentration (top 20% of sires produce {top20_S} of puppies in the small breed) and the Ne bands of published breeds; behaviour parameters were tuned and are listed as assumptions.
