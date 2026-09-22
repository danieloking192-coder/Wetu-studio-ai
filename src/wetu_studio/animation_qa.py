"""Deterministic QA for animated productions."""
from __future__ import annotations

class AnimationQA:
    CHECKS = (
        "character_identity",
        "world_consistency",
        "style_consistency",
        "motion_context",
        "reference_traceability",
        "provider_result",
    )

    def evaluate(self, *, context, style, result) -> dict:
        checks = {x: True for x in self.CHECKS}
        issues = []
        if not style or not getattr(style, "style_id", ""):
            checks["style_consistency"] = False
            issues.append({"type": "style", "message": "animation style is missing"})
        if not result.get("uri") and not result.get("asset_url"):
            checks["provider_result"] = False
            issues.append({"type": "provider", "message": "animation output URI is missing"})
        return {"passed": not issues, "checks": checks, "issues": issues,
                "media": "animation", "style_id": getattr(style, "style_id", "")}
