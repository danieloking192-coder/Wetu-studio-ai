import unittest
from types import SimpleNamespace
from wetu_studio.asset_store import AssetStore
from wetu_studio.reference_store import ReferenceStore

class ReferenceContinuityTests(unittest.TestCase):
    def test_asset_becomes_reusable_reference(self):
        asset=SimpleNamespace(asset_id="a1",project_id="p",scene_id="s1",kind="image",
                              provider="wetu-local",uri="manifest://a1",
                              metadata={"real_media":False})
        record=AssetStore().remember(asset)
        store=ReferenceStore()
        store.remember_asset(record,entity_id="hero",continuity_key="hero.v1")
        self.assertEqual(store.uris_for_scene("p",scene_id="s2",entity_ids=["hero"]),
                         ["manifest://a1"])
