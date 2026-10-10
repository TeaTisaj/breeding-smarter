"""Command line interface (`bsm`)."""

from __future__ import annotations

import logging

import typer
from rich.console import Console
from rich.logging import RichHandler

from breeding_smarter import __version__

app = typer.Typer(
    help="Breeding Smarter command line tools (synthetic data only).", no_args_is_help=True
)
console = Console()
log = logging.getLogger("breeding_smarter")


def _configure_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True, show_path=False)],
        force=True,
    )


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"breeding-smarter {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Debug logging."),
    version: bool = typer.Option(
        False, "--version", callback=_version_callback, is_eager=True, help="Show version."
    ),
) -> None:
    """Breeding Smarter: all data produced here is synthetic."""
    _configure_logging(verbose)


def _stub(name: str) -> None:
    console.print(f"{name}: not implemented yet")


@app.command()
def generate() -> None:
    """Generate a synthetic dataset."""
    _stub("generate")


@app.command()
def validate() -> None:
    """Validate a generated run."""
    _stub("validate")


@app.command()
def metrics() -> None:
    """Population metrics for a run."""
    _stub("metrics")


@app.command()
def match() -> None:
    """Rank candidate sires for a dam."""
    _stub("match")


@app.command()
def experiment() -> None:
    """Run breeding-strategy experiments."""
    _stub("experiment")


@app.command()
def export() -> None:
    """Export bundles and releases."""
    _stub("export")
