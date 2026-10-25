"""Late-window rates on a per-year and per-realised-generation scale (paper revision, additional
analysis, not pre-registered).

The pre-registered Ne (`R_ne_f_late`) is 1 / (2 dF) with dF the rate of realised inbreeding per
*calendar* generation of 4.5 years (`sim.generation_interval_years`). Strategies change the
realised generation interval L (mean parent age at birth, `M13_generation_interval`), so
per replicate:

    dF_year = dF_cal / 4.5,     dF_gen = dF_year * L,     Ne_gen = 1 / (2 dF_gen),

with L the mean of `M13_generation_interval` over generations 6 to 10 (the cohorts of the late
window). Differences are taken on dF (finite for every replicate) and Ne_gen.
In-silico results on synthetic populations.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from breeding_smarter.experiments.summary import t_interval

CAL_YEARS = 4.5  # configs/sim/default.yaml generation_interval_years (calendar generation)
LATE_GENS = range(6, 11)


def late_rates(pr: pd.DataFrame, breed: str, sid: str, adoption: float = 1.0) -> pd.DataFrame:
    """Per replicate: dF_cal, L, dF_year, dF_gen, Ne_gen and realised F at generation 10."""
    sub = pr[(pr["breed"] == breed) & (pr["strategy"] == sid) & (pr["adoption"] == adoption)]

    def metric(name: str, gens: range | None = None) -> pd.Series:
        s = sub[sub["metric"] == name]
        s = s[s["generation"].isin(gens)] if gens is not None else s[s["generation"] == 10]
        return s.groupby("replicate")["value"].mean()

    out = pd.DataFrame({"dF_cal": metric("R_delta_f_late"),
                        "L": metric("M13_generation_interval", LATE_GENS),
                        "F10": metric("M2_realised_ibd")})  # fmt: skip
    out["dF_year"] = out["dF_cal"] / CAL_YEARS
    out["dF_gen"] = out["dF_year"] * out["L"]
    out["Ne_gen"] = np.where(out["dF_gen"] > 0, 1.0 / (2.0 * out["dF_gen"]), np.nan)
    return out


def paired(a: pd.Series, b: pd.Series) -> tuple[float, float, float, int]:
    """Paired mean difference a - b over common replicates with a 95% t-interval."""
    d = (a - b.reindex(a.index)).to_numpy(dtype=float)
    d = d[np.isfinite(d)]
    m, lo, hi = t_interval(d)
    return m, lo, hi, int(d.size)


def population_level(estimates: list[float]) -> tuple[float, float, float, int]:
    """Mean and 95% t-interval with populations as the units (n = number of populations)."""
    x = np.asarray(estimates, dtype=float)
    m, lo, hi = t_interval(x)
    return m, lo, hi, int(np.isfinite(x).sum())
