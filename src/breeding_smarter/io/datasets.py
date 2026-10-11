"""Dataset tags (`configs/datasets.yaml`): tag -> run id, config hash, git commit."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from breeding_smarter.io.paths import RunPaths, configs_dir, data_dir


def _path() -> Path:
    return configs_dir() / "datasets.yaml"


def read_tags() -> dict[str, dict[str, Any]]:
    p = _path()
    if not p.exists():
        return {}
    return dict(yaml.safe_load(p.read_text()).get("datasets") or {})


def tag_dataset(tag: str, run_id: str, **info: Any) -> None:
    p = _path()
    doc = yaml.safe_load(p.read_text()) if p.exists() else {}
    doc = doc or {}
    doc.setdefault("datasets", {})
    doc["datasets"] = doc["datasets"] or {}
    doc["datasets"][tag] = {"run_id": run_id, **info}
    header = "# Dataset tags. Later phases load data by tag, never by a hard-coded run id.\n"
    p.write_text(header + yaml.safe_dump(doc, sort_keys=False))


def resolve_dataset(tag_or_run: str) -> RunPaths:
    """A dataset tag (e.g. `v1`), a run id, or a run folder path."""
    p = Path(tag_or_run)
    if p.is_dir():
        return RunPaths(p.resolve())
    tags = read_tags()
    run_id = tags[tag_or_run]["run_id"] if tag_or_run in tags else tag_or_run
    rp = RunPaths(data_dir() / run_id)
    if not rp.root.is_dir():
        raise FileNotFoundError(f"dataset {tag_or_run!r} not found at {rp.root}")
    return rp
