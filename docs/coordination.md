# Coordinated sire use (P12)

All animals and results here are synthetic (in-silico). Sources and verification labels: `docs/research_coordination.md` and `docs/research.md` section 10.

## Why

Long-term inbreeding depends on how unevenly animals contribute genes, not on how each pair is chosen. Our per-dam recommender (P7) picks the best sire for each dam on its own. When many breeders follow the same ranking, they converge on the same few low-kinship sires. In P8 this cut disease risk and short-term COI, but did not raise the effective population size; in SYN_M it lowered it (share of eligible males used 6.6% vs 13.4% under the status quo). The literature predicts exactly this. Per-dam least-related mating in a Golden Retriever simulation gave a rate of inbreeding of 0.04% per generation for 20 years, rising to 0.39% later, while excluding high-mean-kinship animals held it at 0.12 to 0.14% [windig-2013].

The standard fix has two layers [meuwissen-1997; sonesson-meuwissen-2000; wellmann-2019]:

1. **Contributions** (club level, once a season): decide how many litters each sire may have. This is optimum contribution selection (OCS).
2. **Mate allocation** (pair level): fill those litters with low-kinship pairs, or let breeders choose within the quotas.

## What the planner does each season

Inputs: the dams that will be mated this season (fixed, one litter each), the candidate sires, the pedigree, rule profiles and DNA results.

1. **Kinship.** K = A/2 among sires and dams, from the recorded pedigree (an oracle variant in the experiments uses the true pedigree).
2. **Contributions.** Sire i's expected litters l_i give contributions s_i = l_i / (2 n), and each dam contributes 1/(2 n). The expected coancestry of the planned matings is C = c'Kc.
   - **Conservation** (default): minimise C.
   - **Gain under a budget**: maximise the mean HD breeding value of the chosen sires subject to C + τ ≤ C_next. Here C_next = 1 − (1 − C_now)(1 − ΔF)^(1/L), C_now is the coancestry of last season's matings, L is the generation interval from the pedigree, and τ is the small-cohort term [du-2025]. If the budget is below the conservation minimum, the conservation plan is used and the season is logged as infeasible.
3. **Constraints.**
   - Per-sire yearly cap, cap = clip(round(5 × MK_mean / MK_sire), 1, 5) litters [windig-2013; leroy-rognon-2012].
   - At least one litter to each of the two youngest age classes of sires [sonesson-meuwissen-2001].
   - The litter-weighted mean pedigree depth (EqG) of chosen sires must be at least the candidates' mean, so short foreign pedigrees do not look falsely unrelated [wellmann-2019].
   - Booked litters of breeders who do not use the planner are fixed.
4. **Whole litters.** Sainte-Laguë apportionment of the season's litters; sires below 0.25 expected litters get none [du-2025].
5. **Allocation.**
   - **MC1:** an exact assignment of dams to sire slots that minimises pair kinship + P(affected puppy). Pairs failing a HARD rule are never used.
   - **Random:** a random assignment within the quotas.
   - **Product mode (S3q):** a shared booking ledger. Each breeder sees our ranked shortlist restricted to sires with quota left and chooses among the top three.

Solver: cvxpy with Clarabel (ADR-007). Code: `src/breeding_smarter/coordination/`.

## Parameters

| Parameter | Value | Key / label |
|---|---|---|
| ΔF ladder | 1%, 0.5%, 0.25% per generation; SYN_M also 0.1% | fao-2013, frankham-2014, windig-2013 (verified) |
| Default ΔF | 0.5% (Ne 100) | frankham-2014 (verified) |
| Yearly budget formula | C_next = 1 − (1 − C_now)(1 − ΔF)^(1/L) | du-2025 (exact yearly form unverified) |
| Small-cohort term | on | du-2025 (verified; disputed by wellmann-bennewitz-2019) |
| Cap per sire per year | 5 litters, scaled by mean kinship | windig-2013 (verified slides); scaling is an assumption |
| Minimum expected litters | 0.25 | du-2025 idea; value is a project choice |
| Youngest age classes required | 2 | sonesson-meuwissen-2001 (verified) |
| Depth constraint | on | wellmann-2019 |
| Health weight in allocation | 1.0 | assumption |
| Lifetime cap | off (PEVISA 15 to 120 offspring, STRETCH only) | kennelliitto-pevisa-2026 (verified) |

## Using it

- CLI: `uv run bsm coordinate --breed SYN_M --dataset v1 --date 2027-03-01 [--dams auto|file] [--delta-f 0.005] [--mode ocs|cap]`. It prints the sire quota table and a suggested allocation.
  - `--dams auto` means living females aged 2 to 6 with no litter in the previous 10 months. If there are more than last year's number of litters, a seeded random sample of that size is used.
  - Candidate sires are breeding-age males that sired offspring in the last 5 years or have an HD result, at most 1,500 by lowest mean kinship.
- App: page **Club planner** (breed, date, mode, inbreeding budget). The Mate finder has a **Respect club quotas** toggle that hides sires with no quota left this season.
- Python: `breeding_smarter.coordination.planner.plan_season` (one season) and `coordination.club.club_plan` (registry dataset).

## Limitations

- Kinship comes from the recorded pedigree, which underestimates true kinship, especially for imports. The oracle experiment (E6) measures the cost of this. Genomic kinship or metafounders [legarra-2015] are the long-term fix.
- Only sire contributions are planned. Which dams are bred stays the breeders' decision.
- The yearly budget formula is standard but its exact form is unverified against a primary text.
- OCS keeps recessive disease alleles at low frequency rather than purging them [de-cara-2013]. That is why disease outcomes are reported separately.
- Whether clubs and breeders accept quotas is untested. The FCI prefers education over strict rules [fci-strategies]. The adoption experiment (E7) shows what partial use achieves in silico.
