"""Persistent Entity DNA for humans, animals, dragons, angels, demons and other beings."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

class EntityKind(str, Enum):
    HUMAN="human"; ANIMAL="animal"; CREATURE="creature"; DRAGON="dragon"
    ANGEL="angel"; DEMON="demon"; MYTHIC="mythic"; VEHICLE="vehicle"; OBJECT="object"

@dataclass
class EntitySource:
    source_id: str
    title: str
    tradition: str = ""
    passage: str = ""
    description: str = ""
    confidence: str = "documented"

@dataclass
class EntityDNA:
    entity_id: str
    name: str
    kind: EntityKind
    identity: dict[str, Any] = field(default_factory=dict)
    morphology: dict[str, Any] = field(default_factory=dict)
    visual: dict[str, Any] = field(default_factory=dict)
    behavior: dict[str, Any] = field(default_factory=dict)
    abilities: list[str] = field(default_factory=list)
    voice: dict[str, Any] = field(default_factory=dict)
    relationships: list[dict[str, Any]] = field(default_factory=list)
    continuity: dict[str, Any] = field(default_factory=dict)
    sources: list[EntitySource] = field(default_factory=list)
    interpretation_notes: list[str] = field(default_factory=list)
    version: int = 1

    def validate(self) -> list[str]:
        issues=[]
        if not self.entity_id.strip(): issues.append("entity_id is required")
        if not self.name.strip(): issues.append("name is required")
        if not isinstance(self.kind, EntityKind): issues.append("kind must be an EntityKind")
        if not self.sources: issues.append("at least one provenance source is required")
        return issues

@dataclass
class EntityCatalog:
    entities: dict[str, EntityDNA] = field(default_factory=dict)

    def add(self, entity: EntityDNA) -> None:
        issues=entity.validate()
        if issues: raise ValueError("; ".join(issues))
        self.entities[entity.entity_id]=entity

    def get(self, entity_id: str) -> EntityDNA:
        return self.entities[entity_id]

    def by_kind(self, kind: EntityKind) -> list[EntityDNA]:
        return [e for e in self.entities.values() if e.kind is kind]
