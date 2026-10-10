"""Plug-in interfaces: genetics models (P4) and mating strategies (P3 market, P8 strategies)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Protocol

import numpy as np

from breeding_smarter.config.models import BreedConfig, SimConfig, SpeciesConfig

if TYPE_CHECKING:
    from breeding_smarter.sim.state import SimState


@dataclass(frozen=True)
class SimSetup:
    """Everything a run needs from config: sim, species and the breed configs in order."""

    sim: SimConfig
    species: SpeciesConfig
    breeds: tuple[BreedConfig, ...]

    def breed_index(self, breed_id: str) -> int:
        return [b.breed_id for b in self.breeds].index(breed_id)


class GeneticsModel(Protocol):
    def init_founders(
        self, state: SimState, gids: np.ndarray, rng: np.random.Generator
    ) -> None: ...

    def make_offspring(
        self,
        state: SimState,
        sire: np.ndarray,
        dam: np.ndarray,
        child_gids: np.ndarray,
        rng: np.random.Generator,
    ) -> None:
        """`sire`/`dam` are per child (same length as `child_gids`)."""
        ...

    def is_eligible(self, state: SimState, gids: np.ndarray, year: int) -> np.ndarray: ...

    def pair_avoid(
        self, state: SimState, dams: np.ndarray, sires: np.ndarray, rng: np.random.Generator
    ) -> np.ndarray:
        """Boolean per pair: the breeder would resample this pair (e.g. carrier x carrier)."""
        ...

    def on_year_end(self, state: SimState, year: int, rng: np.random.Generator) -> None: ...

    def on_import(
        self, state: SimState, gids: np.ndarray, year: int, rng: np.random.Generator
    ) -> None: ...

    def state_arrays(self) -> dict[str, np.ndarray]: ...

    def load_arrays(self, arrays: dict[str, np.ndarray]) -> None: ...


class NullGenetics:
    """No genetics: everyone eligible, F stays 0 (P3 default)."""

    def init_founders(self, state: SimState, gids: np.ndarray, rng: np.random.Generator) -> None:
        return None

    def make_offspring(self, state, sire, dam, child_gids, rng) -> None:
        return None

    def is_eligible(self, state: SimState, gids: np.ndarray, year: int) -> np.ndarray:
        return np.ones(gids.shape[0], dtype=bool)

    def pair_avoid(self, state, dams, sires, rng) -> np.ndarray:
        return np.zeros(np.asarray(dams).shape[0], dtype=bool)

    def on_year_end(self, state: SimState, year: int, rng: np.random.Generator) -> None:
        return None

    def on_import(self, state, gids, year, rng) -> None:
        return None

    def state_arrays(self) -> dict[str, np.ndarray]:
        return {}

    def load_arrays(self, arrays: dict[str, np.ndarray]) -> None:
        return None


@dataclass
class YearContext:
    """Read access for strategies to the state of one breed and subpopulation in one year."""

    state: SimState
    setup: SimSetup
    year: int
    breed: int
    subpop: int
    offspring_5y: np.ndarray  # per gid: offspring (animals) in the last 5 years
    genetics: GeneticsModel
    foreign_sires: np.ndarray  # eligible foreign males of the breed (for AI), may be empty
    cache: dict[str, Any] = field(default_factory=dict)  # strategies may memoise here

    @property
    def breed_cfg(self) -> BreedConfig:
        return self.setup.breeds[self.breed]

    @property
    def is_registry_era(self) -> bool:
        return self.year >= self.setup.sim.registry_start_year


class MatingStrategy(Protocol):
    name: str

    def plan_matings(
        self, dams: np.ndarray, sires: np.ndarray, ctx: YearContext, rng: np.random.Generator
    ) -> np.ndarray:
        """Sire gid per dam (-1 = skip). May return foreign sires from `ctx.foreign_sires`."""
        ...
