import unittest
from wetu_studio.media_engine import MediaRegistry, MediaRequest, HttpMediaProvider

class MediaEngineTests(unittest.TestCase):
    def test_local_provider_is_explicitly_non_rendering(self):
        asset=MediaRegistry().generate(MediaRequest("r","p","s","image","x","wetu-local"), {})
        self.assertFalse(asset.metadata["real_media"])

    def test_http_provider_contract(self):
        provider=HttpMediaProvider("test","https://example.invalid/generate","secret")
        self.assertEqual(provider.name,"test")
        self.assertIn("image",provider.capabilities)
