# Gate report: P9 Demo app
Date: 2026-10-11

## Acceptance checklist
- [x] All MVP pages work on dataset v1 locally: Home, 1 Breed overview, 2 Dog profile, 3 Mate finder (main page), 4 Pair check, 5 Simulation results, 6 About. Verified with Streamlit `AppTest` on the v1 bundle (no exceptions on any page) and by the test suite on a bundle built from the tiny run (`tests/integration/test_app.py`: every page runs, banner present, mate finder returns a ranked table, glossary covers every tooltip, bundle loads into `DatasetContext`).
- [ ] **Public URL: [HUMAN]** (accounts and tokens). Step-by-step instructions in `docs/deploy.md` (Streamlit Community Cloud with the bundle as a GitHub release asset, or Hugging Face Spaces).
- [x] Performance (v1 bundle, `AppTest`, same machine): first page load 1.7 s (context build), then per page cold / warm: Breed overview 1.1 / 0.11 s, Dog profile 0.19 / 0.02 s, Mate finder 0.24 / 0.04 s, Pair check 0.22 / 0.05 s, Simulation results 0.61 / 0.42 s, About 0.17 / 0.01 s. Targets: every page under 3 s warm, mate finder under 2 s.
- [x] Banner "Synthetic data: no real dogs. Proof of concept." on every page (not dismissible, asserted in tests). Truth data appears only on the Breed overview behind the explicit toggle "Show ground truth (only possible with synthetic data)".
- [ ] **[HUMAN]** Tea clicks through the demo script once and approves the wording. (I could not do a visual check: the Chrome extension was not connected; all pages were exercised headlessly.)

## What was built
- `bundle.py`: `bsm export demo-bundle` writes a run-like `bundle/` (13 MB) plus `bundle.tar.gz` (11 MB): registry tables, F/D/EqG cache, config snapshot, truth extract (idx, f_true_ibd, f_true_pedigree), validation table, experiment summaries and static figures, demo dams, rules catalogue. `Bundle.open()` uses `BSM_BUNDLE_PATH`, then `./bundle`, then downloads `BSM_BUNDLE_URL`.
- `overview.py` (package, no science in the app): breed KPIs, COI by year (with optional truth), registrations, Lorenz curve, HD shares, carrier frequencies, dog profile, pedigree DOT (COI-band colours, repeated ancestors outlined with "appears N times"), combined litter pedigree with shared ancestors highlighted.
- `app/`: `Home.py`, `pages/1..6`, `components.py` (cached bundle and context, banner, KPI tiles, tier and rule badges with "unverified" tooltip, score card renderer with component bars, ancestor-share bars, health matrix, litter pedigree), `glossary.py` (19 terms), `theme.py` (colours shared with figures), `.streamlit/config.toml`.
- Mate finder: 3 demo-dam buttons plus search, mating date, profile (hr_full, uk_full, nl_full), optional distance limit, weight sliders with "Reset to default" and the breed-club note, summary line, top-20 table with row selection opening the score card, excluded sires with reasons.
- `docs/deploy.md`.

## Deviations from the plan (and why)
1. Status is never colour-only: tier badges carry the tier word; rule badges carry an icon and a word (pass, warning, not permitted, info).
2. Dog search uses a text filter plus a select box (at most 300 matches) instead of one select box over all dogs (150k options would be slow).
3. The Simulation results page states the contradicting P8 finding in plain words (recommender helps on disease and short-term COI; long-term diversity needs coordinated planning).
4. Partner contact and links are placeholders (`TODO-CONTACT`, `TODO-DOI`, GitHub `TODO`) to be filled in P10/P11; I did not put a personal email into a public page.
5. 9.6 local fallback: the app runs from `bundle/` with no URL set (that is how the tests run); a true network-off test on the presentation laptop is part of the HUMAN checklist.

## Numbers worth knowing
- Bundle 13 MB (tar.gz 11 MB). App start about 1.7 s.

## Open questions for Tea
- Contact address for the partner box (email or LinkedIn).

## HUMAN tasks waiting
- Deploy (docs/deploy.md), click through the demo, record the 3-minute screen video (task 9.7) once P11 writes the demo script.
