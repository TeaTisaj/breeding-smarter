"""Command line interface (`bsm`)."""

from __future__ import annotations

import logging
from typing import Any

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


rules_app = typer.Typer(help="Rule profiles.", no_args_is_help=True)
app.add_typer(rules_app, name="rules")


@rules_app.command("docs")
def rules_docs() -> None:
    """Regenerate docs/rules_catalogue.md and docs/rules_verification.md."""
    from breeding_smarter.rules.docs import write_docs

    for p in write_docs():
        console.print(f"wrote {p}")


def load_rule_context(dataset: str) -> Any:
    """RuleContext for a dataset tag, run id or folder (registry tables plus cached F, D)."""
    from breeding_smarter.io.cache import load_registry_animals, pedigree_cache
    from breeding_smarter.io.datasets import resolve_dataset
    from breeding_smarter.io.parquet import read_table
    from breeding_smarter.rules import RuleContext
    from breeding_smarter.schema.tables import BREEDS, DNA_TESTS, HEALTH_TESTS, LITTERS

    rp = resolve_dataset(dataset)
    F, D, _ = pedigree_cache(rp)
    return rp, RuleContext.from_tables(
        load_registry_animals(rp),
        read_table(rp.table(LITTERS), LITTERS),
        read_table(rp.table(HEALTH_TESTS), HEALTH_TESTS),
        read_table(rp.table(DNA_TESTS), DNA_TESTS),
        read_table(rp.table(BREEDS), BREEDS),
        F=F,
        D=D,
    )


@app.command()
def check(
    sire: str = typer.Option(..., "--sire", help="Sire reg_no."),
    dam: str = typer.Option(..., "--dam", help="Dam reg_no."),
    dataset: str = typer.Option("v1", "--dataset", help="Dataset tag, run id or folder."),
    date: str = typer.Option("2026-11-01", "--date", help="Mating date YYYY-MM-DD."),
    profile: str = typer.Option("hr_full", "--profile", help="Rule profile."),
    method: str | None = typer.Option(None, "--method", help="Mating method (ai_frozen...)."),
) -> None:
    """Is this mating permitted under a rule profile? (synthetic data)"""
    from rich.table import Table

    from breeding_smarter.rules import evaluate_pair, load_profile

    _, ctx = load_rule_context(dataset)
    idx = {r: i for i, r in enumerate(ctx.reg_no)}
    res = evaluate_pair(ctx, load_profile(profile), idx[sire], idx[dam], date, method)
    t = Table(title=f"{ctx.label(idx[sire])} x {ctx.label(idx[dam])} on {date}: {res.status}")
    for col in ("rule", "severity", "result", "message", "source", "verified"):
        t.add_column(col)
    for r in res.results:
        ok = "pass" if r.passed and not r.warning else ("warn" if r.passed else "FAIL")
        t.add_row(
            r.rule_id, r.severity, ok, r.message, r.source, "yes" if r.verified else "unverified"
        )
    console.print(t)


docs_app = typer.Typer(help="Generated documentation.", no_args_is_help=True)
app.add_typer(docs_app, name="docs")


@docs_app.command("assumptions")
def docs_assumptions() -> None:
    """Regenerate docs/assumptions.md from the configs."""
    from breeding_smarter.config.assumptions import write_assumptions

    console.print(f"wrote {write_assumptions()}")


demo_app = typer.Typer(help="Demo dams for the app and slides.", no_args_is_help=True)
app.add_typer(demo_app, name="demo")


@demo_app.command("select")
def demo_select(dataset: str = typer.Option("v1", "--dataset")) -> None:
    """Pick the 3 demo dams deterministically and write configs/demo.yaml."""
    from breeding_smarter.matching import load_context
    from breeding_smarter.matching.examples import write_demo

    p = write_demo(load_context(dataset))
    console.print(p.read_text())


def _stub(name: str) -> None:
    console.print(f"{name}: not implemented yet")


