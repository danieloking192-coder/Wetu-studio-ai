from dataclasses import dataclass, field

from .identity import IdentityProfile


@dataclass
class Character:
    character_id: str
    name: str
    role: str = ""
    description: str = ""
    traits: list[str] = field(default_factory=list)
    identity: IdentityProfile | None = None
    visual_identity: dict[str, str] = field(default_factory=dict)

    def is_identifiable(self) -> bool:
        return bool(self.name.strip()) and bool(self.visual_identity)


class CharacterEngine:
    def create(self, character_id: str, name: str, role: str = "", description: str = "",
               identity: IdentityProfile | None = None) -> Character:
        if not character_id.strip() or not name.strip():
            raise ValueError("character_id and name are required")
        return Character(character_id, name, role, description, identity=identity)

    def add_trait(self, character: Character, trait: str) -> None:
        if not trait.strip():
            raise ValueError("trait is required")
        if trait not in character.traits:
            character.traits.append(trait)

    def set_visual_identity(self, character: Character, **attributes: str) -> None:
        allowed = {"face", "skin", "hair", "eyes", "body", "age", "wardrobe", "signature_features"}
        unknown = set(attributes) - allowed
        if unknown:
            raise ValueError(f"unsupported visual attributes: {sorted(unknown)}")
        if not attributes:
            raise ValueError("at least one visual attribute is required")
        character.visual_identity.update({k: v for k, v in attributes.items() if v.strip()})

    def validate_likeness(self, character: Character) -> bool:
        if character.identity is None:
            return True
        return character.identity.can_use_likeness()
