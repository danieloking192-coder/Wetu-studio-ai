from wetu_studio.creator_server import CORE, STATE

def test_demo_runtime_starts_with_expected_project():
    assert STATE.project_id == "demo"
    assert "wetu-demo" in CORE.providers
