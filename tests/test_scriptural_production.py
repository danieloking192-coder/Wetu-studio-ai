from wetu_studio.scriptural_production import build_scriptural_production

def test_exodus_builds_three_scene_production_plan():
    p=build_scriptural_production("exodus")
    assert len(p["scenes"]) == 3
    assert p["source_class"] == "canonical"
    assert p["render_status"] == "provider_required"
    assert p["qa"]["passed"]

def test_tobit_preserves_deuterocanonical_status():
    p=build_scriptural_production("tobit")
    assert p["source_class"] == "deuterocanonical"
