"""E8 to E10 strategy ids: `S3q[-gainNNN][-cBBB][-hc][-oracle]`."""

import pytest

from breeding_smarter.experiments.strategies import S3qSpec, parse_s3q


@pytest.mark.parametrize(
    ("sid", "expected"),
    [
        ("S3q", ("ocs", None, None)),
        ("S3q-gain010", ("ocs_gain", 0.001, None)),
        ("S3q-gain025", ("ocs_gain", 0.0025, None)),
        ("S3q-c075", ("ocs", None, 0.75)),
        ("S3q-gain010-c075", ("ocs_gain", 0.001, 0.75)),
        ("S3q-gain010-c100", ("ocs_gain", 0.001, 1.0)),
        ("S3q-gain010-hc", ("ocs_gain", 0.001, None, True)),
        ("S3q-gain010-c050-oracle", ("ocs_gain", 0.001, 0.5, False, True)),
        ("S3q-c050-hc-oracle", ("ocs", None, 0.5, True, True)),
    ],
)
def test_parse_s3q(sid, expected):
    assert parse_s3q(sid) == S3qSpec(*expected)


@pytest.mark.parametrize(
    "sid",
    [
        "S3",
        "S3q-",
        "S3q-c075-gain010",
        "S3q-gainx",
        "S3q-c",
        "S3q-ocs",
        "S3q-gain010-mc1",
        "S3q-oracle-hc",
        "S3q-gain010-hc-hc",
    ],
)
def test_parse_s3q_rejects(sid):
    with pytest.raises(ValueError):
        parse_s3q(sid)


def test_make_strategy_applies_suffixes():
    from breeding_smarter.experiments.strategies import StrategyParams, make_strategy
    from breeding_smarter.matching.config import load_scoring

    s = make_strategy("S3q-gain010-c050-hc-oracle", StrategyParams(), load_scoring())
    assert s.params.profile == "exp_pairing_hard_carrier"
    assert s.oracle and s.control == "ocs_gain" and s.carrier_factor == 0.5
    plain = make_strategy("S3q", StrategyParams(), load_scoring())
    assert plain.params.profile == "exp_pairing" and not plain.oracle
