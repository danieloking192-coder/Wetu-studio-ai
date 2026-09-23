from wetu_studio.creator_server import CORE, STATE

def test_demo_runtime_starts_with_expected_project():
    assert STATE.project_id == "demo"
    assert "wetu-demo" in CORE.providers


from pathlib import Path


def test_creator_app_manifest_is_exposed():
    manifest = Path(__file__).parents[1] / "prototype" / "creator" / "manifest.webmanifest"
    assert manifest.exists()
    assert '"display": "standalone"' in manifest.read_text(encoding="utf-8")


def test_creator_service_worker_is_exposed():
    worker = Path(__file__).parents[1] / "prototype" / "creator" / "sw.js"
    assert worker.exists()
    source = worker.read_text(encoding="utf-8")
    assert 'addEventListener("fetch"' in source
    assert 'caches.open(CACHE)' in source
