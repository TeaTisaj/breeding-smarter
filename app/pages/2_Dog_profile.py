"""Dog profile: registry card and 4-generation pedigree."""

import components as ui
import streamlit as st
from glossary import tip

from breeding_smarter.overview import COI_BANDS, dog_profile, pedigree_dot

ui.page("Dog profile")
ctx = ui.get_context()
c1, c2, c3 = st.columns([1, 1, 2])
breed = c1.selectbox("Breed", list(ctx.ped.breed_codes))
sex = c2.selectbox("Sex", ["F", "M"])
query = c3.text_input("Search name or reg. no.")
opts = ui.dam_options(ctx, breed, sex, query)
if not opts:
    st.info("No living dog matches.")
    st.stop()
label = st.selectbox("Dog", [o[0] for o in opts], index=len(opts) - 1)
idx = ctx.idx_of(dict(opts)[label])
p = dog_profile(ctx, idx, ui.DEMO_DATE)

st.subheader(f"{p['name']} ({p['reg_no']})")
k = st.columns(6)
ui.kpi(k[0], "COI", ui.pct(p["coi"]), "COI")
ui.kpi(k[1], "Pedigree depth (EqG)", f"{p['eqg']:.1f}", "EqG")
ui.kpi(k[2], "Mean kinship", ui.pct(p["mean_kinship"], 2), "mean kinship")
ui.kpi(k[3], "HD grade", p["hd_grade"], "HD")
ebv = "n/a" if p["ebv_index"] is None else f"{p['ebv_index']:.0f} (acc. {p['ebv_accuracy']:.2f})"
ui.kpi(k[4], "HD index (EBV)", ebv, "EBV")
ui.kpi(k[5], "Litters / offspring", f"{p['n_litters']} / {p['n_offspring']}")
st.markdown(
    f"Breed {p['breed']} · sex {p['sex']} · born {p['birth_date']} · studbook "
    f"{p['studbook']}{' · import' if p['import'] else ''} · {p['registration_type']} "
    f"registration"
)
st.markdown("**DNA results**", help=tip("carrier"))
st.write({k: v for k, v in p["dna"].items()})
st.markdown(
    "**Pedigree (4 generations)**: sire line on top; colour = COI band; ancestors "
    "that appear more than once share an outline colour."
)
st.graphviz_chart(pedigree_dot(ctx, idx, 4))
st.caption(
    "COI bands: "
    + ", ".join(f"{name}" for _, _, name in COI_BANDS)
    + " (green, yellow, orange, red)."
)
