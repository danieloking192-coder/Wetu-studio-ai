from wetu_studio.media_engine import MediaRegistry, MediaRequest
from wetu_studio.timeline_engine import Timeline, TimelineClip
from wetu_studio.realism_qa import RealismQA

def test_media_registry_supports_all_core_kinds():
    reg = MediaRegistry()
    for kind in ("image", "video", "audio"):
        asset = reg.generate(MediaRequest("r-"+kind, "p", "s", kind, "test", "wetu-local"), {})
        assert asset.kind == kind
        assert asset.metadata["provider_result"]["real_media"] is False

def test_timeline_detects_overlap():
    t = Timeline("p")
    t.add(TimelineClip("a", "asset-a", "video", 0, 2))
    t.add(TimelineClip("b", "asset-b", "video", 1, 2))
    assert not t.validate()["passed"]

def test_realism_qa_reports_missing_uri():
    result = RealismQA().evaluate(kind="image", context={"scene": object()}, result={"model":"x"})
    assert not result["passed"]
    assert "media_uri" in result["issues"]