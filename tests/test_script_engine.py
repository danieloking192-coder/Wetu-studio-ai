import pytest
from wetu_studio.script_engine import ScriptEngine


def test_script_and_scene():
    engine = ScriptEngine()
    script = engine.create_script("Demo", "A short story.")
    scene = engine.add_scene(script, "s1", "INT. STUDIO - DAY", "The character enters.")
    engine.add_dialogue(scene, "Bonjour.")
    assert len(script.scenes) == 1
    assert script.scenes[0].dialogue == ["Bonjour."]


def test_duplicate_scene_rejected():
    engine = ScriptEngine()
    script = engine.create_script("Demo")
    engine.add_scene(script, "s1", "INT. ROOM - DAY")
    with pytest.raises(ValueError):
        engine.add_scene(script, "s1", "EXT. STREET - DAY")
