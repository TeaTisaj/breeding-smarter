"""Conference texts: every template renders from numbers.json; the poster stays <= 300 words."""

import importlib.util
import json
from pathlib import Path

import pytest

CONF = Path(__file__).parents[2] / "conference"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, CONF / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.skipif(not (CONF / "numbers.json").exists(), reason="numbers.json not built")
def test_templates_render_and_poster_word_limit():
    bt = _load("build_texts")
    numbers = json.loads((CONF / "numbers.json").read_text())
    for tmpl in bt.TARGETS:
        text = (CONF / "templates" / tmpl).read_text().format_map(numbers)
        assert "{" not in text, tmpl
    poster = (CONF / "templates" / "poster_text.md").read_text().format_map(numbers)
    assert bt.word_count(poster) <= bt.MAX_POSTER_WORDS


def test_word_count():
    bt = _load("build_texts")
    assert bt.word_count("# Title\n- one two\n**three**") == 4
