from wetu_studio import creator_server

def test_project_workspace_isolation(tmp_path, monkeypatch):
    monkeypatch.setattr(creator_server, "STATE_DIR", tmp_path / "projects")
    monkeypatch.setattr(creator_server, "PROJECT_INDEX", tmp_path / "projects.json")

    creator_server._save_projects([{"project_id": "demo", "title": "Demo"}])
    first = creator_server._activate_project("alpha")
    first.memory.remember("alpha_event", {"ok": True})
    creator_server._persist_state(first)

    creator_server._save_projects([
        {"project_id": "demo", "title": "Demo"},
        {"project_id": "alpha", "title": "Alpha"},
        {"project_id": "beta", "title": "Beta"},
    ])
    second = creator_server._activate_project("beta")
    assert second.project_id == "beta"
    assert not second.memory.events

    restored = creator_server._activate_project("alpha")
    assert restored.project_id == "alpha"
    assert restored.memory.events[-1]["type"] == "alpha_event"
