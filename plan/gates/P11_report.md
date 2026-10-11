# Gate report: P11 Conference materials
Date: 2026-10-11

All numbers in the materials come from `conference/numbers.json`, built by
`conference/build_numbers.py` from the v1 validation table, the experiment summaries, the
engine benchmark, the demo dams and literature facts with citation keys. Texts are rendered
from `conference/templates/` by `conference/build_texts.py`; nothing is typed by hand.

## Acceptance checklist
- [x] Poster content pack complete (`conference/poster/`): `text.md` (**207 words** including
  references; the build fails above 300, also tested), figures at print resolution (300 dpi,
  poster fonts 28 pt base): `figA_realised_inbreeding_poster.png/.svg` (headline),
  `fig4_recorded_vs_true_f_poster.png/.svg` (recorded vs true COI), `scorecard.png/.svg`
  (score card of demo dam 2's top match), `pipeline.svg`; a draft 90 x 120 cm layout
  `poster_draft.pptx` (fits in 109 cm; layout sketch until the official template arrives).
- [ ] QR codes tested: **waiting for links** (demo URL, dataset DOI, contact are HUMAN steps).
  `build_figures.py` refuses to make QR codes from TODO placeholders; after
  `conference/links.yaml` is filled, rerun it and scan every code with a phone (HUMAN).
- [x] Slide outline complete with speaker notes (`conference/slides/outline.md`: 12 slides,
  on-slide text and about 80-word notes each, numbers from numbers.json).
- [x] Demo script (`conference/demo_script.md`), partner one-pager
  (`conference/partner_onepager.md`), Q&A (`conference/qa.md`, 17 questions including all 15
  required ones and two on our own contradicting result).
- [ ] Paper: **draft prepared** (`conference/paper/draft.md`, IFMBE fast-track structure with
  the experiments included); submission depends on the organisers accepting a late paper
  (HUMAN email). Not marked as "not needed" because the answer is not known.

## Deviations from the plan (and why)
1. The poster is a PPTX layout sketch generated with python-pptx without the official template
   (not yet received); blocks and figures are ready to paste into the template.
2. The paper draft already includes the experiment results (P8 finished before the 15 October
   deadline), which the fast track allowed to omit.
3. The poster and slides state the contradicting P8 result plainly (random mating keeps Ne
   highest; long-term diversity needs coordinated sire use).
4. The "problem" numbers use the mean genomic F 0.249 from `docs/research.md` section 3.

## Open questions for Tea
- Slot type and talk length (outline assumes 10 to 12 minutes).
- Is the honest framing of the experiment result acceptable for the poster headline?

## HUMAN tasks waiting
- Email organisers (slot, late paper, poster and paper templates).
- Fill `conference/links.yaml`, run `uv run bsm links fill`, rebuild numbers, texts, figures
  (QR codes) and the poster; scan the QR codes.
- Paste the poster blocks into the official template; print by 21 October.
- Build the slide deck from `conference/slides/outline.md` (or ask Claude to build it).
- Print about 50 one-pagers; rehearse twice; test the demo offline on the presentation laptop.
