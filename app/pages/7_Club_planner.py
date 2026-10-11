"""Club planner: litter quotas per sire for the season (P12 coordinated sire use)."""

import components as ui
import pandas as pd
import plotly.express as px
import streamlit as st
from glossary import tip

from breeding_smarter.coordination.club import club_plan

ui.page("Club planner")
ctx = ui.get_context()
st.caption(
    "Club-level planning: quotas decide how often each sire is used; breeders choose within "
    "them. All animals are synthetic."
)
c1, c2, c3, c4 = st.columns(4)
breed = c1.selectbox("Breed", list(ctx.ped.breed_codes), index=len(ctx.ped.breed_codes) - 1)
date = c2.date_input("Season start", pd.Timestamp(ui.DEMO_DATE)).isoformat()
mode = c3.radio("Mode", ["OCS", "cap"], horizontal=True, help=tip("optimum contributions"))
budget = c4.select_slider(
    "Inbreeding budget per generation",
    options=["lowest possible", "1%", "0.5%", "0.25%"],
    value="lowest possible",
    help=tip("inbreeding budget"),
    disabled=mode == "cap",
)
delta_f = None if budget == "lowest possible" or mode == "cap" else float(budget[:-1]) / 100


@st.cache_data(show_spinner="Planning the season...", max_entries=16)
def plan(breed: str, date: str, mode: str, delta_f: float | None):  # type: ignore[no-untyped-def]
    cp = club_plan(ctx, breed, date, mode=mode.lower(), delta_f=delta_f)
    return cp.sires, cp.matings, cp.plan.diagnostics


sires, matings, diag = plan(breed, date, mode, delta_f)
k = st.columns(4)
ui.kpi(k[0], "Dams this season", f"{diag['n_dams']}")
ui.kpi(k[1], "Candidate sires", f"{diag['n_sires']}")
ui.kpi(k[2], "Sires with a quota", f"{diag.get('n_sires_with_quota', 0)}", "club quota")
if "achieved_C" in diag:
    ui.kpi(k[3], "Expected kinship of the litters", f"{diag['achieved_C']:.4f}", "kinship")
if diag.get("infeasible"):
    st.warning("The budget cannot be met this season; the plan uses the lowest kinship possible.")

used = sires[(sires["quota"] > 0) | (sires["litters_last_12m"] > 0)].copy()
long = used.melt(
    id_vars="sire", value_vars=["quota", "litters_last_12m"], var_name="", value_name="litters"
)
long[""] = long[""].map({"quota": "planned quota", "litters_last_12m": "last 12 months"})
order = used.sort_values(["litters_last_12m", "quota"], ascending=False)["sire"].tolist()
fig = px.bar(
    long, x="sire", y="litters", color="", barmode="group",
    category_orders={"sire": order}, title="Litters per sire: planned quota vs last 12 months",
)  # fmt: skip
fig.update_xaxes(showticklabels=False)
st.plotly_chart(fig, width="stretch")
st.markdown("**Sire quotas**", help=tip("club quota"))
st.dataframe(sires, hide_index=True, width="stretch")
with st.expander(f"Suggested matings ({len(matings)} dams, minimum kinship within quotas)"):
    st.dataframe(matings, hide_index=True, width="stretch")
