# E8: Diversity, health and hips at once (pre-registration)

**Goal:** test whether the product mode (S3q: the recommender inside club quotas) can beat today's market on diversity, hips and disease alleles at the same time when its quotas come from gain OCS ("hips within a ΔF budget") with a limit on how often the planned sires pass on tested risk alleles.

**Why:** three loose ends of P12 (`plan/gates/P12_report.md`):
1. H4a failed. In E5, SYN_M, generation 10, S3q ends with *higher* tested risk-allele frequencies than S1 (SOD1_DM 0.127 vs 0.066, ABCB1_MDR1 0.098 vs 0.068): diversity-maximising OCS keeps recessives at heterozygous frequencies [de-cara-2013].
2. Open question 1: gain OCS at dF 0.1% gave the same Ne as conservation OCS in SYN_M (288 vs 289) with a far better mean true HD breeding value (−0.79 vs +0.39). S3q was never run on gain OCS.
3. Open question 3: quotas could take carrier status into account with a linear constraint Σ cᵢ·pᵢ ≤ b (`docs/research_coordination.md`, project inference).

**Framing rule (unchanged):** in silico results on synthetic populations only. Everything below is fixed before any E8 or pilot data exists (this file's commit is the proof). Results are reported whatever they show.

---

## 1. Carrier constraint

For every tested locus l whose candidate mean is above 0, the season's OCS adds

    Σᵢ xᵢ · tᵢₗ ≤ β · mean over candidate sires of tᵢₗ

- `x` = sire share of the season's litters (OCS variable, sums to 1, includes fixed non-adopter contributions);
- `tᵢₗ` = probability that sire i transmits the risk allele at l: genotype / 2 if known (tested or inferred clear), else the breed's reference allele frequency q (`matching.components.transmission`, the quantity the recommender already uses);
- only loci in the observed DNA panel (`ctx.geno`); NOVEL_X (never testable) is excluded by construction.

The bound is relative to the current candidates, so it ratchets down season by season and needs no absolute target. It is a soft limit, not exclusion: excluding all known carriers cost Ne in E3 (SYN_M 190 → 163), and excluding carriers led to near-universal extinction in a small-population study cited in `docs/research_coordination.md` (Bergsma 2022, secondary).

If a season is infeasible, constraints are dropped in this order: carrier, then age classes, then depth (P12 constraints keep priority). Each dropped carrier constraint is logged (`D10_carrier_relaxed`).

## 2. Choosing β (`assumption: true`)

1. Static price curve: v1, SYN_M, current season, S3q-gain010 planning with β ∈ {1.0, 0.9, 0.75, 0.5, 0.25}; report planned risk-allele transmission, planned coancestry relative to no constraint, HD merit lost, feasibility.
2. Dynamic pilot: seed 20261101 (not the main seed), SYN_M, 3 replicates of S3q-gain010, S3q-gain010-c100, -c075, -c050, 10 generations.
3. Rule: the smallest β in {1.0, 0.75, 0.5} such that (i) the carrier constraint is relaxed in ≤ 5% of planned seasons and (ii) the pilot mean late ΔF is ≤ 1.10 × that of S3q-gain010 in the pilot. If none qualifies, β = 1.0. The 5% and 1.10 thresholds are assumptions.

Pilot results are reported separately and never pooled with the main run.

## 3. Main experiment (E8, `configs/experiments/health_gain_quotas.yaml`)

| | SYN_M (20 replicates) | SYN_S (10 replicates) |
|---|---|---|
| anchor | S1 | S1 |
| product mode today | S3q | S3q |
| + carrier limit | S3q-cβ | (none: no segregating tested locus in v1, see E3) |
| + gain OCS | S3q-gain010 | S3q-gain025 (smallest budget tested for SYN_S in E6) |
| + both | S3q-gain010-cβ | (none) |

Seed 20261108, 10 generations, dataset v1, adoption 100%, all other settings as E5 (`configs/experiments/coordination.yaml`). Strategy ids: `S3q[-gainNNN][-cBBB]`, gain budget dF = NNN / 10⁴ per generation, β = BBB / 100.

## 4. Pre-registered criteria

Generation 10 (late window generations 5 to 10 for Ne), paired by replicate, 95% t-intervals.
Ne = 1/(2 × late ΔF of realised IBD) (`R_ne_f_late`); HD = `M8_mean_tbv_hd` (lower is better); freq = sum of `M6_freq_*` over tested loci; affected = sum of `M6_affected_*`.

| id | breed | criterion | pass |
|---|---|---|---|
| H8a | SYN_M | Ne(S3q-gain010-cβ) − Ne(S1) | CI lower bound > 0 |
| H8b | SYN_M | HD(S3q-gain010-cβ) − HD(S1) | CI upper bound < 0 |
| H8c | SYN_M | freq(S3q-gain010-cβ) − freq(S1) | CI upper bound < 0 |
| **H8** | SYN_M | diversity, health and hips at once | H8a and H8b and H8c |
| H8d | SYN_M | affected(S3q-gain010-cβ) − affected(S1) | reported, no pass/fail (rare outcome, see H4a) |
| H8e | SYN_M | 2×2 attribution: carrier effect = mean of (cβ − no limit) over both planners on freq and Ne; gain effect = mean of (gain010 − conservation) over both carrier levels on HD and Ne | reported with CIs |
| H8f | SYN_S | S3q-gain025 vs S1 and vs S3q on Ne and HD | reported, no pass/fail |
| D | both | seasons with carrier constraint relaxed, infeasible seasons, solver time, overflow | reported |

**Health endpoint.** P12's H4a used the affected-genotype share. E8's primary health endpoint is the risk-allele frequency, because it is what the constraint acts on and because affected genotypes are rare (≈ q², about 0.3%), which left H4a with no detectable difference at 10 replicates. This switch is made here, before any E8 data; the affected share is still reported (H8d).

**Sanity checks** (reported): S1 and S3q in E8 show the same direction as in E5 for Ne and freq; planned carrier transmission declines over seasons in the c-arms.

## 5. Out of scope
No change to the P1 data contract, `configs/coordination/default.yaml` or existing strategies; E5 to E7 are not rerun. Conference texts change only after Tea approves the results (poster cutoff 17 Oct 2026).

---

## Addendum (14 Oct 2026, after the pilot, before the main run): β = 0.5

Static price curve (`reports/experiments/E8_pilot/price_curve.md`, one season): without a limit, gain OCS plans *above-average* risk-allele transmission (SOD1_DM 0.228 vs candidate mean 0.202, ABCB1_MDR1 0.142 vs 0.107); every β was feasible; planned coancestry unchanged (≤ 4e-7); planned HD merit lost 0.01 (β 1.0) to 0.14 SD (β 0.25).

Dynamic pilot (seed 20261101, SYN_M, 3 replicates, generation 10):

| arm | late ΔF (%/gen) | ratio to S3q-gain010 | carrier limit relaxed | risk-allele freq (sum) | HD |
|---|---|---|---|---|---|
| S3q-gain010 | 0.169 | 1.00 | n/a | 0.165 | −0.81 |
| S3q-gain010-c100 | 0.198 | 1.17 | 0 of 135 | 0.139 | −0.81 |
| S3q-gain010-c075 | 0.168 | 1.00 | 0 of 135 | 0.068 | −0.79 |
| S3q-gain010-c050 | 0.176 | 1.04 | 0 of 135 | 0.031 | −0.76 |

Rule (section 2): smallest β in {1.0, 0.75, 0.5} with relaxed ≤ 5% and ratio ≤ 1.10 → **β = 0.5** (`-c050`). The non-monotone ΔF (c100 above c075) shows the pilot's noise at 3 replicates; it does not affect the choice. Main arms: S3q-c050 and S3q-gain010-c050.
