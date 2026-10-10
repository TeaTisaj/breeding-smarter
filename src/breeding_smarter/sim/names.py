"""Syllable-based synthetic names (never real kennel affixes)."""

from __future__ import annotations

import numpy as np

from breeding_smarter.io.paths import configs_dir

SYLLABLES = [
    "ka",
    "ri",
    "lo",
    "ma",
    "ve",
    "na",
    "to",
    "sa",
    "mi",
    "re",
    "lu",
    "da",
    "zo",
    "ni",
    "ta",
    "be",
    "ko",
    "ra",
    "vi",
    "no",
    "pe",
    "la",
    "ze",
    "mo",
    "si",
    "ra",
    "du",
    "gi",
    "ne",
    "so",
    "ba",
    "li",
    "ve",
    "ro",
    "ta",
    "ka",
    "mu",
    "ze",
    "di",
    "no",
]
PREFIX = {"DE": "vom", "AT": "vom", "NL": "van", "IT": "del", "HR": "od", "SI": "iz", "RS": "od"}


def _word(rng: np.random.Generator, lo: int = 2, hi: int = 3) -> str:
    k = int(rng.integers(lo, hi + 1))
    return "".join(SYLLABLES[int(i)] for i in rng.integers(0, len(SYLLABLES), k)).capitalize()


def blocklist() -> set[str]:
    """Real affixes that must never be produced (file present, empty for now)."""
    p = configs_dir() / "names_blocklist.txt"
    if not p.exists():
        return set()
    return {ln.strip().lower() for ln in p.read_text().splitlines() if ln.strip()}


def kennel_names(n: int, countries: list[str], rng: np.random.Generator) -> list[str]:
    """`n` unique kennel affixes, e.g. 'od Kavira' (country-specific preposition)."""
    seen: set[str] = set()
    out: list[str] = []
    blocked = blocklist()
    while len(out) < n:
        country = countries[len(out)]
        name = f"{PREFIX.get(country, 'of')} {_word(rng, 2, 3)}"
        if name.lower() in blocked or name in seen:
            continue
        seen.add(name)
        out.append(name)
    return out


def call_names(n: int, rng: np.random.Generator) -> list[str]:
    return [_word(rng, 2, 2) for _ in range(n)]
