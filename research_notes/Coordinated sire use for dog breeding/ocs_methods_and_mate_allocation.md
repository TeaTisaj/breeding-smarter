# Optimum Contribution Selection (OCS) and Mate Allocation: Methods for a Coordinated Dog-Breeding Strategy

Verification note: "VERIFIED" means the claim was read in a primary source or the bibliographic data was confirmed via the Crossref API during this session. Items marked "[UNVERIFIED: from background knowledge]" are standard in the literature but were not confirmed in a fetched primary text in this session. Springer/BMC (link.springer.com), gse-journal.org and the PMC article pages for Pong-Wong & Woolliams 2007 and AlphaMate blocked full-text retrieval. So the exact equations of those papers were not read directly. The main full texts read were Wellmann 2019 (optiSel, PMC) and Du, Bernstein & Hoppe 2025 (arXiv; a recent, rigorous re-derivation of Meuwissen's OCS).

Bibliographic data (title/authors/journal/volume/pages/year) confirmed via Crossref API for these DOIs:
- Meuwissen 1997, "Maximizing the response of selection with a predefined rate of inbreeding", J Anim Sci 75:934–940 — https://doi.org/10.2527/1997.754934x
- Meuwissen & Sonesson 1998, "... predefined rate of inbreeding: overlapping generations", J Anim Sci 76:2575–2583 — https://doi.org/10.2527/1998.76102575x
- Grundy, Villanueva & Woolliams 1998, "Dynamic selection procedures for constrained inbreeding and their consequences for pedigree development", Genetical Research — https://doi.org/10.1017/s0016672398003474
- Grundy, Villanueva & Woolliams 2000, "Dynamic selection for maximizing response with constrained inbreeding in schemes with overlapping generations", Animal Science — https://doi.org/10.1017/s1357729800051717
- Woolliams, Berg, Dagnachew & Meuwissen 2015, "Genetic contributions and their optimization", J Anim Breed Genet 132:89–99 — https://doi.org/10.1111/jbg.12148 (full text NOT read)
- Pong-Wong & Woolliams 2007, Genet Sel Evol 39:3–25 (SDP) — https://doi.org/10.1186/1297-9686-39-1-3
- Sonesson & Meuwissen 2000, "Mating schemes for optimum contribution selection with constrained rates of inbreeding", GSE 32:231–248 — https://doi.org/10.1186/1297-9686-32-3-231
- Sonesson & Meuwissen 2002, "Non-random mating for selection with restricted rates of inbreeding and overlapping generations", GSE 34:23–39 — https://doi.org/10.1186/1297-9686-34-1-23
- Gorjanc & Hickey 2018, "AlphaMate ...", Bioinformatics 34:3408–3411 — https://doi.org/10.1093/bioinformatics/bty375
- Wellmann 2019, "Optimum contribution selection for animal breeding and conservation: the R package optiSel", BMC Bioinformatics 20:25 — https://doi.org/10.1186/s12859-018-2450-5
- Wellmann & Bennewitz 2019, "Key genetic parameters for population management", Front Genet 10:667 — https://doi.org/10.3389/fgene.2019.00667
- Henryon, Ostersen, Ask, Sørensen & Berg 2015, "Most of the long-term genetic gain from optimum-contribution selection can be realised with restrictions imposed during optimisation", GSE 47:21 — https://doi.org/10.1186/s12711-015-0107-7
- (Also found) Villanueva/Woolliams-group: "Optimal mass selection policies for schemes with overlapping generations and restricted inbreeding", GSE 32:339 (2000) — https://doi.org/10.1186/1297-9686-32-4-339

---

## Q1. Standard OCS formulation (objective, kinship constraint, sex constraints, bounds, kinship target from ΔF)

### Takeaway
Standard OCS picks a vector of contributions c (one entry per candidate, entries ≥ 0, summing to 1/2 within each sex) that maximises c'EBV subject to c'Ac/2 ≤ C_{t+1}. The target is C_{t+1} = C_t + ΔF(1 − C_t), where C_t is the current mean coancestry of the candidates and ΔF is the desired rate per generation (or per year divided by generation interval L for overlapping generations). The exact expected coancestry of offspring includes a small extra term that Meuwissen 1997 omitted. It matters most in very small populations.

### Cited Findings
- OCS (Meuwissen 1997) maximises genetic gain each generation under a restriction on the increase in inbreeding per generation. Du et al. describe it as "Meuwissen's fundamental idea was to maximize the genetic revenue in each generation under the restriction that the overall increase in inbreeding per generation is limited" — [Du, Bernstein & Hoppe 2025, arXiv:2504.12895](https://arxiv.org/abs/2504.12895); original [Meuwissen 1997](https://doi.org/10.2527/1997.754934x).
- An earlier description of Meuwissen's algorithm: it obtains "optimum selection decisions at a given (discrete) generation and level of inbreeding by maximising a function of accumulated gain corrected for squared contributions" — quoted in a Cambridge abstract of Grundy et al. ([Cambridge](https://resolve.cambridge.org/core/journals/proceedings-of-the-british-society-of-animal-science/article/maximising-response-with-a-predefined-rate-of-inbreeding-for-overlapping-generation-structure/8C8DE529336C81CF46598A6574160AE8)).
- Contribution definition in optiSel: c_i is the fraction of the next birth cohort's genes that come from individual i, so 2c_i is the fraction of offspring that have i as a parent — [Wellmann 2019](https://pmc.ncbi.nlm.nih.gov/articles/PMC6332575).
- The exact expected mean kinship of the next generation (Du et al., Lemma 2.2), with contributions c_I summing to 1 and N_{t+1} offspring, is k_{P_{t+1}} = Σ_{I,J} c_I c_J k_{IJ} + (1/(2N_{t+1})) Σ_I c_I (1 − k_{II}). Here k_{II} = 1/2 + f_I/2. This is equivalent to Meuwissen's term plus −(1/(4N_{t+1})) Σ c_I f_I + 1/(4N_{t+1}). Du et al. state: "The original derivation of OCS by Meuwissen (1997) apparently overlooks this summand", and the correct formula appears in Wellmann & Pfeiffer 2009 and Wellmann & Bennewitz 2019 — [Du et al. 2025](https://arxiv.org/abs/2504.12895).
- Wellmann & Bennewitz 2019 argue the extra term may be deliberately left out (or modified), because it favours selecting inbred individuals. Du et al. say the validity of this argument "appears unclear" — [Du et al. 2025](https://arxiv.org/abs/2504.12895), citing [Wellmann & Bennewitz 2019](https://doi.org/10.3389/fgene.2019.00667).
- optiSel writes expected mean kinship as a quadratic in c: f(c) = (r0·c + v)' F (r0·c + v) + l(c). Here r0 is the offspring's share of the population, v holds the population shares of existing individuals (overlapping generations), and l(c) is a linear correction — [Wellmann 2019](https://pmc.ncbi.nlm.nih.gov/articles/PMC6332575).
- Kinship target from a rate: Du et al.'s implementation sets the maximum allowed mean kinship as k*_{t+1} = k_t + (Δk/100)·(1 − k_t), where Δk is the percentage by which the panmictic index (1 − k) may fall. The default is 1% per generation, following the FAO (2013) recommendation that inbreeding rate should not exceed 1% per generation — [Du et al. 2025](https://arxiv.org/abs/2504.12895). This is the same form as C_{t+1} = C_t + ΔC(1 − C_t).
- optiSel guidance on the rate: Δf per generation ≤ 1/(2N_e), and per year Δf_y ≤ 1/(2·N_e·L), where L is the generation interval estimated from agecont(). The paper uses N_e ≥ 100 as its target and notes critical sizes of 50–100 — [Wellmann 2019](https://pmc.ncbi.nlm.nih.gov/articles/PMC6332575).
- Canonical matrix form [UNVERIFIED: from background knowledge; consistent with the above]: max_c c'û subject to (i) ½ c'Ac ≤ C_{t+1}, with A the numerator relationship matrix among candidates (so ½A is the coancestry/kinship matrix); (ii) Q'c = [½, ½]', where Q is an n×2 sex-incidence matrix; (iii) c ≥ 0, optionally with c_i ≤ u_i (e.g. a cap of n_max litters/(2N)). Meuwissen 1997 solved the Lagrangian of this problem in closed form and iteratively removed candidates with negative c.

### Inferences
- In a dog simulator using kinship K = A/2 directly, the constraint is c'Kc ≤ C_{t+1}. Using A means the factor ½ must appear exactly once. Mixing these conventions is a classic bug.
- With N_{t+1} of a few hundred puppies, the Du et al. correction term (order 1/(4N)) is ~0.001 or less. That is small but not negligible relative to a per-year ΔF of ~0.1–0.25%. Include it, or at least subtract it from the budget, when targeting per-year rates.

### Gaps
- Exact equations of Meuwissen 1997 (Lagrangian closed form) and Grundy et al. 1998 were not read directly (paywalled). The Woolliams et al. 2015 review was confirmed to exist (J Anim Breed Genet 132:89–99, doi 10.1111/jbg.12148), but its full text was not accessed.

---

## Q2. Conservation variant, overlapping generations and annual decisions

### Takeaway
For conservation, drop the EBV objective and minimise c'Kc (equivalently maximise expected diversity) under the sex and bound constraints. For overlapping generations, existing animals are weighted by age×sex class (their survival/"population share"), and the newborn cohort is the decision variable. The per-generation ΔF is converted to a per-year (per-cycle) rate by dividing by L. A yearly OCS step in the simulator is therefore a natural fit for the optiSel/Wellmann formulation.

### Cited Findings
- The two problem types, "maximising gain with inbreeding at a preset level" and "minimising inbreeding without regard to gain", are both standard and were both formulated as SDPs by [Pong-Wong & Woolliams 2007](https://doi.org/10.1186/1297-9686-39-1-3) (abstract, via [PMC2739432](https://pmc.ncbi.nlm.nih.gov/articles/PMC2739432)). That paper also handles candidates with fixed contributions.
- AlphaMate supports maximising gain, minimising group coancestry, minimising individual-mating inbreeding, or maximising gain for a given increase in coancestry/inbreeding. It is described as covering both selective breeding and conservation — [Gorjanc & Hickey 2018](https://doi.org/10.1093/bioinformatics/bty375) (via [PMC6157072](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6157072/) search abstract).
- The first OCS derivation for overlapping generations was by Meuwissen & Sonesson 1998 — [Du et al. 2025](https://arxiv.org/abs/2504.12895); [Meuwissen & Sonesson 1998](https://doi.org/10.2527/1998.76102575x). The dynamic overlapping-generation version from Woolliams' group is Grundy, Villanueva & Woolliams 2000 ([doi](https://doi.org/10.1017/s1357729800051717)). Its full text was not read.
- Du et al.'s overlapping-generation model: each time step (e.g. a year) P_{t+1} = N_{t+1} ⊔ S_{t+1}, i.e. newborns plus survivors. Survival can be treated as Bernoulli with probability p_I. Wellmann & Bennewitz 2019 use equal survival probabilities within each sex × year class. Individuals are weighted by age×sex class, "Older individuals receive lower weights than younger ones", and all newborns get the same weight — [Du et al. 2025](https://arxiv.org/abs/2504.12895).
- Du et al. warn: for mammals with long generation intervals, the assumed survival vector matters, and "The optimum contributions determined by OCS will then only be optimal if the assumptions turn out to be true" — [Du et al. 2025](https://arxiv.org/abs/2504.12895).
- In optiSel, agecont() estimates contributions of age × sex classes from parents' ages at offspring birth. Non-juvenile males and females are assumed to contribute equally in total. The result is passed to candes() via `cont`; without it, discrete generations are assumed — [Wellmann 2019](https://pmc.ncbi.nlm.nih.gov/articles/PMC6332575).
- Rate per step under overlapping generations: when survivors exist, the FAO per-generation rate "should still be divided by the average generation interval L (Wellmann, 2019)". Example: L = 2.5 gives Δk = 0.4% per step for a 1%/generation target — [Du et al. 2025](https://arxiv.org/abs/2504.12895); optiSel: Δf_y ≤ 1/(2N_eL) ([Wellmann 2019](https://pmc.ncbi.nlm.nih.gov/articles/PMC6332575)).
- Sonesson & Meuwissen 2002 used a 0.25% per year inbreeding restriction in an overlapping-generation OCS+mating study — [GSE 34:23–39](https://doi.org/10.1186/1297-9686-34-1-23) (per search summary of abstract).

### Inferences
- Dog implementation for a yearly simulator: the candidates are all living, fertile dogs aged ~1.5 to 8–12 years. The decision is this year's c (who parents this year's litters). The constraint is applied to the mean kinship of the age-weighted population after adding the newborn cohort (optiSel style), with the target rate ΔF/L per year. For dogs, L ≈ 4–5 years [UNVERIFIED: typical dog generation interval; should be estimated from the simulated pedigree]. With N_e target 100 and L = 4.5, this gives Δf_y ≤ 1/(2·100·4.5) ≈ 0.0011 per year.
- The conservation-only variant (min c'Kc) is a convex QP. Optional "lb on BV" or "ub on disease-risk" can be added as linear constraints (c'x ≥ b), so a dog-specific objective (minimise kinship s.t. mean HD EBV ≥ current, mean disease-carrier risk ≤ x) stays convex.

### Gaps
- Exact optiSel formula for the age-weighted kinship bound with `cont` (the article's bound formulas are images that were not extracted).
- Grundy et al. 2000 and Meuwissen & Sonesson 1998 equations not read directly.

---

## Q3. Solvers: Lagrangian, SDP/SOCP, QP, evolutionary algorithms, optiSel; Python options

### Takeaway
The standard problem (linear objective, one convex quadratic constraint, linear equalities, bounds) is a second-order cone program (SOCP). In Python it is easy to solve with cvxpy (Clarabel/ECOS/SCS) via a Cholesky factor of A. The conservation variant is a plain convex QP. Meuwissen's Lagrangian method is fast but can be sub-optimal (1.5–9% lower gain in Pong-Wong & Woolliams' examples). Evolutionary algorithms (EVA, AlphaMate) matter mainly when mate allocation is optimised jointly or the objective is non-convex.

### Cited Findings
- In small examples, Pong-Wong & Woolliams' SDP always found the optimum. The Lagrangian RSRO method (Meuwissen 1997) "failed to do so in several situations", with expected gains 1.5–9% lower than the SDP optimum — [Pong-Wong & Woolliams 2007](https://doi.org/10.1186/1297-9686-39-1-3) (abstract via [PMC2739432](https://pmc.ncbi.nlm.nih.gov/articles/PMC2739432)).
- Later work describes SDP as giving exact optima but being very slow, and proposes second-order cone programming to speed it up — search-result summary of later citing work (e.g. Yamashita et al., tree-breeding MISOCP, [arXiv:1805.03809](https://arxiv.org/pdf/1805.03809)). [Partly UNVERIFIED: full text not read.]
- There is also a "general quadratic programming method for the optimisation of genetic contributions using interior point algorithm" from the Edinburgh/Roslin group — [Edinburgh Research Explorer listing](https://www.research.ed.ac.uk/en/publications/a-general-quadratic-programming-method-for-the-optimisation-of-ge/) (details not read).
- optiSel solvers (via the optiSolve package): `cccp`/`cccp2` (cone-constrained convex programs) were fastest and correct for linear/quadratic objectives. `alabama` gave sub-optimal results on larger problems and was slowest. `csdp` cannot handle non-convex native-kinship problems. `slsqp` is recommended for maximising native diversity. cccp/cccp2 violated constraints on large non-convex native-kinship problems — [Wellmann 2019](https://pmc.ncbi.nlm.nih.gov/articles/PMC6332575).
- optiSel constraint types: `ub.fPED`/`ub.fSEG` (upper bound on mean pedigree/segment kinship), `ub.fPEDN`/`ub.fSEGN` (native kinship), `lb.equiGen` (minimum equivalent complete generations), bounds on native contributions, `uniform="female"` (equal contributions for females within an age cohort), and individual upper/lower bounds. Example female cap: 5/(2·200) = 0.0125, i.e. at most 5 offspring out of 200 — [Wellmann 2019](https://pmc.ncbi.nlm.nih.gov/articles/PMC6332575). The objective is e.g. `max.EBV`, `min.fPED`. [Note: the names `lb.NC`/`ub.NC` (native contribution bounds) follow the optiSel naming convention but the exact names were not confirmed in the text read.]
- optiSel scale/runtime: example data of 11,000 individuals. The full female-upper-bound optimisation took ~3 min; `uniform="female"` is much faster. Pedigree kinship computation was ~10× faster than other packages and handled 32,698 individuals in 32 GB RAM — [Wellmann 2019](https://pmc.ncbi.nlm.nih.gov/articles/PMC6332575).
- STATUS: optiSel was archived on CRAN on 2026-09-17 ("issues were not corrected in time"). Old versions are at https://CRAN.R-project.org/src/contrib/Archive/optiSel — [CRAN page](https://cran.r-project.org/web/packages/optiSel/index.html). A search snippet earlier listed version 2.1.0 (Feb 2026) on mirrors ([rdrr.io](https://rdrr.io/cran/optiSel/)).
- AlphaMate: frames breeding as multi-objective optimisation of a valid *mating plan* (not just contributions), solved with an evolutionary algorithm. Source is on GitHub (AlphaGenes/AlphaMate) with Windows/Mac/Linux binaries — [Gorjanc & Hickey 2018](https://doi.org/10.1093/bioinformatics/bty375); [Roslin page](https://vet.ed.ac.uk/roslin/research/divisions/quantitative-biology/highlander-lab/software/alphamate). AlphaMate specifies the coancestry target as a trade-off angle in degrees between gain and diversity [UNVERIFIED: from background knowledge; PMC full text blocked].
- EVA (Berg, Nielsen, Sørensen et al.; evolutionary algorithm for optimum contributions and mate allocation) [UNVERIFIED: no primary source fetched this session]. Henryon et al. 2015 (Berg's group) shows that most long-term gain from OCS is kept when practical restrictions are imposed during optimisation — [GSE 47:21](https://doi.org/10.1186/s12711-015-0107-7) (title only verified).
- Du et al. implemented honeybee OCS with optiSolve's `cop`/`solvecop` and note "The program may fail to find an optimum solution if k*_{t+1} is chosen too small" (infeasible target) — [Du et al. 2025](https://arxiv.org/abs/2504.12895).
- Python: `robustocs` (PyPI v0.2.1, MIT, Python ≥3.10, uses HiGHS via highspy or Gurobi). API: `solveROCS(sigma, mu, omega, sex, method, lam, kappa)` returns selection, objective, merit, coancestry. It supports standard and *robust* OCS (uncertainty in EBVs); SQP with HiGHS performed favourably — [Fogg, Ortiz, Pocrnić, Hall & Gorjanc 2024, arXiv:2412.02888](https://arxiv.org/abs/2412.02888); [GitHub Foggalong/RobustOCS](https://github.com/Foggalong/RobustOCS); [PyPI](https://pypi.org/project/robustocs/). The robust OCS paper reformulates the square-root risk term as an SOC constraint.

### Inferences
- Easiest Python route (my construction, standard convex-optimisation practice): factor A_cand = LL' (A is positive definite for non-clone animals). Then ½c'Ac ≤ C becomes ||L'c||₂ ≤ √(2C), and in cvxpy: `cp.Maximize(ebv @ c)`, `cp.norm(L.T @ c, 2) <= np.sqrt(2*C)`, `S_m @ c == 0.5`, `S_f @ c == 0.5`, `c >= 0`, `c <= ub`. Alternatively use `cp.quad_form(c, K) <= C` (cvxpy turns this into an SOC itself; wrap K with `cp.psd_wrap` if needed). Solve with Clarabel (cvxpy's default open-source conic solver). For a dog breed with a few hundred to a few thousand living candidates, this should solve in well under a second to seconds [UNVERIFIED estimate; dense Cholesky of n=5,000 is trivial].
- Conservation variant: `cp.Minimize(cp.quad_form(c, K))` with the same linear constraints is a QP (scipy `minimize(method='SLSQP')` also works for n ≲ 1,000, but cvxpy/OSQP/Clarabel is more robust).
- To combine "maximise gain at fixed ΔF" with "conservation", sweep the kinship target to trace the gain/diversity frontier. This mirrors AlphaMate's angle parameter.
- Disease (Mendelian) risk can enter as a linear constraint on expected carrier contributions (Σ c_i·p_carrier,i ≤ b) or as a penalty in the objective. That keeps the problem convex. Whether this is preferable to handling it in mate allocation (avoid carrier × carrier pairs) is an inference, not from a source.

### Gaps
- No verified runtime benchmarks for cvxpy-based OCS at dog-breed scale were found. Methods sections of the EVA and AlphaMate primary papers were not accessed.
- Exact optiSel argument names beyond those listed (e.g. `lb.NC`) were not verified.

---

## Q4. From optimal contributions to actual matings; rounding to integer litters

### Takeaway
Use two stages. (1) Convert c into integer numbers of matings/offspring per parent: n_i ≈ 2c_i·N, rounded with an unbiased apportionment method. (2) Allocate mates to minimise mean coancestry of mated pairs (or another pair-level cost), subject to each parent being used exactly its quota. This is a transportation/assignment LP with integral solutions. Sonesson & Meuwissen 2000 found minimum-coancestry mating with at most one offspring/litter per pair (MC1) best, with up to ~22% more response than random mating at tight ΔF.

### Cited Findings
- optiSel `noffspring()` converts contributions to counts via n_i ≈ 2c_i·N₀. `matings()` minimises the average kinship of parents weighted by offspring counts. Output is a data frame (Sire, Dam, n) with options such as `ub.nOff` (maximum offspring per mating) and a herd-level sire proportion limit α — [Wellmann 2019](https://pmc.ncbi.nlm.nih.gov/articles/PMC6332575). The optimisation method inside matings() is not named in the article (it is believed to be an LP [UNVERIFIED]).
- `noffspring()` rounding: each parent first gets ⌊N·c_i⌋. The remaining slots are given either randomly with probability ∝ remainder (random=TRUE, default, at most one extra each) or to the largest remainders (random=FALSE). Du et al. identify random=FALSE as Hamilton's (largest-remainder) method — [Du et al. 2025](https://arxiv.org/abs/2504.12895).
- Du et al.'s critique: random rounding can assign an offspring to an animal whose "optimum" contribution is a numerical artefact (~1e-7). Hamilton's method can show paradoxes, where whether hopeless candidates are included changes other animals' quotas. Jefferson/D'Hondt is biased toward large "parties", making large sib-groups larger, which is "detrimental". They prefer Webster/Sainte-Laguë (unbiased, avoids the paradox), possibly modified to make the first "seat" harder to get. That avoids allocating a single use to a parent — [Du et al. 2025](https://arxiv.org/abs/2504.12895).
- Sonesson & Meuwissen 2000 compared mating schemes after OCS. Minimum-coancestry mating with at most one offspring per mating pair (MC1) was best. It raised genetic response ~22% over random mating at ΔF = 1% with 100 candidates, and ~5–6% with looser constraints or more candidates. The gain came mainly from avoiding full-sib matings and spreading ancestral contributions more evenly — [GSE 32:231–248](https://doi.org/10.1186/1297-9686-32-3-231) (per search-result summary of abstract; full text 403'd).
- The overlapping-generations extension (Sonesson & Meuwissen 2002) reported ~18% gain over random mating at 0.25%/year — [GSE 34:23–39](https://doi.org/10.1186/1297-9686-34-1-23) (per search summary).
- AlphaMate optimises the mating plan directly (contributions and pairings at once) by evolutionary algorithm — [Gorjanc & Hickey 2018](https://doi.org/10.1093/bioinformatics/bty375).
- Classic pair-level methods: Kinghorn's mate selection index (Kinghorn 1987; "Mate Selection" software, total utility over a whole mating set) and Toro & Pérez-Enciso 1990 (optimisation of selection response under restricted inbreeding / mate allocation by linear programming / simulated annealing) [UNVERIFIED: from background knowledge; not fetched].

### Inferences (implementation recipe for the dog simulator)
1. Litter quotas: the decision unit is a litter, not an offspring. Let L_tot = number of litters planned this year (fixed by dam availability). Sire quota s_j = round(2·c_j·L_tot) and dam quota d_i ∈ {0,1} (or ≤ 1 litter/year; ≤ k per lifetime). Because each litter has one sire and one dam, Σ_j s_j = Σ_i d_i = L_tot. Use Sainte-Laguë or largest-remainder rounding. Drop c below a threshold (e.g. < 0.25/(2L_tot)) first, to avoid artefact allocations (Du et al.).
2. Mate allocation as a transportation LP: minimise Σ_{i,j} x_ij·k_ij (k_ij = kinship of the pair = inbreeding of the litter), plus optional penalties for disease risk P(affected | carrier probabilities), with Σ_j x_ij = d_i, Σ_i x_ij = s_j, and 0 ≤ x_ij ≤ 1 (MC1: at most one litter per pair). Add x_ij = 0 for forbidden pairs (e.g. both carriers, F > threshold, geography). The constraint matrix is totally unimodular, so the LP relaxation gives integers. scipy.optimize.linprog (HiGHS) or scipy.optimize.linear_sum_assignment (after replicating each sire s_j times) solves it in milliseconds for hundreds of dams.
3. Re-optimise every simulated year with updated pedigree and survivors (a "dynamic" OCS, as in Grundy et al.). Do not reuse multi-year plans.
4. The original per-dam tool can still rank sires within the set chosen by OCS. That is the "coordination" layer: OCS fixes how many litters each sire gets, which stops the over-concentration seen in the 10-generation runs.

### Gaps
- Exact LP formulation used by optiSel's matings() and by Sonesson & Meuwissen 2000 was not read directly.
- No primary source found that specifically addresses OCS for dogs/kennel-club settings, where breeders may decline recommended matings (compliance). That issue is not covered in the OCS literature retrieved.

---

## Q5. Known pitfalls

### Takeaway
The main risks: animals with shallow or incomplete pedigrees look unrelated and get over-used; OCS with BLUP EBVs tends to favour families (and young animals with high parent-average EBVs); infeasible kinship targets when ΔF is set too low; numerical tiny contributions; and survival/age assumptions in overlapping generations. Mitigations are documented in optiSel (lb.equiGen, uniform female contributions, individual caps).

### Cited Findings
- Pedigree completeness: candidates with few equivalent complete generations "can appear artificially unrelated and be overfavored". optiSel offers `lb.equiGen` (lower bound on the mean equivalent complete generations of offspring) — [Wellmann 2019](https://pmc.ncbi.nlm.nih.gov/articles/PMC6332575).
- Founder/unknown-ancestry: pedigree-based native contributions are likely underestimated and native kinships overestimated — [Wellmann 2019](https://pmc.ncbi.nlm.nih.gov/articles/PMC6332575).
- Infeasibility: the solver may fail if the target kinship is chosen too small — [Du et al. 2025](https://arxiv.org/abs/2504.12895).
- Numerical artefacts: solver returns tiny non-zero contributions (~1e-7 to 1e-8) for animals that should get zero. This interacts with the rounding method — [Du et al. 2025](https://arxiv.org/abs/2504.12895).
- Survival assumptions: optimal contributions in overlapping generations are only optimal if the survival assumptions hold. This is especially relevant for long-generation mammals — [Du et al. 2025](https://arxiv.org/abs/2504.12895).
- Inbred-animal preference: the exact kinship formula's extra term rewards inbred parents. Wellmann & Bennewitz suggest omitting or modifying it — [Du et al. 2025](https://arxiv.org/abs/2504.12895); [Wellmann & Bennewitz 2019](https://doi.org/10.3389/fgene.2019.00667).
- Rate target: FAO guidance ≤ 1% inbreeding per generation; optiSel suggests N_e ≥ 100 (critical 50–100), i.e. ΔF ≤ 0.5% per generation, divided by L per year — [Du et al. 2025](https://arxiv.org/abs/2504.12895); [Wellmann 2019](https://pmc.ncbi.nlm.nih.gov/articles/PMC6332575).
- Practical restrictions (caps on use, etc.) imposed during optimisation retain most of the long-term gain of OCS — [Henryon et al. 2015, GSE 47:21](https://doi.org/10.1186/s12711-015-0107-7) (title-level verification only).
- Co-selection of relatives under BLUP, and the observation that OCS achieves its gain by favouring large Mendelian-sampling terms over family means, is the topic of Woolliams' work (e.g. "Mendelian sampling terms as a selective advantage in optimum breeding schemes with restrictions on the rate of inbreeding", Genetics Research — [Cambridge](https://www.cambridge.org/core/journals/genetics-research/article/mendelian-sampling-terms-as-a-selective-advantage-in-optimum-breeding-schemes-with-restrictions-on-the-rate-of-inbreeding/D459CA3ED2A52046E957FF7ABC451F0D)) [content not read].

### Inferences
- Young animals: dogs entering breeding age (1.5–2 y) have no own HD records yet. Their EBVs are pedigree-dominated, so OCS tends to treat sibs as interchangeable and pick a family. Mitigations: per-sire lifetime and per-year litter caps (ub on c), `uniform`-style equal-dam contributions, and weighting existing animals by age class.
- Dogs with unknown parents (imports, registry gaps) should get phantom/unknown-parent group handling or a minimum equivalent-generations constraint. Otherwise OCS will over-use them.
- Reference population for C_t: use the mean kinship of the age-weighted living breeding population (optiSel `cont`-style), not all historical animals.
- For a small breed where current N_e is far below 100, a strict ΔF target will be infeasible. Practical approach: first solve min c'Kc to get the feasible minimum, then set the target as min + fraction of the gap, or ΔF/L per year with a fallback.

### Gaps
- No primary source fetched that quantifies the young-animal bias in OCS or dog-specific pitfalls.
- The Woolliams et al. 2015 review's specific recommendations on reference population choice were not read.

---

## Q6. Open-source Python implementations

### Takeaway
The only verified maintained Python OCS package found is `robustocs` (MIT, HiGHS/Gurobi). Most reference implementations are in R (optiSel/optiSolve, now archived on CRAN as of 2026-09-17) or Fortran (AlphaMate). A custom cvxpy implementation is straightforward and probably the best fit for the simulator.

### Cited Findings
- robustocs 0.2.1 on PyPI: "Tools for solving robust optimal contribution selection problems"; homepage https://github.com/Foggalong/RobustOCS; uses HiGHS/Gurobi; MIT licence — [PyPI](https://pypi.org/project/robustocs/), [GitHub](https://github.com/Foggalong/RobustOCS), [arXiv:2412.02888](https://arxiv.org/abs/2412.02888).
- optiSel (R) archived on CRAN 2026-09-17 — [CRAN](https://cran.r-project.org/web/packages/optiSel/index.html). Its solver back end optiSolve (Wellmann 2021) supports linear, quadratic and rational optimisation and was used for honeybee OCS — [Du et al. 2025](https://arxiv.org/abs/2504.12895).
- AlphaMate source on GitHub (AlphaGenes/AlphaMate) — [Gorjanc & Hickey 2018](https://doi.org/10.1093/bioinformatics/bty375); [Roslin](https://vet.ed.ac.uk/roslin/research/divisions/quantitative-biology/highlander-lab/software/alphamate).
- A PyPI package named "mate-selection" appeared in search results ([libraries.io](https://libraries.io/pypi/mate-selection)), but its content and relevance were not checked.
- No ready-made cvxpy OCS repository was found; cvxpy supports SOC constraints with a Cholesky factor (portfolio-risk pattern) — [CVXPY paper](https://arxiv.org/pdf/1603.00943).

### Inferences
- The recommended stack is a custom OCS in cvxpy (Clarabel), apportionment via Sainte-Laguë, and mate allocation via scipy linprog/HiGHS or linear_sum_assignment. It has no R dependency, and robustocs can serve as a cross-check for the selection step.
- If optiSel is used for validation, install it from the CRAN archive. The archive status means it may break on future R versions.

### Gaps
- AlphaSimR examples of OCS (R) were not searched in this session. pyOCS / other Python packages were not found under those names.
