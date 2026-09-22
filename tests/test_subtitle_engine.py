from wetu_studio.subtitle_engine import SubtitleEngine, SubtitleCue


def test_subtitle_engine_builds_srt_and_vtt():
    track = SubtitleEngine().build_track(
        track_id="sub-1", project_id="demo", scene_id="scene-01", language="fr",
        dialogue=[
            {"start_ms": 0, "end_ms": 1200, "speaker": "Amina", "text": "Bonjour."},
            {"start_ms": 1400, "end_ms": 2500, "text": "Nous commençons."},
        ],
    )
    assert track.validate() == []
    assert "00:00:00,000 --> 00:00:01,200" in track.to_srt()
    assert "WEBVTT" in track.to_vtt()
    assert "Amina: Bonjour." in track.to_srt()


def test_subtitle_engine_rejects_overlap_and_invalid_timing():
    try:
        SubtitleEngine().build_track(
            track_id="sub-2", project_id="demo", scene_id="s1", language="fr",
            dialogue=[
                {"start_ms": 0, "end_ms": 2000, "text": "A"},
                {"start_ms": 1500, "end_ms": 2500, "text": "B"},
            ],
        )
        assert False
    except ValueError as exc:
        assert "non-overlapping" in str(exc)

    try:
        SubtitleCue(1000, 1000, "bad")
        assert False
    except ValueError as exc:
        assert "greater" in str(exc)


def test_subtitle_generation_is_explicitly_disabled():
    try:
        SubtitleEngine().build_track(
            track_id="sub-3", project_id="demo", scene_id="s1", language="fr",
            dialogue=[{"start_ms": 0, "end_ms": 1000, "text": "Bonjour."}],
            enabled=False,
        )
        assert False
    except ValueError as exc:
        assert "disabled" in str(exc)
