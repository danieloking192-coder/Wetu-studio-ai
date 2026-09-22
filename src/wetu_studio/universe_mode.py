"""Project-mode boundaries for WETU productions."""

from dataclasses import dataclass, field
from enum import Enum

class UniverseMode(str, Enum):
    FAN_FILM = "fan_film"
    ORIGINAL = "original"

@dataclass(frozen=True)
class IPCharacterReference:
    character_id: str
    display_name: str
    source_work: str
    notes: str = ""

@dataclass
class UniverseProduction:
    production_id: str
    title: str
    mode: UniverseMode
    character_references: list[IPCharacterReference] = field(default_factory=list)
    original_universe_id: str | None = None
    provenance: list[str] = field(default_factory=list)

    def add_ip_character(self, character_id: str, display_name: str, source_work: str, notes: str = "") -> IPCharacterReference:
        if self.mode is not UniverseMode.FAN_FILM:
            raise ValueError("IP character references are only allowed in FAN_FILM mode.")
        if not character_id or not display_name or not source_work:
            raise ValueError("character_id, display_name and source_work are required.")
        ref = IPCharacterReference(character_id, display_name, source_work, notes)
        self.character_references.append(ref)
        self.provenance.append(f"ip-character:{character_id}:{source_work}")
        return ref

    def attach_original_universe(self, universe_id: str) -> None:
        if self.mode is not UniverseMode.ORIGINAL:
            raise ValueError("An original universe can only be attached in ORIGINAL mode.")
        if not universe_id:
            raise ValueError("universe_id is required.")
        self.original_universe_id = universe_id

    def validate(self) -> list[str]:
        issues: list[str] = []
        if self.mode is UniverseMode.FAN_FILM and self.original_universe_id:
            issues.append("fan-film production cannot silently attach an original-universe id")
        if self.mode is UniverseMode.ORIGINAL and self.character_references:
            issues.append("original production cannot silently contain IP character references")
        return issues