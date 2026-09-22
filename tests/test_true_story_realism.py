from wetu_studio.true_story_realism import TrueStoryMode, TrueStoryRealismEngine


def test_verified_fact_requires_source():
    e = TrueStoryRealismEngine()
    scene = e.build(scene_id="s1", event="event", facts=[{
        "fact_id": "f1", "claim": "A documented event",
        "evidence_class": "verified_fact"
    }], victim_survivor_handling={"dignity": True})
    assert "verified_fact_missing_source:f1" in e.validate(scene)


def test_invented_dialogue_is_flagged_when_presented_as_fact():
    e = TrueStoryRealismEngine()
    scene = e.build(
        scene_id="s1", event="event",
        dialogue=[{"text": "invented", "presented_as_fact": True}],
        victim_survivor_handling={"dignity": True},
    )
    assert "invented_or_unverified_dialogue_presented_as_fact" in e.validate(scene)


def test_dramatization_is_disclosed():
    e = TrueStoryRealismEngine()
    scene = e.build(
        scene_id="s1", event="event",
        mode=TrueStoryMode.DRAMATIZED_RECONSTRUCTION,
        facts=[{"fact_id": "f1", "claim": "reconstructed detail",
                "evidence_class": "reconstruction"}],
        victim_survivor_handling={"dignity": True},
    )
    assert "reconstruction:f1" in scene.disclosure
    assert not e.validate(scene)
