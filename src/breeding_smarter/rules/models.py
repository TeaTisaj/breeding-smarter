"""Rule and profile models (P6). Rules live in YAML; the engine never hard-codes a regulation."""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal, Self

from pydantic import Field, model_validator

from breeding_smarter.config.sourced import Strict, known_sources


class Severity(StrEnum):
    HARD = "HARD"
    SOFT = "SOFT"
    INFO = "INFO"


class Status(StrEnum):
    PERMITTED = "PERMITTED"
    PERMITTED_WITH_WARNINGS = "PERMITTED_WITH_WARNINGS"
    NOT_PERMITTED = "NOT_PERMITTED"


class RuleSpec(Strict):
    """One check: a `type` implemented in code, its `params` and its provenance."""

    id: str
    type: str
    params: dict[str, Any] = Field(default_factory=dict)
    severity: Severity
    source: str
    verified: bool
    article: str | None = None
    note: str | None = None
    derogation: Literal["local_breed"] | None = None
    profile: str = ""  # filled by the loader: the profile that defines the rule
    derogation_granted: bool = False  # filled by the loader from the defining profile

    @model_validator(mode="after")
    def _source(self) -> Self:
        if self.source not in known_sources():
            raise ValueError(f"rule {self.id}: unknown source key {self.source!r}")
        return self


class ProfileSpec(Strict):
    profile: str
    title: str
    include: list[str] = Field(default_factory=list)
    in_application_from: str | None = None
    local_breed_derogation_granted: bool = False
    note: str | None = None
    rules: list[RuleSpec] = Field(default_factory=list)


class Profile(Strict):
    """A composed profile: its own rules plus all included profiles' rules, each id once."""

    name: str
    title: str
    rules: tuple[RuleSpec, ...]
    members: tuple[str, ...]

    def rule(self, rule_id: str) -> RuleSpec:
        return next(r for r in self.rules if r.id == rule_id)
