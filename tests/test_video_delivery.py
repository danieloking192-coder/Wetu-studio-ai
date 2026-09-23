from wetu_studio.video_delivery import VideoDeliveryEngine


def test_mobile_profile_is_bandwidth_efficient():
    target = VideoDeliveryEngine().target({"adaptive": False})
    assert target["width"] == 1280
    assert target["height"] == 720
    assert target["adaptive_delivery"] is False


def test_adaptive_network_selection():
    engine = VideoDeliveryEngine()
    assert engine.target({"network": "very_low"})["profile"] == "mobile_saver"
    assert engine.target({"network": "normal"})["profile"] == "mobile"
    assert engine.target({"network": "good"})["profile"] == "standard"


def test_explicit_profile_overrides_network():
    target = VideoDeliveryEngine().target({"network": "good", "delivery_profile": "mobile_saver"})
    assert target["profile"] == "mobile_saver"


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
