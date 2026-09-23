import unittest
from wetu_studio.media_engine import MediaRegistry, MediaRequest
from wetu_studio.media_orchestrator import MediaOrchestrator

class FailingProvider:
    name = "failing-image"
    capabilities = {"image"}
    def generate(self, request, context):
        raise RuntimeError("provider unavailable")

class WorkingProvider:
    name = "working-image"
    capabilities = {"image"}
    def generate(self, request, context):
        return {"model":"working-v1","uri":"memory://wetu/image","kind":"image","real_media":False}

class MediaOrchestratorTests(unittest.TestCase):
    def test_auto_selection_falls_back_after_provider_failure(self):
        registry = MediaRegistry({"failing-image": FailingProvider(), "working-image": WorkingProvider()})
        job = MediaOrchestrator(registry).generate(
            MediaRequest("r1","p1","s1","image","test","auto"), {}
        )
        self.assertEqual(job.status, "completed")
        self.assertEqual(job.provider, "working-image")
        self.assertEqual(len(job.attempts), 2)
        self.assertEqual(job.attempts[0]["status"], "failed")
        self.assertEqual(job.attempts[1]["status"], "completed")

    def test_unknown_kind_fails_without_attempts(self):
        registry = MediaRegistry({"working-image": WorkingProvider()})
        job = MediaOrchestrator(registry).generate(
            MediaRequest("r2","p1","s1","video","test","auto"), {}
        )
        self.assertEqual(job.status, "failed")
        self.assertEqual(job.attempts, [])
