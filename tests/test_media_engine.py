import unittest

from wetu_studio.media_engine import MediaRegistry, MediaRequest, HttpMediaProvider, MediaCoreAdapter


class DeterministicVideoProvider:
    name = "deterministic-video"
    capabilities = {"video"}

    def generate(self, request, context):
        return {
            "model": "deterministic-video-v1",
            "uri": "memory://wetu/e2e/video",
            "kind": "video",
            "real_media": False,
            "width": 1920,
            "height": 1080,
            "fps": 30,
            "video_bitrate_kbps": 8000,
            "delivery_output": {
                "width": 854,
                "height": 480,
                "fps": 24,
                "video_bitrate_kbps": 900,
                "audio_bitrate_kbps": 64,
            },
            "duration_seconds": 60,
            "frame_timing_stable": True,
            "corrupt": False,
        }


class MediaEngineTests(unittest.TestCase):
    def test_local_provider_is_explicitly_non_rendering(self):
        asset = MediaRegistry().generate(
            MediaRequest("r", "p", "s", "image", "x", "wetu-local"), {}
        )
        self.assertFalse(asset.metadata["real_media"])

    def test_http_provider_contract(self):
        provider = HttpMediaProvider("test", "https://example.invalid/generate", "secret")
        self.assertEqual(provider.name, "test")
        self.assertIn("image", provider.capabilities)

    def test_video_e2e_quality_delivery_contract(self):
        registry = MediaRegistry({"deterministic-video": DeterministicVideoProvider()})
        request = MediaRequest(
            "video-e2e",
            "project-e2e",
            "scene-e2e",
            "video",
            "deterministic test scene",
            "deterministic-video",
            options={"network": "very_low", "quality_profile": "high_quality"},
        )
        asset = registry.generate(request, {"recent_generations": []})

        self.assertEqual(asset.status, "ready")
        self.assertEqual(asset.metadata["video_delivery_target"]["profile"], "mobile_saver")
        self.assertTrue(asset.metadata["video_quality_compliant"])
        self.assertTrue(asset.metadata["video_delivery_compliant"])
        self.assertEqual(asset.metadata["estimated_delivery_size_mb"], 7.06)
        self.assertFalse(asset.metadata["provider_result"]["corrupt"])


    def test_core_adapter_bridges_registry_provider(self):
        registry = MediaRegistry()
        adapter = MediaCoreAdapter(registry, "wetu-local")
        result = adapter.generate(
            kind="image",
            prompt="bridge test",
            context={"project_id": "p", "scene_id": "s", "generation_id": "g"},
        )
        self.assertEqual(result["kind"], "image")
        self.assertFalse(result["real_media"])
        self.assertEqual(result["asset_id"], "g")
