from wetu_studio.character_engine import CharacterEngine


def test_character_can_have_selectable_wardrobe():
    engine = CharacterEngine()
    character = engine.create("c1", "Amani")
    engine.set_visual_identity(character, face="distinctive", skin="deep brown", hair="short", eyes="brown")
    engine.choose_outfit(character, "black suit")
    engine.choose_outfit(character, "casual denim")
    engine.set_current_outfit(character, "black suit")
    assert character.wardrobe == ["black suit", "casual denim"]
    assert character.visual_identity["wardrobe"] == "black suit"


def test_current_outfit_must_exist_in_wardrobe():
    engine = CharacterEngine()
    character = engine.create("c1", "Amani")
    try:
        engine.set_current_outfit(character, "unknown")
        assert False
    except ValueError:
        assert True
