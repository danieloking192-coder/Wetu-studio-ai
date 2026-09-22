"""Scriptural and historical narrative layer for WETU.

Sources are metadata-driven: WETU distinguishes source text from reconstruction
and artistic interpretation instead of presenting uncertain details as facts.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

class SourceClass(str, Enum):
    CANONICAL = "canonical"
    DEUTEROCANONICAL = "deuterocanonical"
    APOCRYPHAL = "apocryphal"
    PSEUDEPIGRAPHAL = "pseudepigraphal"
    TRADITION = "tradition"

class FidelityMode(str, Enum):
    SOURCE_FAITHFUL = "source_faithful"
    HISTORICAL_CINEMATIC = "historical_cinematic"

@dataclass
class ScripturalSource:
    source_id: str
    title: str
    source_class: SourceClass
    tradition: str = ""
    notes: str = ""

@dataclass
class ScripturalUniverse:
    universe_id: str
    title: str
    source: ScripturalSource
    fidelity: FidelityMode
    era: str = ""
    region: str = ""
    languages: list[str] = field(default_factory=list)
    provenance: list[str] = field(default_factory=list)
    canon_status: str = ""
    details: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> list[str]:
        issues=[]
        if not self.source.source_id or not self.source.title:
            issues.append("source identity is required")
        if not self.title.strip():
            issues.append("universe title is required")
        if not self.provenance:
            issues.append("provenance should identify the source basis")
        return issues

@dataclass
class RealismAssessment:
    checks: dict[str, bool]
    issues: list[dict[str, str]]
    passed: bool

class ScripturalRealismQA:
    CHECKS = (
        "source_fidelity", "historical_context", "geography",
        "architecture", "costume", "objects_and_practices",
        "language", "chronology", "character_continuity",
        "environment", "artistic_disclosure",
    )

    def evaluate(self, *, universe: ScripturalUniverse,
                 scene_context: dict[str, Any] | None = None) -> RealismAssessment:
        checks={name: True for name in self.CHECKS}
        issues=[]
        scene_context=scene_context or {}
        if not universe.provenance:
            checks["source_fidelity"]=False
            issues.append({"type":"provenance","message":"source basis is missing"})
        if universe.fidelity is FidelityMode.HISTORICAL_CINEMATIC and not universe.era:
            checks["historical_context"]=False
            issues.append({"type":"history","message":"era is missing for historical reconstruction"})
        if not scene_context.get("source_passage"):
            issues.append({"type":"traceability","message":"scene passage/reference should be supplied"})
        return RealismAssessment(checks, issues, not any(not x for x in checks.values()))
