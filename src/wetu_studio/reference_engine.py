import hashlib
import json
from dataclasses import dataclass, field

@dataclass(frozen=True)
class ReferenceAsset:
    reference_id: str
    character_id: str
    visual_signature: tuple[tuple[str, str], ...]
    wardrobe: str = ""
    metadata: dict[str, str] = field(default_factory=dict)
    content_hash: str = ""

class ReferenceEngine:
    """Builds deterministic character references for downstream generation adapters."""

    def build(self, character, reference_id: str, metadata: dict[str, str] | None = None) -> ReferenceAsset:
        if not reference_id.strip():
            raise ValueError("reference_id is required")
        if not character.is_identifiable():
            raise ValueError("character needs a visual identity before reference creation")
        signature = character.visual_signature()
        wardrobe = character.visual_identity.get("wardrobe", "")
        payload = {
            "character_id": character.character_id,
            "visual_signature": signature,
            "wardrobe": wardrobe,
        }
        digest = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        return ReferenceAsset(
            reference_id=reference_id,
            character_id=character.character_id,
            visual_signature=signature,
            wardrobe=wardrobe,
            metadata=dict(metadata or {}),
            content_hash=digest,
        )

    def verify(self, reference: ReferenceAsset, character) -> bool:
        if reference.character_id != character.character_id:
            return False
        return reference.visual_signature == character.visual_signature()

    def export_payload(self, reference: ReferenceAsset) -> dict[str, object]:
        return {
            "reference_id": reference.reference_id,
            "character_id": reference.character_id,
            "visual_signature": list(reference.visual_signature),
            "wardrobe": reference.wardrobe,
            "metadata": dict(reference.metadata),
            "content_hash": reference.content_hash,
        }
