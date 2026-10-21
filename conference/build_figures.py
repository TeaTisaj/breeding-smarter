"""Poster figures at print size (300 dpi), score card image, pipeline diagram, QR codes (P11).

Usage: uv run python conference/build_figures.py
"""

from __future__ import annotations

import shutil
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import yaml

from breeding_smarter.calibration import plotstyle

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "conference" / "poster"
CM = 1 / 2.54


def fig4_poster() -> Path:
    from breeding_smarter.calibration.data import RunData
    from breeding_smarter.calibration.metrics import recorded_vs_true_f
    from breeding_smarter.calibration.report import _fig_f_by_year

    tags = yaml.safe_load((ROOT / "configs" / "datasets.yaml").read_text())["datasets"]
    rd = RunData.load(ROOT / "data" / "generated" / tags["v1"]["run_id"])
    plotstyle.apply(poster=True)
    old = plt.rcParams["figure.figsize"]
    plt.rcParams["figure.figsize"] = (80 * CM, 28 * CM)
    _fig_f_by_year(rd, recorded_vs_true_f(rd), OUT)  # writes OUT/fig4_recorded_vs_true_f.*
    plt.rcParams["figure.figsize"] = old
    src = OUT / "fig4_recorded_vs_true_f.png"
    dst = OUT / "fig4_recorded_vs_true_f_poster.png"
    src.replace(dst)
    (OUT / "fig4_recorded_vs_true_f.svg").replace(OUT / "fig4_recorded_vs_true_f_poster.svg")
    return dst


def fig_a_poster() -> Path:
    src = ROOT / "reports" / "experiments" / "E1_headline" / "figures"
    for ext in ("png", "svg"):
        shutil.copy(
            src / f"figA_realised_inbreeding_poster.{ext}",
            OUT / f"figA_realised_inbreeding_poster.{ext}",
        )
    return OUT / "figA_realised_inbreeding_poster.png"


def fig_g_poster() -> Path | None:
    """P12 headline (coordination) figure; replaces Fig A on the poster when it exists."""
    src = ROOT / "reports" / "experiments" / "E5_coordination" / "figures"
    if not (src / "figG_coordination_poster.png").exists():
        return None
    for ext in ("png", "svg"):
        shutil.copy(
            src / f"figG_coordination_poster.{ext}", OUT / f"figG_coordination_poster.{ext}"
        )
    return OUT / "figG_coordination_poster.png"


def fig_n_poster() -> Path | None:
    """E9 policy dial; the poster's result figure when it exists (replaces Fig G)."""
    src = ROOT / "reports" / "experiments" / "E9_hypotheses" / "figures"
    if not (src / "figN_policy_dial_poster.png").exists():
        return None
    for ext in ("png", "svg"):
        shutil.copy(src / f"figN_policy_dial_poster.{ext}", OUT / f"figN_policy_dial_poster.{ext}")
    return OUT / "figN_policy_dial_poster.png"


def scorecard_image() -> Path:
    """Score card of demo dam 2's top match rendered with matplotlib (poster size)."""
    from breeding_smarter.matching import load_context, recommend_sires
    from breeding_smarter.matching.examples import load_demo

    ctx = load_context("v1")
    demo = load_demo()
    d = demo["dams"][1]
    rec = recommend_sires(
        ctx, ctx.idx_of(d["reg_no"]), demo["mating_date"], demo["profile"], top_k=1
    )
    card = rec.card(rec.ranked[0].sire)
    plotstyle.apply(poster=True)
    fig = plt.figure(figsize=(80 * CM, 40 * CM))
    fig.suptitle(
        f"Score card: {card.sire_label} x {card.dam_label}", fontsize=36, x=0.02, ha="left"
    )
    fig.text(
        0.02, 0.88, f"{card.tier} ({card.score:.0f}/100). {card.headline}", fontsize=26, wrap=True
    )
    ax1 = fig.add_axes((0.20, 0.10, 0.28, 0.65))
    comps = card.components
    ax1.barh([c.label for c in comps], [c.points for c in comps], color="#0072B2")
    ax1.invert_yaxis()
    ax1.set_xlabel("points of 100")
    ax1.set_title("Why this score?")
    ax2 = fig.add_axes((0.70, 0.10, 0.28, 0.65))
    anc = card.ancestors
    ax2.barh(
        [a.name for a in anc] + ["other ancestors"],
        [100 * a.share for a in anc] + [100 * card.other_ancestors_share],
        color="#D55E00",
    )
    ax2.invert_yaxis()
    ax2.set_xlabel("share of predicted COI (%)")
    ax2.set_title(f"Why this COI? ({100 * card.predicted_coi:.1f}%)")
    out = OUT / "scorecard"
    plotstyle.save(fig, out, "Synthetic data. Shares of predicted COI add up to 100%.")
    return out.with_suffix(".png")


def qr_codes() -> tuple[list[Path], list[str]]:
    import qrcode

    links = yaml.safe_load((ROOT / "conference" / "links.yaml").read_text())
    targets = {
        "qr_demo": links.get("demo_url", ""),
        "qr_dataset": (
            f"https://doi.org/{links['dataset_doi']}"
            if "TODO" not in str(links.get("dataset_doi", "TODO"))
            else "TODO"
        ),
        "qr_contact": links.get("contact", ""),
    }
    made, missing = [], []
    for name, value in targets.items():
        if not value or "TODO" in str(value):
            missing.append(name)
            continue
        img = qrcode.make(value, box_size=20, border=2)
        p = OUT / f"{name}.png"
        img.save(p)
        made.append(p)
    return made, missing


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    shutil.copy(ROOT / "conference" / "templates" / "pipeline.svg", OUT / "pipeline.svg")
    print("wrote", OUT / "pipeline.svg")
    print("wrote", fig_a_poster())
    print("wrote", fig_g_poster())
    print("wrote", fig_n_poster())
    print("wrote", fig4_poster())
    print("wrote", scorecard_image())
    made, missing = qr_codes()
    for p in made:
        print("wrote", p)
    if missing:
        print(f"QR codes NOT generated (fill conference/links.yaml, then rerun): {missing}")


if __name__ == "__main__":
    main()
