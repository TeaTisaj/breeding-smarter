"""Shared app pieces: data loading (cached), banner, tiles, badges, score card renderer."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))

from glossary import tip
from theme import STATUS_ICON, TIER_COLOURS

from breeding_smarter.bundle import Bundle
from breeding_smarter.matching import DatasetContext, ScoreCard

BANNER = "Synthetic data: no real dogs. Proof of concept."
DEMO_DATE = "2026-11-01"


def page(title: str) -> None:
    st.set_page_config(page_title=f"{title} · Breeding Smarter", layout="wide")
    banner()
    st.title(title)


def banner() -> None:
    st.warning(f"**{BANNER}**", icon="🧪")


@st.cache_resource(show_spinner="Loading the synthetic registry...")
def get_bundle() -> Bundle:
    return Bundle.open()


@st.cache_resource(show_spinner="Building the pedigree engine context...")
def get_context() -> DatasetContext:
    return get_bundle().context()


def pct(x: float | None, digits: int = 1) -> str:
    return "n/a" if x is None or pd.isna(x) else f"{100 * x:.{digits}f}%"


def tier_badge(tier: str) -> str:
    colour = TIER_COLOURS.get(tier, "#999999")
    return (
        f'<span style="background:{colour};color:#000;padding:2px 8px;border-radius:6px;'
        f'font-weight:600">{tier}</span>'
    )


def rule_badges(rules: list[dict[str, object]]) -> None:
    for r in rules:
        if r["passed"] and not r["warning"]:
            icon, word = STATUS_ICON["pass"], "pass"
        elif r["passed"] or r["severity"] != "HARD":
            icon, word = STATUS_ICON["warn"], "warning"
        else:
            icon, word = STATUS_ICON["fail"], "not permitted"
        if r["severity"] == "INFO" and not r["passed"]:
            icon, word = STATUS_ICON["info"], "info"
        unverified = "" if r["verified"] else " · **unverified**"
        st.markdown(
            f"{icon} **{word}** · `{r['rule_id']}` ({r['severity']}){unverified}: {r['message']}",
            help=None if r["verified"] else tip("unverified"),
        )


def kpi(col, label: str, value: str, help_key: str | None = None) -> None:  # type: ignore[no-untyped-def]
    col.metric(label, value, help=tip(help_key) if help_key else None)


def dam_options(
    ctx: DatasetContext, breed: str | None = None, sex: str = "F", query: str = "", limit: int = 300
) -> list[tuple[str, str]]:
    """(label, reg_no) of living registered animals matching a search string."""
    a = ctx.animals
    m = (a["sex"] == sex) & a["death_date"].isna() & (a["studbook"] != "FOREIGN")
    if breed:
        m &= a["breed_id"] == breed
    if query:
        q = query.lower()
        m &= a["reg_no"].str.lower().str.contains(q) | a["name"].str.lower().str.contains(q)
    sub = a[m].tail(limit)
    return [(f"{n} ({r})", r) for n, r in zip(sub["name"], sub["reg_no"], strict=True)]


def render_card(ctx: DatasetContext, card: ScoreCard, show_litter_tree: bool = True) -> None:
    from breeding_smarter.overview import litter_dot

    st.markdown(f"### {card.sire_label} × {card.dam_label}")
    st.markdown(
        f"{tier_badge(card.tier)} &nbsp; **{card.score:.0f}/100** &nbsp; rules: "
        f"**{card.status.replace('_', ' ').lower()}**",
        unsafe_allow_html=True,
        help=tip("tier"),
    )
    st.markdown(card.headline)
    c1, c2 = st.columns(2)
    with c1:
        comp = pd.DataFrame([c.model_dump() for c in card.components])
        fig = go.Figure(
            go.Bar(
                x=comp["points"],
                y=comp["label"],
                orientation="h",
                marker_color="#0072B2",
                hovertext=comp["raw"] + " (reference " + comp["reference"] + ")",
            )
        )
        fig.update_layout(
            title="Points per component (weight × sub-score)",
            height=320,
            margin=dict(l=10, r=10, t=40, b=10),
            xaxis_title="points of 100",
        )
        st.plotly_chart(fig, width="stretch")
        st.dataframe(
            comp[["label", "raw", "reference", "sub_score", "weight", "points"]],
            hide_index=True,
            width="stretch",
        )
    with c2:
        st.markdown(
            f"**Why this COI?** Predicted COI {pct(card.predicted_coi)} "
            f"(breed average of recent litters {pct(card.breed_mean_litter_coi)})",
            help=tip("predicted COI"),
        )
        if card.ancestors:
            anc = pd.DataFrame([a.model_dump() for a in card.ancestors])
            anc["who"] = anc["name"] + " (" + anc["reg_no"] + ")"
            anc["generations back (sire/dam side)"] = (
                anc["generations_sire_side"].astype("Int64").astype(str)
                + " / "
                + anc["generations_dam_side"].astype("Int64").astype(str)
            )
            fig = go.Figure(
                go.Bar(
                    x=100 * anc["share"],
                    y=anc["who"],
                    orientation="h",
                    marker_color="#D55E00",
                    hovertext=anc["generations back (sire/dam side)"],
                )
            )
            fig.update_layout(
                height=280,
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis_title="share of predicted COI (%)",
                yaxis=dict(autorange="reversed"),
            )
            st.plotly_chart(fig, width="stretch")
            st.caption(f"Other ancestors: {pct(card.other_ancestors_share)}. {card.share_note}")
        else:
            st.info("No common ancestors in the recorded pedigree.")
        if card.depth_warning:
            st.warning(card.depth_warning, icon="⚠")
    st.markdown("**Health (tested loci)**", help=tip("carrier"))
    health = pd.DataFrame([h.model_dump() for h in card.health])
    if len(health):
        health["P(affected puppy)"] = health["p_affected"].map(lambda x: pct(x))
        health["P(carrier puppy)"] = health["p_carrier"].map(lambda x: pct(x))
        st.dataframe(
            health[["locus", "sire_status", "dam_status", "P(affected puppy)", "P(carrier puppy)"]],
            hide_index=True,
            width="stretch",
        )
    st.caption(card.health_note)
    st.markdown("**Rules**")
    rule_badges(card.rules)
    if show_litter_tree:
        with st.expander("Combined pedigree of the planned litter (shared ancestors outlined)"):
            st.graphviz_chart(litter_dot(ctx, card.sire, card.dam, 3))
