from wetu_studio.video_quality import VideoQualityEngine


def test_high_quality_target_is_full_hd_and_smooth():
    target = VideoQualityEngine().target()
    assert target["width"] == 1920
    assert target["height"] == 1080
    assert target["fps"] == 30
    assert target["smooth_motion"] is True


def test_ultra_hd_target_is_4k():
    target = VideoQualityEngine().target({"quality_profile": "ultra_hd", "fps": 60})
    assert target["width"] == 3840
    assert target["height"] == 2160
    assert target["fps"] == 60


def test_output_validation_catches_resolution_and_stability_failures():
    engine = VideoQualityEngine()
    target = engine.target()
    issues = engine.validate_output(
        {"width": 1280, "height": 720, "fps": 24, "frame_timing_stable": False}, target
    )
    assert "output_resolution_below_target" in issues
    assert "output_fps_mismatch" in issues
    assert "unstable_frame_timing" in issues


def test_invalid_fps_is_rejected():
    try:
        VideoQualityEngine().target({"fps": 29})
        assert False
    except ValueError as exc:
        assert "fps" in str(exc)
