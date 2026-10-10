# P9: Demo app (Streamlit)

**Goal:** an interactive web demo that a vet or kennel-club person understands in two minutes, deployed at a public URL (QR code on the poster), with a local fallback.
**Effort:** 2 days. **Depends on:** P7 (P8 for the results page).

Folder: `app/` (Streamlit multipage). The app contains **no science**: it only calls `breeding_smarter` functions. If you need logic, add it to the package with tests.

---

## 1. Principles
- A banner on every page: "Synthetic data: no real dogs. Proof of concept." Not dismissible.
- Plain language first, numbers second. Every technical term has a tooltip from `app/glossary.py` (COI, kinship, mean kinship, Ne, EBV, EqG, carrier, tier).
- Status is never shown by colour alone (tier label text plus colour; badges with icons and words).
- Percentages with one decimal for COI and kinship.
- Unverified rules show an "unverified" badge with a tooltip explaining why.
- Fast: every page under 3 s warm; mate finder under 2 s.

## 2. Data for the app: demo bundle [MVP]
`bsm export demo-bundle --dataset v1 --experiment <E1 id> --experiment <E2 id>` writes `bundle/`:
registry tables, cached F, D, EqG, per-breed MK reference vectors, validation table, experiment summary tables and figure data, `configs/demo.yaml`, `rules_catalogue.md`, manifest. The app loads the bundle from `BSM_BUNDLE_PATH`; if missing, it downloads the bundle archive from the URL in `BSM_BUNDLE_URL` (Hugging Face dataset repo or GitHub release asset) into a cache folder. Truth tables are included only for the "ground truth" toggles on the breed page (small columns only: `f_true_ibd`, `f_true_pedigree`).

## 3. Pages

### Home [MVP]
Title, one-paragraph pitch (from `00_OVERVIEW.md` 1.1), four cards linking to the pages, dataset version and DOI, team, conference name. Short "How to read this demo" (3 bullets).

### 1 Breed overview [MVP]
- Breed selector.
- KPI tiles: registrations last year, mean COI of last year's litters, Ne (individual dF) and Ne (census) with FKC threshold markers (50 / 200), gene diversity, fe, fg, top-sire share (5 years), number of sires above the FCI 5% threshold.
- Charts (plotly): mean COI per birth year with a toggle **"Show ground truth (only possible with synthetic data)"** that adds true pedigree F and realised IBD (the underestimation story); registrations per year; Lorenz curve of sire use; HD grade shares per period; carrier frequency per tested locus.

### 2 Dog profile [MVP]
- Search box (reg_no or name, `st.selectbox` with search over a breed-filtered list).
- Card: name, reg_no, breed, sex, birth date, kennel, studbook, import flag, COI, EqG, MK, HD grade, DNA results (with "inferred" marker), EBV index and accuracy, number of litters and offspring.
- Pedigree tree, 4 generations, `graphviz` (sire line on top, dam line below), nodes coloured by COI band, repeated ancestors highlighted (same colour outline, label "appears N times").

### 3 Mate finder [MVP, the main page]
1. Choose the dam (default: the 3 demo dams from `configs/demo.yaml` as quick buttons, plus search).
2. Settings: mating date (default 2026-11-01), rule profile (`hr_full` default; `uk_full`, `nl_full`), max distance (off by default), **weights sliders** in an expander with "Reset to default" and a note "Weights are breeding priorities and should be set by the breed club".
3. Result summary line: "N candidate sires, X excluded by rules, Y with warnings."
4. Ranked table (top 20): rank, sire (name and reg_no), tier badge, score, predicted COI, litter diversity, health risk, HD index, sire use, warnings icon.
5. Selecting a row opens the **score card**: headline sentence; component bar chart (points contributed per component); "Why this COI?" bar chart of ancestor shares with names and generations back; combined pedigree of the hypothetical litter (sire and dam trees side by side, shared ancestors highlighted); health matrix; rule badges.
6. Expander "Excluded sires" with the reason for each (for example "Half-brother: prohibited by EU Regulation 2026/1818 (unverified article)").

### 4 Pair check [MVP]
Pick any sire and any dam of the same breed: compliance result and full score card. Useful for audience questions.

### 5 Simulation results [MVP once P8 is done]
- Plain-language explanation of strategies S0 to S4 (one line each).
- Interactive versions of Fig A (headline) and Fig E (adoption sweep); static images of B, C, D, F.
- Summary table at generation 10 with intervals.
- Caption on every chart: "In-silico results on synthetic populations."

### 6 About and methods [MVP]
Methods in short (data generation, calibration, engine, rules, score), validation table (`targets_vs_simulated.csv`) with PASS/WARN status, rules catalogue with verified flags, limitations (bullet list from P10 datasheet), links (GitHub, DOI, Hugging Face), "We are looking for partners with real data" box with contact email.

## 4. Tasks
- **9.1 [MVP]** Demo bundle export (section 2) with a test that the bundle loads into `DatasetContext`.
- **9.2 [MVP]** App skeleton: `app/Home.py`, `app/pages/1_Breed_overview.py` ... `6_About.py`, shared `app/components.py` (banner, KPI tile, tier badge, rule badge, score card renderer), `app/glossary.py`, `app/theme.py` (colours shared with the figures), `.streamlit/config.toml` (theme).
- **9.3 [MVP]** Load context once with `st.cache_resource`; computations cached with `st.cache_data` keyed by inputs.
- **9.4 [MVP]** Pages in this order: Mate finder, Dog profile, Breed overview, Pair check, About, Simulation results.
- **9.5 [MVP]** Deployment: Hugging Face Spaces (Streamlit SDK) with the bundle pulled from the Hugging Face dataset repo, or Streamlit Community Cloud with the bundle from a GitHub release asset. Pick the one that works first; document the steps in `docs/deploy.md`. Accounts and tokens are [HUMAN].
- **9.6 [MVP]** Local fallback: `uv run streamlit run app/Home.py` with the bundle on disk, no network needed. Test it with the network off.
- **9.7 [HUMAN]** Record a 3-minute screen video of the demo flow (P11 demo script) as the last fallback.
- **9.8 [STRETCH]** Croatian UI strings (only if Tea asks), dark mode polish, reverse search page.

## 5. Tests
- `streamlit.testing.v1.AppTest` smoke test for each page on a bundle built from the tiny run: page runs without exceptions; the mate finder returns a table for a fixture dam.
- Glossary covers every term used in tooltips (test scans the page modules for `help=` keys).

## 6. Acceptance checklist (gate)
- [ ] All MVP pages work on dataset v1 locally and on the public URL.
- [ ] Performance targets met (measured, in gate report).
- [ ] Banner visible on every page; no page shows truth data without the explicit toggle.
- [ ] Tea has clicked through the demo script once and approved wording.
