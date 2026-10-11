"""Demo bundle for the app (P9 task 9.1): everything the demo needs, no science in the app.

Layout (a run-like folder, so `DatasetContext.from_run` loads it directly):

    bundle/
    ├── manifest.json            # source run, dataset tag, experiments, created
    ├── registry/*.parquet       # registry tables (synthetic)
    ├── config_snapshot/         # configs of the source run
    ├── cache/                   # F, D, EqG of the registry pedigree
    ├── truth_small.parquet      # idx, f_true_ibd, f_true_pedigree (ground-truth toggle only)
    ├── validation/              # targets_vs_simulated.csv
    ├── experiments/<id>/        # summary.csv, paired_vs_S1.csv, per_generation_replicates.csv.gz
    ├── figures/                 # static experiment figures (PNG)
    ├── demo.yaml                # the three demo dams
    └── rules_catalogue.md

The app reads `BSM_BUNDLE_PATH`; if that is missing it downloads the archive from
`BSM_BUNDLE_URL` into a cache folder and extracts it.
"""

from __future__ import annotations

import json
import os
import shutil
import tarfile
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pandas as pd
import yaml

from breeding_smarter.io.cache import pedigree_cache
from breeding_smarter.io.datasets import resolve_dataset
from breeding_smarter.io.parquet import read_table
from breeding_smarter.io.paths import RunPaths, configs_dir, repo_root
from breeding_smarter.schema.tables import ANIMALS_TRUTH, REGISTRY_TABLES

if TYPE_CHECKING:
    from breeding_smarter.matching.context import DatasetContext

BUNDLE_NAME = "bundle"


def export_bundle(
    dataset: str = "v1", experiments: list[str] | None = None, out: Path | None = None
) -> Path:
    """Write the demo bundle folder and `<out>.tar.gz`; returns the folder."""
    rp = resolve_dataset(dataset)
    out = out or repo_root() / BUNDLE_NAME
    if out.exists():
        shutil.rmtree(out)
    (out / "registry").mkdir(parents=True)
    for spec in REGISTRY_TABLES:
        shutil.copy(rp.table(spec), out / spec.filename)
    shutil.copytree(rp.config_snapshot, out / "config_snapshot")
    pedigree_cache(rp, "registry")
    (out / "cache").mkdir()
    for suffix in ("parquet", "json"):
        src = rp.cache / f"pedigree_F_D_registry.{suffix}"
        dst = out / "cache" / src.name
        if suffix == "json":
            key = json.loads(src.read_text())
            key["run_id"] = out.name
            dst.write_text(json.dumps(key))
        else:
            shutil.copy(src, dst)
    truth = read_table(rp.table(ANIMALS_TRUTH), ANIMALS_TRUTH)
    small = truth.dropna(subset=["idx"])[["idx", "f_true_ibd", "f_true_pedigree"]]
    small.astype({"idx": "int64"}).to_parquet(out / "truth_small.parquet", index=False)
    val = repo_root() / "reports" / "validation" / rp.run_id / "targets_vs_simulated.csv"
    (out / "validation").mkdir()
    if val.exists():
        shutil.copy(val, out / "validation" / val.name)
    for exp in experiments or []:
        src = repo_root() / "reports" / "experiments" / exp
        dst = out / "experiments" / exp
        dst.mkdir(parents=True)
        for name in (
            "summary.csv",
            "paired_vs_S1.csv",
            "per_generation_replicates.csv.gz",
            "summary.md",
        ):
            if (src / name).exists():
                shutil.copy(src / name, dst / name)
        figs = src / "figures"
        if figs.is_dir():
            (out / "figures").mkdir(exist_ok=True)
            for f in figs.glob("*.png"):  # first experiment listed wins a shared figure name
                if "_poster" not in f.name and not (out / "figures" / f.name).exists():
                    shutil.copy(f, out / "figures" / f.name)
    demo = configs_dir() / "demo.yaml"
    if demo.exists():
        shutil.copy(demo, out / "demo.yaml")
    cat = repo_root() / "docs" / "rules_catalogue.md"
    if cat.exists():
        shutil.copy(cat, out / "rules_catalogue.md")
    manifest = {
        "bundle": out.name,
        "dataset": dataset,
        "source_run": rp.run_id,
        "experiments": experiments or [],
        "created_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "scale": json.loads(rp.manifest.read_text()).get("scale"),
        "note": "All animals are synthetic.",
    }
    src_manifest = json.loads(rp.manifest.read_text())
    manifest["source_manifest"] = {
        k: src_manifest.get(k) for k in ("run_id", "seed", "config_hash", "git_commit")
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    with tarfile.open(out.with_suffix(".tar.gz"), "w:gz") as tar:
        tar.add(out, arcname=out.name)
    return out


def _cache_dir() -> Path:
    return Path(os.environ.get("BSM_CACHE_DIR", Path.home() / ".cache" / "breeding-smarter"))


def resolve_bundle() -> Path:
    """`BSM_BUNDLE_PATH`, else `./bundle` in the repo, else download `BSM_BUNDLE_URL`."""
    env = os.environ.get("BSM_BUNDLE_PATH")
    if env:
        return Path(env)
    local = repo_root() / BUNDLE_NAME
    if (local / "manifest.json").exists():
        return local
    url = os.environ.get("BSM_BUNDLE_URL")
    if not url:
        raise FileNotFoundError("no bundle: set BSM_BUNDLE_PATH or BSM_BUNDLE_URL")
    cache = _cache_dir()
    target = cache / BUNDLE_NAME
    if not (target / "manifest.json").exists():
        cache.mkdir(parents=True, exist_ok=True)
        archive = cache / "bundle.tar.gz"
        urllib.request.urlretrieve(url, archive)
        with tarfile.open(archive) as tar:
            tar.extractall(cache, filter="data")
    return target


@dataclass
class Bundle:
    path: Path

    @classmethod
    def open(cls, path: Path | None = None) -> Bundle:
        return cls(Path(path) if path else resolve_bundle())

    @property
    def manifest(self) -> dict[str, Any]:
        data: dict[str, Any] = json.loads((self.path / "manifest.json").read_text())
        return data

    def context(self) -> DatasetContext:
        from breeding_smarter.matching.context import DatasetContext

        return DatasetContext.from_run(RunPaths(self.path), self.manifest.get("dataset"))

    def demo(self) -> dict[str, Any]:
        p = self.path / "demo.yaml"
        return yaml.safe_load(p.read_text()) if p.exists() else {"dams": []}

    def truth_small(self) -> pd.DataFrame:
        return pd.read_parquet(self.path / "truth_small.parquet")

    def validation(self) -> pd.DataFrame | None:
        files = sorted((self.path / "validation").glob("*.csv"))
        return pd.read_csv(files[0]) if files else None

    def experiments(self) -> list[str]:
        d = self.path / "experiments"
        return sorted(p.name for p in d.iterdir()) if d.is_dir() else []

    def experiment_table(self, exp_id: str, name: str = "summary.csv") -> pd.DataFrame | None:
        p = self.path / "experiments" / exp_id / name
        return pd.read_csv(p) if p.exists() else None

    def figure(self, name: str) -> Path | None:
        p = self.path / "figures" / f"{name}.png"
        return p if p.exists() else None

    def rules_catalogue(self) -> str:
        p = self.path / "rules_catalogue.md"
        return p.read_text() if p.exists() else ""
