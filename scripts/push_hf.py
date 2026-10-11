"""Push the release to a Hugging Face dataset repo (P10 task 10.7). [HUMAN: needs a token]

Usage:
    export HF_TOKEN=hf_...            # a write token from https://huggingface.co/settings/tokens
    uv run python scripts/push_hf.py --repo <user>/breeding-smarter-synthetic [--tag v1]

Uploads the Parquet tables, the dataset card (README with YAML metadata), datasheet, data
dictionary, licence, validation files and, if present, bundle.tar.gz for the demo app.
All data is synthetic.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def card_with_metadata(release: Path, tag: str) -> str:
    meta = f"""---
license: cc-by-4.0
pretty_name: Breeding Smarter synthetic dog pedigree dataset ({tag})
tags: [synthetic, pedigree, dogs, animal-genetics, inbreeding]
size_categories: [100K<n<1M]
configs:
  - config_name: animals
    data_files: registry/animals.parquet
  - config_name: litters
    data_files: registry/litters.parquet
  - config_name: health_tests
    data_files: registry/health_tests.parquet
  - config_name: dna_tests
    data_files: registry/dna_tests.parquet
  - config_name: ebv
    data_files: registry/ebv.parquet
  - config_name: kennels
    data_files: registry/kennels.parquet
  - config_name: breeds
    data_files: registry/breeds.parquet
  - config_name: animals_truth
    data_files: truth/animals_truth.parquet
---
"""
    return meta + (release / "README.md").read_text()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--tag", default="v1")
    args = ap.parse_args()
    token = os.environ.get("HF_TOKEN")
    if not token:
        print("set HF_TOKEN first", file=sys.stderr)
        return 2
    from huggingface_hub import HfApi

    release = ROOT / "release" / f"breeding-smarter-synthetic-{args.tag}"
    if not release.is_dir():
        print("run `uv run bsm export release` first", file=sys.stderr)
        return 2
    api = HfApi(token=token)
    api.create_repo(args.repo, repo_type="dataset", exist_ok=True)
    tmp = release / "README.hf.md"
    tmp.write_text(card_with_metadata(release, args.tag))
    api.upload_file(
        path_or_fileobj=str(tmp), path_in_repo="README.md", repo_id=args.repo, repo_type="dataset"
    )
    tmp.unlink()
    api.upload_folder(
        folder_path=str(release),
        repo_id=args.repo,
        repo_type="dataset",
        allow_patterns=[
            "registry/*",
            "truth/*",
            "validation/**",
            "datasheet.md",
            "data_dictionary.md",
            "LICENSE",
            "SHA256SUMS",
            "manifest.json",
        ],
    )
    bundle = ROOT / "bundle.tar.gz"
    if bundle.exists():
        api.upload_file(
            path_or_fileobj=str(bundle),
            path_in_repo="bundle.tar.gz",
            repo_id=args.repo,
            repo_type="dataset",
        )
    print(f"https://huggingface.co/datasets/{args.repo}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
