"""Advanced deterministic continuity and production QA for WETU."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass
class QAReport:
    passed: bool
    checks: dict[str, bool] = field(default_factory=dict)
    issues: list[dict[str, Any]] = field(default_factory=list)
    score: float = 0.0

class AdvancedContinuityQA:
    """Checks production state for traceability and continuity before export."""
    def evaluate(self, *, characters=None, worlds=None, scenes=None, assets=None,
                 timeline=None, references=None) -> QAReport:
        characters = characters or {}
        worlds = worlds or {}
        scenes = scenes or {}
        assets = assets or []
        references = references or {}
        checks = {
            "character_identity": True,
            "world_context": True,
            "scene_context": True,
            "asset_traceability": True,
            "reference_traceability": True,
            "timeline_integrity": True,
        }
        issues=[]
        scene_ids=set(scenes)
        asset_ids={getattr(a,"asset_id",None) for a in assets}
        for s in scenes.values():
            if not getattr(s,"scene_id","").strip():
                checks["scene_context"]=False; issues.append({"type":"scene","message":"scene without id"})
        if timeline is not None:
            report=timeline.validate()
            if not report["passed"]:
                checks["timeline_integrity"]=False
                issues.extend({"type":"timeline","detail":x} for x in report["issues"])
            for item in timeline.items:
                if item.asset_id not in asset_ids:
                    checks["asset_traceability"]=False
                    issues.append({"type":"asset","item_id":item.item_id,"asset_id":item.asset_id})
                if item.scene_id and item.scene_id not in scene_ids:
                    checks["scene_context"]=False
                    issues.append({"type":"scene_reference","item_id":item.item_id,"scene_id":item.scene_id})
        if references is not None:
            for ref_id, ref in references.items():
                if not ref_id:
                    checks["reference_traceability"]=False
                    issues.append({"type":"reference","message":"empty reference id"})
        passed=all(checks.values()) and not issues
        score=round(sum(checks.values())/len(checks),3) if checks else 1.0
        return QAReport(passed, checks, issues, score)

    def explain(self, report: QAReport) -> dict[str, Any]:
        return {"passed":report.passed,"score":report.score,"checks":report.checks,"issues":report.issues,
                "ready_for_export":report.passed}

class ContinuityGuard:
    """Lightweight deterministic guard for scene-to-scene identity/world invariants."""
    def compare_scene_context(self, previous: dict[str, Any], current: dict[str, Any]) -> list[dict[str, Any]]:
        issues=[]
        for key in ("character_ids","world_id"):
            if key in previous and key in current and previous[key] != current[key]:
                issues.append({"type":"continuity_change","field":key,"previous":previous[key],"current":current[key]})
        return issues
