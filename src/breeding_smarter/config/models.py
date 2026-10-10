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


class HealthParams(Strict):
    """Breed health programme (P4): HD screening and DNA testing."""

    hd_screening_start_year: Sourced[int]
    hd_screening_rate_candidates: Sourced[float]
    hd_screening_rate_others: Sourced[float]
    hd_base_distribution: Sourced[dict[str, float]]
    hd_exclude_grades: Sourced[list[str]]
    dna_test_rate_2026: Sourced[float]

    @model_validator(mode="after")
    def _dist(self) -> Self:
        d = self.hd_base_distribution.value
        if list(d) != ["A", "B", "C", "D", "E"] or abs(sum(d.values()) - 1) > 1e-9:
            raise ValueError("hd_base_distribution must give A..E shares summing to 1")
        return self


class BreedConfig(Strict):
    """One synthetic breed archetype."""

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
    health: HealthParams


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


class Locus(Strict):
    id: str
    gene: str
    mode: Literal["recessive"]
    penetrance: Sourced[float]
    test_available_from: Sourced[int] | None

    @property
    def testable(self) -> bool:
        return self.test_available_from is not None


class LociConfig(Strict):
    loci: list[Locus]
    base_allele_frequency: Sourced[dict[str, dict[str, float]]]

    @property
    def ids(self) -> list[str]:
        return [x.id for x in self.loci]

    @model_validator(mode="after")
    def _freqs(self) -> Self:
        for breed, f in self.base_allele_frequency.value.items():
            if set(f) != set(self.ids):
                raise ValueError(f"{breed}: base frequencies must cover exactly {self.ids}")
            if any(not 0 <= q <= 1 for q in f.values()):
                raise ValueError(f"{breed}: frequencies must be in [0, 1]")
        return self


class GeneticsConfig(Strict):
    n_neutral_loci: Sourced[int]
    hd_heritability: Sourced[float]
    hd_screening_age_months: Sourced[tuple[int, int]]
    dna_test_min_age_months: Sourced[int]
    dna_test_rate_initial: Sourced[float]
    dna_test_rate_ramp_end_year: Sourced[int]
    import_dna_test_prob: Sourced[float]
    affected_exclusion_prob: Sourced[float]
    carrier_pair_resample_prob: Sourced[float]
    labs: list[str]
    evaluation_date: str
    ebv_birth_year_group_years: Sourced[int]
    ebv_index_sd_window_years: Sourced[int]


class SimConfig(Strict):
    """Top-level simulation config (`configs/sim/*.yaml`)."""

    name: str
    seed: int
    registry_start_year: int
    end_year: int
    generation_interval_years: Sourced[float]
    burn_in_generations: int
    species: str = "dog"
    genetics: str = "dog"
    loci: str = "dog_mendelian"
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
