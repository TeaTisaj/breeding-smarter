import json

from typer.testing import CliRunner

from breeding_smarter.cli import app
from tests.fixtures.pedigrees import FIRST_COUSINS

runner = CliRunner()


def test_metrics_on_fixture_run(tmp_path):
    run = FIRST_COUSINS.write_run(tmp_path)
    res = runner.invoke(app, ["metrics", "--run", str(run), "--year", "2009", "--json"])
    assert res.exit_code == 0, res.output
    rep = json.loads(res.output)[0]
    assert rep["breed"] == "SYN_M"
    # births 2006 (H, I, F = 0) and 2009 (X, F = 1/16) fall in (2004.5, 2009]
    assert rep["n_reference"] == 3
    assert abs(rep["mean_F"] - 0.0625 / 3) < 1e-12
    assert (run / "cache" / "pedigree_F_D_registry.parquet").exists()
    res2 = runner.invoke(app, ["metrics", "--run", str(run), "--year", "2009"])
    assert res2.exit_code == 0 and "SYN_M" in res2.output
