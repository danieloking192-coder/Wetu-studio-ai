from wetu_studio.character_engine import CharacterEngine


def test_character_creation_and_traits():
    character = CharacterEngine().create("c-001", "Amani", "Hero")
    CharacterEngine().add_trait(character, "curious")
    CharacterEngine().add_trait(character, "curious")
    assert character.name == "Amani"
    assert character.traits == ["curious"]
