import json
import os
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

from wetu_studio import creator_server
from wetu_studio.creator_server import Handler


def req(server, method, path, payload=None, headers=None):
    data = None
    h = dict(headers or {})
    if payload is not None:
        data = json.dumps(payload).encode()
        h["Content-Type"] = "application/json"
    r = urllib.request.Request(
        f"http://127.0.0.1:{server.server_port}{path}",
        data=data, headers=h, method=method
    )
    try:
        with urllib.request.urlopen(r, timeout=3) as response:
            return response.status, dict(response.headers), response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, dict(exc.headers), exc.read()


def test_security_headers_and_bounded_payload(tmp_path, monkeypatch):
    monkeypatch.setattr(creator_server, "STATE_DIR", tmp_path / "projects")
    monkeypatch.setattr(creator_server, "PROJECT_INDEX", tmp_path / "projects.json")
    monkeypatch.setattr(creator_server, "STATE_FILE", tmp_path / "projects" / "demo.json")
    monkeypatch.setattr(creator_server, "MAX_BODY_BYTES", 64)
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        status, headers, _ = req(server, "GET", "/api/state")
        assert status == 200
        assert headers["X-Content-Type-Options"] == "nosniff"
        assert headers["X-Frame-Options"] == "DENY"
        assert headers["Cache-Control"] == "no-store"
        assert "frame-ancestors 'none'" in headers["Content-Security-Policy"]

        status, _, _ = req(server, "POST", "/api/projects/create", {"project_id": "x" * 100, "title": "x"})
        assert status in (400, 413)

        status, _, _ = req(server, "POST", "/api/projects/create", {"project_id": "x" * 1000})
        assert status == 413
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_project_id_path_traversal_is_rejected():
    try:
        creator_server._project_file("../escape")
    except ValueError:
        return
    raise AssertionError("unsafe project id was accepted")


def test_persistence_file_permissions(tmp_path, monkeypatch):
    state_file = tmp_path / "state.json"
    monkeypatch.setattr(creator_server, "STATE_FILE", state_file)
    state = creator_server.CreatorState(project_id="secure")
    creator_server._persist_state(state)
    if os.name != "nt":
        assert oct(state_file.stat().st_mode & 0o777) == "0o600"


def test_authentication_uses_bearer_token(tmp_path, monkeypatch):
    monkeypatch.setattr(creator_server, "AUTH_TOKEN", "test-secret")
    monkeypatch.setattr(creator_server, "_RATE_LIMITER", creator_server.BoundedRateLimiter(window_seconds=60, max_requests=120))
    monkeypatch.setattr(creator_server, "STATE_DIR", tmp_path / "projects")
    monkeypatch.setattr(creator_server, "STATE_FILE", tmp_path / "projects" / "demo.json")
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        status, _, _ = req(server, "GET", "/api/state")
        assert status == 401
        status, _, _ = req(server, "GET", "/api/state", headers={"Authorization": "Bearer wrong"})
        assert status == 401
        status, _, _ = req(server, "GET", "/api/state", headers={"Authorization": "Bearer test-secret"})
        assert status == 200
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_strict_project_id_validation():
    for value in ("../escape", "a/b", "a\\b", " space", "-bad", "a" * 65):
        try:
            creator_server._project_file(value)
        except ValueError:
            continue
        raise AssertionError(f"unsafe project id accepted: {value!r}")


def test_field_limits():
    try:
        creator_server._validate_common({"prompt": "x" * (creator_server.MAX_PROMPT_CHARS + 1)})
    except ValueError:
        return
    raise AssertionError("oversized prompt accepted")


def test_project_runtime_isolation_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(creator_server, "STATE_DIR", tmp_path / "projects")
    monkeypatch.setattr(creator_server, "STATE_FILE", tmp_path / "projects" / "a.json")

    creator_server.UNIVERSE = creator_server.UniverseProduction("a", "Project A", creator_server.UniverseMode.ORIGINAL)
    creator_server.UNIVERSE.attach_original_universe("universe-a")
    creator_server.SCRIPTURAL = None
    creator_server.FAN_PIPELINE = None
    creator_server._save_runtime("a")

    creator_server.UNIVERSE = creator_server.UniverseProduction("b", "Project B", creator_server.UniverseMode.FAN_FILM)
    creator_server.SCRIPTURAL = None
    creator_server.FAN_PIPELINE = creator_server.FanFilmPipeline(creator_server.UNIVERSE)
    creator_server.FAN_PIPELINE.start()
    creator_server._save_runtime("b")

    creator_server.UNIVERSE = creator_server.UniverseProduction("wrong", "Wrong", creator_server.UniverseMode.ORIGINAL)
    creator_server.FAN_PIPELINE = None
    creator_server._load_runtime("a")

    assert creator_server.UNIVERSE.production_id == "a"
    assert creator_server.UNIVERSE.original_universe_id == "universe-a"
    assert creator_server.FAN_PIPELINE is None

    creator_server._load_runtime("b")
    assert creator_server.UNIVERSE.production_id == "b"
    assert creator_server.UNIVERSE.mode is creator_server.UniverseMode.FAN_FILM
    assert creator_server.FAN_PIPELINE is not None
    assert creator_server.FAN_PIPELINE.production is creator_server.UNIVERSE


def test_state_lock_is_reentrant():
    assert creator_server._STATE_LOCK.acquire()
    try:
        assert creator_server._STATE_LOCK.acquire()
        creator_server._STATE_LOCK.release()
    finally:
        creator_server._STATE_LOCK.release()
