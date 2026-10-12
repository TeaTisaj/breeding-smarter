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


def test_e8_known_answers(tmp_path, monkeypatch):
    """Primary arm: better hips than S3q, Ne within 0.9 x S3q, fewer affected than S1 (pass);
    the extra arm has better hips but Ne 0.67 x S3q and no health gain (H8, H9 fail)."""
    rng = np.random.default_rng(1)
    rows = []
    for b in hy.BREEDS:
        noise = rng.normal(0, 1e-4, 6)
        primary = hy.E8_PRIMARY[b]
        dF = {"S1": 0.006, "S3": 0.007, "S3q": 0.004, primary: 0.0042, "S3q-gain025": 0.006}
        hd = {"S1": 0.4, "S3": 0.06, "S3q": 0.4, primary: -0.8, "S3q-gain025": -0.9}
        for sid, d in dF.items():
            rows += _rows(b, sid, "R_delta_f_late", d + noise)
            rows += _rows(b, sid, "R_ne_f_late", 1 / (2 * (d + noise)))
            rows += _rows(b, sid, "M8_mean_tbv_hd", hd[sid] + 100 * noise)
        rows += _rows(b, "S1", "M6_affected_L1", [0.005] * 6)
        rows += _rows(b, primary, "M6_affected_L1", [0.0] * 6)
        rows += _rows(b, "S3q-gain025", "M6_affected_L1", [0.005] * 6)
    (tmp_path / hy.E8).mkdir()
    pd.DataFrame(rows).to_csv(tmp_path / hy.E8 / "per_generation_replicates.csv.gz", index=False)

    def no_results(exp_id):
        raise ValueError("none")

    monkeypatch.setattr(hy, "report_dir", lambda e: tmp_path / e)
    monkeypatch.setattr(hy, "load_results", no_results)
    t = hy.evaluate_e8()
    got = t.set_index(["id", "breed", "strategy"])["pass"]
    for b in hy.BREEDS:
        p = hy.E8_PRIMARY[b]
        assert got[("H7", b, p)] and got[("H8", b, p)]
        assert got[("H7", b, "S3q-gain025")] and not got[("H8", b, "S3q-gain025")]
    assert got[("H9", "SYN_M", hy.E8_PRIMARY["SYN_M"])]
    assert not got[("H9", "SYN_M", "S3q-gain025")]
    assert not (t["id"].eq("H9") & t["breed"].eq("SYN_S")).any()
    h8 = t[(t["id"] == "H8") & (t["strategy"] == hy.E8_PRIMARY["SYN_S"])].iloc[0]
    assert h8["estimate"] == pytest_approx(0.004 / 0.0042)
    heads = hy.e8_headlines(t)
    assert all("all criteria pass" in h for h in heads)
    assert "H7" in hy.write_report_e8().read_text()


def test_fieller_ratio_known_answers():
    """Constant denominator: Fieller = t-interval of the numerator / constant; a denominator
    whose mean is not clearly away from 0 gives an unbounded (nan) interval."""
    from breeding_smarter.experiments.summary import t_interval

    num = pd.Series([0.0040, 0.0044, 0.0037, 0.0042, 0.0039, 0.0041])
    m, lo, hi = t_interval(num.to_numpy())
    r, rlo, rhi, n = hy.fieller_ratio(num, pd.Series([0.005] * 6))
    assert n == 6
    assert (r, rlo, rhi) == (pytest_approx(m / 0.005), pytest_approx(lo / 0.005),
                             pytest_approx(hi / 0.005))  # fmt: skip
    r, rlo, rhi, _ = hy.fieller_ratio(num, pd.Series([0.001, -0.001, 0.002, -0.002, 0.0, 0.0005]))
    assert np.isnan(rlo) and np.isnan(rhi)


def test_e8_headline_when_only_h8_fails():
    """Fallback wording: measured cost quoted from H8; 'above market' only if H10a lo > 0."""

    def table(h10a_lo):
        rows = []
        for b in hy.BREEDS:
            p = hy.E8_PRIMARY[b]
            ids = [("H7", True, -0.5, -0.8, -0.2), ("H8", False, 0.85, 0.78, 0.93)]
            ids += [("H9", True, -0.003, -0.004, -0.002)] if b == "SYN_M" else []
            ids += [("H10a", None, 80.0, h10a_lo, 120.0)]
            for h, ok, est, lo, hi in ids:
                rows.append({"id": h, "breed": b, "strategy": p, "primary": True, "pass": ok,
                             "estimate": est, "lo": lo, "hi": hi})  # fmt: skip
        return pd.DataFrame(rows)

    s, m = hy.e8_headlines(table(40.0))
    assert "hips improve at a measured diversity cost: Ne 85% of S3q (95% CI 78% to 93%)" in s
    assert "hips and health improve" in m and "still above today's market" in m
    s, m = hy.e8_headlines(table(-5.0))
    assert "not shown to be above today's market" in m
