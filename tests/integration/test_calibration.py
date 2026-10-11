"""Calibration metrics, validate CLI and report determinism (P5 section 2)."""

import shutil

import numpy as np
import pytest
from typer.testing import CliRunner

from breeding_smarter.calibration import metrics as M
from breeding_smarter.calibration.data import RunData
from breeding_smarter.calibration.report import write_report
from breeding_smarter.calibration.targets import load_targets
from breeding_smarter.cli import app
from breeding_smarter.io import configs_dir, update_manifest
from breeding_smarter.pedigree.population import gini, top_share
from breeding_smarter.sim.run import generate, load_setup, make_genetics, snapshot_configs
from tests.fixtures.pedigrees import REPEATED_FULL_SIB

TINY = configs_dir() / "sim" / "tiny.yaml"
TINY_TARGETS = configs_dir() / "calibration" / "targets_tiny.yaml"


def test_population_helpers_known_answers():
    assert gini([1, 1, 1, 1]) == 0
    assert top_share([10, 1, 1, 1, 1]) == pytest.approx(10 / 14)


@pytest.fixture
def fixture_rd(tmp_path):
    """REPEATED_FULL_SIB as a run with the tiny config snapshot (breed SYN_L)."""
    run = REPEATED_FULL_SIB.write_run(tmp_path, breed="SYN_L")
    snapshot_configs(load_setup(TINY), TINY, run / "config_snapshot")
    update_manifest(run / "manifest.json", scale=0.02)
    return RunData.load(run)


def test_metrics_on_handmade_run(fixture_rd):
    rd = fixture_rd
    # litters: (0x1), (2x3), (4x5), (6x7): each has 2 registered pups except the last (1)
    ls = M.litter_size(rd).values["SYN_L"]
    assert ls["mean"] == pytest.approx(np.mean([2, 2, 2, 1]))
    assert ls["deviation_from_config"] == pytest.approx(ls["mean"] - 6.4)
    assert M.perinatal_loss_share(rd).values["SYN_L"]["share"] == 0.0
    # births: 0,1 in 2000; 2,3 in 2003; 4,5 in 2006; 6,7 in 2009; 8 in 2012.
    # Born 2005-2015 with offspring: 4, 5 (parents of 6, 7), 6, 7 (parents of 8) -> 4 of 5.
    assert M.share_with_offspring(rd).values["SYN_L"]["share"] == pytest.approx(4 / 5)
    # males born 2005-2015: 4, 6, 8; sired a litter: 4, 6 -> 2/3
    assert M.share_males_sired(rd).values["SYN_L"]["share"] == pytest.approx(2 / 3)
    # true pedigree F equals recorded F here (registry = truth): T11 not lower
    f = M.recorded_vs_true_f
    with pytest.raises(KeyError):
        f(rd)  # no 2025 cohort in this pedigree
    reg = M.ibd_regression  # truth f_true_ibd is 0 in fixtures: slope 0
    assert reg(rd).values["SYN_L"]["slope"] == pytest.approx(0.0, abs=1e-12)


@pytest.fixture(scope="module")
def tiny_dog_run(tmp_path_factory):
    out = tmp_path_factory.mktemp("cal")
    return generate(TINY, out=out, genetics=make_genetics("dog", TINY), run_id="tiny-dog")


def test_validate_cli_exit_codes(tiny_dog_run, tmp_path):
    runner = CliRunner()
    ok = runner.invoke(
        app,
        [
            "validate",
            "--run",
            str(tiny_dog_run),
            "--targets",
            str(TINY_TARGETS),
            "--out",
            str(tmp_path / "rep"),
        ],
    )
    assert ok.exit_code == 0, ok.output
    for name in (
        "validation_report.md",
        "targets_vs_simulated.csv",
        "figures/fig4_recorded_vs_true_f.png",
        "figures/fig4_recorded_vs_true_f.svg",
    ):
        assert (tmp_path / "rep" / name).exists()
    strict = runner.invoke(
        app, ["validate", "--run", str(tiny_dog_run), "--out", str(tmp_path / "rep2")]
    )
    assert strict.exit_code == 1  # the tiny run is not calibrated: hard targets fail
    text = (tmp_path / "rep" / "validation_report.md").read_text()
    assert text.splitlines()[2] == "All animals in this dataset are synthetic."


def test_report_is_deterministic(tiny_dog_run, tmp_path):
    rd = RunData.load(tiny_dog_run)
    cfg = load_targets(TINY_TARGETS)
    write_report(rd, cfg, tmp_path / "a")
    write_report(rd, cfg, tmp_path / "b")
    for name in ("validation_report.md", "targets_vs_simulated.csv", "figures/fig6_ne.svg"):
        assert (tmp_path / "a" / name).read_bytes() == (tmp_path / "b" / name).read_bytes()
    shutil.rmtree(tmp_path / "a")
