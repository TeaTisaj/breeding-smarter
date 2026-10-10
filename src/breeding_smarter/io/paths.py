"""Resolve file paths of a run folder."""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from breeding_smarter.schema.tables import TableSpec

PACKAGE_ROOT = Path(__file__).resolve().parents[1]


def repo_root() -> Path:
    """Repository root (`BSM_ROOT` overrides; default: two levels above the package)."""
    env = os.environ.get("BSM_ROOT")
    if env:
        return Path(env).resolve()
    candidate = PACKAGE_ROOT.parents[1]
    if (candidate / "configs").is_dir():
        return candidate
    return Path.cwd()


def configs_dir() -> Path:
    return repo_root() / "configs"


def data_dir() -> Path:
    return Path(os.environ.get("BSM_DATA_DIR", repo_root() / "data" / "generated"))


def make_run_id(config_name: str, seed: int, day: date | None = None) -> str:
    """`<YYYYMMDD>-<config name>-s<seed>`, e.g. `20261013-default-s42`."""
    d = day or date.today()
    return f"{d:%Y%m%d}-{config_name}-s{seed}"


@dataclass(frozen=True)
class RunPaths:
    """All paths of one run folder."""

    root: Path

    @classmethod
    def for_run(cls, run_id: str, base: Path | None = None) -> RunPaths:
        return cls((base or data_dir()) / run_id)

    @property
    def run_id(self) -> str:
        return self.root.name

    @property
    def manifest(self) -> Path:
        return self.root / "manifest.json"

    @property
    def config_snapshot(self) -> Path:
        return self.root / "config_snapshot"

    @property
    def registry(self) -> Path:
        return self.root / "registry"

    @property
    def truth(self) -> Path:
        return self.root / "truth"

    @property
    def state(self) -> Path:
        return self.root / "state"

    @property
    def cache(self) -> Path:
        return self.root / "cache"

    def table(self, spec: TableSpec) -> Path:
        return self.root / spec.filename
