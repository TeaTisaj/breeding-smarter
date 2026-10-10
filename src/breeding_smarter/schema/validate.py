"""Validate a run folder against the data contract (all failures, not just the first)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd

from breeding_smarter.io.parquet import check_file_schema, read_table
from breeding_smarter.schema.tables import ALL_TABLES, TABLES, TableSpec

if TYPE_CHECKING:
    from breeding_smarter.config.models import SpeciesConfig

DAYS_PER_MONTH = 365.25 / 12
GESTATION_WINDOW_DAYS = (56, 70)


@dataclass
class Failure:
    table: str
    rule: str
    count: int
    examples: list[dict[str, Any]] = field(default_factory=list)

    def __str__(self) -> str:
        return f"[{self.table}] {self.rule}: {self.count} row(s); e.g. {self.examples[:2]}"


@dataclass
class ValidationResult:
    failures: list[Failure] = field(default_factory=list)
    tables_checked: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.failures

    def rules_failed(self) -> set[tuple[str, str]]:
        return {(f.table, f.rule) for f in self.failures}

    def summary(self) -> str:
        if self.ok:
            return f"OK: {len(self.tables_checked)} tables valid"
        return "\n".join(str(f) for f in self.failures)


class _Checker:
    def __init__(self) -> None:
        self.result = ValidationResult()

    def add(self, table: str, rule: str, bad: pd.DataFrame) -> None:
        if len(bad):
            head = bad.head(5).astype(object)
            records = head.where(head.notna(), None).to_dict("records")
            ex = [{str(k): v for k, v in r.items()} for r in records]
            self.result.failures.append(Failure(table, rule, len(bad), ex))


def _species_for_run(run_dir: Path) -> SpeciesConfig:
    from breeding_smarter.config.loader import load_species  # local: avoids an import cycle

    snap = run_dir / "config_snapshot" / "species"
    if snap.is_dir():
        files = sorted(snap.glob("*.yaml"))
        if files:
            return load_species(files[0].stem, base=run_dir / "config_snapshot")
    return load_species()


def _check_keys(chk: _Checker, spec: TableSpec, df: pd.DataFrame) -> None:
    dup = df[df.duplicated(list(spec.primary_key), keep=False)]
    chk.add(spec.name, "primary_key_unique", dup)
    for f in spec.fields:
        if f.domain is not None:
            col = df[f.name]
            bad = df[col.notna() & ~col.isin(f.domain)]
            chk.add(spec.name, f"domain:{f.name}", bad)


def _check_foreign_keys(chk: _Checker, tables: dict[str, pd.DataFrame]) -> None:
    for name, df in tables.items():
        for fk in TABLES[name].foreign_keys:
            if fk.ref_table not in tables:
                continue
            ref = tables[fk.ref_table]
            col, ref_col = fk.columns[0], fk.ref_columns[0]
            vals = df[col]
            bad = df[vals.notna() & ~vals.isin(ref[ref_col])]
            chk.add(name, f"foreign_key:{col}->{fk.ref_table}.{ref_col}", bad)


def _check_animals(chk: _Checker, a: pd.DataFrame, species: SpeciesConfig) -> None:
    t = "registry/animals"
    by_idx = a.set_index("idx")
    for col, sex in (("sire_idx", "M"), ("dam_idx", "F")):
        has = a[a[col].notna()]
        psex = has[col].map(by_idx["sex"])
        chk.add(t, f"{col}_sex_is_{sex}", has[psex.notna() & (psex != sex)])
        chk.add(t, f"{col}_before_idx", has[has[col] >= has["idx"]])
        pbirth = has[col].map(by_idx["birth_date"])
        months = species.min_breeding_age_months.for_sex(sex)
        age_days = (has["birth_date"] - pbirth).dt.days.to_numpy(dtype=float, na_value=np.nan)
        too_young = age_days < months * DAYS_PER_MONTH
        chk.add(t, f"{col}_min_breeding_age", has[pbirth.notna().to_numpy() & too_young])
    dead = a[a["death_date"].notna()]
    chk.add(t, "death_after_birth", dead[dead["death_date"] < dead["birth_date"]])
    chk.add(t, "reg_no_unique", a[a["reg_no"].duplicated(keep=False)])
    chk.add(t, "microchip_unique", a[a["microchip"].duplicated(keep=False)])
    bad_chip = ~a["microchip"].str.fullmatch(r"999\d{12}")
    chk.add(t, "microchip_format_999", a[bad_chip.fillna(True)])
    bad_reg = ~a["reg_no"].str.startswith("SYN-")
    chk.add(t, "reg_no_synthetic_prefix", a[bad_reg.fillna(True)])
    contiguous = np.array_equal(np.sort(a["idx"].to_numpy()), np.arange(len(a)))
    if not contiguous:
        chk.add(t, "idx_contiguous", a.head(5))


def _check_litters(chk: _Checker, lit: pd.DataFrame, a: pd.DataFrame) -> None:
    t = "registry/litters"
    gest = (lit["whelp_date"] - lit["mating_date"]).dt.days
    lo, hi = GESTATION_WINDOW_DAYS
    chk.add(t, "gestation_56_to_70_days", lit[(gest < lo) | (gest > hi)])
    counts = a.loc[a["litter_id"].notna(), "litter_id"].astype("int64").value_counts()
    actual = lit["litter_id"].map(counts).fillna(0).astype(int)
    chk.add(t, "n_registered_matches_animals", lit[actual != lit["n_registered"]])
    chk.add(
        t,
        "litter_counts_consistent",
        lit[(lit["n_born_alive"] > lit["n_born"]) | (lit["n_registered"] > lit["n_born_alive"])],
    )
    by_idx = a.set_index("idx")["sex"]
    chk.add(t, "sire_sex_is_M", lit[lit["sire_idx"].map(by_idx).fillna("M") != "M"])
    chk.add(t, "dam_sex_is_F", lit[lit["dam_idx"].map(by_idx).fillna("F") != "F"])
    members = a[a["litter_id"].notna()].merge(
        lit[["litter_id", "sire_idx", "dam_idx"]], on="litter_id", suffixes=("", "_litter")
    )
    mismatch = (members["sire_idx"] != members["sire_idx_litter"]) | (
        members["dam_idx"] != members["dam_idx_litter"]
    )
    chk.add("registry/animals", "litter_parents_match", members[mismatch.fillna(True)])


def _check_truth(chk: _Checker, truth: pd.DataFrame, a: pd.DataFrame) -> None:
    t = "truth/animals_truth"
    mapped = truth.loc[truth["idx"].notna(), "idx"].astype("int64")
    counts = mapped.value_counts()
    n_map = a["idx"].map(counts).fillna(0).astype(int)
    chk.add(t, "registry_animal_maps_to_one_truth_row", a[n_map != 1])
    chk.add(t, "is_hidden_iff_idx_null", truth[truth["is_hidden"] != truth["idx"].isna()])
    for col in ("true_sire_gid", "true_dam_gid"):
        has = truth[truth[col].notna()]
        chk.add(t, f"{col}_before_gid", has[has[col] >= has["gid"]])


def validate_run(
    run_dir: Path,
    species: SpeciesConfig | None = None,
    allowed_loci: set[str] | None = None,
    require_all: bool = True,
) -> ValidationResult:
    """Check every table of a run folder against the contract.

    Checks: schema (names, types, nullability), primary keys, foreign keys, categorical
    domains, parent sexes, topological order (`sire_idx < idx`), parent at least the minimum
    breeding age, gestation length 56 to 70 days, `n_registered` counts, `death_date >=
    birth_date`, synthetic ID conventions, and the registry-to-truth mapping.
    """
    run_dir = Path(run_dir)
    species = species or _species_for_run(run_dir)
    chk = _Checker()
    tables: dict[str, pd.DataFrame] = {}
    for spec in ALL_TABLES:
        path = run_dir / spec.filename
        if not path.exists():
            if require_all:
                chk.add(spec.name, "missing_table", pd.DataFrame([{"path": str(path)}]))
            continue
        problems = check_file_schema(path, spec)
        if problems:
            chk.add(spec.name, "schema", pd.DataFrame({"problem": problems}))
            continue
        df = read_table(path, spec)
        tables[spec.name] = df
        chk.result.tables_checked.append(spec.name)
        _check_keys(chk, spec, df)
    _check_foreign_keys(chk, tables)
    a = tables.get("registry/animals")
    if a is not None:
        _check_animals(chk, a, species)
        if "registry/litters" in tables:
            _check_litters(chk, tables["registry/litters"], a)
        if "truth/animals_truth" in tables:
            _check_truth(chk, tables["truth/animals_truth"], a)
    if allowed_loci is not None and "registry/dna_tests" in tables:
        dna = tables["registry/dna_tests"]
        chk.add("registry/dna_tests", "locus_in_config", dna[~dna["locus_id"].isin(allowed_loci)])
    return chk.result
