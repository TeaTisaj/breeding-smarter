# P11: Conference materials

**Goal:** everything needed in Zagreb on 24 to 25 October: poster (printed), slides, live demo plan with fallbacks, partner one-pager, Q&A preparation, and the short paper if the organisers accept a late submission.
**Effort:** 1.5 days. **Depends on:** P8, P9, P10 (paper fast track: P5 and P7).

Folder: `conference/`. All numbers in these materials are pulled from generated files (`targets_vs_simulated.csv`, `summary.csv`), never typed by hand. Claude Code writes a small script `conference/build_numbers.py` that produces `conference/numbers.json`, and every text references those values.

---

## 1. Before anything [HUMAN]
- Confirm the slot type (talk, poster, demo table), talk length, and whether a late full paper is accepted by 15 October. Ask the organisers for the official poster template and the paper template (IFMBE Proceedings, Springer).
- Until confirmed, prepare both poster and slides; they share figures and text.

## 2. Paper fast track (only if a late paper is accepted) [MVP-conditional]
The deadline (15 Oct) falls before the experiments (P8 starts on 15 Oct), and building the experiment runner faster would put the core at risk. So the paper does not depend on P8:
1. Content available by 14 Oct: dataset and validation (P5), engine correctness evidence (T12, T13), rule engine (P6), recommender with a worked case study of the three demo dams (P7).
2. The multi-generation evaluation is described as method and stated as ongoing, with results presented at the congress (and added to the camera-ready version if the organisers allow).
3. Ask the organisers in the same email whether this structure is acceptable for a late submission.

Paper outline (`conference/paper/`), check the length limit in the IFMBE template:
- Title (fixed): "Breeding Smarter: A Data-Driven Matching System for Genetic Diversity in Dogs and Beyond"
- Abstract (as allowed by the template)
- 1 Introduction: purebred inbreeding (F about 0.25 genomic across 227 breeds; popular sires in all 215 KC breeds; 57% of dogs carry a risk variant), EU Regulation 2026/1818, the lookup-vs-decision gap.
- 2 Related work: the tools table (short).
- 3 Methods: synthetic data generation and calibration; pedigree engine (Meuwissen and Luo, Colleau, exact ancestor decomposition); rule engine; scoring; experimental design.
- 4 Results: validation highlights (T05, T07, T11 to T13) and the demo-dam case study; E1 and E2 only in the camera-ready version, if allowed.
- 5 Discussion and limitations: synthetic data, assumptions, pedigree vs genomic relatedness, linear model on grades, policy weights; "and beyond": species-agnostic config.
- 6 Conclusion and call for partners.
- Statements: no animals were used (all data synthetic); data and code availability with DOIs; author contributions; no conflicts.
- References (from `docs/research.md` section 9, formatted to the template).

## 3. Poster [MVP]
Constraints (`docs/research.md` section 1): **90 x 120 cm**, about **300 words** including references, official template, printed by us.
- Claude Code produces the content pack in `conference/poster/`:
  - `text.md` with every text block and an automatic word count (script fails above 300 words).
  - Figures at final print size, 300 dpi, poster font sizes (titles at least 60 pt, body at least 28 pt at 100% scale): Fig A headline, P5 figure 4 (recorded vs true COI), one score card rendered as an image (from the app or matplotlib), a pipeline diagram (data generation, engine, rules, score, experiments) as SVG.
  - QR codes (`qrcode` package): demo URL, dataset DOI, contact (email or LinkedIn).
  - If the template is PPTX: fill it with `python-pptx` (`conference/poster/build_poster.py`), Tea polishes visually. If it is another format, deliver the pack and a layout sketch.
- Layout (top to bottom): title band with authors and FER logo; "The problem" (3 numbers); "Why now" (EU Regulation 2026/1818, one line); "What we built" (pipeline diagram); "Does it work?" (Fig A plus one-sentence result); "Explainable matches" (score card); "Honesty box" (synthetic data, validation table summary); "Partner with us" (QR codes).
- **[HUMAN]** Print by **21 October**, check colours on a test print if possible.

## 4. Slides [MVP]
Claude Code writes `conference/slides/outline.md` (one section per slide: title, on-slide text of at most 25 words, figure, speaker notes of about 80 words). Tea builds the deck in her tool of choice, or asks Claude to build it. Default plan for a 10 to 12 minute talk (adjust to the confirmed length):
1. Title
2. The problem in three numbers
3. Why now: the EU regulation and kennel-club rules
4. The gap: lookup tools vs decision tools (tools table)
5. Our approach (pipeline)
6. Synthetic data you can trust? Calibration and validation (one table, Fig 4 from P5)
7. The engine and the explanation (score card)
8. Live demo (2 to 3 minutes) or video
9. Results: Fig A
10. Results: adoption sweep (Fig E) and the trade-off (Fig D)
11. Limitations, said plainly
12. Call for partners and QR codes

## 5. Demo script [MVP]
`conference/demo_script.md`: exact click path using the demo dams from `configs/demo.yaml`:
1. Breed overview of SYN_S: toggle ground truth, point at the underestimated COI (20 s).
2. Mate finder for demo dam 2: the most popular sire is not on top; open its score card: quota and kinship (60 s).
3. Excluded list: a half-brother blocked by the EU rule (20 s).
4. Score card of the top match: ancestor shares and health matrix (40 s).
5. Simulation results page: Fig A (20 s).
Fallbacks in order: public URL, local app (network off), recorded video ([HUMAN] from P9).

## 6. Partner one-pager [MVP]
`conference/partner_onepager.md` (A4, exported to PDF by Tea or via the Docs/PDF tooling): the problem; what we have (open engine, validated benchmark, demo); what we offer a partner (free pilot: diversity report for one breed, compliance check against EU 2026/1818, mate recommendations); what we need (pedigree, health and DNA data under a data-sharing agreement, or an on-premises run where the code goes to the data and nothing leaves the club); contacts and QR codes. **[HUMAN]** print about 50 copies.

## 7. Q&A preparation [MVP]
`conference/qa.md`: at least 15 likely questions with short answers backed by our files. Must include:
- Why synthetic data? Isn't that circular?
- How do you know the simulated population is realistic?
- How is this different from Mate Select or KoiraNet?
- Pedigree COI vs genomic COI (Embark, Wisdom Panel)?
- Who sets the score weights?
- What about the EU regulation's application dates and the local-breed derogation?
- Does excluding carriers help or hurt?
- How do you handle imports with short pedigrees?
- Data privacy and ownership for kennel clubs?
- Does it work for horses or cats?
- What would a pilot with a kennel club look like, and what does it cost?
- What are the biggest limitations?
- Why HD as a linear model on grades?
- How fast is it on a national registry?
- What is next (thesis, startup, partners)?

## 8. Final checklist for 23 October [HUMAN]
- [ ] Poster printed and in a tube.
- [ ] Laptop: app runs locally with the bundle, network off tested; video on the desktop; slides offline (PDF too).
- [ ] Adapters (HDMI, USB-C), charger.
- [ ] One-pagers printed.
- [ ] Demo URL and DOIs live and checked on a phone (scan every QR code).
- [ ] Rehearsed the talk twice with a timer, and the demo once on the presentation laptop.

## 9. Acceptance checklist (gate)
- [ ] Poster content pack complete, word count at most 300, figures at print resolution, QR codes tested.
- [ ] Slide outline complete with speaker notes; numbers from `numbers.json`.
- [ ] Demo script, one-pager and Q&A written.
- [ ] Paper submitted, or explicitly marked not needed.
