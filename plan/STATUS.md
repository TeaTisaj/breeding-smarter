# Status

Update this file at the end of every task. Tea reads it to see progress.
Standing instructions for the autonomous run: `plan/GOAL.md` (gates pre-approved by Tea).

**Autonomous run finished 2026-10-11:** all MVP tasks P0 to P11 implemented with gate reports in `plan/gates/`; E3 done. What remains are the HUMAN tasks below (accounts, verification of legal texts, deployment, publishing, printing) and STRETCH items (not started).

**P12 (coordinated sire use) finished 2026-10-11:** all MVP tasks 12.0 to 12.14 done; E5 to E7 run with planned replicates; gate report `plan/gates/P12_report.md` (H1, H2, H4b pass; H3, H4a and SYN_M H5 fail, reported). STRETCH 12.15 not started.

| Phase | Status | Gate report | Approved by Tea |
|---|---|---|---|
| P0 Setup | done | [P0](gates/P0_report.md) | pre-approved (GOAL.md) |
| P1 Data model | done | [P1](gates/P1_report.md) | pre-approved (GOAL.md) |
| P2 Pedigree engine | done | [P2](gates/P2_report.md) | pre-approved (GOAL.md) |
| P3 Population simulator | done | [P3](gates/P3_report.md) | pre-approved (GOAL.md) |
| P4 Genetics | done | [P4](gates/P4_report.md) | pre-approved (GOAL.md) |
| P5 Calibration | done | [P5](gates/P5_report.md) | pre-approved (GOAL.md) |
| P6 Rules | done | [P6](gates/P6_report.md) | pre-approved (GOAL.md) |
| P7 Matching | done | [P7](gates/P7_report.md) | pre-approved (GOAL.md) |
| P8 Experiments | done (incl. E3) | [P8](gates/P8_report.md) | pre-approved (GOAL.md) |
| P9 Demo app | done (deploy is HUMAN) | [P9](gates/P9_report.md) | pre-approved (GOAL.md) |
| P10 Release | done (publishing is HUMAN) | [P10](gates/P10_report.md) | pre-approved (GOAL.md) |
| P11 Conference | done (printing, links, submission are HUMAN) | [P11](gates/P11_report.md) | pre-approved (GOAL.md) |
| P12 Coordination | done | [P12](gates/P12_report.md) | pre-approved (GOAL.md) |

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

### P7
- [x] 7.1 DatasetContext  - [x] 7.2 Candidates  - [x] 7.3 Components  - [x] 7.4 Score  - [x] 7.5 Score card  - [x] 7.6 recommend_sires/score_pair  - [x] 7.6b rank_fast  - [x] 7.7 `bsm match`  - [x] 7.8 Demo dams (`configs/demo.yaml`)

### P8
- [x] 8.0 exp_pairing  - [x] 8.1 Strategies S0-S4 + IncrementalContext  - [x] 8.2 Runner  - [x] 8.3 Checkpointing  - [x] 8.4 Summary  - [x] 8.5 Figures A-F  - [x] 8.6 CLI  - [x] 8.7 Runtime planning (no reduction)  - [x] E3 ablation (run after P11; results appended to the P8 gate report)

### P9
- [x] 9.1 Demo bundle  - [x] 9.2 App skeleton  - [x] 9.3 Caching  - [x] 9.4 Pages  - [ ] 9.5 Deployment (HUMAN, steps in docs/deploy.md)  - [x] 9.6 Local fallback  - [ ] 9.7 Screen video (HUMAN)

### P10
- [x] 10.1 Release package  - [x] 10.2 Datasheet  - [x] 10.3 README  - [x] 10.4 Reproducibility  - [ ] 10.5 GitHub (HUMAN, prepared)  - [ ] 10.6 Zenodo (HUMAN, prepared)  - [ ] 10.7 Hugging Face push (HUMAN token; script ready)  - [x] 10.8 Link placeholders tooling (`bsm links check/fill`)

### P11
- [x] numbers.json + rendered texts  - [ ] Paper (draft ready; submission HUMAN)  - [x] Poster content pack (QR codes wait for links)  - [x] Slides outline  - [x] Demo script  - [x] Partner one-pager  - [x] Q&A

### P12
- [x] 12.0 Solver spike + ADR-007  - [x] 12.1 Sources + config  - [x] 12.2 Targets  - [x] 12.3 OCS  - [x] 12.4 OCS tests  - [x] 12.5 Caps, quotas, allocation, ledger  - [x] 12.6 Planner  - [x] 12.7 Truth kinship  - [x] 12.8 Strategies + runner  - [x] 12.9 Metrics  - [x] 12.10 Experiments E5-E7  - [x] 12.11 Figures G-L  - [x] 12.12 CLI + app  - [x] 12.13 Docs  - [x] 12.14 Conference (conditional)

