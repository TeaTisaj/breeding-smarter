"""Kennel club desk: mating applications checked before the mating (prototype)."""

import components as ui
import pandas as pd
import plotly.express as px
import streamlit as st
import yaml
from glossary import tip

from breeding_smarter import desk
from breeding_smarter.coordination.club import club_plan
from breeding_smarter.io import configs_dir
from breeding_smarter.matching import recommend_sires
from breeding_smarter.rules import load_profile

PROFILE = "hr_full"
SEASON = ui.DEMO_DATE
RANKED, MANUAL = "Ranked within club quotas", "Enter a sire"

ui.page("Kennel club desk")
st.caption(
    f"{desk.PROTOTYPE_NOTE} A breeder applies for a mating, the stud owner confirms and the "
    "breeding officer decides. Every rule is checked before the mating, and every approved "
    "mating uses one litter of the sire's club quota."
)
ctx = ui.get_context()
demo = ui.get_bundle().demo()


@st.cache_data
def source_refs() -> dict[str, str]:
    data = yaml.safe_load((configs_dir() / "sources.yaml").read_text(encoding="utf-8"))
    return {k: v["ref"] for k, v in data["sources"].items()}


@st.cache_data(show_spinner="Planning this season's club quotas...", max_entries=8)
def season_plan(
    breed: str, date: str, mode: str, delta_f: float | None, carrier: float | None
) -> tuple[list[int], list[int]]:
    cp = club_plan(
        ctx, breed, date, profile=PROFILE, mode=mode.lower(), delta_f=delta_f,
        carrier_factor=carrier,
    )  # fmt: skip
    return [int(s) for s in cp.plan.sires], [int(q) for q in cp.plan.quotas]


def quota_for(breed: str) -> desk.SeasonQuota:
    """Season quota ledger per breed under the club policy set on the Club planner; a new
    policy starts a fresh ledger (a new season plan)."""
    pol = ui.club_policy()
    key = (pol["mode"], pol["delta_f"], pol["carrier"])
    if st.session_state.get("desk_quota_policy") != key:
        st.session_state["desk_quota_policy"] = key
        st.session_state["desk_quotas"] = {}
    quotas = st.session_state["desk_quotas"]
    if breed not in quotas:
        sires, q = season_plan(breed, SEASON, pol["mode"], pol["delta_f"], pol["carrier"])
        quotas[breed] = desk.SeasonQuota.from_plan(sires, q)
    return quotas[breed]


# Plain names for the HARD rules that can block a mating; the id stays in the checks table
RULE_NAME = {
    "base_same_breed": "Sire and dam must be of the same breed",
    "base_alive": "Both parents must be alive on the mating date",
    "eu_close_relatives": "Ban on close-relative matings",
    "eu_dam_min_age": "Minimum age of the dam",
    "eu_dam_litter_frequency": "Maximum number of litters of the dam",
    "fci_registration_type": "Both parents need full registration",
    "hks_hd_exclusion": "Hip dysplasia grade excludes breeding",
    "hks_dam_min_age": "Minimum age of the dam",
    "hks_dam_max_age": "Maximum age of the dam",
    "hks_max_caesareans": "Too many caesarean litters",
    "hks_one_litter_12m": "At most one litter in 12 months",
}


def assess(app: desk.MatingApplication) -> desk.Assessment:
    return desk.assess(ctx, app, PROFILE, quota_for(ctx.breed_of(app.dam)))


@st.cache_data(show_spinner="Ranking candidate sires...", max_entries=32)
def ranked_sires(dam: int, date: str) -> list[tuple[int, float, str]]:
    rec = recommend_sires(ctx, dam, date, PROFILE, top_k=0)
    return [(int(r.sire), float(r.score), r.tier) for r in rec.ranked]


def checks_table(a: desk.Assessment) -> pd.DataFrame:
    refs = source_refs()
    return pd.DataFrame(
        {
            "": [c.symbol for c in a.checks],
            "check": [f"{c.rule_id} ({c.profile})" if c.profile else c.rule_id for c in a.checks],
            "severity": [c.severity for c in a.checks],
            "result": [c.message for c in a.checks],
            "source": [refs.get(c.source, c.source) for c in a.checks],
            "verified": ["yes" if c.verified else "unverified" for c in a.checks],
        }
    )