@app.command()
def generate(
    config: str = typer.Option("configs/sim/default.yaml", "--config", help="Sim config YAML."),
    seed: int | None = typer.Option(None, "--seed", help="Master seed (default: config)."),
    scale: float | None = typer.Option(None, "--scale", help="Override population scale."),
    out: str | None = typer.Option(None, "--out", help="Output base folder."),
    run_id: str | None = typer.Option(None, "--run-id", help="Override the run id."),
    genetics: str = typer.Option("dog", "--genetics", help="dog (P4) or null (structure only)."),
) -> None:
    """Simulate a synthetic dataset, write the run folder and validate it."""
    from pathlib import Path

    from rich.progress import Progress

    from breeding_smarter.io.manifest import read_manifest
    from breeding_smarter.sim.run import generate as run_generate
    from breeding_smarter.sim.run import make_genetics

    with Progress(console=console, transient=True) as prog:
        task = prog.add_task("simulating", total=None)

        def tick(year: int) -> None:
            if year % 10 == 0:
                prog.update(task, description=f"simulating: reached {year}")

        path = run_generate(
            Path(config),
            seed=seed,
            scale=scale,
            out=Path(out) if out else None,
            genetics=make_genetics(genetics, Path(config), scale),
            run_id=run_id,
            progress=tick,
        )
    m = read_manifest(path / "manifest.json")
    console.print(f"wrote {path} in {m['generator_wall_seconds']} s")
    console.print(m["row_counts"])
    console.print(f"validation: {m.get('validation_summary')}")
    if not m.get("validation_ok", False):
        raise typer.Exit(1)


@app.command()
def ebv(run: str = typer.Option(..., "--run", help="Run id or folder.")) -> None:
    """(Re)compute HD EBVs from registry data only (pedigree BLUP)."""
    from breeding_smarter.config.loader import load_genetics
    from breeding_smarter.evaluation.blup import evaluate_run
    from breeding_smarter.io.cache import resolve_run

    cfg = load_genetics()
    path = evaluate_run(resolve_run(run).root, cfg.hd_heritability.value, cfg)
    console.print(f"wrote {path}")


@app.command()
def validate(
    run: str = typer.Option(..., "--run", help="Run id or folder."),
    targets: str = typer.Option(
        "configs/calibration/targets.yaml", "--targets", help="Calibration targets YAML."
    ),
    out: str | None = typer.Option(None, "--out", help="Report folder (default reports/...)."),
) -> None:
    """Schema validation, true-pedigree F, calibration targets and the validation report.

    Exits with code 1 if the schema check or any hard target fails.
    """
    from pathlib import Path

    from breeding_smarter.calibration.report import validate_and_report
    from breeding_smarter.calibration.targets import load_targets
    from breeding_smarter.config.loader import load_loci
    from breeding_smarter.io.cache import resolve_run
    from breeding_smarter.io.paths import repo_root
    from breeding_smarter.schema.validate import validate_run

    rp = resolve_run(run)
    schema = validate_run(rp.root, allowed_loci=set(load_loci().ids))
    console.print(f"schema: {schema.summary()}")
    dest = Path(out) if out else repo_root() / "reports" / "validation" / rp.run_id
    rows, ok = validate_and_report(rp.root, load_targets(Path(targets)), dest)
    counts = {s: sum(r.status == s for r in rows) for s in ("PASS", "WARN", "FAIL")}
    console.print(f"targets: {counts}; report: {dest / 'validation_report.md'}")
    for r in rows:
        if r.status == "FAIL":
            console.print(f"[red]FAIL[/red] {r.id} {r.breed} {r.component} = {r.value} {r.target}")
    if not (schema.ok and ok):
        raise typer.Exit(1)


