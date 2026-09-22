from wetu_studio.fan_film_pipeline import FanFilmPipeline
from wetu_studio.universe_mode import UniverseMode, UniverseProduction

def test_pipeline_requires_fan_film_mode():
    p = UniverseProduction("p", "Original", UniverseMode.ORIGINAL)
    try:
        FanFilmPipeline(p).start()
    except ValueError:
        pass
    else:
        raise AssertionError("pipeline must reject ORIGINAL mode")

def test_pipeline_exports_traceable_stages():
    p = UniverseProduction("p", "Fan Short", UniverseMode.FAN_FILM)
    p.add_ip_character("naruto", "Naruto Uzumaki", "Naruto Shippuden")
    pipe = FanFilmPipeline(p)
    pipe.start()
    pipe.add_scene("s1", "Opening", 5000, ["naruto"])
    pipe.add_animation_request({"request_id": "a1", "scene_id": "s1"})
    pipe.add_audio_request({"request_id": "v1", "scene_id": "s1", "language": "fr"})
    pipe.add_timeline_item({"item_id": "i1", "asset_id": "a1", "kind": "VIDEO", "start_ms": 0, "duration_ms": 5000})
    pipe.add_qa({"passed": True})
    manifest = pipe.export_manifest()
    assert manifest["mode"] == "fan_film"
    assert "export" in manifest["stages"]
    assert manifest["render_status"] == "provider_required"
