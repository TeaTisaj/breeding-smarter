"""Breed overview: diversity KPIs and trends (with an explicit ground-truth toggle)."""

import components as ui
import plotly.express as px
import streamlit as st

from breeding_smarter.overview import (
    breed_kpis,
    carrier_frequency,
    coi_by_year,
    hd_shares,
    lorenz,
    registrations_per_year,
)

ui.page("Breed overview")
ctx = ui.get_context()
breed = st.selectbox("Breed", list(ctx.ped.breed_codes), index=len(ctx.ped.breed_codes) - 1)


@st.cache_data(show_spinner="Computing breed statistics...")
def kpis(breed: str) -> dict:  # type: ignore[type-arg]
    return breed_kpis(ctx, breed)


k = kpis(breed)
r1 = st.columns(4)
ui.kpi(r1[0], f"Registrations {k['year']}", f"{k['registrations']}")
ui.kpi(r1[1], f"Mean COI of {k['year']} litters", ui.pct(k["mean_coi_last_year"]), "COI")
ui.kpi(
    r1[2],
    "Ne (individual delta F)",
    f"{k['ne_delta_f']:.0f}" + (" (below 50!)" if k["ne_delta_f"] <= 50 else ""),
    "Ne",
)
ui.kpi(
    r1[3],
    "Ne (census)",
    f"{k['ne_census']:.0f}" + (" (at most 200)" if k["ne_census"] <= 200 else ""),
    "Ne census",
)
r2 = st.columns(4)
ui.kpi(r2[0], "Gene diversity", f"{k['gene_diversity']:.3f}", "gene diversity")
ui.kpi(r2[1], "fe / fg", f"{k['fe']:.0f} / {k['fg']:.0f}", "fe")
ui.kpi(r2[2], "Top sire share (5 y)", ui.pct(k["top_sire_share"]), "FCI 5% rule")
ui.kpi(r2[3], "Sires above FCI 5%", f"{k['n_above_fci']}", "FCI 5% rule")
st.caption("FKC strategy flags: Ne from inbreeding at most 50, or census Ne at most 200.")

truth = st.toggle(
    "Show ground truth (only possible with synthetic data)", help=ui.tip("realised IBD")
)
coi = coi_by_year(ctx, breed, ui.get_bundle().truth_small() if truth else None)
cols = [c for c in ("recorded", "true_pedigree", "realised_ibd") if c in coi]
fig = px.line(coi, x="year", y=cols, labels={"value": "mean inbreeding", "variable": ""})
fig.update_yaxes(tickformat=".0%")
fig.update_layout(title="Mean COI per birth year" + (" vs ground truth" if truth else ""))
st.plotly_chart(fig, width="stretch")
if truth:
    st.info(
        "The recorded pedigree starts in 1980 and imports carry short pedigrees, so recorded "
        "COI underestimates true inbreeding. A real registry cannot see this gap; our "
        "synthetic data can."
    )
c1, c2 = st.columns(2)
reg = registrations_per_year(ctx, breed)
c1.plotly_chart(
    px.bar(reg, x="year", y="registrations", title="Registrations per year"), width="stretch"
)
lz = lorenz(ctx, breed, k["year"])
f2 = px.line(lz, x="share_sires", y="share_offspring", title="Lorenz curve of sire use (5 y)")
f2.add_scatter(
    x=[0, 1], y=[0, 1], mode="lines", line=dict(dash="dot", color="grey"), name="equal use"
)
c2.plotly_chart(f2, width="stretch")
c3, c4 = st.columns(2)
hd = hd_shares(ctx, breed)
c3.plotly_chart(
    px.bar(hd, x="period", y=list("ABCDE"), title="HD grades by birth period"), width="stretch"
)
cf = carrier_frequency(ctx, breed, k["year"] + 1)
c4.plotly_chart(
    px.bar(
        cf,
        x="locus",
        y=["carrier", "affected"],
        barmode="group",
        title="Tested animals of the last 10 years",
    ),
    width="stretch",
)