def show_outcome(a: desk.Assessment) -> None:
    label = desk.OUTCOME_LABEL[a.outcome]
    if a.outcome == desk.Outcome.BLOCKED:
        first = a.failed_hard[0]
        name = RULE_NAME.get(first.rule_id, first.rule_id)
        law = load_profile(first.profile).title if first.profile else ""
        note = f"{law}{'' if first.verified else ' · unverified'}"
        st.error(f"### {label}: {name}\n{note}\n\n{first.message}", icon="⛔")
    elif a.outcome == desk.Outcome.NEEDS_REVIEW:
        st.warning(f"### {label}\n" + "\n".join(f"- {r}" for r in a.reasons), icon="⚠️")
    else:
        st.success(f"### {label}\nAll automatic checks passed.", icon="✅")
    st.markdown("\n".join(f"- {s}" for s in desk.explain(a)))


if "desk_apps" not in st.session_state:
    breed0 = demo["dams"][0]["breed"] if demo["dams"] else ctx.ped.breed_codes[0]
    st.session_state["desk_apps"] = desk.example_applications(
        ctx, quota_for(breed0), breed0, SEASON, PROFILE
    )
apps: list[desk.MatingApplication] = st.session_state["desk_apps"]


NEW = "New application"
STEP_DONE, STEP_WAIT, STEP_NO = "✅", "⏳", "❌"


def app_label(app_id: str) -> str:
    if app_id == NEW:
        return "➕ New application"
    x = next(a for a in apps if a.app_id == app_id)
    status = x.status.value.replace("_", " ").lower()
    return f"{x.app_id}: {ctx.rules.name[x.dam]} x {ctx.rules.name[x.sire]} ({status})"


def application_tab() -> None:
    options = [NEW, *(x.app_id for x in apps)]
    if st.session_state.get("desk_view") not in options:
        st.session_state["desk_view"] = NEW
    view = st.selectbox(
        "Application",
        options,
        format_func=app_label,
        key="desk_view",
        help="Start a new application, or open one to follow it; the stud owner signs it there.",
    )
    if view == NEW:
        new_application_form()
    else:
        application_view(next(x for x in apps if x.app_id == view))


