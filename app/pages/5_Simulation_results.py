"""Simulation results: does the recommender help? (in-silico, synthetic populations)"""

import components as ui
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from streamlit.errors import StreamlitPageNotFoundError
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
if "E5_coordination" in exps:
    st.subheader("The fix: club quotas on sire use (coordinated planning)")
    st.markdown(
        "Once a season the club planner decides how many litters each sire may have "
        "(optimum contribution selection: lowest expected kinship of the next generation, "
        "at most 5 litters per sire and fewer for highly related sires). Matings are then "
        "chosen within those quotas, either by the planner (least related pairs) or by "
        "breeders from our ranked list (**S3q**). Success criteria were fixed before running."
    )
    e5 = bundle.experiment_table("E5_coordination")
    late = e5[(e5["metric"] == "R_delta_f_late") & (e5["generation"] == 10)]
    keep = ["S0", "S1", "S3", "CC-ocs-mc1", "S3q", "CC-none-mc1"]
    late = late[late["strategy"].isin(keep)].assign(
        rate=lambda d: d["mean"].map(lambda v: f"{100 * v:.2f}%"),
        Ne=lambda d: d["mean"].map(lambda v: f"{1 / (2 * v):.0f}" if v > 0 else "very large"),
    )
    st.dataframe(
        late.pivot_table(
            index="strategy", columns="breed", values=["rate", "Ne"], aggfunc="first"
        ).reindex(keep),
        width="stretch",
    )
    st.caption(
        "Rate of inbreeding per generation and Ne, generations 5 to 10. CC-ocs-mc1 = planner "
        "quotas and least-related pairs; CC-none-mc1 = least-related sire per dam without "
        "quotas. " + CAPTION
    )
    c1, c2 = st.columns(2)
    for col, name, title in (
        (c1, "figG_coordination", "Realised inbreeding with and without quotas"),
        (c2, "figH_factorial", "Contribution control vs mating method"),
    ):
        p = bundle.figure(name)
        if p:
            col.image(str(p), caption=f"{title}. {CAPTION}")
    st.markdown(
        "**Honestly:** quotas beat today's market and the recommender alone in both breeds; "
        "least-related mating without quotas was the worst option; random mating still kept "
        "more diversity in the medium breed."
    )
e9 = ui.e9_means(str(bundle.path))
E9_ROWS = (
    ("Today's market (S1)", "S1"),
    ("Plain club quotas (S3q)", "S3q"),
    ("Quotas + hips budget 0.1% + carrier limit", "S3q-gain010-c050"),
)
if e9 is not None and {sid for _, sid in E9_ROWS} <= set(e9.index):
    st.subheader("Health and hips inside club quotas (E8 to E10)")
    s1 = e9.loc["S1"]
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "strategy": label,
                    "Ne (higher is better)": f"{e9.loc[sid, 'Ne']:.0f}",
                    "Ne vs market": f"{e9.loc[sid, 'Ne'] - s1['Ne']:+.0f}",
                    "hip breeding value (lower is better)": f"{e9.loc[sid, 'HD']:+.2f}",
                    "hips vs market": f"{e9.loc[sid, 'HD'] - s1['HD']:+.2f}",
                    "disease-allele frequency": f"{100 * e9.loc[sid, 'freq']:.1f}%",
                    "disease alleles vs market": (
                        f"{100 * (e9.loc[sid, 'freq'] - s1['freq']):+.1f} points"
                    ),
                }
                for label, sid in E9_ROWS
            ]
        ),
        hide_index=True,
        width="stretch",
    )
    st.markdown(
        "Synthetic medium breed, generation 10, 20 replicates (E9, an independent seed; E8 gave "
        "the same result). Plain quotas protect diversity but let disease alleles rise; adding "
        "a hips budget and a carrier limit beats today's market on diversity, hips and disease "
        "alleles at once. The club chooses the budget on the Club planner.\n\n"
        "**Honestly:** the carrier limit needs most breeders to take part (at 50% the health "
        "gain disappears), and planning on true kinship did not raise diversity here. "
        "Pre-registered criteria and results: `plan/gates/E9_report.md`."
    )
    try:  # page links resolve only in the multipage app started from Home.py
        st.page_link("pages/7_Club_planner.py", label="Open the policy dial", icon="🎚️")
    except StreamlitPageNotFoundError:
        st.caption("The policy dial is on the Club planner page.")
    st.caption(CAPTION)

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