### Kennel club desk (branch `feature/kennel-club-desk`, spec by Marija Perković)
- [x] B1 Quotas on by default  - [x] B2 `max_caesareans` + HKS/EU rules (unverified)  - [x] B3 `desk.py`  - [x] B4 tabs 1-2 (application, officer queue, 3 examples, certificate)  - [x] B5 Docs (`docs/kennel_club_desk.md`, demo script, changelog)  - [x] B4 tab 3 (season overview, CSV)  - [ ] Freeze from 22 Oct: end-to-end demo rehearsal [HUMAN]

## HUMAN tasks (Tea or colleague)
- [ ] Email info@orthoing.com: confirm a slot (talk, poster or demo) and whether a late full paper by 15 Oct is possible.
- [ ] Verify EU Regulation 2026/1818 breeding provisions against the EUR-Lex text: work through `docs/rules_verification.md`, fill `article`/`in_application_from` in `configs/rules/eu_2026_1818.yaml`, set `verified: true`, run `uv run bsm rules docs`.
- [ ] Verify HKS rules (`configs/rules/hks_hr.yaml`) against the current Pravilnik o uzgoju (age windows for non-hunting breeds, litter interval).
- [ ] Create GitHub repo and Zenodo account link (see P10).
- [ ] Poster: get the official template, paste the blocks from `conference/poster/` (draft layout `poster_draft.pptx`), regenerate QR codes after filling links (`uv run python conference/build_figures.py`), test-print and print by 21 Oct.
- [ ] Decide on the paper: if a late submission is accepted, adapt `conference/paper/draft.md` to the IFMBE template and submit by 15 Oct.
- [ ] Build the slides from `conference/slides/outline.md`; print ~50 copies of `conference/partner_onepager.md`; final checklist in `plan/12_P11_conference.md` section 8.
- [ ] Look at the key poster figure: `reports/validation/20261011-default-s42/figures/fig4_recorded_vs_true_f.png` (P5).
- [ ] Review score card wording: `reports/matching/demo_dams.md` (P7).
- [ ] Deploy the demo app: follow `docs/deploy.md` (Streamlit Community Cloud or Hugging Face Spaces); put the URL in `conference/links.yaml`.
- [ ] Click through the demo once (`uv run streamlit run app/Home.py`) and approve wording; record a 3-minute screen video of `conference/demo_script.md` (P9 task 9.7).
- [x] Fill colleague's name: Marija Perković, FER (2026-10-12). ORCIDs still open (Release step A5).

## Release steps (HUMAN, click by click)
Prepared by Claude Code; nothing has been published.

**A. GitHub (code)**
1. https://github.com/new: name `breeding-smarter`, Public, no README/licence (the repo has them). Create.
2. In the project folder: `git remote add origin git@github.com:<you>/breeding-smarter.git` then `git push -u origin main`.
3. Repo > Actions: enable workflows if asked; the CI run should be green.
4. Before step 6, do B1 (Zenodo integration) so the release gets a DOI.
5. Edit `CITATION.cff`: colleague's name (and ORCIDs).
6. Repo > Releases > Draft a new release: tag `v0.1.0`, title "Breeding Smarter 0.1.0", paste `release/RELEASE_NOTES_v0.1.0.md`, attach `release/breeding-smarter-synthetic-v1.zip` and `bundle.tar.gz` (build them with `uv run bsm export release` and `uv run bsm export demo-bundle --experiment E1_headline --experiment E2_adoption --experiment E5_coordination --experiment E6_budget_and_kinship --experiment E7_adoption_quotas`). Publish.

**B. Zenodo**
1. https://zenodo.org > log in with GitHub > account menu > GitHub > flip the switch for `breeding-smarter` (code DOI is minted when the release in A6 is published).
2. Dataset record: Zenodo > New upload > upload `release/breeding-smarter-synthetic-v1.zip`; Resource type "Dataset"; copy title, creators, description, keywords, licence (CC BY 4.0) from `release/zenodo_metadata.json`; add related identifiers (GitHub URL, code DOI).
3. Click **Reserve DOI** first, copy it into `conference/links.yaml` (`dataset_doi`) so it can go on the poster; publish when ready.
4. Put the code DOI from B1 into `conference/links.yaml` (`code_doi`).

**C. Hugging Face (optional, first to cut)**
1. https://huggingface.co/settings/tokens > New token (write).
2. `export HF_TOKEN=...` then `uv run python scripts/push_hf.py --repo <you>/breeding-smarter-synthetic`.
3. Put the dataset URL into `conference/links.yaml` (`huggingface`).

**D. Fill the links everywhere**
1. Edit `conference/links.yaml` (demo_url from P9 deploy, github, dataset_doi, code_doi, huggingface, contact).
2. `uv run bsm links fill` then `uv run bsm links check` (must print 0 placeholders); rebuild the bundle and the release, commit, push.

