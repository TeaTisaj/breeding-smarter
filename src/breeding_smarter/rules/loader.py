"""Load and compose rule profiles from `configs/rules/*.yaml`."""

from __future__ import annotations

from pathlib import Path

from breeding_smarter.config.loader import ConfigError, load_config
from breeding_smarter.io.paths import configs_dir
from breeding_smarter.pedigree.relationships import Relationship
from breeding_smarter.rules.models import Profile, ProfileSpec, RuleSpec


class RuleConfigError(ConfigError):
    """A rule profile is invalid (unknown type, relationship, source, include cycle)."""


def rules_dir() -> Path:
    return configs_dir() / "rules"


def load_spec(name: str, base: Path | None = None) -> ProfileSpec:
    path = (base or rules_dir()) / f"{name}.yaml"
    try:
        spec = load_config(path, ProfileSpec)
    except ConfigError as exc:
        raise RuleConfigError(str(exc)) from exc
    if spec.profile != name:
        raise RuleConfigError(f"{path}: profile name {spec.profile!r} != file name {name!r}")
    return spec


def _check_rule(rule: RuleSpec) -> None:
    from breeding_smarter.rules.types import RULE_TYPES

    if rule.type not in RULE_TYPES:
        raise RuleConfigError(f"rule {rule.id}: unknown rule type {rule.type!r}")
    RULE_TYPES[rule.type].validate_params(rule)
    if rule.type == "relationship_ban":
        for name in rule.params.get("relationships", []):
            if name not in Relationship.__members__:
                raise RuleConfigError(f"rule {rule.id}: unknown relationship {name!r}")


def load_profile(name: str, base: Path | None = None) -> Profile:
    """Compose a profile with its includes (depth first); a rule included twice is kept once."""
    rules: dict[str, RuleSpec] = {}
    members: list[str] = []

    def visit(n: str, stack: tuple[str, ...]) -> None:
        if n in stack:
            raise RuleConfigError(f"include cycle: {' -> '.join((*stack, n))}")
        spec = load_spec(n, base)
        for inc in spec.include:
            visit(inc, (*stack, n))
        if n not in members:
            members.append(n)
        for r in spec.rules:
            r = r.model_copy(
                update={"profile": n, "derogation_granted": spec.local_breed_derogation_granted}
            )
            _check_rule(r)
            if r.id in rules and rules[r.id] != r:
                raise RuleConfigError(f"rule id {r.id} defined twice with different content")
            rules.setdefault(r.id, r)

    first = load_spec(name, base)
    visit(name, ())
    return Profile(
        name=name, title=first.title, rules=tuple(rules.values()), members=tuple(members)
    )


def available_profiles(base: Path | None = None) -> list[str]:
    return sorted(p.stem for p in (base or rules_dir()).glob("*.yaml"))
