"""Breed overview, dog profile and pedigree-tree data for the demo app (P9).

Pure functions on a `DatasetContext` (plus the small truth extract for the explicit
"ground truth" toggle). The app only renders what these return.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from breeding_smarter.matching.context import DatasetContext
from breeding_smarter.pedigree import population_report
from breeding_smarter.pedigree.population import gini, offspring_per_sire
from breeding_smarter.rules.context import ALIVE, GRADES

COI_BANDS = [
    (0.0625, "#009E73", "below 6.25%"),
    (0.125, "#F0E442", "6.25 to 12.5%"),
    (0.25, "#E69F00", "12.5 to 25%"),
    (1.01, "#D55E00", "25% or more"),
]


def _year(day: np.ndarray) -> np.ndarray:
    return np.asarray(day, dtype="datetime64[D]").astype("datetime64[Y]").astype(int) + 1970


def breed_mask(ctx: DatasetContext, breed: str, domestic: bool = True) -> np.ndarray:
    m = ctx.ped.breed == ctx.ped.breed_codes.index(breed)
    if domestic:
        m &= ~ctx.is_foreign
    return np.asarray(m)


def last_full_year(ctx: DatasetContext) -> int:
    return int(_year(ctx.rules.birth_day[ctx.rules.birth_day < ALIVE]).max()) - 1


def registrations_per_year(ctx: DatasetContext, breed: str) -> pd.DataFrame:
    y = _year(ctx.rules.birth_day[breed_mask(ctx, breed)])
    s = pd.Series(y).value_counts().sort_index()
    return pd.DataFrame({"year": s.index.astype(int), "registrations": s.to_numpy()})


def coi_by_year(
    ctx: DatasetContext, breed: str, truth: pd.DataFrame | None = None, since: int = 1980
) -> pd.DataFrame:
    """Mean recorded COI per birth year; with `truth`, also true pedigree F and realised IBD
    (only possible with synthetic data)."""
    m = breed_mask(ctx, breed)
    df = pd.DataFrame(
        {"idx": np.flatnonzero(m), "year": _year(ctx.rules.birth_day[m]), "recorded": ctx.F[m]}
    )
    if truth is not None:
        df = df.merge(truth, on="idx", how="left").rename(
            columns={"f_true_pedigree": "true_pedigree", "f_true_ibd": "realised_ibd"}
        )
    out = df[df["year"] >= since].groupby("year").mean(numeric_only=True).drop(columns="idx")
    return out.reset_index()


def lorenz(ctx: DatasetContext, breed: str, year: int, window: int = 5) -> pd.DataFrame:
    """Lorenz curve of registered offspring per sire born in the `window` years to `year`."""
    by = ctx.ped.birth_year.astype(int)
    m = breed_mask(ctx, breed, domestic=False) & (by > year - window) & (by <= year)
    _, counts = offspring_per_sire(ctx.ped, m)
    c = np.sort(counts)
    cum = np.r_[0, np.cumsum(c)] / max(int(c.sum()), 1)
    return pd.DataFrame({"share_sires": np.linspace(0, 1, cum.size), "share_offspring": cum})


def hd_shares(ctx: DatasetContext, breed: str, period: int = 5) -> pd.DataFrame:
    """Share of latest HD grades A to E by birth period (5 years) of the screened animals."""
    m = breed_mask(ctx, breed) & (ctx.rules.hd_grade >= 0)
    p = (_year(ctx.rules.birth_day[m]) // period) * period
    g = ctx.rules.hd_grade[m]
    tab = pd.crosstab(p, g, normalize="index").reindex(columns=range(5), fill_value=0.0)
    tab.columns = list(GRADES)
    return tab.reset_index(names="period")


def carrier_frequency(ctx: DatasetContext, breed: str, year: int, window: int = 10) -> pd.DataFrame:
    """Per tested locus: tested animals born in the window, carrier and affected shares."""
    m = breed_mask(ctx, breed)
    y = _year(ctx.rules.birth_day)
    m &= (y > year - window) & (y <= year)
    rows = []
    for j, locus in enumerate(ctx.loci):
        g = ctx.rules.dna[m, j]
        t = g[g >= 0]
        rows.append(
            {
                "locus": locus,
                "n_tested": int(t.size),
                "carrier": float((t == 1).mean()) if t.size else np.nan,
                "affected": float((t == 2).mean()) if t.size else np.nan,
                "allele_frequency": float(t.mean() / 2) if t.size else np.nan,
            }
        )
    return pd.DataFrame(rows)


def breed_kpis(ctx: DatasetContext, breed: str, year: int | None = None) -> dict[str, Any]:
    """KPI tiles: registrations, mean COI of last year's litters, Ne (two methods), gene
    diversity, fe, fg, top-sire share (5 y), sires above the FCI 5% threshold."""
    year = year or last_full_year(ctx)
    gi = 4.5
    rep = population_report(ctx.ped, ctx.F, ctx.D, ctx.eqg, breed, year, gi)
    m = breed_mask(ctx, breed)
    y = _year(ctx.rules.birth_day)
    last = m & (y == year)
    _, counts = offspring_per_sire(
        ctx.ped,
        breed_mask(ctx, breed, False)
        & (ctx.ped.birth_year > year - 5)
        & (ctx.ped.birth_year <= year),
    )
    return {
        "year": year,
        "registrations": int(last.sum()),
        "mean_coi_last_year": float(ctx.F[last].mean()) if last.any() else np.nan,
        "ne_delta_f": rep.ne_delta_f.ne,
        "ne_census": rep.ne_census.ne,
        "gene_diversity": rep.gene_diversity,
        "fe": rep.founders.fe,
        "fg": rep.founders.fg,
        "top_sire_share": rep.sire_usage.top_sire_share,
        "top20_share": rep.sire_usage.top20_share,
        "gini_sires": gini(counts),
        "n_above_fci": rep.sire_usage.n_above_fci,
        "mean_eqg": rep.mean_eqg,
    }


def dog_profile(ctx: DatasetContext, idx: int, date: str = "2026-11-01") -> dict[str, Any]:
    """Everything the dog profile card shows (registry data only)."""
    a = ctx.animals.iloc[idx]
    r = ctx.rules
    ref = ctx.reference(ctx.breed_of(idx), date)
    dna = {
        lc: (
            ["clear", "carrier", "affected"][int(ctx.geno[idx, j])]
            if ctx.geno[idx, j] >= 0
            else "unknown"
        )
        + (" (inferred)" if ctx.inferred[idx, j] else "")
        for j, lc in enumerate(ctx.loci)
    }
    n_off = int(((ctx.ped.sire == idx) | (ctx.ped.dam == idx)).sum())
    n_lit = int(r.dam_litters.ptr[idx + 1] - r.dam_litters.ptr[idx]) + int(
        r.sire_litters.ptr[idx + 1] - r.sire_litters.ptr[idx]
    )
    return {
        "name": str(a["name"]),
        "reg_no": str(a["reg_no"]),
        "breed": ctx.breed_of(idx),
        "sex": str(a["sex"]),
        "birth_date": str(pd.Timestamp(a["birth_date"]).date()),
        "studbook": str(a["studbook"]),
        "import": bool(a["import_flag"]),
        "registration_type": str(a["registration_type"]),
        "coi": float(ctx.F[idx]),
        "eqg": float(ctx.eqg[idx]),
        "mean_kinship": float(ref.mk[idx]),
        "hd_grade": GRADES[r.hd_grade[idx]] if r.hd_grade[idx] >= 0 else "not screened",
        "dna": dna,
        "ebv_index": None if np.isnan(ctx.ebv_index[idx]) else float(ctx.ebv_index[idx]),
        "ebv_accuracy": float(ctx.ebv_accuracy[idx]),
        "n_litters": n_lit,
        "n_offspring": n_off,
        "alive": bool(r.death_day[idx] == ALIVE),
    }


def _ancestors(ctx: DatasetContext, idx: int, depth: int) -> dict[tuple[int, ...], int]:
    """Pedigree positions (path of 0 = sire, 1 = dam) -> idx, up to `depth` generations."""
    out: dict[tuple[int, ...], int] = {(): idx}
    frontier: list[tuple[tuple[int, ...], int]] = [((), idx)]
    for _ in range(depth):
        nxt = []
        for path, i in frontier:
            for k, par in enumerate((ctx.ped.sire[i], ctx.ped.dam[i])):
                if par >= 0:
                    out[(*path, k)] = int(par)
                    nxt.append(((*path, k), int(par)))
        frontier = nxt
    return out


def coi_colour(f: float) -> str:
    return next(c for lim, c, _ in COI_BANDS if f < lim)


def _pedigree_lines(
    ctx: DatasetContext, idx: int, depth: int, prefix: str, highlight: set[int] | None
) -> list[str]:
    pos = _ancestors(ctx, idx, depth)
    uniq, cnt = np.unique(np.array(list(pos.values()), dtype=np.int64), return_counts=True)
    counts = {int(u): int(c) for u, c in zip(uniq, cnt, strict=True)}
    repeated = [u for u, c in counts.items() if c > 1 and u != idx]
    palette = ["#0072B2", "#CC79A7", "#56B4E9", "#000000", "#E69F00", "#009E73"]
    outline = {int(i): palette[k % len(palette)] for k, i in enumerate(repeated)}

    def node(path: tuple[int, ...]) -> str:
        return prefix + ("n" + "".join(map(str, path)) if path else "root")

    lines = []
    for path, i in sorted(pos.items(), key=lambda kv: (len(kv[0]), kv[0])):
        label = f"{ctx.rules.name[i]}\\n{ctx.rules.reg_no[i]}\\nCOI {100 * ctx.F[i]:.1f}%"
        extra = ""
        if int(i) in outline:
            label += f"\\nappears {int(counts[i])} times"
            extra = f', color="{outline[int(i)]}", penwidth=3'
        if highlight and int(i) in highlight:
            extra = ', color="#D55E00", penwidth=4'
        lines.append(
            f'{node(path)} [label="{label}", fillcolor="{coi_colour(float(ctx.F[i]))}"{extra}];'
        )
        if path:
            lines.append(f"{node(path)} -> {node(path[:-1])};")
    return lines


def pedigree_dot(
    ctx: DatasetContext, idx: int, depth: int = 4, highlight: set[int] | None = None
) -> str:
    """Graphviz DOT of a pedigree (sire branch on top), nodes coloured by COI band; ancestors
    that appear more than once share an outline colour and say how often they appear."""
    head = "digraph P { rankdir=RL; node [shape=box, style=filled, fontsize=10];"
    return "\n".join([head, *_pedigree_lines(ctx, idx, depth, "", highlight), "}"])


def litter_dot(ctx: DatasetContext, sire: int, dam: int, depth: int = 3) -> str:
    """Combined pedigree of a hypothetical litter: sire and dam trees side by side, shared
    ancestors highlighted (thick orange outline)."""
    a = set(_ancestors(ctx, sire, depth).values())
    b = set(_ancestors(ctx, dam, depth).values())
    shared = (a & b) - {sire, dam}
    lines = [
        "digraph L { rankdir=RL; node [shape=box, style=filled, fontsize=10];",
        'litter [label="Planned litter", shape=ellipse, fillcolor="#FFFFFF"];',
    ]
    lines += _pedigree_lines(ctx, sire, depth, "s", shared)
    lines += _pedigree_lines(ctx, dam, depth, "d", shared)
    lines += ["sroot -> litter;", "droot -> litter;", "}"]
    return "\n".join(lines)


def shared_ancestors(ctx: DatasetContext, sire: int, dam: int, depth: int = 3) -> set[int]:
    a = set(_ancestors(ctx, sire, depth).values())
    b = set(_ancestors(ctx, dam, depth).values())
    return (a & b) - {sire, dam}
