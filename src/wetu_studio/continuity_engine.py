from dataclasses import dataclass, field

@dataclass
class ContinuityRecord:
    character_id: str
    previous_signature: tuple[tuple[str, str], ...] = field(default_factory=tuple)
    current_signature: tuple[tuple[str, str], ...] = field(default_factory=tuple)
    wardrobe: str = ""
    consistent: bool = True
    notes: list[str] = field(default_factory=list)

class ContinuityEngine:
    def capture(self, character, wardrobe: str = "") -> ContinuityRecord:
        signature = character.visual_signature()
        return ContinuityRecord(character.character_id, signature, signature, wardrobe or character.visual_identity.get("wardrobe", ""))

    def compare(self, previous: ContinuityRecord, character, wardrobe: str = "") -> ContinuityRecord:
        current = character.visual_signature()
        chosen = wardrobe or character.visual_identity.get("wardrobe", "")
        return ContinuityRecord(character.character_id, previous.current_signature, current, chosen, previous.current_signature == current, [])

    def require_consistency(self, record: ContinuityRecord) -> None:
        if not record.consistent: raise ValueError("character visual continuity mismatch")
