"""Rule engine: jurisdiction profiles in YAML, vectorised compliance checks (P6)."""

from breeding_smarter.rules.context import RuleContext, day_number
from breeding_smarter.rules.engine import (
    CandidateEvaluation,
    ComplianceResult,
    RuleResult,
    evaluate_candidates,
    evaluate_pair,
)
from breeding_smarter.rules.loader import RuleConfigError, available_profiles, load_profile
from breeding_smarter.rules.models import Profile, RuleSpec, Severity, Status

__all__ = [
    "CandidateEvaluation",
    "ComplianceResult",
    "Profile",
    "RuleConfigError",
    "RuleContext",
    "RuleResult",
    "RuleSpec",
    "Severity",
    "Status",
    "available_profiles",
    "day_number",
    "evaluate_candidates",
    "evaluate_pair",
    "load_profile",
]
