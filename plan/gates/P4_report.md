# Gate report: P4 Genetics and observations
Date: 2026-10-10

## Acceptance checklist
- [x] Dataset v0 generated (default config, seed 42, `DogGenetics`): `data/generated/v0-default-s42`; `validate_run` passes (also checks every DNA locus is in the loci config).
- [x] All tests pass, slow ones included: 127 fast + 8 slow (`uv run pytest -m slow`: 8 passed in 30 s). Slow genetics results: full-sib offspring mean realised IBD within 3 SE of 0.25 (2000 offspring); carrier x carrier 1:2:1, chi-square p > 0.001 at every locus over 10,000 offspring; no systematic allele-frequency drift over 50 replicate random-mating runs. Fast: HD base phenotypic variance in [0.9, 1.1], offspring-on-mid-parent TBV slope in [0.95, 1.05]; Henderson A-inverse = inv(A) on 20 random pedigrees (atol 1e-8); BLUP beats the phenotype (corr(EBV, TBV) > corr(-grade, TBV) among screened animals with at least 5 screened progeny); DNA results equal the true genotypes; `NOVEL_X` never appears in any registry file (byte search); neutral alleles held only by living animals after compaction.
- [x] Gate report numbers (below).
- [x] Simulation wall time: 28.2 s generator wall time for the default run (P3: 8.4 s). The increase comes from the gene drop (200 loci) and from about twice as many litters (inbred dams have smaller litters, so more litters are needed to meet registration demand). Still far inside the 10-minute target.

## Numbers (dataset v0, seed 42)
Row counts: animals 160,754; litters 52,750; health_tests 29,027; dna_tests 89,952; ebv 155,698; truth animals 301,546; genotypes 1,507,730.

Mean realised IBD (`f_true_ibd`) of the 2025 cohort: SYN_L 0.372, SYN_M 0.536, SYN_S 0.363. **Far too high; see "Known issues".**

Risk-allele frequency among registered births, 1980 vs 2026 (base founders in brackets):
| Breed | PRCD_PRA | SOD1_DM | ABCB1_MDR1 | DNM1_EIC | NOVEL_X |
|---|---|---|---|---|---|
| SYN_L | 0.000 vs 0.000 (0.08) | 0.442 vs 0.668 (0.25) | 0 vs 0 (0) | 0.016 vs 0.004 (0.10) | 0 vs 0 (0.05) |
| SYN_M | 0 vs 0 (0.05) | 0 vs 0 (0.15) | 0 vs 0 (0.12) | 0 vs 0 (0) | 0 vs 0 (0.05) |
| SYN_S | 0.20 vs 0.06 (0.12) | 0 vs 0 (0.10) | 0 vs 0 (0) | 0 vs 0 (0) | 0 vs 0 (0.05) |

Carrier share of 2026 births: SYN_L SOD1_DM 0.501, DNM1_EIC 0.008; SYN_S PRCD_PRA 0.119; everything else 0.

HD grade shares by decade of screening (A/B/C/D/E): SYN_L 1980s 0.33/0.27/0.22/0.12/0.06 -> 2020s 0.36/0.28/0.20/0.12/0.05; SYN_M 0.62/0.24/0.09/0.04/0.01 -> 0.70/0.21/0.07/0.02/0.00; SYN_S 0.44/0.26/0.14/0.11/0.04 -> 0.73/0.17/0.08/0.03/0.00. D+E falls over time as screening selects (skk-hd-2020 pattern).

EBVs: 155,698 animals (L 123,244; M 28,087; S 4,367), mean accuracy 0.549. Screened animals: corr(EBV index, -TBV) L 0.646 (mean reported accuracy 0.765, n 22,815), M 0.527 (0.756, n 5,183), S 0.689 (0.723, n 1,029).

## What was built
- `configs/loci/dog_mendelian.yaml` (5 loci, base frequencies as one `Sourced` block, assumption), `configs/genetics/dog.yaml` (200 neutral loci, h2 0.35 (skk-hd-2020 range), screening and testing parameters), breed `health:` sections (screening start 1985, rates 0.7/0.05, base grade distributions, `hd_exclude_grades [E]` (hks-pravilnik), DNA test rate 2026 0.6).
- `sim/genetics.py` `DogGenetics`: gene drop with allele ids `2*gid, 2*gid+1` for founders, alleles stored only for living animals (yearly compaction); disease loci (risk-allele counts, Mendelian transmission); infinitesimal HD model with inbreeding-adjusted Mendelian sampling; liability thresholds from the base grade distribution; yearly DNA testing (ramp 0.1 -> breed rate by 2026), testing of imports and foreign AI sires on entry (0.7); HD screening at 12 to 24 months; eligibility (grade E; known affected w.p. 0.8, fixed per animal); carrier x carrier pair resampling (0.9); table output (health_tests, dna_tests, truth columns, genotypes); state serialisation.
- `evaluation/blup.py`: Henderson A-inverse with inbreeding, MME with birth-year-group (5 y) and sex fixed effects, CG with Jacobi preconditioner (spsolve fallback), approximate reliability, SKK-style index. `bsm ebv --run`; EBVs are written automatically by `bsm generate` (`post_write` hook) before validation.

## Deviations from the plan (and why)
1. **Inbreeding depression is absolute, not multiplicative (plan error).** The plan's `mean * (1 - id_slope * F)` with `id_slope = 10` removes every puppy at F = 0.1; the source (chu-2019) says about one puppy fewer per 10% COI. Implemented `mean - 10 * F` puppies.
2. **Litter planning accounts for dam inbreeding.** Target litters use the expected litter size of the eligible dams (including their mean F), so registration demand is still met when litters shrink. Without it v0 had half the registrations.
3. **Rescue imports (assumption).** When a domestic population cannot supply enough dams or sires even after recruitment, young foreign candidates are brought in (also in the hidden era). Counted in `state.meta`. The tiny config went extinct in 4 of 6 seeds without it; with it, 8 of 8 seeds survive.
4. **EBV index is centred** on animals born in the last 5 years (`100 - 10 (ebv - mean) / sd`) so the index has mean 100 and SD 10 as the P1 table states; the plan's formula omitted the centring.
5. HD screening and DNA results are recorded for registered non-stub animals (HD) and all registered animals (DNA, so tested foreign AI sires show their results). The foreign population is screened too (hidden), so foreign breeders also exclude grade E.
6. `GeneticsModel.pair_avoid` implements the carrier-pairing behaviour; `on_import` the entry tests.
7. The simulation runs to the end of 2026 (dates up to December 2026), while the EBV evaluation date is 2026-09-30.
8. Validator parent lookups rewritten with index positions (a pandas `Int64.map` datetime bug).

## Known issues (to fix in P5 calibration)
- **Realised inbreeding is far too high and most disease alleles are lost before 1980.** The runaway popular-sire concentration from P3 (alpha = 1) makes the hidden history's effective size tiny: NOVEL_X is lost in every breed and SYN_M keeps no risk allele at all. P5 must calibrate alpha/beta and the candidate shares against T05 to T07, and check that allele frequencies survive; otherwise P8 (M6, M7, E3) has nothing to show. This is the top priority of P5.

## Open questions for Tea
- None blocking.

## HUMAN tasks waiting
- [STRETCH 4.8] Donner 2023 frequencies (not started; stretch).
