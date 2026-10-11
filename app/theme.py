"""Colours shared with the figures (calibration/plotstyle.py)."""

from breeding_smarter.calibration.plotstyle import BREED_COLOURS, STRATEGY_COLOURS

TIER_COLOURS = {
    "Excellent": "#009E73",
    "Good": "#56B4E9",
    "Acceptable": "#F0E442",
    "Caution": "#E69F00",
    "Not recommended": "#D55E00",
}
STATUS_ICON = {"pass": "✓", "warn": "⚠", "fail": "✗", "info": "ℹ"}

__all__ = ["BREED_COLOURS", "STATUS_ICON", "STRATEGY_COLOURS", "TIER_COLOURS"]
