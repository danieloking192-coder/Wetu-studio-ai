from wetu_studio.emotion_atmosphere import EmotionAtmosphereEngine


def test_emotion_atmosphere_requires_real_context():
    engine = EmotionAtmosphereEngine()
    scene = engine.build(
        scene_id="s1",
        mood="tense anticipation",
        beats=[{
            "beat_id": "b1",
            "trigger": "an unknown figure appears",
            "state": {
                "primary": "fear",
                "intensity": 0.9,
                "arousal": 0.95,
                "cause": "an unknown figure appears",
                "bodily_signals": ["breathing becomes shallow", "hands tense"],
                "micro_expressions": ["eyes widen briefly"],
                "behavior": ["steps back without turning away"],
            },
            "continuity_key": "fear-after-encounter",
        }],
        atmosphere={
            "time_of_day": "dusk",
            "weather": "dry wind",
            "lighting": {"source": "low sun", "direction": "side light"},
            "environment_sounds": ["wind", "distant voices"],
            "ambient_motion": ["dust moving across the ground"],
        },
        sensory_focus=["breath", "dust", "distant voices"],
        camera_guidance=["close-up on eyes", "hold long enough to capture hesitation"],
    )
    assert engine.validate(scene) == []
    snapshot = engine.continuity_snapshot(scene)
    assert snapshot["beats"][0]["primary"] == "fear"
    assert snapshot["beats"][0]["continuity_key"] == "fear-after-encounter"


def test_high_intensity_without_behavior_is_flagged():
    engine = EmotionAtmosphereEngine()
    scene = engine.build(
        scene_id="s2",
        mood="shock",
        beats=[{"trigger": "revelation", "state": {"primary": "shock", "intensity": 1.0}}],
        atmosphere={"lighting": {"source": "interior lamp"}, "environment_sounds": ["silence"]},
    )
    issues = engine.validate(scene)
    assert any("physical behavior" in issue for issue in issues)
