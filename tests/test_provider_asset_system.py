import unittest
from wetu_studio.provider_registry import ProviderSelector
from wetu_studio.asset_store import AssetStore
from wetu_studio.media_engine import MediaRegistry, MediaRequest

class ProviderAssetTests(unittest.TestCase):
    def test_provider_selector_lists_local_provider(self):
        profiles=ProviderSelector(MediaRegistry()).profiles()
        self.assertEqual(profiles[0].name,"wetu-local")
    def test_asset_store_remembers_generated_asset(self):
        asset=MediaRegistry().generate(MediaRequest("r","p","s","image","x","wetu-local"),{})
        store=AssetStore()
        record=store.remember(asset)
        self.assertEqual(store.get("r").uri,record.uri)
        self.assertEqual(store.references_for_scene("s"),[record.uri])
