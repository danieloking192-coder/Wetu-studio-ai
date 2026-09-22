"""WETU Mature 18+ access and non-explicit sensual-content policy.

This module is an access/policy gate. It does not generate explicit sexual
content. Ambiguous age or consent fails closed.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Any

class MatureAccess(str, Enum):
    UNVERIFIED="unverified"
    VERIFIED_18_PLUS="verified_18_plus"
    UNDER_18="under_18"

@dataclass(frozen=True)
class MatureRequest:
    access: MatureAccess
    all_characters_adult: bool
    consent_confirmed: bool
    real_person: bool = False
    explicit: bool = False
    ambiguous_age: bool = False

@dataclass(frozen=True)
class MatureDecision:
    allowed: bool
    reasons: tuple[str, ...]
    policy_version: str = "1.0"

class MaturePolicy:
    def evaluate(self, request: MatureRequest) -> MatureDecision:
        reasons=[]
        if request.access is not MatureAccess.VERIFIED_18_PLUS:
            reasons.append("18+ verification required")
        if not request.all_characters_adult:
            reasons.append("all characters must be explicitly adult")
        if request.ambiguous_age:
            reasons.append("ambiguous age is not permitted")
        if not request.consent_confirmed:
            reasons.append("consent confirmation required")
        if request.explicit:
            reasons.append("explicit sexual generation is outside WETU Mature scope")
        if request.real_person and not request.consent_confirmed:
            reasons.append("real-person use requires consent")
        return MatureDecision(not reasons, tuple(reasons))

def decision_json(decision: MatureDecision) -> dict[str, Any]:
    return {"allowed":decision.allowed,"reasons":list(decision.reasons),"policy_version":decision.policy_version}
