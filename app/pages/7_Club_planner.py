"""Club planner: litter quotas per sire for the season (P12) and the policy dial (E9)."""

from pathlib import Path

import components as ui
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from glossary import tip

from breeding_smarter.bundle import Bundle
from breeding_smarter.coordination.club import club_plan

# Budget options = the E9 budget ladder; a budget always comes with the E8/E9 carrier limit
BUDGETS = {
    "lowest possible": None,
    "0.05%": 0.0005,
    "0.1%": 0.001,
    "0.15%": 0.0015,
    "0.25%": 0.0025,
    "0.5%": 0.005,
}
CARRIER_LIMIT = 0.5  # assumption (pre-registered pilot rule, plan/14_E8_health_gain_quotas.md)
DIAL_ARMS = {None: "S3q"} | {
    v: f"S3q-gain{round(v * 1e4):03d}-c050" for v in BUDGETS.values() if v is not None
}

ui.page("Club planner")
ctx = ui.get_context()
st.caption(
    "Club-level planning: quotas decide how often each sire is used; breeders choose within "
    "them. All animals are synthetic."
)
codes = list(ctx.ped.breed_codes)
c1, c2, c3, c4 = st.columns(4)
breed = c1.selectbox("Breed", codes, index=codes.index("SYN_M") if "SYN_M" in codes else 0)
date = c2.date_input("Season start", pd.Timestamp(ui.DEMO_DATE)).isoformat()
mode = c3.radio("Mode", ["OCS", "cap"], horizontal=True, help=tip("optimum contributions"))
budget = c4.select_slider(
    "Inbreeding budget per generation",
    options=list(BUDGETS),
    value="lowest possible",
    help=tip("inbreeding budget")
    + " A budget also switches on the carrier limit: the season's sires may pass on tested "
    "disease alleles at most half as often as the average candidate.",
    disabled=mode == "cap",
)
delta_f = None if mode == "cap" else BUDGETS[budget]
carrier = CARRIER_LIMIT if delta_f is not None else None


@st.cache_data(show_spinner=False)
def dial_table(bundle_path: str) -> pd.DataFrame | None:
    """Generation-10 means per E9 arm (SYN_M): Ne, hip breeding value, disease-allele freq."""
    pr = Bundle(Path(bundle_path)).experiment_table(
        "E9_policy_dial", "per_generation_replicates.csv.gz"
    )
    if pr is None:
        return None
    g = pr[(pr["breed"] == "SYN_M") & (pr["generation"] == 10) & (pr["adoption"] == 1.0)]
    rows = []
    for sid in ["S1", *DIAL_ARMS.values()]:
        sub = g[g["strategy"] == sid]
        if sub.empty:
            continue
        freq = sub[sub["metric"].str.startswith("M6_freq_")].groupby("replicate")["value"].sum()
        rows.append(
            {
                "strategy": sid,
                "Ne": sub[sub["metric"] == "R_ne_f_late"]["value"].mean(),
                "HD": sub[sub["metric"] == "M8_mean_tbv_hd"]["value"].mean(),
                "freq": freq.mean(),
            }
        )
    return pd.DataFrame(rows).set_index("strategy") if rows else None


dial = dial_table(str(ui.get_bundle().path))
arm = DIAL_ARMS[delta_f]
if mode == "OCS" and dial is not None and {"S1", arm} <= set(dial.index):
    st.markdown("#### What this budget buys over 10 generations")
    st.caption(
        "Simulation of the synthetic medium breed (experiment E9): 20 replicates, generation 10 "
        "(about 45 years), compared with today's breeding market. In-silico results."
        + ("" if breed == "SYN_M" else " The projection is shown for SYN_M.")
    )
    sel, s1 = dial.loc[arm], dial.loc["S1"]
    k = st.columns(3)
    k[0].metric(
        "Diversity (Ne)",
        f"{sel['Ne']:.0f}",
        f"{sel['Ne'] - s1['Ne']:+.0f} vs today's market",
        help=tip("Ne"),
    )
    k[1].metric(
        "Hip breeding value",
        f"{sel['HD']:+.2f}",
        f"{sel['HD'] - s1['HD']:+.2f} vs today's market",
        delta_color="inverse",
        help="Mean true genetic value for hip dysplasia of the puppies; lower is better.",
    )
    k[2].metric(
        "Disease-allele frequency",
        f"{100 * sel['freq']:.1f}%",
        f"{100 * (sel['freq'] - s1['freq']):+.1f} points vs today's market",
        delta_color="inverse",
        help=tip("carrier"),
    )
    ladder = dial.loc[[a for a in DIAL_ARMS.values() if a in dial.index and a != "S3q"]]
    names = {a: label for label, v in BUDGETS.items() for a in [DIAL_ARMS[v]]}
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=ladder["Ne"],
            y=ladder["HD"],
            mode="lines+markers+text",
            text=[names[a] for a in ladder.index],
            textposition="top center",
            name="budget + carrier limit",
            marker={"size": 10, "color": "#0072B2"},
            line={"color": "#0072B2"},
        )
    )
    for sid, label, colour, symbol in (
        ("S1", "today's market", "#D55E00", "square"),
        ("S3q", "plain quotas", "#56B4E9", "diamond"),
    ):
        if sid in dial.index:
            fig.add_trace(
                go.Scatter(
                    x=[dial.loc[sid, "Ne"]],
                    y=[dial.loc[sid, "HD"]],
                    mode="markers",
                    name=label,
                    marker={"size": 13, "color": colour, "symbol": symbol},
                )
            )
    fig.add_trace(
        go.Scatter(
            x=[sel["Ne"]],
            y=[sel["HD"]],
            mode="markers",
            name="your choice",
            marker={"size": 24, "color": "rgba(0,0,0,0)", "line": {"width": 3, "color": "#111"}},
        )
    )
    fig.update_layout(
        title="Diversity vs hips for each budget (lower hip value is better)",
        xaxis_title="Ne (higher is better)",
        yaxis_title="hip breeding value (lower is better)",
        height=420,
        margin={"t": 60, "b": 40},
    )
    st.plotly_chart(fig, width="stretch")
    st.markdown("#### This season's quotas")


@st.cache_data(show_spinner="Planning the season...", max_entries=16)
def plan(breed: str, date: str, mode: str, delta_f: float | None, carrier: float | None):  # type: ignore[no-untyped-def]
    cp = club_plan(ctx, breed, date, mode=mode.lower(), delta_f=delta_f, carrier_factor=carrier)
    return cp.sires, cp.matings, cp.plan.diagnostics


sires, matings, diag = plan(breed, date, mode, delta_f, carrier)
k = st.columns(4)
ui.kpi(k[0], "Dams this season", f"{diag['n_dams']}")
ui.kpi(k[1], "Candidate sires", f"{diag['n_sires']}")
ui.kpi(k[2], "Sires with a quota", f"{diag.get('n_sires_with_quota', 0)}", "club quota")
if "achieved_C" in diag:
    ui.kpi(k[3], "Expected kinship of the litters", f"{diag['achieved_C']:.4f}", "kinship")
if diag.get("infeasible"):
    st.warning("The budget cannot be met this season; the plan uses the lowest kinship possible.")
if diag.get("carrier_relaxed"):
    st.info("The carrier limit could not be met this season and was relaxed.")

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
