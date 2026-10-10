"""Load YAML configs into validated pydantic models."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml
from pydantic import BaseModel, ValidationError

from breeding_smarter.config.models import BreedConfig, SimConfig, SpeciesConfig
from breeding_smarter.io.paths import configs_dir


class ConfigError(ValueError):
    """A config file is missing or invalid."""


def load_yaml(path: Path) -> object:
    try:
        return yaml.safe_load(Path(path).read_text())
    except FileNotFoundError as exc:
        raise ConfigError(f"config file not found: {path}") from exc
    except yaml.YAMLError as exc:
        raise ConfigError(f"{path}: invalid YAML: {exc}") from exc


def load_config[M: BaseModel](path: Path, model: type[M]) -> M:
    """Parse `path` (plain YAML, no templating) into `model`; errors name the file and field."""
    data = load_yaml(path)
    try:
        return model.model_validate(data)
    except ValidationError as exc:
        raise ConfigError(f"{path}: {exc}") from exc


def config_hash(model: BaseModel | list[BaseModel]) -> str:
    """sha256 of the canonical JSON of one model or a list of models."""
    models = model if isinstance(model, list) else [model]
    payload = json.dumps([m.model_dump(mode="json") for m in models], sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()


def load_species(name: str = "dog", base: Path | None = None) -> SpeciesConfig:
    return load_config((base or configs_dir()) / "species" / f"{name}.yaml", SpeciesConfig)


def load_breed(name: str, base: Path | None = None) -> BreedConfig:
    """`name` is the file stem, e.g. `syn_medium`."""
    return load_config((base or configs_dir()) / "breeds" / f"{name}.yaml", BreedConfig)


def load_sim(path: Path) -> SimConfig:
    return load_config(path, SimConfig)
