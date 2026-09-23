import unittest
from wetu_studio.usage_control import UsageLedger

class UsageControlTests(unittest.TestCase):
    def test_free_plan_reserves_and_refunds(self):
        ledger = UsageLedger()
        units = ledger.reserve("image")
        self.assertEqual(units, 1)
        self.assertEqual(ledger.snapshot()["month_units_used"], 1)
        ledger.refund(units, "image")
        self.assertEqual(ledger.snapshot()["month_units_used"], 0)

    def test_video_scales_by_duration(self):
        ledger = UsageLedger(plan="CREATOR")
        self.assertEqual(ledger.estimate_units("video", {"duration_seconds": 3}), 30)

    def test_plan_limits_are_real_guards(self):
        ledger = UsageLedger()
        for _ in range(5):
            ledger.reserve("image")
        with self.assertRaises(PermissionError):
            ledger.reserve("image")

class PostProductionTests(unittest.TestCase):
    def test_overlap_is_rejected(self):
        from wetu_studio.postproduction import PostProductionEngine, TimelineItem
        issues = PostProductionEngine().validate_timeline([
            TimelineItem("a","video","asset-a",0,1000),
            TimelineItem("b","video","asset-b",900,1500)])
        self.assertTrue(any("overlaps" in x for x in issues))

    def test_export_manifest_contains_quality_gate(self):
        from wetu_studio.postproduction import PostProductionEngine, TimelineItem
        result = PostProductionEngine().export_manifest(
            project_id="p", items=[TimelineItem("a","video","asset-a",0,1000)],
            captions=[], audio_mix=[], delivery_profiles=["mobile_saver"])
        self.assertTrue(result["ready"])
