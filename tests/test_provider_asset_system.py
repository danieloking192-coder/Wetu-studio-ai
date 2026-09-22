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



def test_provider_gateway_selects_capable_provider_and_tracks_references():
    from wetu_studio.provider_registry import ProviderGateway, ProviderRequest, AssetReference
    from wetu_studio.media_engine import MediaRegistry
    registry = MediaRegistry()
    gateway = ProviderGateway(registry)
    provider, manifest = gateway.prepare(ProviderRequest(
        request_id="req-1", kind="video",
        options={"quality_profile": "high_quality"},
        references=[AssetReference("char-1", "ref://char-1", kind="character")],
    ))
    assert provider.name == "wetu-local"
    assert manifest["real_provider"] is False
    assert manifest["references"] == ["char-1"]


def test_provider_gateway_rejects_unsupported_kind():
    from wetu_studio.provider_registry import ProviderGateway, ProviderRequest
    from wetu_studio.media_engine import MediaRegistry
    try:
        ProviderGateway(MediaRegistry()).prepare(ProviderRequest("req-2", "unknown"))
        assert False
    except ValueError as exc:
        assert "no provider supports" in str(exc)