def new_application_form() -> None:
    st.markdown("**1. Dam and mating date**")

    def pick_dam(reg_no: str) -> None:
        st.session_state["desk_dam"] = reg_no

    def load_blocked_demo() -> None:
        ex = next((x for x in apps if x.applicant == "Synthetic breeder 1"), None)
        if ex is not None:
            st.session_state["desk_dam"] = ctx.rules.reg_no[ex.dam]
            st.session_state["desk_sire_mode"] = MANUAL
            st.session_state["desk_sire_query"] = ctx.rules.reg_no[ex.sire]

    cols = st.columns(len(demo["dams"]) + 2)
    for i, d in enumerate(demo["dams"]):
        cols[i].button(
            f"Demo dam {i + 1}: {d['name']} ({d['breed']})",
            on_click=pick_dam,
            args=(d["reg_no"],),
            key=f"desk_demo_dam_{i}",
        )
    cols[-2].button(
        "Demo: dam with her half-brother", on_click=load_blocked_demo, key="desk_demo_blocked"
    )
    with cols[-1]:
        dq = st.text_input("or search a dam", key="desk_dam_query")
    if dq:
        opts = ui.dam_options(ctx, query=dq)
        if opts:
            lab = st.selectbox("matching dams", [o[0] for o in opts], key="desk_dam_pick")
            st.session_state["desk_dam"] = dict(opts)[lab]
        else:
            st.info("No living dam matches.")
    default_dam = demo["dams"][0]["reg_no"] if demo["dams"] else None
    if default_dam is None and apps:
        default_dam = ctx.rules.reg_no[apps[0].dam]
    dam_reg = st.session_state.get("desk_dam", default_dam)
    if dam_reg is None:
        st.info("Choose a dam.")
        return
    dam = ctx.idx_of(dam_reg)
    breed = ctx.breed_of(dam)
    date = st.date_input("Planned mating date", pd.Timestamp(SEASON), key="desk_date").isoformat()
    st.markdown(f"Dam: **{ctx.rules.label(dam)}**, breed {breed}")

    st.markdown("**2. Sire**", help=tip("club quota"))
    st.caption(ui.policy_line())
    quota = quota_for(breed)
    mode = st.radio(
        "How to choose the sire", [RANKED, MANUAL], horizontal=True, key="desk_sire_mode"
    )
    sire: int | None = None
    if mode == RANKED:
        within = [(s, sc, t) for s, sc, t in ranked_sires(dam, date) if quota.remaining(s) > 0]
        if within:
            labels = [
                f"{ctx.rules.label(s)}: {t}, score {sc:.0f}, "
                f"{quota.remaining(s)} of {quota.of(s)} litters left"
                for s, sc, t in within[:15]
            ]
            pick = st.selectbox(
                "Recommended sires with club quota left", labels, key="desk_sire_rank"
            )
            sire = within[labels.index(pick)][0]
        else:
            st.info("No permitted sire has club quota left this season. Enter a sire instead.")
    else:
        sq = st.text_input("Search sire by name or reg. no.", key="desk_sire_query")
        opts = ui.dam_options(ctx, breed, "M", sq)
        if opts:
            lab = st.selectbox(
                "Sire", [o[0] for o in opts], index=len(opts) - 1, key="desk_sire_pick"
            )
            sire = ctx.idx_of(dict(opts)[lab])
        else:
            st.info("No living male of this breed matches.")
    if sire is not None:
        draft_and_submit(dam, sire, date)


def submit(dam: int, sire: int, date: str, applicant: str) -> None:
    """Button callback: record the application and open it (runs before the next rerun)."""
    app = desk.new_application(desk.next_app_id(apps), dam, sire, date, applicant)
    apps.append(app)
    st.session_state["desk_view"] = app.app_id


def confirm(app_id: str) -> None:
    desk.confirm_stud_owner(next(x for x in apps if x.app_id == app_id))


def draft_and_submit(dam: int, sire: int, date: str) -> None:
    st.markdown("**3. Automatic checks**")
    applicant = st.text_input("Applicant (synthetic)", "Synthetic breeder", key="desk_applicant")
    a = assess(desk.new_application("DRAFT", dam, sire, date, applicant))
    show_outcome(a)
    st.dataframe(checks_table(a), hide_index=True, width="stretch")
    st.markdown(
        "**Manual checks for the breeding officer** (documents the registry does not hold):\n"
        + "\n".join(f"- {m.text}" + (" (required here)" if m.conditional else "") for m in a.manual)
    )
    with st.expander("Score card"):
        ui.render_card(ctx, a.card, show_litter_tree=False)

    st.markdown("**4. Submit**")
    blocked = not desk.can_submit(a)
    dup = next(
        (
            x
            for x in apps
            if (x.dam, x.sire, x.mating_date) == (dam, sire, date)
            and x.status != desk.AppStatus.REJECTED
        ),
        None,
    )
    st.button(
        "Submit application",
        disabled=blocked or dup is not None,
        key="desk_submit",
        type="primary",
        on_click=submit,
        args=(dam, sire, date, applicant),
    )
    if blocked:
        st.caption("Submission is disabled: a hard rule fails, so the club cannot accept it.")
    elif dup is not None:
        st.caption(f"This mating is already submitted as {dup.app_id}: open it under Application.")
    else:
        st.caption("After submitting, the application opens here for the stud owner to sign.")


