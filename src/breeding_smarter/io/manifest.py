"""Run manifests (`manifest.json`)."""

from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from breeding_smarter import __version__


def git_commit(cwd: Path | None = None) -> str:
    """Current git commit hash, with `-dirty` if the tree has changes; 'unknown' outside git."""
    try:
        sha = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=cwd, capture_output=True, text=True, check=True
        ).stdout.strip()
        dirty = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=no"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        return sha + ("-dirty" if dirty else "")
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def write_manifest(path: Path, **fields: Any) -> dict[str, Any]:
    """Write a manifest. Adds package version, git commit and a UTC timestamp if missing."""
    data = {
        "package_version": __version__,
        "git_commit": git_commit(path.parent),
        "written_at": datetime.now(UTC).isoformat(timespec="seconds"),
    }
    data.update(fields)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True, default=str) + "\n")
    return data


def read_manifest(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = json.loads(path.read_text())
    return result


def update_manifest(path: Path, **fields: Any) -> dict[str, Any]:
    data = read_manifest(path) if path.exists() else {}
    data.update(fields)
    path.write_text(json.dumps(data, indent=2, sort_keys=True, default=str) + "\n")
    return data
