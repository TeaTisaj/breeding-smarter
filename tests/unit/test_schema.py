import pandas as pd
import pytest

from breeding_smarter.io import SchemaError, duckdb_connect, read_table, write_table
from breeding_smarter.schema import TABLES, validate_run
from breeding_smarter.schema.dictionary import default_path, render_dictionary
from tests.fixtures.pedigrees import ALL_FIXTURES, FIRST_COUSINS, write_tables


@pytest.mark.parametrize("name", list(TABLES))
def test_schema_roundtrip(tmp_path, name):
    spec = TABLES[name]
    df = FIRST_COUSINS.tables()[name]
    path = write_table(df, spec, tmp_path / spec.filename)
    back = read_table(path, spec)
    assert list(back.columns) == spec.columns
    assert len(back) == len(df)
    again = write_table(back, spec, tmp_path / "again.parquet")
    assert read_table(again, spec).equals(back)


def test_roundtrip_types_preserved(tmp_path):
    spec = TABLES["registry/animals"]
    df = FIRST_COUSINS.tables()[spec.name]
    back = read_table(write_table(df, spec, tmp_path / "a.parquet"), spec)
    assert str(back["idx"].dtype) == "int64"
    assert str(back["sire_idx"].dtype) == "Int64"
    assert back["sire_idx"].isna().sum() == 4
    assert pd.api.types.is_datetime64_any_dtype(back["birth_date"])
    assert back["birth_date"].iloc[0] == pd.Timestamp("2000-03-01")


def test_write_rejects_nulls_in_not_null_field(tmp_path):
    spec = TABLES["registry/animals"]
    df = FIRST_COUSINS.tables()[spec.name]
    df.loc[0, "reg_no"] = None
    with pytest.raises(SchemaError, match="nulls"):
        write_table(df, spec, tmp_path / "a.parquet")


def test_write_rejects_lossy_cast_and_wrong_columns(tmp_path):
    spec = TABLES["registry/kennels"]
    df = FIRST_COUSINS.tables()[spec.name]
    bad = df.assign(registered_year=1999.5)
    with pytest.raises(SchemaError):
        write_table(bad, spec, tmp_path / "k.parquet")
    with pytest.raises(SchemaError, match="unexpected"):
        write_table(df.assign(extra=1), spec, tmp_path / "k.parquet")


def test_read_rejects_wrong_schema(tmp_path):
    p = tmp_path / "x.parquet"
    pd.DataFrame({"breed_id": ["a"]}).to_parquet(p)
    with pytest.raises(SchemaError):
        read_table(p, TABLES["registry/breeds"])


@pytest.mark.parametrize("fx", ALL_FIXTURES, ids=lambda f: f.name)
def test_fixture_runs_are_valid(tmp_path, fx):
    res = validate_run(fx.write_run(tmp_path))
    assert res.ok, res.summary()


def test_validate_catches_errors(tmp_path):
    t = FIRST_COUSINS.tables()
    a = t["registry/animals"]
    a.loc[8, "sire_idx"] = 7  # dam (female) as sire, and parent not older than offspring rule
    a.loc[6, "dam_idx"] = 6  # self-parenting: topological order
    a.loc[5, "sire_idx"] = 6  # younger sire: topological order
    a.loc[4, "birth_date"] = pd.Timestamp("2000-06-01")  # parent 0/1 born 2000-03: too young
    a.loc[2, "death_date"] = pd.Timestamp("1990-01-01")  # death before birth
    a.loc[3, "coat_colour"] = "red"
    a.loc[3, "sex"] = "X"  # domain
    a.loc[1, "microchip"] = "123456789012345"  # not 999
    a.loc[0, "breeder_id"] = 77  # FK to kennels broken
    lit = t["registry/litters"]
    lit.loc[0, "mating_date"] = lit.loc[0, "whelp_date"] - pd.Timedelta(days=90)
    lit.loc[1, "n_registered"] = 5
    tr = t["truth/animals_truth"]
    t["truth/animals_truth"] = tr[tr["gid"] != 8]  # registry animal 8 has no truth row
    t["registry/breeds"] = pd.concat([t["registry/breeds"]] * 2)  # duplicate PK
    run = write_tables(t, tmp_path / "bad")
    res = validate_run(run)
    rules = {r for _, r in res.rules_failed()}
    expected = {
        "sire_idx_sex_is_M",
        "sire_idx_before_idx",
        "dam_idx_before_idx",
        "sire_idx_min_breeding_age",
        "death_after_birth",
        "domain:sex",
        "microchip_format_999",
        "foreign_key:breeder_id->registry/kennels.kennel_id",
        "gestation_56_to_70_days",
        "n_registered_matches_animals",
        "registry_animal_maps_to_one_truth_row",
        "primary_key_unique",
        "litter_parents_match",
    }
    assert expected <= rules, expected - rules
    for f in res.failures:
        assert f.count >= 1 and len(f.examples) <= 5


def test_validate_reports_missing_tables_and_schema(tmp_path):
    run = FIRST_COUSINS.write_run(tmp_path)
    (run / "registry" / "ebv.parquet").unlink()
    pd.DataFrame({"x": [1]}).to_parquet(run / "registry" / "dna_tests.parquet")
    rules = validate_run(run).rules_failed()
    assert ("registry/ebv", "missing_table") in rules
    assert ("registry/dna_tests", "schema") in rules


def test_duckdb_views(tmp_path):
    run = FIRST_COUSINS.write_run(tmp_path)
    con = duckdb_connect(run)
    n = con.execute("select count(*) from registry_animals").fetchone()[0]
    assert n == FIRST_COUSINS.n
    assert con.execute("select count(*) from truth_animals_truth").fetchone()[0] == n


def test_data_dictionary_up_to_date():
    assert default_path().read_text() == render_dictionary(), "run `bsm schema dictionary`"
