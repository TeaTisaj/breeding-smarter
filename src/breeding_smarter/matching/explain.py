"""Explainable score card for one sire x dam pair (P7 task 7.5)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from breeding_smarter.matching.components import Components
from breeding_smarter.matching.config import COMPONENTS, ScoringConfig
from breeding_smarter.matching.context import BreedReference, DatasetContext
from breeding_smarter.pedigree import pair_kinship_decomposed
from breeding_smarter.pedigree.relationships import ancestor_depths
from breeding_smarter.rules.engine import ComplianceResult

SHARE_TEXT = (
    "Each ancestor's share is the part of the predicted inbreeding that traces to genetic "
    "variation originating in that ancestor; shares add up to 100%."
)
LABELS = {
    "inbreeding": "Predicted inbreeding (COI)",
    "diversity": "Litter diversity (mean kinship)",
    "health": "Mendelian health risk",
    "ebv": "HD breeding value",
    "sire_use": "Sire use (FCI 5% rule)",
    "depth": "Pedigree depth (EqG)",
}
GENO = ("clear", "carrier", "affected")


class ComponentRow(BaseModel):
    component: str
    label: str
    raw: str
    reference: str
    sub_score: float
    weight: float
    points: float


class AncestorShare(BaseModel):
    idx: int
    reg_no: str
    name: str
    generations_sire_side: int | None
    generations_dam_side: int | None
    contribution: float
    share: float


class HealthRow(BaseModel):
    locus: str
    sire_status: str
    dam_status: str
    p_affected: float
    p_carrier: float


class ScoreCard(BaseModel):
    sire: int
    dam: int
    sire_label: str
    dam_label: str
    breed: str
    mating_date: str
    score: float
    tier: str
    status: str
    headline: str
    components: list[ComponentRow]
    predicted_coi: float
    breed_mean_litter_coi: float
    ancestors: list[AncestorShare]
    other_ancestors_share: float
    share_note: str = SHARE_TEXT
    depth_warning: str | None
    health: list[HealthRow]
    health_note: str
    rules: list[dict[str, Any]]
    excluded: bool
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json")

    def to_markdown(self) -> str:
        lines = [
            f"## Score card: {self.sire_label} x {self.dam_label}",
            "",
            f"*Synthetic data. Breed {self.breed}, mating date {self.mating_date}.*",
            "",
            f"**{self.tier}** ({self.score:.0f}/100, rules: {self.status}). {self.headline}",
            "",
            "| Component | Raw value | Breed reference | Sub-score | Weight | Points |",
            "|---|---|---|---|---|---|",
        ]
        for c in self.components:
            lines.append(
                f"| {c.label} | {c.raw} | {c.reference} | {c.sub_score:.2f} | "
                f"{c.weight:.2f} | {c.points:.1f} |"
            )
        lines += ["", f"### Why this COI? ({100 * self.predicted_coi:.1f}%)", ""]
        if self.ancestors:
            lines += [
                "| Ancestor | Generations back (sire side / dam side) | Share |",
                "|---|---|---|",
            ]
            for a in self.ancestors:
                g = f"{a.generations_sire_side or '-'} / {a.generations_dam_side or '-'}"
                lines.append(f"| {a.name} ({a.reg_no}) | {g} | {100 * a.share:.1f}% |")
            lines.append(f"| other ancestors | | {100 * self.other_ancestors_share:.1f}% |")
            lines += ["", self.share_note]
        else:
            lines.append("No common ancestors in the recorded pedigree.")
        if self.depth_warning:
            lines += ["", f"**Warning:** {self.depth_warning}"]
        lines += [
            "",
            "### Health (tested loci)",
            "",
            "| Locus | Sire | Dam | P(affected puppy) | P(carrier puppy) |",
            "|---|---|---|---|---|",
        ]
        for h in self.health:
            lines.append(
                f"| {h.locus} | {h.sire_status} | {h.dam_status} | "
                f"{100 * h.p_affected:.1f}% | {100 * h.p_carrier:.1f}% |"
            )
        lines += ["", self.health_note, "", "### Rules", ""]
        for r in self.rules:
            ok = "pass" if r["passed"] and not r["warning"] else ("warn" if r["passed"] else "FAIL")
            badge = "" if r["verified"] else " [unverified]"
            lines.append(
                f"- {ok.upper()} `{r['rule_id']}` ({r['severity']}){badge}: {r['message']}"
            )
        return "\n".join(lines) + "\n"


def _status_text(ctx: DatasetContext, i: int, j: int) -> str:
    g = int(ctx.geno[i, j])
    if g < 0:
        return "unknown"
    return f"{GENO[g]} (inferred)" if ctx.inferred[i, j] else f"{GENO[g]} (tested)"


def _phrase(c: str, good: bool, comp: Components, ref: BreedReference, k: int) -> str:
    f = comp.f_off[k]
    if c == "inbreeding":
        rel = f"{100 * f:.1f}% vs breed average {100 * ref.mean_litter_f:.1f}%"
        return f"low predicted inbreeding ({rel})" if good else f"high predicted inbreeding ({rel})"
    if c == "diversity":
        return (
            "the litter adds genetic diversity (low mean kinship)"
            if good
            else "the litter adds little diversity (high mean kinship)"
        )
    if c == "health":
        return (
            "low Mendelian disease risk"
            if good
            else f"risk of affected puppies ({100 * comp.p_any[k]:.0f}%)"
        )
    if c == "ebv":
        idx = comp.ebv_mean[k]
        return f"good HD index ({idx:.0f})" if good else f"HD index below average ({idx:.0f})"
    if c == "sire_use":
        r = 100 * comp.sire_use_ratio[k]
        return (
            "an under-used sire" if good else f"a heavily used sire ({r:.0f}% of the FCI 5% limit)"
        )
    return "a deep recorded pedigree" if good else "a shallow recorded pedigree"


def headline(comp: Components, ref: BreedReference, k: int, scoring: ScoringConfig) -> str:
    """Template summary from the strongest positive and negative components."""
    w = scoring.weights.value
    active = [c for c in COMPONENTS if w[c] > 0]
    pos = sorted(
        (c for c in active if comp.sub[c][k] >= 0.7), key=lambda c: -w[c] * comp.sub[c][k]
    )[:2]
    neg = sorted(
        (c for c in active if comp.sub[c][k] < 0.5), key=lambda c: -w[c] * (1 - comp.sub[c][k])
    )[:1]
    parts = []
    if pos:
        parts.append(" and ".join(_phrase(c, True, comp, ref, k) for c in pos))
    if neg:
        parts.append(_phrase(neg[0], False, comp, ref, k))
    text = "; ".join(parts) if parts else "no component stands out"
    return text[0].upper() + text[1:] + "."


def _raw(c: str, comp: Components, ref: BreedReference, k: int) -> tuple[str, str]:
    if c == "inbreeding":
        return f"{100 * comp.f_off[k]:.1f}%", f"{100 * ref.mean_litter_f:.1f}% (recent litters)"
    if c == "diversity":
        return f"{100 * comp.mk_off[k]:.2f}%", f"{100 * ref.mean_mk:.2f}% (mean MK)"
    if c == "health":
        return f"{100 * comp.p_any[k]:.1f}% affected", "tested loci, breed frequencies"
    if c == "ebv":
        miss = " (missing EBV counted as 100)" if comp.ebv_missing[k] else ""
        return f"{comp.ebv_mean[k]:.0f}{miss}", "100 (breed mean)"
    if c == "sire_use":
        return (
            f"{comp.sire_offspring_5y[k]:.0f} pups ({100 * comp.sire_use_ratio[k]:.0f}%)",
            "100% = FCI 5% in 5 years",
        )
    return f"{comp.depth[k]:.1f}", "target 6 generations"


def build_card(
    ctx: DatasetContext,
    dam: int,
    k: int,
    comp: Components,
    ref: BreedReference,
    scoring: ScoringConfig,
    score: float,
    tier: str,
    compliance: ComplianceResult,
    mating_date: str,
) -> ScoreCard:
    sire = int(comp.sires[k])
    w = scoring.weights.value
    pts = comp.points(scoring, k)
    rows = []
    for c in COMPONENTS:
        raw, refv = _raw(c, comp, ref, k)
        rows.append(
            ComponentRow(
                component=c,
                label=LABELS[c],
                raw=raw,
                reference=refv,
                sub_score=float(comp.sub[c][k]),
                weight=w[c],
                points=pts[c],
            )
        )
    dec = pair_kinship_decomposed(ctx.ped, ctx.F, ctx.D, sire, dam)
    total = sum(dec.values())
    ds = ancestor_depths(ctx.ped, sire, 30)
    dd = ancestor_depths(ctx.ped, dam, 30)
    top = sorted(dec.items(), key=lambda kv: -kv[1])[:5]
    ancestors = [
        AncestorShare(
            idx=j,
            reg_no=str(ctx.rules.reg_no[j]),
            name=str(ctx.rules.name[j]),
            generations_sire_side=ds[j] + 1 if j in ds else None,
            generations_dam_side=dd[j] + 1 if j in dd else None,
            contribution=c,
            share=c / total if total > 0 else 0.0,
        )
        for j, c in top
        if c > 0
    ]
    other = 1.0 - sum(a.share for a in ancestors) if total > 0 else 0.0
    low = scoring.low_depth_warning_eqg.value
    depth_warning = None
    if min(ctx.eqg[sire], ctx.eqg[dam]) < low:
        depth_warning = (
            "Recorded inbreeding is probably underestimated (shallow pedigree, "
            "for example an import)."
        )
    health = [
        HealthRow(
            locus=lc,
            sire_status=_status_text(ctx, sire, j),
            dam_status=_status_text(ctx, dam, j),
            p_affected=float(comp.p_aff[k, j]),
            p_carrier=float(comp.p_carrier[k, j]),
        )
        for j, lc in enumerate(ctx.loci)
    ]
    rules = [r.model_dump(mode="json") for r in compliance.results]
    warnings = [r.message for r in compliance.warnings]
    if depth_warning:
        warnings.append(depth_warning)
    return ScoreCard(
        sire=sire,
        dam=dam,
        sire_label=ctx.rules.label(sire),
        dam_label=ctx.rules.label(dam),
        breed=ctx.breed_of(dam),
        mating_date=mating_date,
        score=score,
        tier=tier,
        status=str(compliance.status),
        headline=headline(comp, ref, k, scoring),
        components=rows,
        predicted_coi=float(comp.f_off[k]),
        breed_mean_litter_coi=ref.mean_litter_f,
        ancestors=ancestors,
        other_ancestors_share=max(0.0, other),
        depth_warning=depth_warning,
        health=health,
        health_note=(
            "Allele frequencies for untested parents are estimated from tested animals "
            "born in the last 10 years; who gets tested biases them. Only tested loci "
            "are shown; untestable variants cannot be scored."
        ),
        rules=rules,
        excluded=bool(compliance.failed_hard),
        warnings=warnings,
    )
