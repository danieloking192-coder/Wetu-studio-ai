"""Structured cinematic QA boundary; deterministic checks only."""
from __future__ import annotations
from typing import Any

class RealismQA:
    def evaluate(self, *, kind: str, context: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
        checks = [
            ("identity_context", bool(context.get("characters") or not context.get("scene"))),
            ("world_context", bool(context.get("world") or not context.get("scene"))),
            ("scene_memory", bool(context.get("scene"))),
            ("provider_result", bool(result)),
            ("references_traceable", "references" in result or not result.get("references_required", False)),
            ("media_uri", bool(result.get("uri") or result.get("asset_url"))),
        ]
        issues = [name for name, passed in checks if not passed]
        return {"passed": not issues, "checks": [name for name, _ in checks],
                "issues": issues, "kind": kind}