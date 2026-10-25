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


def test_pareto_front_known_answer():
    pts = {"a": (300, 0.4), "b": (280, -0.8), "c": (250, -0.9), "d": (200, 0.4), "e": (280, -0.5)}
    assert hy.pareto_front(pts) == ["a", "b", "c"]


def test_e9_known_answers(tmp_path, monkeypatch):
    rng = np.random.default_rng(2)
    arms_m = {  # Ne, HD, freq per locus (two loci), affected per locus
        "S1": (200, 0.40, 0.06, 0.004),
        "S3q": (320, 0.40, 0.10, 0.006),
        "S3q-gain010": (280, -0.80, 0.12, 0.005),
        "S3q-gain010-hc": (279, -0.80, 0.11, 0.0005),
        "S3q-gain010-c050": (278, -0.78, 0.015, 0.0001),
        "S3q-gain010-c050-oracle": (500, -0.75, 0.015, 0.0001),
        "S3q-gain005-c050": (300, -0.50, 0.015, 0.0001),
        "S3q-gain015-c050": (250, -0.95, 0.015, 0.0001),
        "S3q-gain010-c100": (279, -0.79, 0.07, 0.001),
    }
    rows = []
    for sid, (ne, hd, fq, af) in arms_m.items():
        z = rng.normal(0, 1, (3, 20))
        rows += _rows("SYN_M", sid, "R_ne_f_late", ne + 5 * z[0])
        rows += _rows("SYN_M", sid, "M8_mean_tbv_hd", hd + 0.02 * z[1])
        for locus in ("L1", "L2"):
            rows += _rows("SYN_M", sid, f"M6_freq_{locus}", fq + 0.001 * z[2])
            rows += _rows("SYN_M", sid, f"M6_affected_{locus}", [af] * 20)
    for sid, (ne, hd) in {"S1": (33, 0.1), "S3q": (55, 0.1), "S3q-gain025": (75, -0.6)}.items():
        rows += _rows("SYN_S", sid, "R_ne_f_late", ne + rng.normal(0, 1, 20))
        rows += _rows("SYN_S", sid, "M8_mean_tbv_hd", hd + rng.normal(0, 0.01, 20))
    pr9 = pd.DataFrame(rows)
    rows10 = []
    for ad, (ne, hd, fq) in {0.25: (230, -0.2, 0.05), 0.5: (250, -0.4, 0.03)}.items():
        for metric, v in (("R_ne_f_late", ne), ("M8_mean_tbv_hd", hd), ("M6_freq_L1", fq)):
            r = _rows("SYN_M", "S3q-gain010-c050", metric, v + rng.normal(0, 1e-3, 20))
            rows10 += [{**x, "adoption": ad} for x in r]
    pr10 = pd.DataFrame(rows10)
    t = hy.evaluate_e9(pr9, pr10).set_index("id")
    assert t.loc["H9-rep", "pass"]
    assert t.loc["H9-hc", "pass"]  # population limit lowers carrier frequency more than the block
    assert t.loc["H10-dna", "pass"]
    assert t.loc["H10-adopt", "pass"]
    front = set(t.loc["H9-pareto"]["quantity"])
    assert any("S3q-gain015-c050" in q for q in front)
    assert not any(q.endswith(": S1") for q in front)
    assert hy._ladder(pr9, "SYN_M")[0] == (0.0005, "S3q-gain005-c050")
    assert hy._ladder(pr9, "SYN_S") == [(0.0025, "S3q-gain025")]

    from breeding_smarter.experiments.figures import fig_n, fig_o

    assert any(p.name == "figN_policy_dial.png" for p in fig_n(pr9, tmp_path))
    assert any(p.name == "figO_adoption.png" for p in fig_o(pr9, pr10, tmp_path))


def test_e11_cap_reading_known_answers():
    assert hy.cap_reading(5, 40, 300) == "OCS better"
    assert hy.cap_reading(-40, -5, 300) == "simple control better"
    assert hy.cap_reading(-50, 50, 300) == "as good"  # within 20% of 300
    assert hy.cap_reading(-70, 50, 300) == "inconclusive"


