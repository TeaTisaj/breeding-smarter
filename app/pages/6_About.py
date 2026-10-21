"""About and methods: data generation, validation, rules, limitations, partners."""

import components as ui
import streamlit as st

ui.page("About and methods")
bundle = ui.get_bundle()
st.markdown(
    "**Data.** An open, seeded simulator generates three fictional dog breeds (1935 to 2026): "
    "a hidden pre-registry history, a registry founded in 1980, kennels, popular sires, "
    "imports with short foreign pedigrees, disease genes, hip dysplasia and DNA tests. Only "
    "what a kennel club would record goes into the registry tables; the ground truth "
    "(realised inbreeding, true breeding values) is kept separately for validation.\n\n"
    "**Calibration.** Litter sizes, sire concentration, effective population sizes and other "
    "targets come from published studies; every number is cited or marked as an assumption.\n\n"
    "**Engine.** Inbreeding by Meuwissen and Luo (1992), kinship products by Colleau (2002), "
    "an exact additive explanation of each pair's predicted inbreeding by ancestor, mean "
    "kinship, Ne, founder statistics and pedigree completeness.\n\n"
    "**Rules.** EU Regulation 2026/1818, FCI, Kennel Club UK, Raad van Beheer and HKS profiles "
    "in YAML, each with its source and article; unverified rules are marked. EU rules are "
    "checked against the [Official Journal text](https://eur-lex.europa.eu/eli/reg/2026/1818/oj/eng)"
    ".\n\n"
    "**Score.** Weighted sum of inbreeding, litter diversity, Mendelian risk, HD breeding "
    "value, sire use and pedigree depth; weights are breeding priorities for the breed club."
)
val = bundle.validation()
if val is not None:
    st.subheader("Validation: target vs simulated")
    show = val[val["status"].isin(["PASS", "WARN", "FAIL"])]
    st.dataframe(
        show[["id", "breed", "component", "value", "target", "status", "source"]],
        hide_index=True,
        width="stretch",
    )
st.subheader("Rules catalogue")
st.markdown(bundle.rules_catalogue() or "Not available.")
st.subheader("Limitations")
st.markdown(
    "- All data is synthetic; numbers describe our model, not real breeds.\n"
    "- HD is a linear model on grades; allele frequencies are illustrative; no linkage between "
    "loci; registration and import processes are stylised.\n"
    "- Recorded pedigrees underestimate true inbreeding; genomic data is not used yet.\n"
    "- EU 2026/1818 rules not encoded: no breeding before the second oestrus (registries do "
    "not record oestrus), one year of rest after three litters in two years, and a vet check "
    "before breeding a bitch aged 8 or more (Annex I 3.2, 3.4, 3.6).\n"
    "- Score weights are policy choices."
)
st.subheader("Links")
st.markdown(f"Code: {ui.GITHUB} · Dataset and demo data: [release v0.1.0]({ui.RELEASE})")
st.success(
    "**We are looking for partners with real data.** Kennel clubs and breed clubs: a "
    "free pilot gives you a diversity report, an EU 2026/1818 compliance check and mate "
    "recommendations; the code can run on your premises so no data leaves the club. "
    "Contact: Tea Ćetojević Tisaj and Marija Perković, University of Zagreb FER."
)
