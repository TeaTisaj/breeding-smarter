"""Coordination policy model (`configs/coordination/*.yaml`)."""

from __future__ import annotations

from pathlib import Path

from breeding_smarter.config.loader import load_config
from breeding_smarter.config.sourced import Sourced, Strict
from breeding_smarter.io.paths import configs_dir


class CoordinationConfig(Strict):
    delta_f_ladder: Sourced[list[float]]
    delta_f_extra_medium: Sourced[list[float]]
    delta_f_default: Sourced[float]
    generation_interval_window_years: Sourced[int]
    small_cohort_term: Sourced[bool]
    cap_base_litters_per_year: Sourced[int]
    cap_mk_scaling: Sourced[bool]
    min_expected_litters: Sourced[float]
    youngest_age_classes_required: Sourced[int]
    depth_constraint: Sourced[bool]
    health_weight_in_allocation: Sourced[float]
    lifetime_cap_offspring: Sourced[int | None]
    solver: Sourced[str]


def load_coordination(name: str = "default", base: Path | None = None) -> CoordinationConfig:
    return load_config(
        (base or configs_dir()) / "coordination" / f"{name}.yaml", CoordinationConfig
    )
