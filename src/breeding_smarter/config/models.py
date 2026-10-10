"""Pydantic models for species, breed and simulation configs (YAML in `configs/`)."""

from __future__ import annotations

from typing import Literal, Self

from pydantic import model_validator

from breeding_smarter.config.sourced import Provenance, Sourced, SourcedSeries, Strict

SizeClass = Literal["toy", "small", "medium", "large", "giant"]


class BySex(Strict):
    female: Sourced[float]
    male: Sourced[float]

    def for_sex(self, sex: str) -> float:
        """`sex` is 'F' or 'M'."""
        return self.female.value if sex == "F" else self.male.value


class Weibull(Provenance):
    shape: float
    scale_years: float


class SpeciesConfig(Strict):
    """Species-level biology (no breed-specific values)."""

    species: str
    gestation_days: Sourced[int]
    gestation_sd_days: Sourced[float]
    min_breeding_age_months: BySex
    max_breeding_age_years: BySex
    lifespan_weibull: Weibull
    sex_ratio_male: Sourced[float]
    death_cause_shares: Sourced[dict[str, float]]
    inbreeding_litter_slope: Sourced[float]
    attractiveness_sd: Sourced[float]
    fertility_log_sd: Sourced[float]

    @model_validator(mode="after")
    def _shares(self) -> Self:
        s = sum(self.death_cause_shares.value.values())
        if abs(s - 1) > 1e-9:
            raise ValueError(f"death_cause_shares must sum to 1, got {s}")
        return self


class PopulationParams(Strict):
    registrations_per_year: SourcedSeries
    founders_base_generation: Sourced[int]
    burn_in_size_fraction: Sourced[float]
    split_year: Sourced[int]


class ReproductionParams(Strict):
    litter_size_mean: Sourced[float]
    litter_size_dispersion: Sourced[float]
    perinatal_loss_rate: Sourced[float]
    registration_rate: Sourced[float]
    caesarean_rate: Sourced[float]
    max_litters_per_dam: Sourced[int]
    min_months_between_litters: Sourced[int]


class MarketParams(Strict):
    female_candidate_share: Sourced[float]
    male_candidate_share: Sourced[float]
    popular_sire_alpha: SourcedSeries
    attractiveness_beta: Sourced[float]
    import_rate: Sourced[float]
    foreign_ai_sire_share: Sourced[float]
    ai_frozen_share: Sourced[float]
    import_pedigree_depth: Sourced[int]
    close_mating_avoidance: Sourced[float]


class BreedConfig(Strict):
    """One synthetic breed archetype. Health and genetics sections are added in P4."""

    breed_id: str
    display_name: str
    size_class: SizeClass
    is_local_breed: bool
    archetype_description: str
    studbook: str = "HR"
    population: PopulationParams
    reproduction: ReproductionParams
    market: MarketParams
    coat_colours: list[str]
    expected_ne: Sourced[tuple[float, float]]


class ForeignParams(Strict):
    size_factor: Sourced[float]
    countries: list[str]


class MarketDefaults(Strict):
    """Behavioural constants of the status-quo market shared by all breeds (P3 task 3.5)."""

    distance_scale_km: Sourced[float]
    same_kennel_exclusion_prob: Sourced[float]
    prime_age_years: Sourced[tuple[float, float]]
    off_prime_age_factor: Sourced[float]
    max_resample_retries: Sourced[int]


class RegistryParams(Strict):
    """Constants used when writing registry tables (P3 task 3.8)."""

    limited_registration_share: Sourced[float]
    titles_rate: Sourced[float]
    dogs_per_private_owner: Sourced[float]
    min_founders: Sourced[int]


class SimConfig(Strict):
    """Top-level simulation config (`configs/sim/*.yaml`)."""

    name: str
    seed: int
    registry_start_year: int
    end_year: int
    generation_interval_years: Sourced[float]
    burn_in_generations: int
    species: str = "dog"
    breeds: list[str]
    scale: float = 1.0
    foreign: ForeignParams
    market: MarketDefaults
    registry: RegistryParams

    @property
    def start_year(self) -> int:
        """First simulated year: registry start minus the burn-in generations."""
        gi = self.generation_interval_years.value
        return self.registry_start_year - round(self.burn_in_generations * gi)

    @model_validator(mode="after")
    def _years(self) -> Self:
        if self.end_year <= self.registry_start_year:
            raise ValueError("end_year must be after registry_start_year")
        if self.scale <= 0:
            raise ValueError("scale must be positive")
        return self
