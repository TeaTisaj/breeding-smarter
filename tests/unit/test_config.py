import re
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from breeding_smarter.config import (
    ConfigError,
    SpeciesConfig,
    collect_assumptions,
    config_hash,
    load_breed,
    load_config,
    load_sim,
    load_species,
)
from breeding_smarter.config.sourced import Sourced, SourcedSeries
from breeding_smarter.io import configs_dir, repo_root


def _species_dict():
    return yaml.safe_load((configs_dir() / "species" / "dog.yaml").read_text())


def test_load_species_and_breeds():
    sp = load_species()
    assert sp.gestation_days.value == 63
    assert sp.min_breeding_age_months.for_sex("F") == 15
    for name, bid in [("syn_large", "SYN_L"), ("syn_medium", "SYN_M"), ("syn_small", "SYN_S")]:
        b = load_breed(name)
        assert b.breed_id == bid
        assert 3.5 <= b.reproduction.litter_size_mean.value <= 7.1
    assert load_breed("syn_small").is_local_breed


def test_config_forbids_extra_keys(tmp_path):
    d = _species_dict()
    d["gestaton_days"] = {"value": 63, "assumption": True}
    p = tmp_path / "dog.yaml"
    p.write_text(yaml.safe_dump(d))
    with pytest.raises(ConfigError, match="gestaton_days"):
        load_config(p, SpeciesConfig)


def test_config_requires_source_or_assumption():
    with pytest.raises(ValidationError, match="source"):
        Sourced[float].model_validate({"value": 1.0})
    with pytest.raises(ValidationError, match="unknown source key"):
        Sourced[float].model_validate({"value": 1.0, "source": "not-a-key"})
    assert Sourced[float].model_validate({"value": 1.0, "source": "borge-2011"}).value == 1.0
    assert Sourced[float].model_validate({"value": 1.0, "assumption": True}).assumption


def test_nested_missing_source_fails_with_path(tmp_path):
    d = _species_dict()
    d["sex_ratio_male"] = {"value": 0.5}
    p = tmp_path / "dog.yaml"
    p.write_text(yaml.safe_dump(d))
    with pytest.raises(ConfigError, match="sex_ratio_male"):
        load_config(p, SpeciesConfig)


def test_invalid_yaml_and_missing_file(tmp_path):
    p = tmp_path / "x.yaml"
    p.write_text("a: [1, 2\n")
    with pytest.raises(ConfigError, match="invalid YAML"):
        load_config(p, SpeciesConfig)
    with pytest.raises(ConfigError, match="not found"):
        load_config(tmp_path / "nope.yaml", SpeciesConfig)


def test_series_interpolation():
    s = SourcedSeries(points=[(1980, 100), (2000, 300)], assumption=True)
    assert s.at(1990) == 200
    assert s.at(1970) == 100 and s.at(2030) == 300
    with pytest.raises(ValidationError):
        SourcedSeries(points=[(2000, 1), (1990, 2)], assumption=True)


def test_config_hash_stable_and_sensitive():
    c = load_sim(configs_dir() / "sim" / "default.yaml")
    assert config_hash(c) == config_hash(c.model_copy())
    assert config_hash(c) != config_hash(c.model_copy(update={"seed": 1}))


def test_sources_cover_research_keys():
    text = (repo_root() / "docs" / "research.md").read_text().split("## 9. Citation keys")[1]
    keys = {k for k in re.findall(r"^\| ([a-z0-9\-]+) \|", text, re.M) if k != "Key"}
    sources = set(yaml.safe_load((configs_dir() / "sources.yaml").read_text())["sources"])
    assert len(keys) >= 40
    assert keys <= sources, keys - sources


def test_collect_assumptions_lists_values():
    found = dict((p, v) for p, v, _ in collect_assumptions(load_breed("syn_medium")))
    assert found["population.founders_base_generation"] == 120
    assert "market.popular_sire_alpha" in found
    assert "expected_ne" not in found  # sourced, not an assumption


def test_microchip_source_registered():
    assert "icar-999" in yaml.safe_load(Path(configs_dir() / "sources.yaml").read_text())["sources"]
