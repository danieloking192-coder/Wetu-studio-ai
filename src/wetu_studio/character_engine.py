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
    wardrobe: list[str] = field(default_factory=list)

    def validate_likeness(self) -> bool:
        if self.identity is None:
            return True
        return self.identity.can_use_likeness()

    def is_identifiable(self) -> bool:
        return bool(self.name.strip()) and bool(self.visual_identity)

    def visual_signature(self) -> tuple[tuple[str, str], ...]:
        return tuple(sorted(self.visual_identity.items()))


class CharacterEngine:
    VISUAL_ATTRIBUTES = {
        "face", "skin", "hair", "eyes", "body", "age", "wardrobe",
        "signature_features"
    }

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
        unknown = set(attributes) - self.VISUAL_ATTRIBUTES
        if unknown:
            raise ValueError(f"unsupported visual attributes: {sorted(unknown)}")
        if not attributes:
            raise ValueError("at least one visual attribute is required")
        character.visual_identity.update({k: v for k, v in attributes.items() if v.strip()})

    def choose_outfit(self, character: Character, outfit: str) -> None:
        if not outfit.strip():
            raise ValueError("outfit is required")
        if outfit not in character.wardrobe:
            character.wardrobe.append(outfit)

    def set_current_outfit(self, character: Character, outfit: str) -> None:
        if outfit not in character.wardrobe:
            raise ValueError("outfit must first be added to the wardrobe")
        character.visual_identity["wardrobe"] = outfit

    def remove_outfit(self, character: Character, outfit: str) -> None:
        if outfit in character.wardrobe:
            character.wardrobe.remove(outfit)
            if character.visual_identity.get("wardrobe") == outfit:
                character.visual_identity.pop("wardrobe", None)

    def validate_likeness(self, character: Character) -> bool:
        if character.identity is None:
            return True
        return character.identity.can_use_likeness()
