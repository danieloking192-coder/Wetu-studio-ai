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


def test_localization_and_voice_generation_are_provider_neutral(tmp_path, monkeypatch):
    from wetu_studio import creator_server
    monkeypatch.setattr(creator_server, "STATE_DIR", tmp_path / "projects")
    monkeypatch.setattr(creator_server, "STATE_FILE", tmp_path / "projects" / "demo.json")
    creator_server.STATE = creator_server.CreatorState(project_id="demo")
    creator_server.CORE = creator_server.CreatorApplicationCore(
        creator_server.STATE,
        providers={"wetu-demo": creator_server.DemoProvider()},
        qa=creator_server.PassQA(),
        continuity=creator_server.DemoContinuity(),
    )
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        status, localized = request(server, "POST", "/api/localization/line", {
            "scene_id": "scene-1", "line_id": "l1", "speaker_id": "hero",
            "language": "ln", "text": "Mbote na bino", "subtitle": "Mbote na bino"
        })
        assert status == 200
        assert localized["line"]["language"] == "ln"

        status, voice = request(server, "POST", "/api/audio/voice", {
            "request_id": "voice-1", "scene_id": "scene-1", "speaker_id": "hero",
            "language": "ln", "text": "Mbote na bino"
        })
        assert status == 200
        assert voice["asset"]["real_audio"] is False
        assert voice["asset"]["provider"] == "wetu-local-audio"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

def test_subtitles_are_explicitly_toggleable_and_persisted(tmp_path, monkeypatch):
    from wetu_studio import creator_server
    monkeypatch.setattr(creator_server, "STATE_DIR", tmp_path / "projects")
    monkeypatch.setattr(creator_server, "STATE_FILE", tmp_path / "projects" / "demo.json")
    creator_server.STATE = creator_server.CreatorState(project_id="demo")
    creator_server.CORE = creator_server.CreatorApplicationCore(
        creator_server.STATE,
        providers={"wetu-demo": creator_server.DemoProvider()},
        qa=creator_server.PassQA(),
        continuity=creator_server.DemoContinuity(),
    )
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        status, state = request(server, "GET", "/api/state")
        assert status == 200
        assert state["subtitles_enabled"] is False

        status, changed = request(server, "POST", "/api/subtitles/settings", {"enabled": True})
        assert status == 200
        assert changed["subtitles_enabled"] is True

        reloaded = creator_server._load_persistent_state()
        assert reloaded.subtitles_enabled is True

        status, changed = request(server, "POST", "/api/subtitles/settings", {"enabled": False})
        assert status == 200
        assert changed["subtitles_enabled"] is False
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

def test_subtitle_generation_api_requires_toggle_and_persists_track(tmp_path, monkeypatch):
    from wetu_studio import creator_server
    monkeypatch.setattr(creator_server, "STATE_DIR", tmp_path / "projects")
    monkeypatch.setattr(creator_server, "STATE_FILE", tmp_path / "projects" / "demo.json")
    creator_server.STATE = creator_server.CreatorState(project_id="demo")
    creator_server.CORE = creator_server.CreatorApplicationCore(
        creator_server.STATE,
        providers={"wetu-demo": creator_server.DemoProvider()},
        qa=creator_server.PassQA(),
        continuity=creator_server.DemoContinuity(),
    )
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        try:
            request(server, "POST", "/api/subtitles/generate", {
                "scene_id": "s1", "language": "fr",
                "dialogue": [{"start_ms": 0, "end_ms": 1000, "text": "Bonjour."}],
            })
            assert False
        except Exception as exc:
            assert "409" in str(exc)

        status, _ = request(server, "POST", "/api/subtitles/settings", {"enabled": True})
        assert status == 200
        status, result = request(server, "POST", "/api/subtitles/generate", {
            "track_id": "sub-api", "scene_id": "s1", "language": "fr",
            "dialogue": [{"start_ms": 0, "end_ms": 1000, "speaker": "Amina", "text": "Bonjour."}],
        })
        assert status == 200
        assert result["track"]["track_id"] == "sub-api"
        assert "WEBVTT" in result["vtt"]
        assert "Amina: Bonjour." in result["srt"]
        assert any(e.get("type") == "subtitle_track_created" for e in creator_server.STATE.memory.events)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_economic_roles_and_admin_guard(tmp_path, monkeypatch):
    from wetu_studio import creator_server
    from wetu_studio.economic_core import EconomicLedger
    monkeypatch.setattr(creator_server, "ECONOMY", EconomicLedger(promotional_units=5, purchased_units=10))
    monkeypatch.setenv("WETU_ADMIN_KEY", "test-admin-key")
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        status, public = request(server, "GET", "/api/economy")
        assert status == 200
        assert public["economy"]["user"]["promotional_units"] == 5

        try:
            request(server, "GET", "/api/admin/economy")
            assert False
        except Exception as exc:
            assert "403" in str(exc)

        try:
            request(server, "POST", "/api/media-generate", {
                "request_id": "admin-media-1", "kind": "image", "provider": "wetu-local",
                "prompt": "admin test", "account_type": "ADMIN"
            })
            assert False
        except Exception as exc:
            assert "403" in str(exc)

        # The client may only use ADMIN when it also presents the server-side key.
        url = f"http://127.0.0.1:{server.server_port}/api/media-generate"
        payload = json.dumps({
            "request_id": "admin-media-2", "kind": "image", "provider": "wetu-local",
            "prompt": "admin test", "account_type": "ADMIN"
        }).encode()
        req = urllib.request.Request(url, data=payload, headers={
            "Content-Type": "application/json", "X-WETU-ADMIN-KEY": "test-admin-key"
        }, method="POST")
        with urllib.request.urlopen(req, timeout=5) as response:
            result = json.loads(response.read().decode())
            assert response.status == 200
        assert result["economy"]["user"]["promotional_units"] == 5
        assert result["economy"]["admin"]["provider_cost_logged"] == 0.0
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_media_generate_uses_orchestrator_and_exposes_job(tmp_path, monkeypatch):
    from wetu_studio import creator_server
    from wetu_studio.media_engine import MediaRegistry
    from wetu_studio.media_orchestrator import MediaOrchestrator
    monkeypatch.setattr(creator_server, "MEDIA", MediaRegistry())
    monkeypatch.setattr(creator_server, "MEDIA_ORCHESTRATOR", MediaOrchestrator(creator_server.MEDIA))
    class Provider:
        name = "test-image"
        capabilities = {"image"}
        def generate(self, request, context):
            return {"model": "test", "uri": "memory://test/image", "kind": "image", "real_media": False}
    creator_server.MEDIA.register(Provider())
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        status, result = request(server, "POST", "/api/media-generate", {
            "request_id": "orch-1", "kind": "image", "provider": "test-image",
            "prompt": "test image"
        })
        assert status == 200
        assert result["ok"] is True
        assert result["status"] == "completed"
        assert result["job"]["provider"] == "test-image"
        assert result["asset"]["status"] == "ready"

        status, job = request(server, "POST", "/api/media-jobs", {"job_id": "orch-1"})
        assert status == 200
        assert job["job"]["status"] == "completed"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
