"""Shared figure style (validation, experiments, poster). Colourblind-safe (Okabe-Ito)."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

OKABE_ITO = ["#0072B2", "#E69F00", "#009E73", "#D55E00", "#CC79A7", "#56B4E9", "#F0E442", "#000000"]
BREED_COLOURS = {"SYN_L": "#0072B2", "SYN_M": "#E69F00", "SYN_S": "#009E73"}
STRATEGY_COLOURS = {
    "S0": "#999999",
    "S1": "#D55E00",
    "S2": "#E69F00",
    "S3": "#0072B2",
    "S4": "#009E73",
    "S5": "#CC79A7",
    "S3hc": "#56B4E9",
    "S3xc": "#000000",
    # P12: one hue per contribution-control family; mating method is the line style
    "CC-none-rand": "#666666",
    "CC-none-mc1": "#666666",
    "CC-mkx-rand": "#8C6D00",
    "CC-mkx-mc1": "#8C6D00",
    "CC-cap-rand": "#E69F00",
    "CC-cap-mc1": "#E69F00",
    "CC-ocs-rand": "#009E73",
    "CC-ocs-mc1": "#009E73",
    "CC-ocs-mc1-oracle": "#000000",
    "CC-gain100-mc1": "#E8A5CF",
    "CC-gain050-mc1": "#CC79A7",
    "CC-gain025-mc1": "#9C3F7A",
    "CC-gain010-mc1": "#5E1A48",
    "S3q": "#56B4E9",
    # E8: S3q + carrier limit (green), + gain OCS (purple), both (blue)
    "S3q-c050": "#009E73",
    "S3q-gain010": "#CC79A7",
    "S3q-gain025": "#CC79A7",
    "S3q-gain010-c050": "#0072B2",
}
SYNTHETIC_NOTE = "Synthetic data (no real dogs)."


def apply(poster: bool = False) -> None:
    base = 28 if poster else 10  # poster: at least 28 pt at 100% print scale (P11)
    plt.rcParams.update(
        {
            "font.size": base,
            "axes.titlesize": base + 2,
            "axes.labelsize": base,
            "legend.fontsize": base - 1,
            "xtick.labelsize": base - 1,
            "ytick.labelsize": base - 1,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.3,
            "svg.hashsalt": "breeding-smarter",
            "savefig.dpi": 300,
        }
    )


def save(fig: Figure, path_stem: Path, note: str = SYNTHETIC_NOTE) -> list[Path]:
    """Save PNG (300 dpi) and SVG with a small provenance note; returns both paths."""
    if note:
        fig.text(0.99, -0.02, note, ha="right", va="top", fontsize=7, color="#555555")
    path_stem.parent.mkdir(parents=True, exist_ok=True)
    out = []
    for ext in ("png", "svg"):
        p = path_stem.with_suffix(f".{ext}")
        fig.savefig(p, bbox_inches="tight", metadata={"Date": None} if ext == "svg" else None)
        out.append(p)
    plt.close(fig)
    return out
