"""Mate finder: ranked, explained candidate sires for a dam (the main demo page)."""

import components as ui
import pandas as pd
import streamlit as st
from glossary import tip

from breeding_smarter.matching import load_scoring, recommend_sires
from breeding_smarter.matching.config import COMPONENTS

ui.page("Mate finder")
ctx = ui.get_context()
bundle = ui.get_bundle()
demo = bundle.demo()

st.markdown("**1. Choose the dam**")
cols = st.columns(len(demo["dams"]) + 1)
for i, d in enumerate(demo["dams"]):
    if cols[i].button(f"Demo dam {i + 1}: {d['name']} ({d['breed']})", help=d["story"]):
        st.session_state["dam"] = d["reg_no"]
with cols[-1]:
    query = st.text_input("or search by name / reg. no.", key="dam_query")
if query:
    opts = ui.dam_options(ctx, query=query)
    if opts:
        label = st.selectbox("matching dams", [o[0] for o in opts])
        st.session_state["dam"] = dict(opts)[label]
    else:
        st.info("No living dam matches.")
dam_reg = st.session_state.get("dam", demo["dams"][0]["reg_no"] if demo["dams"] else None)
if dam_reg is None:
    st.stop()
dam = ctx.idx_of(dam_reg)
st.markdown(f"Dam: **{ctx.rules.label(dam)}**, breed {ctx.breed_of(dam)}")

st.markdown("**2. Settings**")
s1, s2, s3, s4 = st.columns(4)
date = s1.date_input("Mating date", pd.Timestamp(ui.DEMO_DATE)).isoformat()
profile = s2.selectbox("Rule profile", ["hr_full", "uk_full", "nl_full"])
use_dist = s3.checkbox("Limit distance")
max_km = s3.slider("max km", 50, 1000, 300) if use_dist else None
quotas_on = s4.toggle("Respect club quotas", value=True, help=tip("club quota"))
base = load_scoring()
with st.expander("Weights", expanded=False):
    st.caption("Weights are breeding priorities and should be set by the breed club.")
    if st.button("Reset to default"):
        for c in COMPONENTS:
            st.session_state[f"w_{c}"] = float(base.weights.value[c])
    w = {
        c: st.slider(
            c, 0.0, 1.0, float(base.weights.value[c]), 0.05, key=f"w_{c}", help=tip("weights")
        )
        for c in COMPONENTS
    }
scoring = base.with_weights(w) if sum(w.values()) > 0 else base


@st.cache_data(show_spinner="Ranking candidate sires...", max_entries=32)
def run(dam: int, date: str, profile: str, weights: tuple, max_km):  # type: ignore[no-untyped-def]
    sc = base.with_weights(dict(weights))
    rec = recommend_sires(ctx, dam, date, profile, sc, top_k=20, max_distance_km=max_km)
    rows = []
    for i, r in enumerate(rec.ranked[:20], 1):
        c = rec.card(r.sire)
        comp = {x.component: x for x in c.components}
        rows.append(
            {
                "rank": i,
                "sire_idx": int(r.sire),
                "sire": c.sire_label,
                "tier": c.tier,
                "score": round(c.score, 1),
                "predicted COI": ui.pct(c.predicted_coi),
                "litter diversity (MK)": comp["diversity"].raw,
                "health risk": comp["health"].raw,
                "HD index": comp["ebv"].raw,
                "sire use": comp["sire_use"].raw,
                "warnings": "⚠ " + str(len(c.warnings)) if c.warnings else "",
            }
        )
    cards = {i: rec.card(r.sire) for i, r in enumerate(rec.ranked[:20])}
    excluded = [(ctx.rules.label(s), "; ".join(msgs)) for s, msgs in rec.excluded]
    return (
        pd.DataFrame(rows),
        cards,
        excluded,
        rec.n_candidates,
        rec.n_excluded,
        rec.n_with_warnings,
    )


table, cards, excluded, n_c, n_x, n_w = run(dam, date, profile, tuple(sorted(w.items())), max_km)


@st.cache_data(show_spinner="Planning club quotas for the season...", max_entries=8)
def season_quotas(
    breed: str, date: str, mode: str, delta_f: float | None, carrier: float | None
) -> dict[int, int]:
    from breeding_smarter.coordination.club import club_plan

    cp = club_plan(ctx, breed, date, mode=mode.lower(), delta_f=delta_f, carrier_factor=carrier)
    return {int(s): int(q) for s, q in zip(cp.plan.sires, cp.plan.quotas, strict=True)}


if quotas_on and len(table):
    pol = ui.club_policy()
    q = season_quotas(ctx.breed_of(dam), date, pol["mode"], pol["delta_f"], pol["carrier"])
    st.caption(ui.policy_line())
    table["quota left"] = table["sire_idx"].map(lambda s: q.get(int(s), 0))
    keep = table["quota left"] > 0
    st.caption(
        f"Club quotas on: {int((~keep).sum())} of the top {len(table)} sires have no quota left "
        "this season and are hidden."
    )
    cards = {j: cards[int(i)] for j, i in enumerate(table.index[keep])}
    table = table[keep].reset_index(drop=True)
    table["rank"] = range(1, len(table) + 1)
table = table.drop(columns="sire_idx")
st.markdown(f"**3. Result:** {n_c} candidate sires, {n_x} excluded by rules, {n_w} with warnings.")
st.markdown("**4. Ranked sires** (select a row for the score card)", help=tip("tier"))
sel = st.dataframe(
    table,
    hide_index=True,
    width="stretch",
    on_select="rerun",
    selection_mode="single-row",
    key="ranked",
)
rows = sel.selection.rows if sel and sel.selection else []
k = rows[0] if rows else 0
if cards:
    st.divider()
    ui.render_card(ctx, cards[k])
with st.expander(f"Excluded sires ({len(excluded)})"):
    st.dataframe(
        pd.DataFrame(excluded, columns=["sire", "reason"]), hide_index=True, width="stretch"
    )
