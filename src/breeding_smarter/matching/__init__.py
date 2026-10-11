"""Mate matching: explainable multi-factor scores for candidate sires (P7)."""

from breeding_smarter.matching.config import ScoringConfig, load_scoring
from breeding_smarter.matching.context import DatasetContext, load_context
from breeding_smarter.matching.explain import ScoreCard
from breeding_smarter.matching.recommend import (
    Recommendation,
    rank_fast,
    recommend_sires,
    score_pair,
)

__all__ = [
    "DatasetContext",
    "Recommendation",
    "ScoreCard",
    "ScoringConfig",
    "load_context",
    "load_scoring",
    "rank_fast",
    "recommend_sires",
    "score_pair",
]
