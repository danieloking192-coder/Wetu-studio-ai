"""True-story realism and provenance guard for WETU productions.

The engine separates verified facts from reconstruction and dramatization.
It is intentionally provider-neutral: it prepares a safe, traceable scene
specification for a renderer rather than inventing historical truth.
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List


class TrueStoryMode(str, Enum):
    DOCUMENTARY_REALISM = "documentary_realism"
    DRAMATIZED_RECONSTRUCTION = "dramatized_reconstruction"


class EvidenceClass(str, Enum):
    VERIFIED_FACT = "verified_fact"
    RECONSTRUCTION = "reconstruction"
    DRAMATIZATION = "dramatization"
    UNKNOWN = "unknown"


@dataclass
class FactRecord:
    fact_id: str
    claim: str
    source: str = ""
    evidence_class: EvidenceClass = EvidenceClass.UNKNOWN
    confidence: float = 0.0
    time: str = ""
    location: str = ""
    notes: str = ""

    def validate(self) -> List[str]:
        issues: List[str] = []
        if not self.fact_id or not self.claim:
            issues.append("fact_record_requires_id_and_claim")
        if not 0 <= self.confidence <= 1:
            issues.append(f"invalid_confidence:{self.fact_id}")
        if self.evidence_class is EvidenceClass.VERIFIED_FACT and not self.source:
            issues.append(f"verified_fact_missing_source:{self.fact_id}")
        return issues


@dataclass
class TrueStoryScene:
    scene_id: str
    event: str
    mode: TrueStoryMode
    factual_context: List[FactRecord] = field(default_factory=list)
    emotional_context: Dict[str, Any] = field(default_factory=dict)
    environmental_context: Dict[str, Any] = field(default_factory=dict)
    dialogue: List[Dict[str, Any]] = field(default_factory=list)
    internal_thoughts: List[Dict[str, Any]] = field(default_factory=list)
    victim_survivor_handling: Dict[str, Any] = field(default_factory=dict)
    cinematic_direction: Dict[str, Any] = field(default_factory=dict)
    disclosure: List[str] = field(default_factory=list)
    provenance: List[str] = field(default_factory=list)


class TrueStoryRealismEngine:
    """Build and validate respectful, source-traceable true-story scenes."""

    DIGNITY_RULES = [
        "do_not_invent_private_thoughts_as_verified_fact",
        "do_not_present_invented_quotes_as_verified",
        "do_not_turn_real_suffering_into_gore_or_spectacle",
        "preserve_victim_and_survivor_dignity",
        "label_reconstruction_and_dramatization",
        "keep_uncertainty_visible",
    ]

    def build(
        self,
        *,
        scene_id: str,
        event: str,
        mode: TrueStoryMode = TrueStoryMode.DOCUMENTARY_REALISM,
        facts: List[Dict[str, Any]] | None = None,
        emotional_context: Dict[str, Any] | None = None,
        environmental_context: Dict[str, Any] | None = None,
        dialogue: List[Dict[str, Any]] | None = None,
        internal_thoughts: List[Dict[str, Any]] | None = None,
        victim_survivor_handling: Dict[str, Any] | None = None,
        cinematic_direction: Dict[str, Any] | None = None,
    ) -> TrueStoryScene:
        records = []
        for item in facts or []:
            raw = dict(item)
            raw["evidence_class"] = EvidenceClass(raw.get("evidence_class", "unknown"))
            records.append(FactRecord(**raw))
        scene = TrueStoryScene(
            scene_id=scene_id,
            event=event,
            mode=mode,
            factual_context=records,
            emotional_context=emotional_context or {},
            environmental_context=environmental_context or {},
            dialogue=dialogue or [],
            internal_thoughts=internal_thoughts or [],
            victim_survivor_handling=victim_survivor_handling or {},
            cinematic_direction=cinematic_direction or {},
        )
        scene.disclosure = self._disclosures(scene)
        scene.provenance = [f.source for f in records if f.source]
        return scene

    def validate(self, scene: TrueStoryScene) -> List[str]:
        issues: List[str] = []
        if not scene.scene_id or not scene.event:
            issues.append("scene_requires_id_and_event")
        for fact in scene.factual_context:
            issues.extend(fact.validate())

        for item in scene.dialogue:
            if item.get("presented_as_fact") and not item.get("source"):
                issues.append("invented_or_unverified_dialogue_presented_as_fact")
        for item in scene.internal_thoughts:
            if item.get("presented_as_fact") and not item.get("source"):
                issues.append("invented_internal_thought_presented_as_fact")

        if scene.mode is TrueStoryMode.DOCUMENTARY_REALISM:
            for fact in scene.factual_context:
                if fact.evidence_class in (EvidenceClass.RECONSTRUCTION, EvidenceClass.DRAMATIZATION):
                    if not fact.notes and not fact.source:
                        issues.append(f"undisclosed_nonfact:{fact.fact_id}")
            if scene.cinematic_direction.get("sensationalism"):
                issues.append("sensationalism_not_allowed_in_documentary_mode")

        if not scene.victim_survivor_handling:
            issues.append("victim_survivor_dignity_context_missing")
        elif scene.victim_survivor_handling.get("dehumanizing") is True:
            issues.append("dehumanizing_direction_not_allowed")

        return issues

    def _disclosures(self, scene: TrueStoryScene) -> List[str]:
        disclosures = list(self.DIGNITY_RULES)
        if scene.mode is TrueStoryMode.DOCUMENTARY_REALISM:
            disclosures.append("documentary_mode_prioritizes_verified_evidence")
        else:
            disclosures.append("dramatized_reconstruction_may_reconstruct_unrecorded_details")
        for fact in scene.factual_context:
            if fact.evidence_class is EvidenceClass.RECONSTRUCTION:
                disclosures.append(f"reconstruction:{fact.fact_id}")
            elif fact.evidence_class is EvidenceClass.DRAMATIZATION:
                disclosures.append(f"dramatization:{fact.fact_id}")
            elif fact.evidence_class is EvidenceClass.UNKNOWN:
                disclosures.append(f"uncertain:{fact.fact_id}")
        return disclosures

    def to_dict(self, scene: TrueStoryScene) -> Dict[str, Any]:
        return asdict(scene)
