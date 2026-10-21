# Kennel club desk (prototype)

**Prototype on synthetic data. Not an official kennel club form.** Every dog, breeder and
registration number is synthetic.

Today a mating is registered on paper, and most clubs check their rules only when the litter
is registered, after the puppies are born (UK, Finland, Sweden; Croatia: the HKS mating
certificate and litter registration forms). The desk checks every rule **before the mating**,
uses the club's sire quotas from the club planner, and keeps the two signatures (breeder and
stud owner) and the breeding officer's decision that every federation uses.

App page: **Kennel club desk** (`app/pages/8_Kennel_club_desk.py`). Logic:
`src/breeding_smarter/desk.py` (pure functions). Tests: `tests/unit/test_desk.py` and the desk
tests in `tests/integration/test_app.py`.

## Flow
1. **Mating application** (breeder): choose the dam and the planned mating date, then the sire.
   The sire comes from the recommender's ranked list, restricted to sires with club quota left,
   or is entered by hand.
2. The **automatic checks** appear at once:
   - the outcome;
   - every rule of the profile (`hr_full`), with ✓ ✗ ⚠ ℹ, its source and whether it is verified;
   - the club quota;
   - an explanation in 3 to 5 sentences built from templates and the score card's numbers;
   - the full score card.
3. **Submit application** (disabled when the outcome is Blocked or the same mating is already
   submitted). At the top of the tab, **Application** switches between a new application and
   the submitted ones; after submitting, the new one opens. Each application shows its checks
   and its steps: submitted, the stud owner's signature (**Stud owner confirms APP-…**, the
   second signature, signed right there), then the breeding officer's decision. A blocked
   application needs no signature, because the club cannot approve it.
4. **Breeding officer queue**: the officer ticks the manual checks, adds a note and approves or
   rejects.
   - Approval needs the stud owner's confirmation and every manual check ticked.
   - Approval books one litter of the sire's club quota, exactly once. Rejection books nothing.
   - An approved application gives a downloadable **mating certificate (prototype)** in HTML,
     marked as a prototype at the top and bottom.

5. **Season overview** (the club):
   - counts of applications, approved, blocked, waiting and rejected;
   - blocked applications by rule, with their sources, and how many are blocked by EU 2026/1818
     rules or wait with no club quota left;
   - litters booked vs left per sire;
   - **Export compliance report (CSV)**: one row per application with its outcome, status, every
     rule with its result, source and verification status, and the quota.

Status: `SUBMITTED → STUD_OWNER_CONFIRMED → APPROVED / REJECTED`.

"Blocked" counts every application whose automatic checks fail a hard rule, whatever its status,
so it can overlap with "rejected"; "waiting" means open and not blocked.

## Outcome of the automatic checks
| Outcome | When |
|---|---|
| **Blocked** | a HARD rule fails (for example the EU close-relative ban) |
| **Needs club review** | no HARD failure, but a SOFT rule warns, the sire has no club quota left, or a conditional manual check applies |
| **Allowed** (READY) | every automatic check passed; the standard manual checks still wait for the officer |

The standard manual checks are always listed and do not change the outcome:
- breeding examination of the dam;
- breeding examination of the sire;
- show grade;
- original health certificates.

The only conditional check is a veterinary certificate for a dam older than 7 years. The
7 years is an **assumption** taken from the desk specification; it has no source in
`docs/research.md`.

**Club quota.**
- Quotas come from the club planner (`coordination.club.club_plan`, conservation OCS) for the
  dam's breed on the season date (1 November 2026). They are shared by all applications in the
  session.
- An assessment shows the quota left *before* its own booking, so an approved application
  keeps its outcome.
- A sire without quota can be approved only as an explicit club exception with a note. Nothing
  is booked, and the certificate says so.

## Rules added for the desk (all `verified: false`)
| Profile | Rule | Check | Source |
|---|---|---|---|
| hks_hr | `hks_max_caesareans` | no mating after 2 or more caesarean litters (HARD) | `hks-clubs-2026` |
| hks_hr | `hks_one_litter_12m` | at most 1 litter in 12 months (HARD); HKS says one per calendar year, so this is an approximation | `hks-clubs-2026` |

The caesarean flag already exists in `registry/litters` (`caesarean`), so the data contract did
not change. `RuleContext` reads it when present; contexts without it (the experiments) count
every litter as natural. The experiment profiles (`exp_pairing*`) do not include these rules.

## Demo examples
On first opening, the queue holds three applications for the first demo dam's breed. They are
found in the data, not typed in:
1. a dam and her half-brother, blocked only by the EU close-relative ban;
2. a clean pair within the club quota, waiting for the stud owner;
3. a pair whose sire has no club quota this season (Needs club review).

## Out of scope
- Real submission, user accounts, a database, digital signatures (BankID or similar).
- Litter registration after whelping, microchips, pedigree certificates.
- Changes to the planner, the recommender or the experiments.

## Open questions
- **EU caesarean rule (resolved 21 October 2026).** The Official Journal text confirms it
  (Annex I point 3.5, binding through Art. 16(2)(a)). `eu_max_caesareans` (`max_caesareans`,
  n = 2, HARD, source `eurlex-2026-1818`) is now in the EU profile.
- **The B2B assessment is not in the repository.** Only its title is cited.
- **Quota planning time.** Planning quotas for SYN_L takes about 26 s on a laptop the first time
  a SYN_L dam is chosen. Later choices use the cached result. The same applies to the Mate
  finder, whose quota toggle is now on by default.