def application_view(app: desk.MatingApplication) -> None:
    """One application: its automatic checks and its steps; the stud owner signs here."""
    a = assess(app)
    head = (
        f"**{app.app_id}**: {ctx.rules.label(app.dam)} x {ctx.rules.label(app.sire)}, "
        f"planned mating {app.mating_date}"
    )
    show_outcome(a)
    with st.expander("All automatic checks"):
        st.dataframe(checks_table(a), hide_index=True, width="stretch")
    st.markdown("**Progress**")
    blocked = a.outcome == desk.Outcome.BLOCKED
    steps = [f"{STEP_DONE} Submitted by {app.applicant}"]
    if app.stud_owner_confirmed:
        steps.append(f"{STEP_DONE} Stud owner confirmed (second signature)")
    elif blocked:
        steps.append(
            f"{STEP_NO} A hard rule fails: the club cannot approve this mating, so no stud "
            "owner signature is needed"
        )
    else:
        steps.append(f"{STEP_WAIT} Waiting for the stud owner's signature")
    if app.status == desk.AppStatus.APPROVED:
        steps.append(
            f"{STEP_DONE} Approved by the breeding officer (certificate in the Breeding officer "
            "queue tab)"
        )
    elif app.status == desk.AppStatus.REJECTED:
        steps.append(f"{STEP_NO} Rejected by the breeding officer")
    elif app.stud_owner_confirmed:
        steps.append(f"{STEP_WAIT} Waiting for the breeding officer (Breeding officer queue tab)")
    text = head + "\n\n" + "\n\n".join(steps)
    if blocked or app.status == desk.AppStatus.REJECTED:
        st.error(text)
    elif app.stud_owner_confirmed:
        st.success(text)
    else:
        st.info(text)
    if app.status == desk.AppStatus.SUBMITTED and not blocked:
        st.button(
            f"Stud owner confirms {app.app_id}",
            key="desk_confirm",
            type="primary",
            on_click=confirm,
            args=(app.app_id,),
        )


def queue_tab() -> None:
    if not apps:
        st.info("No applications yet.")
        return
    assessed = {x.app_id: assess(x) for x in apps}
    st.dataframe(
        pd.DataFrame(
            {
                "application": [x.app_id for x in apps],
                "dam": [ctx.rules.label(x.dam) for x in apps],
                "sire": [ctx.rules.label(x.sire) for x in apps],
                "mating date": [x.mating_date for x in apps],
                "automatic checks": [desk.OUTCOME_LABEL[assessed[x.app_id].outcome] for x in apps],
                "status": [x.status.value for x in apps],
                "stud owner": ["confirmed" if x.stud_owner_confirmed else "-" for x in apps],
            }
        ),
        hide_index=True,
        width="stretch",
    )
    ids = [x.app_id for x in apps]
    if st.session_state.get("desk_pick") not in ids:
        open_ids = [x.app_id for x in apps if x.status != desk.AppStatus.APPROVED]
        st.session_state["desk_pick"] = open_ids[0] if open_ids else ids[0]
    app_id = st.selectbox("Application", ids, key="desk_pick")
    app = next(x for x in apps if x.app_id == app_id)
    a = assessed[app_id]
    st.markdown(
        f"**{app.app_id}**: {ctx.rules.label(app.dam)} x {ctx.rules.label(app.sire)}, "
        f"{app.mating_date}, applicant {app.applicant}, status **{app.status.value}**"
    )
    if app.stud_owner_confirmed:
        st.markdown(f"{STEP_DONE} Stud owner confirmed")
    else:
        st.markdown(
            f"{STEP_WAIT} Stud owner has not confirmed yet (confirmation is in the "
            "Mating application tab)"
        )
    show_outcome(a)
    with st.expander("All automatic checks"):
        st.dataframe(checks_table(a), hide_index=True, width="stretch")
    final = app.status in (desk.AppStatus.APPROVED, desk.AppStatus.REJECTED)
    st.markdown("**Manual checks**")
    for m in a.manual:
        done = st.checkbox(
            m.text, value=m.key in app.manual_done, disabled=final, key=f"desk_m_{app_id}_{m.key}"
        )
        if done:
            app.manual_done.add(m.key)
        else:
            app.manual_done.discard(m.key)
    note = st.text_area("Officer note", app.note, disabled=final, key=f"desk_note_{app_id}")
    over_quota = a.quota_left is not None and a.quota_left <= 0 and not app.booked
    exception = False
    if over_quota and not final and a.outcome != desk.Outcome.BLOCKED:
        exception = st.checkbox(
            "Approve as a club exception over the quota (needs a note; books nothing)",
            key=f"desk_exc_{app_id}",
        )
    ok, why = desk.can_approve(app, a)
    c1, c2 = st.columns(2)
    if c1.button("Approve", disabled=final or not ok, key="desk_approve", type="primary"):
        try:
            desk.approve(app, a, quota_for(ctx.breed_of(app.dam)), note=note, exception=exception)
            st.rerun()
        except desk.DeskError as exc:
            st.error(str(exc))
    if c2.button("Reject", disabled=final, key="desk_reject"):
        desk.reject(app, note)
        st.rerun()
    if not ok and not final:
        st.caption(f"Approve is not possible yet: {why}")
    if app.status == desk.AppStatus.APPROVED:
        st.success("Approved. The mating certificate (prototype) is ready.")
        st.download_button(
            "Download mating certificate (prototype, HTML)",
            desk.certificate_html(app, a, pd.Timestamp.today().date().isoformat()),
            file_name=f"mating_certificate_{app.app_id}.html",
            mime="text/html",
            key=f"desk_cert_{app_id}",
        )


