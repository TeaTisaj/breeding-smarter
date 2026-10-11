"""Pair check: any sire and dam of the same breed (useful for audience questions)."""

import components as ui
import streamlit as st

from breeding_smarter.matching import score_pair

ui.page("Pair check")
ctx = ui.get_context()
breed = st.selectbox("Breed", list(ctx.ped.breed_codes))
c1, c2 = st.columns(2)
sq = c1.text_input("Search sire")
dq = c2.text_input("Search dam")
sires = ui.dam_options(ctx, breed, "M", sq)
dams = ui.dam_options(ctx, breed, "F", dq)
if not sires or not dams:
    st.info("Search for a living sire and dam of this breed.")
    st.stop()
s_label = c1.selectbox("Sire", [o[0] for o in sires], index=len(sires) - 1)
d_label = c2.selectbox("Dam", [o[0] for o in dams], index=len(dams) - 1)
date = st.date_input("Mating date", __import__("pandas").Timestamp(ui.DEMO_DATE)).isoformat()
profile = st.selectbox("Rule profile", ["hr_full", "uk_full", "nl_full"])
card = score_pair(
    ctx, ctx.idx_of(dict(sires)[s_label]), ctx.idx_of(dict(dams)[d_label]), date, profile
)
ui.render_card(ctx, card)
