from dataclasses import dataclass, field


@dataclass
class Character:
    character_id: str
    name: str
    role: str = ""
    description: str = ""
    traits: list[str] = field(default_factory=list)


class CharacterEngine:
    def create(self, character_id: str, name: str, role: str = "", description: str = "") -> Character:
        if not character_id.strip() or not name.strip():
            raise ValueError("character_id and name are required")
        return Character(character_id, name, role, description)

    def add_trait(self, character: Character, trait: str) -> None:
        if not trait.strip():
            raise ValueError("trait is required")
        if trait not in character.traits:
            character.traits.append(trait)