@app.command()
def calibrate(
    config: str = typer.Option("configs/sim/default.yaml", "--config"),
    grid: str = typer.Option("configs/calibration/grid.yaml", "--grid"),
    breeds: list[str] | None = typer.Option(None, "--breeds"),
    seeds: list[int] = typer.Option([1, 2], "--seed"),
) -> None:
    """Run the calibration grid and print the best combination per breed (never edits configs)."""
    from pathlib import Path

    from breeding_smarter.calibration.grid import best, run_grid
    from breeding_smarter.calibration.targets import load_targets
    from breeding_smarter.io.paths import repo_root

    out = repo_root() / "reports" / "validation" / "calibration_grid.csv"
    agg = run_grid(Path(config), Path(grid), load_targets(), breeds, tuple(seeds), out)
    console.print(f"wrote {out}")
    for b, row in best(agg).items():
        console.print(f"{b}: {row}")


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
def match(
    dam: str = typer.Option(..., "--dam", help="Dam reg_no."),
    dataset: str = typer.Option("v1", "--dataset", help="Dataset tag, run id or folder."),
    date: str = typer.Option("2026-11-01", "--date", help="Mating date YYYY-MM-DD."),
    profile: str = typer.Option("hr_full", "--profile", help="Rule profile."),
    top: int = typer.Option(10, "--top", help="Number of ranked sires to show."),
    explain: str | None = typer.Option(None, "--explain", help="Sire reg_no: print score card."),
    max_distance_km: float | None = typer.Option(None, "--max-distance-km"),
) -> None:
    """Rank candidate sires for a dam with an explainable score (synthetic data)."""
    from rich.markdown import Markdown
    from rich.table import Table

    from breeding_smarter.matching import load_context, recommend_sires, score_pair

    ctx = load_context(dataset)
    d = ctx.idx_of(dam)
    if explain:
        card = score_pair(ctx, ctx.idx_of(explain), d, date, profile)
        console.print(Markdown(card.to_markdown()))
        return
    rec = recommend_sires(ctx, d, date, profile, top_k=top, max_distance_km=max_distance_km)
    console.print(
        f"{ctx.rules.label(d)} on {date} ({profile}): {rec.n_candidates} candidate sires, "
        f"{rec.n_excluded} excluded by rules, {rec.n_with_warnings} with warnings."
    )
    t = Table(title="Ranked sires (synthetic data)")
    for col in (
        "rank",
        "sire",
        "tier",
        "score",
        "COI",
        "MK litter",
        "P(affected)",
        "HD idx",
        "sire use",
        "warnings",
    ):
        t.add_column(col)
    for i, r in enumerate(rec.ranked[:top], 1):
        c = rec.card(r.sire)
        comp = {x.component: x for x in c.components}
        t.add_row(
            str(i),
            c.sire_label,
            c.tier,
            f"{c.score:.1f}",
            f"{100 * c.predicted_coi:.1f}%",
            comp["diversity"].raw,
            comp["health"].raw,
            comp["ebv"].raw,
            comp["sire_use"].raw,
            str(len(r.warnings)),
        )
    console.print(t)


@app.command()
def coordinate(
    breed: str = typer.Option(..., "--breed", help="Breed id, e.g. SYN_M."),
    dataset: str = typer.Option("v1", "--dataset", help="Dataset tag, run id or folder."),
    date: str = typer.Option("2027-03-01", "--date", help="Planning date YYYY-MM-DD."),
    dams: str = typer.Option(
        "auto", "--dams", help="'auto' or a text file with one dam reg_no per line."
    ),
    delta_f: float | None = typer.Option(
        None, "--delta-f", help="Rate of inbreeding per generation (OCS gain under a budget)."
    ),
    mode: str = typer.Option("ocs", "--mode", help="ocs (optimum contributions) or cap."),
    profile: str = typer.Option("hr_full", "--profile", help="Rule profile."),
    top: int = typer.Option(25, "--top", help="Sires to show."),
) -> None:
    """Club-level season plan: litter quotas per sire and a suggested allocation (synthetic)."""
    from pathlib import Path

    import numpy as np
    from rich.table import Table

    from breeding_smarter.coordination.club import club_plan
    from breeding_smarter.matching import load_context

    if mode not in ("ocs", "cap"):
        raise typer.BadParameter("--mode must be ocs or cap")
    ctx = load_context(dataset)
    dam_idx = None
    if dams != "auto":
        regs = [x.strip() for x in Path(dams).read_text().splitlines() if x.strip()]
        dam_idx = np.array([ctx.idx_of(x) for x in regs], dtype=np.int64)
    cp = club_plan(ctx, breed, date, dam_idx, mode=mode, delta_f=delta_f, profile=profile)
    d = cp.plan.diagnostics
    console.print(
        f"{breed} on {date}, mode {mode}"
        + (f", dF {100 * delta_f:g}% per generation" if delta_f is not None else "")
        + f": {d['n_dams']} dams, {d['n_sires']} candidate sires, "
        f"{d.get('n_sires_with_quota', 0)} with a quota. Synthetic data."
    )
    if "achieved_C" in d:
        extra = f", budget {d['budget']:.4f}" if "budget" in d else ""
        console.print(f"Expected coancestry of the planned matings {d['achieved_C']:.4f}{extra}.")
    t = Table(title="Sire quotas (synthetic data)")
    for col in cp.sires.columns:
        t.add_column(col)
    for _, r in cp.sires.head(top).iterrows():
        t.add_row(*[str(v) for v in r.to_numpy()])
    console.print(t)
    m = Table(title="Suggested matings (minimum coancestry within quotas)")
    for col in cp.matings.columns:
        m.add_column(col)
    for _, r in cp.matings.iterrows():
        m.add_row(*[str(v) for v in r.to_numpy()])
    console.print(m)


