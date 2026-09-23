from wetu_studio.adaptive_streaming import AdaptiveStreamingEngine

def test_network_policy_prefers_low_data_on_weak_networks():
    engine = AdaptiveStreamingEngine()
    assert engine.select("very_low")["profile"] == "mobile_saver"
    assert engine.select("low")["profile"] == "mobile_saver"
    assert engine.select("normal")["profile"] == "mobile"
    assert engine.select("good")["profile"] == "standard"

def test_explicit_profile_overrides_network_policy():
    assert AdaptiveStreamingEngine().select("low", "standard")["profile"] == "standard"

def test_hls_and_dash_manifests_are_prepared():
    manifests = AdaptiveStreamingEngine().manifests("https://cdn.example/media")
    assert manifests["hls"]["master_playlist"].endswith("/hls/master.m3u8")
    assert manifests["dash"]["manifest"].endswith("/dash/manifest.mpd")
    assert len(manifests["hls"]["variants"]) == 3
    assert len(manifests["dash"]["variants"]) == 3

def test_contract_does_not_claim_deployment():
    assert AdaptiveStreamingEngine().contract()["deployment_active"] is False
