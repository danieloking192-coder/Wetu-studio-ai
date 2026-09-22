from wetu_studio.advanced_qa import AdvancedContinuityQA, ContinuityGuard
from wetu_studio.production_timeline import ProductionTimeline, EditItem

def test_qa_catches_missing_asset():
    t=ProductionTimeline("t")
    t.add(EditItem("v","missing","VIDEO",0,1000,0))
    report=AdvancedContinuityQA().evaluate(scenes={"s":object()},assets=[],timeline=t)
    assert not report.passed
    assert not report.checks["asset_traceability"]

def test_continuity_guard_detects_identity_change():
    issues=ContinuityGuard().compare_scene_context(
        {"character_ids":["c1"],"world_id":"w1"},
        {"character_ids":["c2"],"world_id":"w1"})
    assert issues and issues[0]["field"]=="character_ids"