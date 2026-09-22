from wetu_studio.world_bible import WorldBibleEngine


def test_world_bible():
    engine = WorldBibleEngine()
    bible = engine.create("Demo", "cinematic realism", "mysterious")
    engine.add_location(bible, "Kinshasa")
    engine.add_rule(bible, "Keep visual continuity.")
    engine.add_reference(bible, "reference-001")
    assert bible.visual_style == "cinematic realism"
    assert bible.locations == ["Kinshasa"]
    assert bible.rules == ["Keep visual continuity."]
    assert bible.references == ["reference-001"]
