"""Pick the three demo dams deterministically (P7 task 7.8) and write `configs/demo.yaml`.

1. SYN_S dam with the fewest good options (candidates scoring Good or better).
2. SYN_M dam for which the breed's most used candidate sire is permitted but ranked lowest
   (sire quota and kinship pull it down).
3. A dam whose best match is a sire with a shallow, import-type recorded pedigree (a foreign AI
   sire with a short export pedigree), which triggers the depth warning.
Dams: alive on the demo date, 2 to 6 years old, full registration, domestic records.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import yaml

from breeding_smarter.io.paths import configs_dir
from breeding_smarter.matching.config import load_scoring
from breeding_smarter.matching.context import DatasetContext
from breeding_smarter.matching.recommend import rank_fast, recommend_sires
from breeding_smarter.pedigree.core import IntArray
from breeding_smarter.rules import day_number

DEMO_DATE = "2026-11-01"
PROFILE = "hr_full"


def eligible_dams(ctx: DatasetContext, breed: str | None, day: int) -> IntArray:
    r = ctx.rules
    age = (day - r.birth_day) / 365.25
    m = (ctx.ped.sex == 0) & (age >= 2) & (age <= 6) & (r.birth_day <= day)
    m &= day < r.death_day
    m &= ~r.limited & ~ctx.is_foreign
    if breed is not None:
        m &= ctx.ped.breed == ctx.ped.breed_codes.index(breed)
    return np.flatnonzero(m).astype(np.int64)


def pick_few_options(ctx: DatasetContext, day: int, max_dams: int = 300) -> int:
    sc = load_scoring()
    good = next(t for t, label in sc.tiers.value if label == "Good")
    best: tuple[int, int] | None = None
    for d in eligible_dams(ctx, "SYN_S", day)[:max_dams]:
        _, scores = rank_fast(ctx, int(d), day, PROFILE)
        n_good = int((scores >= good).sum())
        if best is None or (n_good, int(d)) < best:
            best = (n_good, int(d))
    assert best is not None
    return best[1]


def pick_popular_sire_low(ctx: DatasetContext, day: int, max_dams: int = 300) -> tuple[int, int]:
    """(dam, popular sire): the most used candidate sire in 5 years ranked lowest."""
    from breeding_smarter.matching.candidates import candidate_sires

    since = day - int(365.25 * 5)
    best: tuple[float, int, int] | None = None
    for d in eligible_dams(ctx, "SYN_M", day)[:max_dams]:
        cands = candidate_sires(ctx, int(d), day)
        off = ctx.rules.sire_offspring.count_before(cands, day, since)
        top = int(cands[int(np.argmax(off))])
        sires, _ = rank_fast(ctx, int(d), day, PROFILE)
        if top not in set(sires.tolist()):
            continue
        rel_rank = float(np.flatnonzero(sires == top)[0]) / max(1, sires.size)
        key = (-rel_rank, int(d), top)
        if best is None or key < best:
            best = key
    assert best is not None
    return best[1], best[2]


def pick_shallow(ctx: DatasetContext, day: int, max_dams: int = 400) -> int:
    """A dam whose top-ranked sire has a shallow recorded pedigree (EqG below the warning
    level, typically a foreign AI sire registered with a short export pedigree): the
    litter's recorded COI is probably underestimated. Prefers SYN_M, then any breed."""
    low = load_scoring().low_depth_warning_eqg.value
    for breed in ("SYN_M", "SYN_L", "SYN_S"):
        for d in eligible_dams(ctx, breed, day)[:max_dams]:
            sires, _ = rank_fast(ctx, int(d), day, PROFILE)
            if sires.size and ctx.eqg[sires[0]] < low:
                return int(d)
    dams = eligible_dams(ctx, None, day)
    return int(dams[int(np.argmin(ctx.eqg[dams]))])


def select_demo(ctx: DatasetContext, date: str = DEMO_DATE) -> dict[str, Any]:
    day = day_number(date)
    d1 = pick_few_options(ctx, day)
    d2, pop = pick_popular_sire_low(ctx, day)
    d3 = pick_shallow(ctx, day)
    r = ctx.rules

    def entry(i: int, story: str, **extra: Any) -> dict[str, Any]:
        return {
            "reg_no": str(r.reg_no[i]),
            "name": str(r.name[i]),
            "breed": ctx.breed_of(i),
            "story": story,
            **extra,
        }

    rec3 = recommend_sires(ctx, d3, date, PROFILE, top_k=1)
    return {
        "dataset": ctx.tag,
        "mating_date": date,
        "profile": PROFILE,
        "dams": [
            entry(d1, "Small local breed: few good options."),
            entry(
                d2,
                "The most popular sire is not on top: sire quota and kinship.",
                popular_sire=str(r.reg_no[pop]),
            ),
            entry(
                d3,
                "Top match is a foreign AI sire with a shallow recorded pedigree: the "
                "litter's recorded COI is probably underestimated.",
                top_sire=str(r.reg_no[rec3.ranked[0].sire]) if rec3.ranked else None,
                top_sire_eqg=round(float(ctx.eqg[rec3.ranked[0].sire]), 2) if rec3.ranked else None,
                depth_warning=bool(rec3.ranked and rec3.card(rec3.ranked[0].sire).depth_warning),
            ),
        ],
    }


def write_demo(ctx: DatasetContext, path: Path | None = None) -> Path:
    p = path or configs_dir() / "demo.yaml"
    doc = select_demo(ctx)
    p.write_text(
        "# Demo dams, selected automatically by `bsm demo select` "
        "(matching/examples.py). Synthetic data.\n" + yaml.safe_dump(doc, sort_keys=False)
    )
    return p


def load_demo(path: Path | None = None) -> dict[str, Any]:
    data: dict[str, Any] = yaml.safe_load((path or configs_dir() / "demo.yaml").read_text())
    return data
