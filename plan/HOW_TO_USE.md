# Breeding Smarter: plan bundle

Planning documents for the BioMedVetMech 2026 proof of concept "Breeding Smarter: A Data-Driven Matching System for Genetic Diversity in Dogs and Beyond".

## Contents
```
CLAUDE.md                      # working rules for Claude Code (goes in the repo root)
plan/00_OVERVIEW.md            # start here: scope, timeline, architecture, stack, conventions
plan/01_P0_setup.md ... 12_P11_conference.md   # one file per phase
plan/STATUS.md                 # progress tracker and HUMAN tasks
plan/HOW_TO_USE.md             # this file
docs/research.md               # domain facts, numbers and citation keys
docs/reference/algorithm_check.py   # verified prototype of the core pedigree algorithms
```

## How to use with Claude Code
1. Create an empty folder for the repo and copy this whole bundle into it (CLAUDE.md at the root).
2. Optionally save the full research report as `docs/research_report_full.md`.
3. Open Claude Code in that folder and say: "Read CLAUDE.md and plan/00_OVERVIEW.md, then start P0 in plan mode."
4. At the end of each phase Claude Code writes a gate report in `plan/gates/` and stops. Review it, then say "Approved, start P1" (and so on).
5. With two people, after P1 run two sessions on separate branches: Track A (P2, P6, P7, P9) and Track B (P3, P4, P5, P8). See `plan/00_OVERVIEW.md` section 3.

## First HUMAN task today
Email info@orthoing.com to confirm a slot at the congress and whether a late full paper (deadline 15 Oct) is possible.
