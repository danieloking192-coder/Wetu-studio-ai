from wetu_studio.character_engine import CharacterEngine
from wetu_studio.reference_engine import ReferenceEngine

def test_reference_is_deterministic_and_verifiable():
    ce = CharacterEngine()
    character = ce.create("hero", "Hero")
    ce.set_visual_identity(character, face="oval", skin="brown", hair="short", eyes="brown")
    ce.choose_outfit(character, "black suit")
    ce.set_current_outfit(character, "black suit")

    engine = ReferenceEngine()
    ref = engine.build(character, "hero-ref-v1")
    assert ref.content_hash
    assert engine.verify(ref, character)

def test_reference_detects_identity_change():
    ce = CharacterEngine()
    character = ce.create("hero", "Hero")
    ce.set_visual_identity(character, face="oval", skin="brown")
    engine = ReferenceEngine()
    ref = engine.build(character, "hero-ref-v1")
    ce.set_visual_identity(character, face="round")
    assert not engine.verify(ref, character)