def _arm(rng, breed, sid, ne, hd, fq, males, n, adoption=1.0):
    z = rng.normal(0, 1, (5, n))
    rows = _rows(breed, sid, "R_ne_f_late", ne + 2 * z[0])
    rows += _rows(breed, sid, "R_ne_c_late", ne + 2 * z[1])
    rows += _rows(breed, sid, "M8_mean_tbv_hd", hd + 0.01 * z[2])
    rows += _rows(breed, sid, "M6_freq_L1", fq + 0.001 * z[3])
    rows += _rows(breed, sid, "M10_share_sires_used", males + 0.001 * z[4])
    return [{**r, "adoption": adoption} for r in rows]


def test_e11_known_answers():
    rng = np.random.default_rng(11)
    base = {  # Ne, HD, freq, share of males used
        "S1": (200, 0.4, 0.06, 0.13),
        "S3": (180, 0.1, 0.03, 0.07),
        "S3q": (320, 0.4, 0.10, 0.15),
        "S3q-gain010-c050": (280, -0.8, 0.01, 0.14),
    }
    pops = {}
    for pop in ("v1", "v1b", "v1c", "v1d"):
        rows = []
        for b in hy.BREEDS:
            for sid, v in base.items():
                # population v1d: quotas do not beat the market (one failure of four)
                ne = 190 if (pop == "v1d" and sid == "S3q") else v[0]
                rows += _arm(rng, b, sid, ne, *v[1:], n=10)
        pops[pop] = pd.DataFrame(rows)
    rb = []
    arms_b = dict(base)
    arms_b |= {"S3q-cap": (320, 0.4, 0.1, 0.15), "S3q-mkx": (200, 0.4, 0.1, 0.10)}
    for x in ("t1", "u5"):
        arms_b[f"S3-{x}"] = (170, 0.1, 0.03, 0.06 if x == "t1" else 0.135)  # u5: no herding
        arms_b[f"S3q-{x}"] = (320, 0.4, 0.1, 0.15)
    for b in hy.BREEDS:
        for sid, v in arms_b.items():
            rb += _arm(rng, b, sid, *v, n=20)
    rc = []
    for ad in (0.25, 0.5, 0.75, 1.0):
        rc += _arm(rng, "SYN_M", "S3q-gain010-c050", 300, -0.5, 0.07, 0.14, 20, ad)
        rc += _arm(rng, "SYN_M", "S3q-gain010-c050f", 300, -0.5, 0.02, 0.14, 20, ad)
    t = hy.evaluate_e11(pops, pd.DataFrame(rb), pd.DataFrame(rc))
    one = t.set_index(["id", "breed", "quantity"])

    def row(h, q, b="SYN_M"):
        return one.loc[(h, b, q)]

    assert row("H11-pop-a", "S3 - S1 males used: holds in 4 of 4")["pass"]
    assert row("H11-pop-b", "S3q - S1 Ne late: holds in 3 of 4")["pass"]  # 3 of 4 is enough
    assert row("H11-pop-c", "S3q-gain010-c050 - S1 Ne, HD, freq: holds in 4 of 4")["pass"]
    assert row("H11-cap", "Ne late: S3q - S3q-cap")["reading"] == "as good"
    assert row("H11-cap", "Ne late: S3q - S3q-mkx")["reading"] == "OCS better"
    assert not row("H11-free-a", "S3-x - S1 males used < 0 for every x")["pass"]  # u5 fails
    assert row("H11-free-b", "S3q-x - S1 Ne late > 0 for every x")["pass"]
    assert row("H11-adopt", "freq: S3q-gain010-c050f at adoption 0.5 - S1")["pass"]
    assert (t["id"] == "H11-pop-pooled").any() and (t["id"] == "H11-pop-range").any()
    assert t[t["quantity"].str.contains("coancestry")].shape[0] > 0  # Ne cross-check rows
