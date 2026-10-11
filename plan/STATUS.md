# Status

Update this file at the end of every task. Tea reads it to see progress.
Standing instructions for the autonomous run: `plan/GOAL.md` (gates pre-approved by Tea).

| Phase | Status | Gate report | Approved by Tea |
|---|---|---|---|
| P0 Setup | done | [P0](gates/P0_report.md) | pre-approved (GOAL.md) |
| P1 Data model | done | [P1](gates/P1_report.md) | pre-approved (GOAL.md) |
| P2 Pedigree engine | done | [P2](gates/P2_report.md) | pre-approved (GOAL.md) |
| P3 Population simulator | done | [P3](gates/P3_report.md) | pre-approved (GOAL.md) |
| P4 Genetics | done | [P4](gates/P4_report.md) | pre-approved (GOAL.md) |
| P5 Calibration | done | [P5](gates/P5_report.md) | pre-approved (GOAL.md) |
| P6 Rules | done | [P6](gates/P6_report.md) | pre-approved (GOAL.md) |
| P7 Matching | not started | | |
| P8 Experiments | not started | | |
| P9 Demo app | not started | | |
| P10 Release | not started | | |
| P11 Conference | not started | | |

Status values: not started, in progress, at gate (waiting for review), done.

## Task tracker (MVP)

### P0
- [x] 0.1 Project  - [x] 0.2 Tooling  - [x] 0.3 Skeleton  - [x] 0.4 CLI  - [x] 0.5 Repo files  - [x] 0.6 CI  - [x] 0.7 Plan, docs, ADRs  - [x] 0.8 Smoke test

### P1
- [x] 1.1 Schema module  - [x] 1.2 IO  - [x] 1.3 Config framework  - [x] 1.4 Species and breed YAML  - [x] 1.5 Fixtures  - [x] 1.6 Microchip convention (ICAR 999 confirmed)

### P2
- [x] 2.1 Pedigree container  - [x] 2.2 Known-answer tests  - [x] 2.3 Dense oracle  - [x] 2.4 Meuwissen-Luo (+extend, +py twin)  - [x] 2.5 L-rows, pair kinship, decomposition  - [x] 2.6 Colleau  - [x] 2.7 Completeness  - [x] 2.8 Population metrics  - [x] 2.9 Relationships  - [x] 2.10 CLI + cache  - [x] 2.11 Benchmarks

### P3
- [x] 3.1 Configs  - [x] 3.2 SimState  - [x] 3.3 Kennels  - [x] 3.4 Demography  - [x] 3.5 Market  - [x] 3.6 Reproduction  - [x] 3.7 Registry founding and imports  - [x] 3.8 Writer  - [x] 3.9 Run and CLI  - [x] 3.10 Tiny config

### P4
- [x] 4.1 DogGenetics  - [x] 4.2 Gene drop  - [x] 4.3 Mendelian loci  - [x] 4.4 DNA testing  - [x] 4.5 HD trait  - [x] 4.6 BLUP EBVs  - [x] 4.7 Dataset v0  - [ ] 4.8 STRETCH (skipped)

### P5
- [x] 5.1 Targets  - [x] 5.2 Metrics  - [x] 5.3 True-pedigree F  - [x] 5.4 Report and `bsm validate`  - [x] 5.5 Calibration grid (applied)  - [x] 5.6 Dataset v1 frozen (`20261011-default-s42`) + sensitivity

### P6
- [x] 6.1 Models and loader  - [x] 6.2 RuleContext  - [x] 6.3 Rule types  - [x] 6.4 Engine  - [x] 6.5 `bsm check`  - [ ] 6.6 HUMAN verification (checklist generated: docs/rules_verification.md)  - [x] 6.7 Rules catalogue

## HUMAN tasks (Tea or colleague)
- [ ] Email info@orthoing.com: confirm a slot (talk, poster or demo) and whether a late full paper by 15 Oct is possible.
- [ ] Verify EU Regulation 2026/1818 breeding provisions against the EUR-Lex text: work through `docs/rules_verification.md`, fill `article`/`in_application_from` in `configs/rules/eu_2026_1818.yaml`, set `verified: true`, run `uv run bsm rules docs`.
- [ ] Verify HKS rules (`configs/rules/hks_hr.yaml`) against the current Pravilnik o uzgoju (age windows for non-hunting breeds, litter interval).
- [ ] Create GitHub repo and Zenodo account link (see P10).
- [ ] Print poster by 21 Oct (see P11).
- [ ] Look at the key poster figure: `reports/validation/20261011-default-s42/figures/fig4_recorded_vs_true_f.png` (P5).
- [ ] Fill colleague's name (search the repo for `TODO colleague`).
