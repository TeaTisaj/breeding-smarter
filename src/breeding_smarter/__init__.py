"""Breeding Smarter: explainable, rule-aware mate matching on synthetic pedigrees.

All animals in datasets produced by this package are synthetic.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("breeding-smarter")
except PackageNotFoundError:  # pragma: no cover - running from a source tree without install
    __version__ = "0.1.0"

__all__ = ["__version__"]
