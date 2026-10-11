"""List every config value marked `assumption: true` (for gate reports and the datasheet)."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from breeding_smarter.config.loader import load_breed, load_genetics, load_loci, load_sim
from breeding_smarter.config.sourced import collect_assumptions
from breeding_smarter.io.paths import configs_dir, repo_root


def config_models(sim_path: Path | None = None) -> list[tuple[str, BaseModel]]:
    from breeding_smarter.config.loader import load_species
    from breeding_smarter.matching.config import load_scoring

    sim = load_sim(sim_path or configs_dir() / "sim" / "default.yaml")
    out: list[tuple[str, BaseModel]] = [
        ("sim", sim),
        ("species", load_species(sim.species)),
        ("genetics", load_genetics(sim.genetics)),
        ("loci", load_loci(sim.loci)),
        ("scoring", load_scoring()),
    ]
    out += [(f"breed {b}", load_breed(b)) for b in sim.breeds]
    return out


def render_assumptions() -> str:
    lines = [
        "# Assumptions",
        "",
        "Generated from the YAML configs (`bsm docs assumptions`). Every value below is marked",
        "`assumption: true`: it is a modelling or policy choice, not a published number.",
        "Values with a `source` are cited in `configs/sources.yaml` and not listed here.",
        "",
        "| Config | Parameter | Value | Note |",
        "|---|---|---|---|",
    ]
    for name, model in config_models():
        for path, value, note in collect_assumptions(model):
            v = str(value).replace("|", "/")
            lines.append(f"| {name} | {path} | {v} | {note or ''} |")
    return "\n".join(lines) + "\n"


def write_assumptions(path: Path | None = None) -> Path:
    p = path or repo_root() / "docs" / "assumptions.md"
    p.write_text(render_assumptions())
    return p
