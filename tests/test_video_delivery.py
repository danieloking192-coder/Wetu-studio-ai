from wetu_studio.video_delivery import VideoDeliveryEngine

def test_mobile_profile_is_bandwidth_efficient():
    target = VideoDeliveryEngine().target()
    assert target["width"] == 1280
    assert target["height"] == 720
    assert target["adaptive_delivery"] is True

def test_size_estimate_is_bounded():
    engine = VideoDeliveryEngine()
    target = engine.target({"delivery_profile": "mobile_saver"})
    assert engine.estimate_size_mb(60, target) < 10

def test_delivery_output_rejects_excessive_bitrate():
    engine = VideoDeliveryEngine()
    target = engine.target()
    issues = engine.validate_delivery_output(
        {"width": 1280, "height": 720, "video_bitrate_kbps": 3000}, target
    )
    assert "delivery_bitrate_exceeds_target" in issues

def test_master_is_kept_separately():
    assert VideoDeliveryEngine().target()["master_kept_separately"] is True
