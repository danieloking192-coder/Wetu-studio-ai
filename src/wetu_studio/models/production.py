"""Persistent production-domain models for the WETU Creator Application Core."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

@dataclass
class CharacterDNA:
    character_id: str
    name: str
    face: dict[str, Any] = field(default_factory=dict)
    body: dict[str, Any] = field(default_factory=dict)
    hair: dict[str, Any] = field(default_factory=dict)
    eyes: dict[str, Any] = field(default_factory=dict)
    wardrobe: dict[str, Any] = field(default_factory=dict)
    traits: list[str] = field(default_factory=list)
    voice_profile: dict[str, Any] = field(default_factory=dict)
    version: int = 1
    updated_at: str = field(default_factory=utc_now)

@dataclass
class WorldDNA:
    world_id: str
    name: str
    geography: dict[str, Any] = field(default_factory=dict)
    architecture: dict[str, Any] = field(default_factory=dict)
    environment: dict[str, Any] = field(default_factory=dict)
    culture: dict[str, Any] = field(default_factory=dict)
    landmarks: list[str] = field(default_factory=list)
    version: int = 1
    updated_at: str = field(default_factory=utc_now)

@dataclass
class SceneMemory:
    scene_id: str
    project_id: str
    sequence: int
    character_ids: list[str] = field(default_factory=list)
    world_id: str | None = None
    previous_scene_ids: list[str] = field(default_factory=list)
    state: dict[str, Any] = field(default_factory=dict)
    language: str = "fr"
    continuity_notes: list[str] = field(default_factory=list)

@dataclass
class GenerationRecord:
    generation_id: str
    project_id: str
    scene_id: str | None
    provider: str
    model: str
    kind: str
    prompt: str
    status: str = "created"
    accepted: bool = False
    parent_generation_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)

@dataclass
class ProductionDecision:
    decision_id: str
    project_id: str
    description: str
    chosen_generation_id: str | None = None
    rejected_generation_ids: list[str] = field(default_factory=list)
    reason: str = ""
    created_at: str = field(default_factory=utc_now)

@dataclass
class ProductionMemory:
    generations: dict[str, GenerationRecord] = field(default_factory=dict)
    decisions: dict[str, ProductionDecision] = field(default_factory=dict)
    references: dict[str, dict[str, Any]] = field(default_factory=dict)
    events: list[dict[str, Any]] = field(default_factory=list)

    def remember(self, event_type: str, payload: dict[str, Any]) -> None:
        self.events.append({"type": event_type, "at": utc_now(), "payload": payload})

    def add_generation(self, record: GenerationRecord) -> None:
        self.generations[record.generation_id] = record
        self.remember("generation", {"generation_id": record.generation_id})

    def add_decision(self, decision: ProductionDecision) -> None:
        self.decisions[decision.decision_id] = decision
        self.remember("decision", {"decision_id": decision.decision_id})

    def context_for(self, scene: SceneMemory) -> dict[str, Any]:
        related = [
            g for g in self.generations.values()
            if g.project_id == scene.project_id and
            (g.scene_id in scene.previous_scene_ids or g.scene_id == scene.scene_id)
        ]
        decisions = [
            d for d in self.decisions.values() if d.project_id == scene.project_id
        ]
        return {
            "scene": scene,
            "recent_generations": related[-20:],
            "decisions": decisions[-20:],
            "references": dict(self.references),
        }
