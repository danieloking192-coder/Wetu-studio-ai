"""Dependency-free HTTP application server for the WETU Creator prototype."""
from __future__ import annotations
import json
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from .creator_core import CreatorApplicationCore, CreatorState
from .models.production import CharacterDNA, WorldDNA, SceneMemory
from .universe_mode import UniverseMode, UniverseProduction
from .animation_engine import AnimationEngine, AnimationRequest, AnimationStyle

ROOT = Path(__file__).resolve().parents[2]
UI = ROOT / "prototype" / "creator" / "index.html"

class DemoProvider:
    name = "wetu-demo"
    def generate(self, *, kind, prompt, context):
        return {"model": "wetu-demo-v1", "asset_url": "memory://demo/" + kind, "kind": kind,
                "context_items": len(context.get("recent_generations", []))}

class PassQA:
    def evaluate(self, *, kind, context, result):
        return {"passed": True, "checks": ["identity_context", "world_context", "scene_memory", "provider_result"]}

class DemoContinuity:
    def check(self, *, scene, context):
        available = {c.character_id for c in context.get("characters", [])}
        missing = [cid for cid in scene.character_ids if cid not in available]
        return {"passed": not missing, "issues": missing}

STATE = CreatorState(project_id="demo")
UNIVERSE = UniverseProduction("demo", "WETU Demo Production", UniverseMode.ORIGINAL)
ANIMATION = AnimationEngine()
CORE = CreatorApplicationCore(STATE, providers={"wetu-demo": DemoProvider()}, qa=PassQA(), continuity=DemoContinuity())

def _jsonable(value):
    if hasattr(value, "__dataclass_fields__"):
        return {k: _jsonable(v) for k, v in asdict(value).items()}
    if isinstance(value, dict):
        return {k: _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    return value

class Handler(BaseHTTPRequestHandler):
    def _send(self, status, payload, content_type="application/json; charset=utf-8"):
        raw = payload if isinstance(payload, bytes) else json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            try: self._send(200, UI.read_bytes(), "text/html; charset=utf-8")
            except FileNotFoundError: self._send(404, {"error": "creator UI not found"})
            return
        if path == "/api/state":
            self._send(200, {"project_id": STATE.project_id,
                              "characters": [_jsonable(x) for x in STATE.characters.values()],
                              "worlds": [_jsonable(x) for x in STATE.worlds.values()],
                              "scenes": [_jsonable(x) for x in STATE.scenes.values()],
                              "generations": [_jsonable(x) for x in STATE.memory.generations.values()],
                              "events": STATE.memory.events[-30:],
                              "universe": {"production_id": UNIVERSE.production_id, "title": UNIVERSE.title, "mode": UNIVERSE.mode.value,
                                           "character_references": [_jsonable(x) for x in UNIVERSE.character_references],
                                           "original_universe_id": UNIVERSE.original_universe_id,
                                           "provenance": list(UNIVERSE.provenance)}})
            return
        self._send(404, {"error": "not found"})

    def do_POST(self):
        path = urlparse(self.path).path
        try:
            size = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(size) or b"{}")
            if path == "/api/universe":
                mode = UniverseMode(body.get("mode", "original"))
                global UNIVERSE
                UNIVERSE = UniverseProduction(body.get("production_id", "demo"), body.get("title", "WETU Production"), mode)
                if mode is UniverseMode.FAN_FILM:
                    for item in body.get("character_references", []):
                        UNIVERSE.add_ip_character(item["character_id"], item["display_name"], item["source_work"], item.get("notes", ""))
                elif body.get("original_universe_id"):
                    UNIVERSE.attach_original_universe(body["original_universe_id"])
                issues = UNIVERSE.validate()
                self._send(200 if not issues else 400, {"ok": not issues, "issues": issues, "universe": _jsonable(UNIVERSE)}); return
            if path == "/api/animation":
                style = AnimationStyle(**body["style"])
                request = AnimationRequest(body["request_id"], body.get("project_id", STATE.project_id), body["scene_id"], style, body["prompt"], body.get("references", []), body.get("options", {}))
                self._send(200, ANIMATION.build_request(request)); return
            if path == "/api/characters":
                CORE.add_character(CharacterDNA(**body)); self._send(201, {"ok": True}); return
            if path == "/api/worlds":
                CORE.add_world(WorldDNA(**body)); self._send(201, {"ok": True}); return
            if path == "/api/scenes":
                CORE.add_scene(SceneMemory(**body)); self._send(201, {"ok": True}); return
            if path == "/api/generate":
                result = CORE.generate(**body)
                self._send(200, _jsonable(result)); return
            self._send(404, {"error": "not found"})
        except (ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
            self._send(400, {"error": str(exc)})

def serve(host="127.0.0.1", port=8787):
    print(f"WETU Creator: http://{host}:{port}")
    ThreadingHTTPServer((host, port), Handler).serve_forever()

if __name__ == "__main__":
    serve()
