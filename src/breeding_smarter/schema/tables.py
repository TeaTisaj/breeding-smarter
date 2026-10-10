"""Table specifications: the data contract between the simulator and the engine.

Single source of truth for every Parquet table in a run folder (see `plan/02_P1_data_model.md`).
`docs/data_dictionary.md` is generated from these specs (`bsm schema dictionary`).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pyarrow as pa


@dataclass(frozen=True)
class FieldSpec:
    """One column: Arrow type, nullability, description and optional categorical domain."""

    name: str
    type: pa.DataType
    nullable: bool
    description: str
    domain: tuple[str, ...] | None = None


@dataclass(frozen=True)
class ForeignKey:
    """`columns` of this table reference `ref_columns` of `ref_table` (nulls are ignored)."""

    columns: tuple[str, ...]
    ref_table: str
    ref_columns: tuple[str, ...]


@dataclass(frozen=True)
class TableSpec:
    """A table: relative path inside the run folder (without extension), fields and keys."""

    name: str
    description: str
    fields: tuple[FieldSpec, ...]
    primary_key: tuple[str, ...]
    foreign_keys: tuple[ForeignKey, ...] = field(default_factory=tuple)

    @property
    def schema(self) -> pa.Schema:
        return pa.schema([pa.field(f.name, f.type, nullable=f.nullable) for f in self.fields])

    @property
    def columns(self) -> list[str]:
        return [f.name for f in self.fields]

    def field(self, name: str) -> FieldSpec:
        for f in self.fields:
            if f.name == name:
                return f
        raise KeyError(f"{self.name} has no field {name!r}")

    @property
    def filename(self) -> str:
        return f"{self.name}.parquet"


def F(
    name: str,
    type_: pa.DataType,
    nn: bool,
    description: str,
    domain: tuple[str, ...] | None = None,
) -> FieldSpec:
    """Shorthand: `nn=True` means not null."""
    return FieldSpec(name, type_, not nn, description, domain)


STR, I8, I16, I32, I64 = pa.string(), pa.int8(), pa.int16(), pa.int32(), pa.int64()
F64, BOOL, DATE = pa.float64(), pa.bool_(), pa.date32()

SEX = ("M", "F")
SIZE_CLASS = ("toy", "small", "medium", "large", "giant")
STUDBOOK = ("HR", "HUR", "FOREIGN")
KENNEL_KIND = ("breeder", "private_owner")
REG_TYPE = ("full", "limited")
DEATH_CAUSE = ("age", "disease", "accident", "unknown")
MATING_METHOD = ("natural", "ai_fresh", "ai_chilled", "ai_frozen")
HD_GRADE = ("A", "B", "C", "D", "E")
GENOTYPE = ("clear", "carrier", "affected")

BREEDS = TableSpec(
    name="registry/breeds",
    description="Synthetic breeds (fictional archetypes).",
    fields=(
        F("breed_id", STR, True, "Breed code, e.g. SYN_L, SYN_M, SYN_S."),
        F("display_name", STR, True, "Human-readable fictional name, e.g. 'Synthetic Breed L'."),
        F("species", STR, True, "Species, e.g. 'dog'."),
        F("size_class", STR, True, "Body size class.", SIZE_CLASS),
        F("studbook", STR, True, "Registry setting (HR for all synthetic breeds)."),
        F("is_local_breed", BOOL, True, "Local breed with a limited gene pool (EU derogation)."),
        F("archetype_description", STR, True, "One-sentence description of the archetype."),
    ),
    primary_key=("breed_id",),
)

KENNELS = TableSpec(
    name="registry/kennels",
    description="Breeders and private owners (synthetic, syllable-generated names).",
    fields=(
        F("kennel_id", I32, True, "Kennel or owner id."),
        F("name", STR, True, "Generated affix or owner label; never a real kennel."),
        F("kind", STR, True, "breeder or private_owner.", KENNEL_KIND),
        F("country", STR, True, "ISO 3166-1 alpha-2 country code."),
        F("lat", F64, True, "Synthetic latitude inside the country bounding box."),
        F("lon", F64, True, "Synthetic longitude inside the country bounding box."),
        F("registered_year", I16, True, "Year the kennel or owner first appears."),
    ),
    primary_key=("kennel_id",),
)

ANIMALS = TableSpec(
    name="registry/animals",
    description="Registered animals (what a kennel club knows). idx is in birth order.",
    fields=(
        F("idx", I64, True, "Contiguous registry id in birth order; parents have smaller idx."),
        F("reg_no", STR, True, "Registration number, SYN-HR-<year>-<seq> or SYN-FOREIGN-..."),
        F("name", STR, True, "Generated name: kennel affix plus call name."),
        F("species", STR, True, "Species."),
        F("breed_id", STR, True, "Breed (FK breeds)."),
        F("sex", STR, True, "M or F.", SEX),
        F("birth_date", DATE, True, "Date of birth."),
        F("sire_idx", I64, False, "Registered sire idx; null if unknown or not registered."),
        F("dam_idx", I64, False, "Registered dam idx; null if unknown or not registered."),
        F("litter_id", I64, False, "Registered litter; null for founders, imports and stubs."),
        F("breeder_id", I32, False, "Breeder kennel (FK kennels)."),
        F("owner_id", I32, True, "Current owner (FK kennels)."),
        F("country_of_birth", STR, True, "ISO 3166-1 alpha-2 country of birth."),
        F(
            "studbook",
            STR,
            True,
            "HR (domestic, 3 generations known), HUR (domestic with an unknown parent or "
            "grandparent) or FOREIGN (pedigree record of a foreign ancestor).",
            STUDBOOK,
        ),
        F("import_flag", BOOL, True, "True if imported from abroad."),
        F("original_reg_no", STR, False, "Foreign registration number of imports."),
        F("microchip", STR, True, "15 digits starting with ISO 11784 test code 999."),
        F("coat_colour", STR, True, "Coat colour from the breed list."),
        F("registration_type", STR, True, "full or limited.", REG_TYPE),
        F("death_date", DATE, False, "Date of death if dead before the data end date."),
        F("death_cause", STR, False, "Cause of death.", DEATH_CAUSE),
        F("titles_count", I16, True, "Show or working titles (0 for most)."),
    ),
    primary_key=("idx",),
    foreign_keys=(
        ForeignKey(("sire_idx",), "registry/animals", ("idx",)),
        ForeignKey(("dam_idx",), "registry/animals", ("idx",)),
        ForeignKey(("litter_id",), "registry/litters", ("litter_id",)),
        ForeignKey(("breeder_id",), "registry/kennels", ("kennel_id",)),
        ForeignKey(("owner_id",), "registry/kennels", ("kennel_id",)),
        ForeignKey(("breed_id",), "registry/breeds", ("breed_id",)),
    ),
)

LITTERS = TableSpec(
    name="registry/litters",
    description="Registered litters; both parents are registered.",
    fields=(
        F("litter_id", I64, True, "Litter id."),
        F("breed_id", STR, True, "Breed."),
        F("sire_idx", I64, True, "Sire (FK animals)."),
        F("dam_idx", I64, True, "Dam (FK animals)."),
        F("mating_date", DATE, True, "Mating date (about 63 days before whelping)."),
        F("whelp_date", DATE, True, "Whelping date."),
        F("n_born", I16, True, "Puppies born."),
        F("n_born_alive", I16, True, "Puppies born alive."),
        F("n_registered", I16, True, "Puppies in animals with this litter_id."),
        F("mating_method", STR, True, "Natural mating or AI.", MATING_METHOD),
        F("caesarean", BOOL, True, "Delivered by caesarean section."),
        F("breeder_id", I32, True, "Breeder kennel."),
    ),
    primary_key=("litter_id",),
    foreign_keys=(
        ForeignKey(("sire_idx",), "registry/animals", ("idx",)),
        ForeignKey(("dam_idx",), "registry/animals", ("idx",)),
        ForeignKey(("breeder_id",), "registry/kennels", ("kennel_id",)),
        ForeignKey(("breed_id",), "registry/breeds", ("breed_id",)),
    ),
)

HEALTH_TESTS = TableSpec(
    name="registry/health_tests",
    description="Official health screening results (HD in the MVP).",
    fields=(
        F("test_id", I64, True, "Test id."),
        F("idx", I64, True, "Animal (FK animals)."),
        F("test_type", STR, True, "Screening type.", ("HD",)),
        F("scheme", STR, True, "Grading scheme.", ("FCI",)),
        F("result", STR, True, "FCI grade A to E.", HD_GRADE),
        F("test_date", DATE, True, "Screening date."),
        F("age_months", I16, True, "Age at screening in months."),
        F("official", BOOL, True, "Official result."),
    ),
    primary_key=("test_id",),
    foreign_keys=(ForeignKey(("idx",), "registry/animals", ("idx",)),),
)

DNA_TESTS = TableSpec(
    name="registry/dna_tests",
    description="DNA test results at testable Mendelian loci (exact; lab error out of scope).",
    fields=(
        F("idx", I64, True, "Animal (FK animals)."),
        F("locus_id", STR, True, "Locus id from configs/loci."),
        F("genotype", STR, True, "clear, carrier or affected.", GENOTYPE),
        F("test_date", DATE, True, "Test date."),
        F("lab", STR, True, "Fictional laboratory name."),
    ),
    primary_key=("idx", "locus_id"),
    foreign_keys=(ForeignKey(("idx",), "registry/animals", ("idx",)),),
)

EBV = TableSpec(
    name="registry/ebv",
    description="Estimated breeding values from a registry-only pedigree BLUP.",
    fields=(
        F("idx", I64, True, "Animal (FK animals)."),
        F("trait", STR, True, "Trait.", ("HD",)),
        F("ebv_index", F64, True, "Index scale: mean 100, SD 10, higher is better (SKK)."),
        F("accuracy", F64, True, "Approximate accuracy (0 to 1)."),
        F("evaluation_date", DATE, True, "Evaluation date."),
    ),
    primary_key=("idx", "trait", "evaluation_date"),
    foreign_keys=(ForeignKey(("idx",), "registry/animals", ("idx",)),),
)

ANIMALS_TRUTH = TableSpec(
    name="truth/animals_truth",
    description="Ground truth for every simulated animal, including hidden ones.",
    fields=(
        F("gid", I64, True, "Global simulation id in birth order."),
        F("idx", I64, False, "Registry idx if registered."),
        F("breed_id", STR, True, "Breed."),
        F("sex", STR, True, "M or F.", SEX),
        F("birth_year", I16, True, "Birth year."),
        F("true_sire_gid", I64, False, "True sire; null only for base-generation animals."),
        F("true_dam_gid", I64, False, "True dam; null only for base-generation animals."),
        F("is_hidden", BOOL, True, "True if not in the registry."),
        F("f_true_ibd", F64, True, "Realised identity by descent from neutral gene drop."),
        F("f_true_pedigree", F64, True, "Pedigree F on the full true pedigree (filled in P5)."),
        F("tbv_hd", F64, True, "True HD breeding value (liability scale)."),
        F("hd_liability", F64, False, "HD phenotype liability; null if never screened."),
        F("attractiveness", F64, True, "Latent show or marketing value."),
        F("fertility", F64, True, "Latent fertility multiplier."),
    ),
    primary_key=("gid",),
    foreign_keys=(
        ForeignKey(("idx",), "registry/animals", ("idx",)),
        ForeignKey(("true_sire_gid",), "truth/animals_truth", ("gid",)),
        ForeignKey(("true_dam_gid",), "truth/animals_truth", ("gid",)),
    ),
)

GENOTYPES_TRUTH = TableSpec(
    name="truth/genotypes_truth",
    description="True genotypes at every Mendelian disease locus for every animal.",
    fields=(
        F("gid", I64, True, "Animal (FK animals_truth)."),
        F("locus_id", STR, True, "Locus id."),
        F("n_risk_alleles", I8, True, "0, 1 or 2 risk alleles."),
    ),
    primary_key=("gid", "locus_id"),
    foreign_keys=(ForeignKey(("gid",), "truth/animals_truth", ("gid",)),),
)

REGISTRY_TABLES: tuple[TableSpec, ...] = (
    BREEDS,
    KENNELS,
    ANIMALS,
    LITTERS,
    HEALTH_TESTS,
    DNA_TESTS,
    EBV,
)
TRUTH_TABLES: tuple[TableSpec, ...] = (ANIMALS_TRUTH, GENOTYPES_TRUTH)
ALL_TABLES: tuple[TableSpec, ...] = REGISTRY_TABLES + TRUTH_TABLES
TABLES: dict[str, TableSpec] = {t.name: t for t in ALL_TABLES}
