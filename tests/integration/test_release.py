"""Release, datasheet and link placeholders (P10)."""

import pytest
import yaml

from breeding_smarter import release
from breeding_smarter.io.datasets import resolve_dataset


def _have_v1() -> bool:
    try:
        resolve_dataset("v1")
        return True
    except (FileNotFoundError, KeyError):
        return False


@pytest.mark.skipif(not _have_v1(), reason="no dataset v1")
def test_datasheet_sections_complete():
    text = release.render_datasheet("v1")
    for section in (
        "## Motivation",
        "## Composition",
        "## Generation process",
        "## Calibration",
        "### Parameters marked as assumptions",
        "## Known deviations and limitations",
        "## Uses",
        "## Distribution",
        "## Maintenance",
    ):
        assert section in text
    assert release.SYNTHETIC in text
    assert "| T07 |" in text and "assumption" in text.lower()


@pytest.mark.skipif(not _have_v1(), reason="no dataset v1")
def test_zenodo_metadata():
    meta = release.zenodo_metadata("v1")["metadata"]
    assert meta["upload_type"] == "dataset" and meta["license"] == "cc-by-4.0"
    assert len(meta["creators"]) == 2
    assert "synthetic" in meta["notes"].lower()


def test_placeholders_found_and_filled(tmp_path, monkeypatch):
    (tmp_path / "docs").mkdir()
    (tmp_path / "conference").mkdir()
    (tmp_path / "README.md").write_text("DOI: TODO-DOI\nDemo: TODO-DEMO-URL\n")
    (tmp_path / "docs" / "x.md").write_text("contact TODO-CONTACT\n")
    (tmp_path / "conference" / "links.yaml").write_text(
        yaml.safe_dump(
            {
                "dataset_doi": "10.5281/zenodo.123",
                "demo_url": "TODO-DEMO-URL",
                "contact": "team@example.org",
            }
        )
    )
    monkeypatch.setattr(release, "repo_root", lambda: tmp_path)
    assert len(release.find_placeholders(tmp_path)) == 3
    assert release.fill_placeholders(tmp_path) == 2
    left = release.find_placeholders(tmp_path)
    assert [h[2] for h in left] == ["Demo: TODO-DEMO-URL"]  # not filled yet: still reported
    assert "10.5281/zenodo.123" in (tmp_path / "README.md").read_text()
