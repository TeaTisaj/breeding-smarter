"""Quick sanity plots of a generated run (P3 acceptance)."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from breeding_smarter.io.parquet import read_table
from breeding_smarter.schema.tables import ANIMALS, LITTERS


def sanity_plots(run_dir: Path, out_dir: Path) -> list[Path]:
    """Registrations per year per breed, litter size histogram, offspring per sire (log)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    a = read_table(run_dir / ANIMALS.filename, ANIMALS)
    lit = read_table(run_dir / LITTERS.filename, LITTERS)
    dom = a[(a["studbook"] != "FOREIGN") & ~a["import_flag"]]
    paths = []
    fig, ax = plt.subplots(figsize=(7, 4))
    for b, g in dom.groupby("breed_id"):
        c = g.groupby(g["birth_date"].dt.year).size()
        ax.plot(c.index.to_numpy(), c.to_numpy(), label=b)
    ax.set(
        xlabel="birth year",
        ylabel="registrations",
        yscale="log",
        title="Registrations per year (synthetic)",
    )
    ax.legend()
    paths.append(out_dir / "registrations_per_year.png")
    fig.savefig(paths[-1], dpi=150, bbox_inches="tight")
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(7, 4))
    for b, g in lit.groupby("breed_id"):
        ax.hist(
            g["n_born"],
            bins=[x + 0.5 for x in range(16)],
            histtype="step",
            density=True,
            label=f"{b} (mean {g['n_born'].mean():.2f})",
        )
    ax.set(xlabel="puppies born", ylabel="share of litters", title="Litter size (synthetic)")
    ax.legend()
    paths.append(out_dir / "litter_size_hist.png")
    fig.savefig(paths[-1], dpi=150, bbox_inches="tight")
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(7, 4))
    off = a[a["sire_idx"].notna()].groupby(["breed_id", "sire_idx"]).size()
    for b in off.index.get_level_values(0).unique():
        c = np.sort(off.loc[b].to_numpy())[::-1]
        ax.loglog(np.arange(1, c.size + 1), c, label=b)
    ax.set(
        xlabel="sire rank",
        ylabel="registered offspring",
        title="Offspring per sire, rank plot (synthetic)",
    )
    ax.legend()
    paths.append(out_dir / "offspring_per_sire.png")
    fig.savefig(paths[-1], dpi=150, bbox_inches="tight")
    plt.close(fig)
    return paths