def overview_tab() -> None:
    assessed = {x.app_id: assess(x) for x in apps}
    s = desk.season_summary(apps, assessed)
    k = st.columns(5)
    k[0].metric("Applications", s.applications)
    k[1].metric("Approved", s.approved)
    k[2].metric("Blocked", s.blocked, help="Automatic checks fail a hard rule (any status).")
    k[3].metric("Waiting", s.waiting, help="Open and not blocked.")
    k[4].metric("Rejected", s.rejected)
    k = st.columns(2)
    k[0].metric("Blocked by EU 2026/1818 rules", s.eu_bans)
    k[1].metric("Waiting with no club quota left", s.without_quota, help=tip("club quota"))
    if s.blocked_by_rule:
        source = {
            c.rule_id: c.source for a in assessed.values() for c in a.failed_hard
        }  # one source per rule id
        refs = source_refs()
        st.markdown("**Blocked applications by rule**")
        st.dataframe(
            pd.DataFrame(
                {
                    "rule": list(s.blocked_by_rule),
                    "applications": list(s.blocked_by_rule.values()),
                    "source": [refs.get(source[r], source[r]) for r in s.blocked_by_rule],
                }
            ),
            hide_index=True,
            width="stretch",
        )
    st.markdown("**Club quota per sire this season**", help=tip("club quota"))
    for breed, quota in st.session_state.get("desk_quotas", {}).items():
        usage = desk.quota_usage(ctx, quota)
        if usage.empty:
            continue
        long = usage.melt(
            id_vars="sire", value_vars=["booked", "left"], var_name="status", value_name="litters"
        )
        fig = px.bar(
            long, x="sire", y="litters", color="status", barmode="stack",
            category_orders={"sire": usage["sire"].tolist(), "status": ["booked", "left"]},
            title=f"{breed}: litters booked vs left per sire ({int(usage['booked'].sum())} "
            f"of {int(usage['quota'].sum())} booked)",
        )  # fmt: skip
        fig.update_xaxes(showticklabels=False)
        st.plotly_chart(fig, width="stretch", key=f"desk_quota_chart_{breed}")
    report = desk.compliance_report(ctx, apps, assessed)
    st.download_button(
        "Export compliance report (CSV)",
        report.to_csv(index=False),
        file_name="compliance_report_prototype.csv",
        mime="text/csv",
        key="desk_csv",
    )
    st.caption(f"{desk.PROTOTYPE_NOTE} One row per application, with every rule and its source.")


tab_apply, tab_queue, tab_season = st.tabs(
    ["Mating application", "Breeding officer queue", "Season overview"]
)
with tab_apply:
    application_tab()
with tab_queue:
    queue_tab()
with tab_season:
    overview_tab()
