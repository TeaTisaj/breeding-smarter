"""E8 strategy ids: `S3q[-gainNNN][-cBBB]`."""

import pytest

from breeding_smarter.experiments.strategies import parse_s3q


@pytest.mark.parametrize(
    ("sid", "expected"),
    [
        ("S3q", ("ocs", None, None)),
        ("S3q-gain010", ("ocs_gain", 0.001, None)),
        ("S3q-gain025", ("ocs_gain", 0.0025, None)),
        ("S3q-c075", ("ocs", None, 0.75)),
        ("S3q-gain010-c075", ("ocs_gain", 0.001, 0.75)),
        ("S3q-gain010-c100", ("ocs_gain", 0.001, 1.0)),
    ],
)
def test_parse_s3q(sid, expected):
    assert parse_s3q(sid) == expected


@pytest.mark.parametrize(
    "sid", ["S3", "S3q-", "S3q-c075-gain010", "S3q-gainx", "S3q-c", "S3q-ocs", "S3q-gain010-mc1"]
)
def test_parse_s3q_rejects(sid):
    with pytest.raises(ValueError):
        parse_s3q(sid)
