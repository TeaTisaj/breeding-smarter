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
    """Both add-ons help (carrier: freq, gain: HD), Ne above S1: H8 passes; S3q alone does not."""
    rng = np.random.default_rng(1)
    rows = []
    arms = {  # Ne, HD, freq per locus (two loci)
        "S1": (200, 0.40, 0.07),
        "S3q": (340, 0.40, 0.11),
        "S3q-c075": (330, 0.42, 0.05),
        "S3q-gain010": (340, -0.80, 0.13),
        "S3q-gain010-c075": (330, -0.70, 0.05),
    }
    for sid, (ne, hd, fq) in arms.items():
        z = rng.normal(0, 1, (3, 20))
        rows += _rows("SYN_M", sid, "R_ne_f_late", ne + 5 * z[0])
        rows += _rows("SYN_M", sid, "M8_mean_tbv_hd", hd + 0.02 * z[1])
        for locus in ("L1", "L2"):
            rows += _rows("SYN_M", sid, f"M6_freq_{locus}", fq + 0.002 * z[2])
            rows += _rows("SYN_M", sid, f"M6_affected_{locus}", fq**2 + 0 * z[2])
    for sid in ("S1", "S3q", "S3q-gain025"):
        rows += _rows("SYN_S", sid, "R_ne_f_late", 50 + rng.normal(0, 1, 10))
        rows += _rows("SYN_S", sid, "M8_mean_tbv_hd", rng.normal(0, 0.01, 10))
    (tmp_path / hy.E8).mkdir()
    pd.DataFrame(rows).to_csv(tmp_path / hy.E8 / "per_generation_replicates.csv.gz", index=False)
    monkeypatch.setattr(hy, "report_dir", lambda e: tmp_path / e)

    def no_results(exp_id):
        raise ValueError("none")

    monkeypatch.setattr(hy, "load_results", no_results)
    pr = pd.read_csv(tmp_path / hy.E8 / "per_generation_replicates.csv.gz")
    assert hy.e8_arms(pr)["carrier"] == "S3q-c075"
    t = hy.evaluate_e8(pr)
    got = t.set_index("id")
    assert got.loc["H8a", "pass"] and got.loc["H8b", "pass"] and got.loc["H8c", "pass"]
    assert got.loc["H8", "pass"]
    h8c = got.loc["H8c"]
    assert h8c["estimate"] == pytest_approx(2 * (0.05 - 0.07))
    e = t[t["id"] == "H8e"].set_index("quantity")["estimate"]
    assert e["carrier-limit effect on freq (mean over planners)"] == pytest_approx(-0.14)
    assert e["gain-OCS effect on HD (mean over carrier levels)"] == pytest_approx(-1.16)
    assert (t["id"] == "H8f").sum() == 4
    assert "H8a" in hy.write_e8_report().read_text()
