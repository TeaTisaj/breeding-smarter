"""Per-year and per-generation rates (paper revision): known answers on a toy table."""

import numpy as np
import pandas as pd
import pytest
from scipy import stats

from breeding_smarter.experiments import rates


def _rows(sid, dF_cal, L, F10, n=3):
    rows = []
    for r in range(n):
        rows.append(
            {
                "breed": "SYN_M",
                "strategy": sid,
                "adoption": 1.0,
                "replicate": r,
                "metric": "R_delta_f_late",
                "generation": 10,
                "value": dF_cal,
            }
        )
        rows.append(
            {
                "breed": "SYN_M",
                "strategy": sid,
                "adoption": 1.0,
                "replicate": r,
                "metric": "M2_realised_ibd",
                "generation": 10,
                "value": F10,
            }
        )
        for g in range(1, 11):  # L only counts generations 6 to 10
            rows.append(
                {
                    "breed": "SYN_M",
                    "strategy": sid,
                    "adoption": 1.0,
                    "replicate": r,
                    "metric": "M13_generation_interval",
                    "generation": g,
                    "value": L if g >= 6 else 99.0,
                }
            )
    return rows  # fmt: skip


def test_late_rates_known_answer():
    pr = pd.DataFrame(_rows("A", 0.0045, 6.0, 0.13))
    t = rates.late_rates(pr, "SYN_M", "A")
    assert t["L"].tolist() == [6.0] * 3
    assert t["dF_year"].iloc[0] == pytest.approx(0.001)
    assert t["dF_gen"].iloc[0] == pytest.approx(0.006)
    assert t["Ne_gen"].iloc[0] == pytest.approx(1 / 0.012)
    assert t["F10"].iloc[0] == pytest.approx(0.13)


def test_non_positive_rate_gives_nan_ne():
    t = rates.late_rates(pd.DataFrame(_rows("A", -0.001, 5.0, 0.1)), "SYN_M", "A")
    assert t["Ne_gen"].isna().all()


def test_population_level_interval_uses_populations_as_units():
    m, lo, hi, n = rates.population_level([156.0, 42.0, 79.0, 8.0])
    assert n == 4 and m == pytest.approx(71.25)
    half = stats.t.ppf(0.975, 3) * np.std([156, 42, 79, 8], ddof=1) / 2
    assert (lo, hi) == pytest.approx((71.25 - half, 71.25 + half))