experiment_app = typer.Typer(
    help="Breeding-strategy experiments (in silico).", no_args_is_help=True
)
app.add_typer(experiment_app, name="experiment")


@experiment_app.command("run")
def experiment_run(
    config: str = typer.Argument(
        ..., help="Experiment YAML, e.g. configs/experiments/headline.yaml"
    ),
    workers: int = typer.Option(1, "--workers", help="Parallel processes."),
    limit: int | None = typer.Option(None, "--limit", help="Run at most this many parts."),
) -> None:
    """Run all unfinished parts of an experiment (checkpointed per part)."""
    from pathlib import Path

    from breeding_smarter.experiments.runner import run_experiment

    out = run_experiment(Path(config), workers=workers, limit=limit)
    console.print(f"parts in {out}")


@experiment_app.command("report")
def experiment_report(
    exp_id: str = typer.Argument(..., help="Experiment id, e.g. E1_headline"),
) -> None:
    """Summary tables (mean, 95% CI, paired differences vs S1) and figures."""
    from breeding_smarter.experiments.summary import write_summary

    for p in write_summary(exp_id):
        console.print(f"wrote {p}")


@experiment_app.command("hypotheses")
def experiment_hypotheses() -> None:
    """Evaluate the pre-registered P12 criteria H1 to H6 from the E5 and E6 summaries."""
    from breeding_smarter.experiments.hypotheses import write_report

    console.print(f"wrote {write_report()}")


export_app = typer.Typer(help="Export the demo bundle and the release.", no_args_is_help=True)
app.add_typer(export_app, name="export")


@export_app.command("demo-bundle")
def export_demo_bundle(
    dataset: str = typer.Option("v1", "--dataset"),
    experiment: list[str] = typer.Option([], "--experiment", help="Experiment id (repeatable)."),
    out: str | None = typer.Option(None, "--out", help="Bundle folder (default ./bundle)."),
) -> None:
    """Write the demo bundle (registry tables, engine cache, summaries) for the app."""
    from pathlib import Path

    from breeding_smarter.bundle import export_bundle

    path = export_bundle(dataset, experiment, Path(out) if out else None)
    console.print(f"wrote {path} and {path.with_suffix('.tar.gz')}")


@export_app.command("release")
def export_release_cmd(dataset: str = typer.Option("v1", "--dataset")) -> None:
    """Write release/breeding-smarter-synthetic-<tag>/ (+ zip, SHA256SUMS, Zenodo metadata)."""
    from breeding_smarter.release import export_release

    out = export_release(dataset)
    z = out.parent / f"{out.name}.zip"
    console.print(f"wrote {out} and {z} ({z.stat().st_size / 1e6:.1f} MB)")


links_app = typer.Typer(help="Public links and DOIs (conference/links.yaml).", no_args_is_help=True)
app.add_typer(links_app, name="links")


@links_app.command("check")
def links_check() -> None:
    """List remaining TODO link placeholders; exit 1 if any remain."""
    from breeding_smarter.release import find_placeholders

    hits = find_placeholders()
    for f, line, text in hits:
        console.print(f"{f}:{line}: {text[:100]}")
    console.print(f"{len(hits)} placeholder(s) remaining")
    if hits:
        raise typer.Exit(1)


@links_app.command("fill")
def links_fill() -> None:
    """Replace placeholders with the values filled in conference/links.yaml."""
    from breeding_smarter.release import fill_placeholders

    console.print(f"updated {fill_placeholders()} file(s)")
