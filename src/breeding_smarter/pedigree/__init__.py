"""Pedigree engine: inbreeding, kinship, mean kinship, diversity, Ne, founders, completeness.

All functions are pure (no I/O). See `core.py` for notation and references.
"""

from breeding_smarter.pedigree.completeness import (
    complete_generations,
    equivalent_generations,
    max_generations,
)
from breeding_smarter.pedigree.core import Pedigree, PedigreeError
from breeding_smarter.pedigree.inbreeding import (
    inbreeding,
    inbreeding_extend,
    inbreeding_py,
    l_row,
    l_row_virtual,
    pair_kinship,
    pair_kinship_decomposed,
)
from breeding_smarter.pedigree.kinship import (
    A_times,
    contributions,
    kinship_matrix,
    kinship_to_all,
    mean_kinship,
)
from breeding_smarter.pedigree.population import PopulationReport, population_report
from breeding_smarter.pedigree.relationships import (
    Relationship,
    nearest_common_ancestor,
    relationship,
)

ENGINE_VERSION = "1"

__all__ = [
    "ENGINE_VERSION",
    "A_times",
    "Pedigree",
    "PedigreeError",
    "PopulationReport",
    "Relationship",
    "complete_generations",
    "contributions",
    "equivalent_generations",
    "inbreeding",
    "inbreeding_extend",
    "inbreeding_py",
    "kinship_matrix",
    "kinship_to_all",
    "l_row",
    "l_row_virtual",
    "max_generations",
    "mean_kinship",
    "nearest_common_ancestor",
    "pair_kinship",
    "pair_kinship_decomposed",
    "population_report",
    "relationship",
]
