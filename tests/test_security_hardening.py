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
