import numpy as np
from numba import njit
from typer.testing import CliRunner

import breeding_smarter
from breeding_smarter.cli import app

runner = CliRunner()


def test_import_and_version():
    assert breeding_smarter.__version__ == "0.1.0"


def test_cli_help_lists_subcommands():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for cmd in ["generate", "validate", "metrics", "match", "experiment", "export"]:
        assert cmd in result.output


def test_cli_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_numba_toolchain():
    @njit(cache=False)
    def add(a, b):
        return a + b

    assert add(2, 3) == 5
    assert add(np.float64(1.5), 2.0) == 3.5
