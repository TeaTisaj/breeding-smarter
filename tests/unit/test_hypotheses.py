"""P12 hypothesis evaluation on toy per-replicate tables (known answers)."""

import numpy as np
import pandas as pd

from breeding_smarter.experiments import hypotheses as hy


def _rows(breed, sid, metric, values):
    return [
        {"breed": breed, "strategy": sid, "adoption": 1.0, "replicate": r, "metric": metric,
         "generation": 10, "value": v}
        for r, v in enumerate(values)
    ]  # fmt: skip


def test_hypotheses_known_answers(tmp_path, monkeypatch):
    rng = np.random.default_rng(0)
    e5, e6 = [], []
    for b in hy.BREEDS:
        noise = rng.normal(0, 1e-4, 6)
        dF = {"S0": 0.002, "S1": 0.006, "S3": 0.007, "CC-ocs-mc1": 0.004, "S3q": 0.0045}
        for c in hy.CONTROLS:
            for m in hy.MATINGS:  # control matters (0.001 steps), mating barely (0.0001)
                dF[f"CC-{c}-{m}"] = 0.006 - 0.001 * hy.CONTROLS.index(c) + 0.0001 * (m == "rand")
        for sid, d in dF.items():
            e5 += _rows(b, sid, "R_delta_f_late", d + noise)
            e5 += _rows(b, sid, "R_ne_f_late", 1 / (2 * (d + noise)))
        e5 += _rows(b, "S1", "M6_affected_L1", [0.01] * 6)
        e5 += _rows(b, "S3q", "M6_affected_L1", [0.002] * 6)
        for sid, d in {"CC-ocs-mc1": 0.004, "CC-ocs-mc1-oracle": 0.0021}.items():
            e6 += _rows(b, sid, "R_delta_f_late", d + noise)
            e6 += _rows(b, sid, "R_ne_f_late", 1 / (2 * (d + noise)))
    for exp, rows in ((hy.E5, e5), (hy.E6, e6)):
        (tmp_path / exp).mkdir()
        pd.DataFrame(rows).to_csv(tmp_path / exp / "per_generation_replicates.csv.gz", index=False)

    def no_results(exp_id):
        raise ValueError("none")

    monkeypatch.setattr(hy, "report_dir", lambda e: tmp_path / e)
    monkeypatch.setattr(hy, "load_results", no_results)
    t, _ = hy.evaluate()
    got = t.set_index(["id", "breed"])["pass"]
    for b in hy.BREEDS:
        assert got[("H1", b)] and got[("H2", b)] and got[("H3", b)] and got[("H5", b)]
    assert got[("H4a", "SYN_M")] and got[("H4b", "SYN_M")]
    assert ("H4a", "SYN_S") not in got.index
    h5 = t[(t["id"] == "H5") & (t["breed"] == "SYN_S")].iloc[0]
    assert h5["estimate"] == pytest_approx(0.002 / 0.0021)
    path = hy.write_report()
    assert "H1" in path.read_text()


def pytest_approx(x):
    import pytest

    return pytest.approx(x, rel=0.05)
