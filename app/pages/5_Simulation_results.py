"""Simulation results: does the recommender help? (in-silico, synthetic populations)"""

import components as ui
import plotly.graph_objects as go
import streamlit as st
from theme import STRATEGY_COLOURS

CAPTION = "In-silico results on synthetic populations."
LABEL = {
    "S0": "S0 random",
    "S1": "S1 status quo market",
    "S2": "S2 compliant market",
    "S3": "S3 recommender",
    "S4": "S4 coordinated planner",
}

ui.page("Simulation results")
bundle = ui.get_bundle()
exps = bundle.experiments()
if "E1_headline" not in exps:
    st.info("Simulation results are not in this bundle yet.")
    st.stop()
st.markdown(
    "Starting from the 2026 state of the synthetic breeds we simulated 10 more generations "
    "(45 years) under five strategies, with replicates:\n"
    "- **S0 random**: any eligible male, uniformly.\n"
    "- **S1 status quo market**: popular sires, nearby studs, partial avoidance of close "
    "relatives (how breeders behave today in our model).\n"
    "- **S2 compliant market**: S1 plus the EU close-relative ban and a 6.5% COI cap.\n"
    "- **S3 recommender**: each breeder picks one of the top 3 sires of our tool.\n"
    "- **S4 coordinated planner**: the club assigns all matings of the year jointly."
)
summ = bundle.experiment_table("E1_headline")
m2 = summ[(summ["metric"] == "M2_realised_ibd") & (summ["adoption"] == 1.0)]
breed = st.radio("Breed", sorted(m2["breed"].unique()), horizontal=True)
fig = go.Figure()
for sid, g in m2[m2["breed"] == breed].groupby("strategy"):
    g = g.sort_values("generation")
    c = STRATEGY_COLOURS[sid]
    fig.add_scatter(
        x=g["generation"],
        y=100 * g["mean"],
        mode="lines",
        name=LABEL[sid],
        line=dict(color=c, width=3),
    )
    fig.add_scatter(
        x=list(g["generation"]) + list(g["generation"])[::-1],
        y=list(100 * g["hi"]) + list(100 * g["lo"])[::-1],
        fill="toself",
        line=dict(width=0),
        fillcolor=c,
        opacity=0.2,
        showlegend=False,
        hoverinfo="skip",
    )
fig.update_layout(
    title=f"{breed}: realised inbreeding (truth)",
    xaxis_title="generations after 2026",
    yaxis_title="realised inbreeding (%)",
)
st.plotly_chart(fig, width="stretch")
st.caption(CAPTION + " Mean and 95% interval over replicates.")
st.markdown(
    "**What we learned (honestly):** the recommender lowers predicted COI, nearly removes "
    "affected puppies at tested loci and improves hips; but when every breeder picks the "
    "same top sires, long-term diversity (Ne) does not improve, and random mating remains a "
    "strong baseline. Long-term diversity needs coordinated planning of sire use."
)
if "E2_adoption" in exps:
    per = bundle.experiment_table("E2_adoption", "per_generation_replicates.csv.gz")
    d = (
        per[per["metric"] == "M3_delta_f"]
        .groupby("adoption")["value"]
        .agg(["mean", "std", "count"])
    )
    f2 = go.Figure(
        go.Scatter(
            x=100 * d.index,
            y=100 * d["mean"],
            mode="lines+markers",
            error_y=dict(array=196 * d["std"] / d["count"] ** 0.5),
        )
    )
    f2.update_layout(
        title="Adoption sweep (SYN_S): rate of inbreeding vs share of breeders using the tool",
        xaxis_title="breeders using the recommender (%)",
        yaxis_title="rate of inbreeding per generation (%)",
    )
    st.plotly_chart(f2, width="stretch")
    st.caption(CAPTION)
cols = st.columns(2)
for i, (name, title) in enumerate(
    [
        ("figB_ne", "Effective population size"),
        ("figC_disease", "Disease: tested vs untestable variant"),
        ("figD_tradeoff", "Trade-off: HD gain vs inbreeding rate"),
        ("figF_sire_concentration", "Sire concentration"),
    ]
):
    p = bundle.figure(name)
    if p:
        cols[i % 2].image(str(p), caption=f"{title}. {CAPTION}")
t10 = summ[
    (summ["generation"] == 10)
    & (summ["adoption"] == 1.0)
    & summ["metric"].isin(
        ["M2_realised_ibd", "M1_recorded_F", "M3_ne", "M5_he_relative", "M9_top20_share"]
    )
]
t10 = t10.assign(
    value=t10.apply(lambda r: f"{r['mean']:.3g} ({r['lo']:.3g} to {r['hi']:.3g})", axis=1)
)
st.markdown("**Generation 10** (mean and 95% interval)")
st.dataframe(
    t10.pivot_table(index=["breed", "strategy"], columns="metric", values="value", aggfunc="first"),
    width="stretch",
)
st.caption(CAPTION)
