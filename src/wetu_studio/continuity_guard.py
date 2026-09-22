"""Continuity Guard for persistent visual identity and world state."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass
class ContinuityIssue:
    code: str
    message: str
    entity_id: str | None = None
    severity: str = "warning"

class VisualContinuityGuard:
    def check(self, *, scene, context, references=None):
        issues=[]
        refs=references or []
        expected=context.get("continuity", {}) or {}
        for entity_id, expected_keys in expected.items():
            matching=[r for r in refs if getattr(r,"entity_id",None)==entity_id or
                      getattr(r,"continuity_key",None) in set(expected_keys or [])]
            if not matching:
                issues.append(ContinuityIssue(
                    "MISSING_REFERENCE",
                    f"No persistent visual reference found for {entity_id}.",
                    entity_id, "warning"))
        return {"passed": not any(i.severity=="block" for i in issues),
                "issues":[i.__dict__ for i in issues],
                "checked_references":len(refs)}

    def compare(self, *, expected: dict[str, Any], observed: dict[str, Any]):
        issues=[]
        for key, value in expected.items():
            if key in observed and observed[key] != value:
                issues.append(ContinuityIssue("UNEXPLAINED_CHANGE",
                    f"Continuity value changed for {key}.", key, "block"))
        return {"passed": not any(i.severity=="block" for i in issues),
                "issues":[i.__dict__ for i in issues]}

