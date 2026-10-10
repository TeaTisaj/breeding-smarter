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


schema_app = typer.Typer(help="Data contract tools.", no_args_is_help=True)
app.add_typer(schema_app, name="schema")


@schema_app.command("dictionary")
def schema_dictionary() -> None:
    """Regenerate docs/data_dictionary.md from the table specs."""
    from breeding_smarter.schema.dictionary import write_dictionary

    path = write_dictionary()
    console.print(f"wrote {path}")


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
def metrics(
    run: str = typer.Option(..., "--run", help="Run id (under data/generated) or run folder."),
    breed: list[str] | None = typer.Option(None, "--breed", help="Breed id(s); default all."),
    year: int | None = typer.Option(None, "--year", help="Reference year; default last year."),
    interval: float = typer.Option(4.5, "--interval", help="Generation interval (years)."),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output."),
) -> None:
    """Population metrics for a run (F and D are cached in the run's cache/ folder)."""
    import json

    from rich.table import Table

    from breeding_smarter.io.cache import load_registry_animals, pedigree_cache, resolve_run
    from breeding_smarter.pedigree import Pedigree, population_report

    rp = resolve_run(run)
    ped = Pedigree.from_registry(load_registry_animals(rp))
    F, D, eqg = pedigree_cache(rp)
    y = year if year is not None else int(ped.birth_year.max())
    reports = [
        population_report(ped, F, D, eqg, b, y, interval) for b in (breed or ped.breed_codes)
    ]
    if as_json:
        print(json.dumps([r.model_dump(mode="json") for r in reports], indent=2))
        return
    for r in reports:
        t = Table(title=f"{r.breed}: reference cohort born {r.reference_years} (synthetic)")
        t.add_column("metric")
        t.add_column("value", justify="right")
        rows = [
            ("reference animals", f"{r.n_reference}"),
            ("mean F (COI)", f"{100 * r.mean_F:.1f}%"),
            ("mean kinship", f"{100 * r.mean_mk:.1f}%"),
            ("gene diversity", f"{r.gene_diversity:.4f}"),
            ("mean EqG", f"{r.mean_eqg:.2f}"),
            ("Ne (individual dF)", f"{r.ne_delta_f.ne:.1f} (n={r.ne_delta_f.n_used})"),
            ("Ne (census, breeding animals)", f"{r.ne_census.ne:.1f}"),
            ("generation interval (y)", f"{r.generation_interval.overall:.2f}"),
            ("fe / fg", f"{r.founders.fe:.1f} / {r.founders.fg:.1f}"),
            ("top sire share (5 y)", f"{100 * r.sire_usage.top_sire_share:.1f}%"),
            ("top 20% sires share", f"{100 * r.sire_usage.top20_share:.1f}%"),
            ("sires above FCI 5%", f"{r.sire_usage.n_above_fci}"),
        ]
        for k, v in rows:
            t.add_row(k, v)
        console.print(t)


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
