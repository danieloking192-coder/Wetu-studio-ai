import json
import threading
import urllib.request
from http.server import ThreadingHTTPServer

from wetu_studio.creator_server import Handler


def request(server, method, path, payload=None):
    url = f"http://127.0.0.1:{server.server_port}{path}"
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=5) as response:
        return response.status, json.loads(response.read().decode())


def fixture():
    return {
        "project_id": "api-flow",
        "brief": "A realistic cinematic story about Amina.",
        "characters": [{
            "character_id": "hero",
            "name": "Amina",
            "face": {"identity": "stable", "age_range": "adult"},
            "hair": {"style": "braided"},
            "eyes": {"color": "brown"},
            "wardrobe": {"clothing": "blue coat"},
            "traits": ["calm", "determined"],
        }],
        "world": {
            "world_id": "kinshasa",
            "name": "Kinshasa",
            "geography": {"city": "Kinshasa"},
            "architecture": {"style": "contemporary"},
            "environment": {"weather": "warm"},
        },
        "scenes": [{
            "scene_id": "s1",
            "project_id": "api-flow",
            "sequence": 1,
            "language": "fr",
            "character_ids": ["hero"],
            "world_id": "kinshasa",
            "state": {"title": "Arrival", "summary": "Amina arrives."},
        }, {
            "scene_id": "s2",
            "project_id": "api-flow",
            "sequence": 2,
            "language": "fr",
            "character_ids": ["hero"],
            "world_id": "kinshasa",
            "previous_scene_ids": ["s1"],
            "state": {"title": "Decision", "summary": "Amina decides."},
        }],
        "provider": "wetu-local",
        "kind": "image",
        "default_mood": "tense",
    }


def test_creator_api_end_to_end_production_flow():
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        status, providers = request(server, "POST", "/api/providers", {})
        assert status == 200
        assert any(p["name"] == "wetu-local" for p in providers["providers"])

        body = fixture()
        status, plan = request(server, "POST", "/api/creative-plan", body)
        assert status == 200
        assert plan["ok"] is True
        assert len(plan["plan"]["scenes"]) == 2

        status, produced = request(server, "POST", "/api/produce", body)
        assert status == 200
        assert produced["ok"] is True
        assets = [a for a in produced["production"]["assets"] if a["status"] == "generated"]
        assert len(assets) == 2
        assert produced["production"]["pipeline"]["memory_preserved"] is True
        assert produced["production"]["pipeline"]["continuity_preflight"] is True

        status, media = request(server, "POST", "/api/media-generate", {
            "request_id": "media-api-1",
            "project_id": "api-flow",
            "scene_id": "s1",
            "kind": "image",
            "provider": "wetu-local",
            "prompt": "Amina in Kinshasa, cinematic realism.",
            "references": ["hero"],
            "options": {"aspect_ratio": "16:9"},
        })
        assert status == 200
        assert media["ok"] is True
        assert media["asset"]["provider"] == "wetu-local"
        assert media["asset"]["status"] == "ready"
        assert media["real_media"] is False
        assert media["asset"]["metadata"]["references"] == ["hero"]

        status, state = request(server, "GET", "/api/state")
        assert status == 200
        assert state["project_id"] == "demo"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_project_manager_endpoints(tmp_path, monkeypatch):
    from wetu_studio import creator_server
    monkeypatch.setattr(creator_server, "STATE_DIR", tmp_path / "projects")
    monkeypatch.setattr(creator_server, "PROJECT_INDEX", tmp_path / "projects.json")
    creator_server._save_projects([{"project_id": "demo", "title": "Demo"}])
    projects = creator_server._list_projects()
    assert projects[0]["project_id"] == "demo"
    creator_server._save_projects(projects + [{"project_id": "film-1", "title": "Film 1"}])
    state = creator_server._activate_project("film-1")
    assert state.project_id == "film-1"
    assert creator_server.STATE_FILE == tmp_path / "projects" / "film-1.json"
