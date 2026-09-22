from wetu_studio.character_engine import CharacterEngine
from wetu_studio.continuity_engine import ContinuityEngine

def test_continuity_matches_visual_signature():
    c = CharacterEngine().create("hero", "Hero")
    CharacterEngine().set_visual_identity(c, face="oval", skin="brown", hair="short")
    r = ContinuityEngine().capture(c)
    assert r.consistent
