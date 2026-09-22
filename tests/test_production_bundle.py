from wetu_studio.production_bundle import ProductionBundle
from wetu_studio.creator_core import CreatorState

def test_bundle_contains_core_sections():
    b = ProductionBundle().build(CreatorState("demo"))
    assert b["schema_version"] == "1.0"
    assert b["project_id"] == "demo"
    assert "characters" in b and "timeline" in b and "qa" in b