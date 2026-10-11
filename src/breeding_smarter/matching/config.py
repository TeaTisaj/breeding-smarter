"""Scoring policy model (`configs/scoring/*.yaml`)."""

from __future__ import annotations

from pathlib import Path
from typing import Self

from pydantic import model_validator

from breeding_smarter.config.loader import load_config
from breeding_smarter.config.sourced import Sourced, Strict
from breeding_smarter.io.paths import configs_dir

COMPONENTS = ("inbreeding", "diversity", "health", "ebv", "sire_use", "depth")


class InbreedingParams(Strict):
    f_low: Sourced[float]
    f_high: Sourced[float]


class HealthScoreParams(Strict):
    p_any_zero_score: Sourced[float]


class EbvParams(Strict):
    index_mean: Sourced[float]
    index_sd: Sourced[float]


class SireUseParams(Strict):
    fci_share: Sourced[float]
    window_years: Sourced[int]


class DepthParams(Strict):
    eqg_target: Sourced[float]


class ScoringConfig(Strict):
    weights: Sourced[dict[str, float]]
    inbreeding: InbreedingParams
    health: HealthScoreParams
    ebv: EbvParams
    sire_use: SireUseParams
    depth: DepthParams
    tiers: Sourced[list[tuple[float, str]]]
    soft_warning_caps_tier_at: Sourced[str]
    low_depth_warning_eqg: Sourced[float]
    allele_frequency_window_years: Sourced[int]

    @model_validator(mode="after")
    def _check(self) -> Self:
        w = self.weights.value
        if set(w) != set(COMPONENTS):
            raise ValueError(f"weights must cover exactly {COMPONENTS}")
        if abs(sum(w.values()) - 1.0) > 1e-9 or min(w.values()) < 0:
            raise ValueError("weights must be non-negative and sum to 1")
        labels = [t[1] for t in self.tiers.value]
        if self.soft_warning_caps_tier_at.value not in labels:
            raise ValueError("soft_warning_caps_tier_at must be a tier label")
        if self.inbreeding.f_low.value >= self.inbreeding.f_high.value:
            raise ValueError("f_low must be below f_high")
        return self

    def with_weights(self, weights: dict[str, float]) -> ScoringConfig:
        """Copy with new weights (renormalised to sum to 1), e.g. from app sliders."""
        tot = sum(weights.values())
        w = {k: float(weights.get(k, 0.0)) / tot for k in COMPONENTS}
        return self.model_copy(update={"weights": self.weights.model_copy(update={"value": w})})

    def tier(self, score: float) -> str:
        for lo, label in sorted(self.tiers.value, reverse=True):
            if score >= lo:
                return label
        return self.tiers.value[-1][1]

    def tier_rank(self, label: str) -> int:
        """0 = best tier."""
        ordered = [t[1] for t in sorted(self.tiers.value, reverse=True)]
        return ordered.index(label)


def load_scoring(name_or_path: str | Path = "default") -> ScoringConfig:
    p = Path(name_or_path)
    if not p.suffix:
        p = configs_dir() / "scoring" / f"{name_or_path}.yaml"
    return load_config(p, ScoringConfig)
