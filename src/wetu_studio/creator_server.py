"""Dependency-free HTTP application server for the WETU Creator prototype."""
from __future__ import annotations
import json
import os
import tempfile
import re
import time
import threading
import hmac
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from .creator_core import CreatorApplicationCore, CreatorState
from .models.production import CharacterDNA, WorldDNA, SceneMemory
from .universe_mode import UniverseMode, UniverseProduction, IPCharacterReference
from .animation_engine import AnimationEngine, AnimationRequest, AnimationStyle
from .fan_film_pipeline import FanFilmPipeline
from .scriptural_universe import ScripturalSource, ScripturalUniverse, SourceClass, FidelityMode, ScripturalRealismQA
from .scriptural_catalog import catalog_summary, story_manifest
from .mature_policy import MatureAccess, MatureRequest, MaturePolicy, decision_json
from .scriptural_production import build_scriptural_production
from .scriptural_entity_catalog import CATALOG
from .emotion_atmosphere import EmotionAtmosphereEngine
from .true_story_realism import TrueStoryRealismEngine, TrueStoryMode
from .production_realism import ProductionRealismOrchestrator
from .creative_orchestrator import WetuCreativeOrchestrator
from .media_engine import MediaRegistry, MediaRequest, provider_from_environment
from .subtitle_engine import SubtitleEngine
from .localization_engine import LocalizationEngine, LocalizationTrack
from .audio_pipeline import AudioRegistry, VoiceRequest
from .media_sync import MediaSyncEngine, SyncCue
from .security_controls import BoundedRateLimiter, validate_content_length

ROOT = Path(__file__).resolve().parents[2]
UI = ROOT / "prototype" / "creator" / "index.html"
STATE_DIR = Path(os.environ.get("WETU_STATE_DIR", str(ROOT / ".wetu" / "projects")))
PROJECT_INDEX = Path(os.environ.get("WETU_PROJECT_INDEX", str(ROOT / ".wetu" / "projects.json")))
STATE_FILE = Path(os.environ.get("WETU_STATE_FILE", str(STATE_DIR / "demo.json")))
MAX_BODY_BYTES = int(os.environ.get("WETU_MAX_BODY_BYTES", "2097152"))
RATE_LIMIT_WINDOW = int(os.environ.get("WETU_RATE_LIMIT_WINDOW", "60"))
RATE_LIMIT_MAX = int(os.environ.get("WETU_RATE_LIMIT_MAX", "120"))
_STATE_LOCK = threading.RLock()
AUTH_TOKEN = os.environ.get("WETU_AUTH_TOKEN")
PROJECT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
MAX_PROJECTS = int(os.environ.get("WETU_MAX_PROJECTS", "1000"))
MAX_TITLE_CHARS = int(os.environ.get("WETU_MAX_TITLE_CHARS", "200"))
MAX_ID_CHARS = int(os.environ.get("WETU_MAX_ID_CHARS", "128"))
MAX_PROMPT_CHARS = int(os.environ.get("WETU_MAX_PROMPT_CHARS", "20000"))
MAX_LIST_ITEMS = int(os.environ.get("WETU_MAX_LIST_ITEMS", "200"))
_RATE_LIMITER = BoundedRateLimiter(window_seconds=RATE_LIMIT_WINDOW, max_requests=RATE_LIMIT_MAX)
LOCALIZATION = LocalizationEngine()
AUDIO = AudioRegistry()
_LOCALIZATION_TRACKS = {}

def _load_persistent_state():
    state = CreatorState(project_id="demo")
    if not STATE_FILE.exists():
        return state
    try:
        payload = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        state.project_id = str(payload.get("project_id", "demo"))
        state.characters = {x["character_id"]: CharacterDNA(**x) for x in payload.get("characters", [])}
        state.worlds = {x["world_id"]: WorldDNA(**x) for x in payload.get("worlds", [])}
        state.scenes = {x["scene_id"]: SceneMemory(**x) for x in payload.get("scenes", [])}
        from .models.production import GenerationRecord, ProductionDecision
        state.memory.generations = {x["generation_id"]: GenerationRecord(**x) for x in payload.get("generations", [])}
        state.memory.decisions = {x["decision_id"]: ProductionDecision(**x) for x in payload.get("decisions", [])}
        state.memory.references = payload.get("references", {})
        state.memory.events = payload.get("events", [])
        state.memory.sync_manifests = payload.get("sync_manifests", {})
        state.subtitles_enabled = bool(payload.get("subtitles_enabled", False))
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError):
        return CreatorState(project_id="demo")
    return state

def _project_file(project_id):
    if not isinstance(project_id, str) or not PROJECT_ID_RE.fullmatch(project_id):
        raise ValueError("invalid project_id")
    return STATE_DIR / (project_id + ".json")

def _runtime_file(project_id):
    return STATE_DIR / (project_id + ".runtime.json")

def _save_runtime(project_id):
    payload = _jsonable({
        "universe": UNIVERSE,
        "scriptural": SCRIPTURAL,
        "fan_pipeline": FAN_PIPELINE,
    })
    path = _runtime_file(project_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix="wetu-runtime-", suffix=".json", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
        _secure_file(path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)

def _load_runtime(project_id):
    path = _runtime_file(project_id)
    if not path.exists():
        return
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        universe = payload.get("universe") or {}
        mode = UniverseMode(universe.get("mode", "original"))
        production = UniverseProduction(universe.get("production_id", project_id), universe.get("title", "WETU Production"), mode)
        production.original_universe_id = universe.get("original_universe_id")
        production.provenance = list(universe.get("provenance", []))
        production.character_references = [IPCharacterReference(**x) for x in universe.get("character_references", [])]
        global UNIVERSE, SCRIPTURAL, FAN_PIPELINE
        UNIVERSE = production
        s = payload.get("scriptural")
        SCRIPTURAL = None
        if s:
            source_data = s.get("source", {})
            source = ScripturalSource(source_data["source_id"], source_data["source_title"], SourceClass(source_data["source_class"]), source_data.get("tradition", ""), source_data.get("source_notes", ""))
            SCRIPTURAL = ScripturalUniverse(s["universe_id"], s["title"], source, FidelityMode(s["fidelity"]), s.get("era", ""), s.get("region", ""), s.get("languages", []), s.get("provenance", []), s.get("canon_status", ""), s.get("details", {}))
        fp = payload.get("fan_pipeline")
        FAN_PIPELINE = None
        if fp:
            FAN_PIPELINE = FanFilmPipeline(UNIVERSE, list(fp.get("stages", [])), list(fp.get("scenes", [])), list(fp.get("animation_requests", [])), list(fp.get("audio_requests", [])), list(fp.get("timeline_items", [])), list(fp.get("qa_reports", [])))
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError):
        return

def _secure_file(path):
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass

def _rate_limited(client):
    return not _RATE_LIMITER.allow(client)

def _authorized(handler):
    if not AUTH_TOKEN:
        return True
    supplied = handler.headers.get("Authorization", "")
    return hmac.compare_digest(supplied, "Bearer " + AUTH_TOKEN)

def _bounded_string(value, name, limit):
    if value is None:
        return value
    if not isinstance(value, str) or len(value) > limit:
        raise ValueError(f"{name} exceeds allowed length")
    return value

def _validate_common(body):
    if "project_id" in body:
        project_id = body["project_id"]
        if not isinstance(project_id, str) or not PROJECT_ID_RE.fullmatch(project_id):
            raise ValueError("invalid project_id")
    for key in ("request_id", "scene_id", "character_id", "world_id", "generation_id"):
        if key in body:
            _bounded_string(body[key], key, MAX_ID_CHARS)
    if "title" in body:
        _bounded_string(body["title"], "title", MAX_TITLE_CHARS)
    if "brief" in body:
        _bounded_string(body["brief"], "brief", MAX_PROMPT_CHARS)
    if "prompt" in body:
        _bounded_string(body["prompt"], "prompt", MAX_PROMPT_CHARS)
    for key in ("characters", "scenes", "references", "languages"):
        if key in body and isinstance(body[key], list) and len(body[key]) > MAX_LIST_ITEMS:
            raise ValueError(f"{key} contains too many items")

def _list_projects():
    if not PROJECT_INDEX.exists():
        return [{"project_id": "demo", "title": "WETU Demo Production"}]
    try:
        data = json.loads(PROJECT_INDEX.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return [{"project_id": "demo", "title": "WETU Demo Production"}]

def _save_projects(projects):
    if len(projects) > MAX_PROJECTS:
        raise ValueError("project limit reached")
    PROJECT_INDEX.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix="wetu-projects-", suffix=".json", dir=str(PROJECT_INDEX.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(projects, handle, ensure_ascii=False, indent=2)
        os.replace(tmp, PROJECT_INDEX)
        _secure_file(PROJECT_INDEX)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)

def _activate_project(project_id):
    global STATE, CORE, STATE_FILE
    with _STATE_LOCK:
        if STATE is not None:
            _persist_state(STATE)
            _save_runtime(STATE.project_id)
        STATE_FILE = _project_file(project_id)
        STATE = _load_persistent_state()
        STATE.project_id = project_id
        CORE = CreatorApplicationCore(STATE, providers={"wetu-demo": DemoProvider()}, qa=PassQA(), continuity=DemoContinuity())
        _persist_state(STATE)
        _load_runtime(project_id)
        return STATE

def _persist_state(state):
    payload = _jsonable({
        "project_id": state.project_id,
        "characters": list(state.characters.values()),
        "worlds": list(state.worlds.values()),
        "scenes": list(state.scenes.values()),
        "generations": list(state.memory.generations.values()),
        "decisions": list(state.memory.decisions.values()),
        "references": state.memory.references,
        "events": state.memory.events,
        "sync_manifests": state.memory.sync_manifests,
        "subtitles_enabled": bool(getattr(state, "subtitles_enabled", False)),
    })
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix="wetu-state-", suffix=".json", dir=str(STATE_FILE.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
        os.replace(tmp, STATE_FILE)
        _secure_file(STATE_FILE)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)

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

STATE = _load_persistent_state()
UNIVERSE = UniverseProduction("demo", "WETU Demo Production", UniverseMode.ORIGINAL)
ANIMATION = AnimationEngine()
FAN_PIPELINE = None
SCRIPTURAL = None
SCRIPTURAL_QA = ScripturalRealismQA()
EMOTION_ATMOSPHERE = EmotionAtmosphereEngine()
TRUE_STORY_REALISM = TrueStoryRealismEngine()
PRODUCTION_REALISM = ProductionRealismOrchestrator(emotion=EMOTION_ATMOSPHERE, true_story=TRUE_STORY_REALISM)
MEDIA = MediaRegistry()
ENV_MEDIA = provider_from_environment()
if ENV_MEDIA:
    MEDIA.register(ENV_MEDIA)
CREATIVE_ORCHESTRATOR = WetuCreativeOrchestrator(realism=PRODUCTION_REALISM, media=MEDIA)
MATURE_POLICY = MaturePolicy()
CORE = CreatorApplicationCore(STATE, providers={"wetu-demo": DemoProvider()}, qa=PassQA(), continuity=DemoContinuity())

def _jsonable(value):
    if hasattr(value, "__dataclass_fields__"):
        return {k: _jsonable(v) for k, v in asdict(value).items()}
    if isinstance(value, dict):
        return {k: _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_jsonable(v) for v in value]
    return value

class Handler(BaseHTTPRequestHandler):
    def _send(self, status, payload, content_type="application/json; charset=utf-8"):
        raw = payload if isinstance(payload, bytes) else json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Connection", "close")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        path = urlparse(self.path).path
        if path.startswith("/api/"):
            if _rate_limited(self.client_address[0]):
                self._send(429, {"error": "rate limit exceeded"})
                return
            if not _authorized(self):
                self._send(401, {"error": "authentication required"})
                return
        if path in ("/", "/index.html"):
            try: self._send(200, UI.read_bytes(), "text/html; charset=utf-8")
            except FileNotFoundError: self._send(404, {"error": "creator UI not found"})
            return
        if path == "/sw.js":
            service_worker = UI.parent / "sw.js"
            try:
                self._send(200, service_worker.read_bytes(), "application/javascript; charset=utf-8")
            except FileNotFoundError:
                self._send(404, {"error": "service worker not found"})
            return
        if path == "/manifest.webmanifest":
            manifest = UI.parent / "manifest.webmanifest"
            try: self._send(200, manifest.read_bytes(), "application/manifest+json; charset=utf-8")
            except FileNotFoundError: self._send(404, {"error": "app manifest not found"})
            return
        if path == "/api/state":
            with _STATE_LOCK:
                snapshot = {"project_id": STATE.project_id,
                              "characters": [_jsonable(x) for x in STATE.characters.values()],
                              "worlds": [_jsonable(x) for x in STATE.worlds.values()],
                              "scenes": [_jsonable(x) for x in STATE.scenes.values()],
                              "generations": [_jsonable(x) for x in STATE.memory.generations.values()],
                              "events": STATE.memory.events[-30:],
                              "decisions": [_jsonable(x) for x in STATE.memory.decisions.values()],
                              "references": _jsonable(STATE.memory.references),
                              "sync_manifests": _jsonable(STATE.memory.sync_manifests),
                              "subtitles_enabled": STATE.subtitles_enabled,
                              "universe": {"production_id": UNIVERSE.production_id, "title": UNIVERSE.title, "mode": UNIVERSE.mode.value,
                                           "scriptural": _jsonable(SCRIPTURAL),
                                           "mature": {"mode": "MATURE_18_PLUS", "policy_version": "1.0"},
                                           "character_references": [_jsonable(x) for x in UNIVERSE.character_references],
                                           "original_universe_id": UNIVERSE.original_universe_id,
                                           "provenance": list(UNIVERSE.provenance)}}
            self._send(200, snapshot)
            return
        self._send(404, {"error": "not found"})

    def do_POST(self):
        path = urlparse(self.path).path
        try:
            if _rate_limited(self.client_address[0]):
                self._send(429, {"error": "rate limit exceeded"})
                return
            if AUTH_TOKEN and path.startswith("/api/"):
                if not _authorized(self):
                    self._send(401, {"error": "authentication required"})
                    return
            try:
                size = validate_content_length(self.headers.get("Content-Length"), MAX_BODY_BYTES)
            except ValueError as exc:
                message = str(exc)
                self._send(411 if message == "Content-Length required" else 413, {"error": message})
                return
            body = json.loads(self.rfile.read(size) or b"{}")
            if not isinstance(body, dict):
                self._send(400, {"error": "JSON object required"})
                return
            _validate_common(body)
            if path == "/api/projects":
                self._send(200, {"ok": True, "active_project_id": STATE.project_id, "projects": _list_projects()})
                return
            if path == "/api/projects/create":
                project_id = body.get("project_id")
                title = body.get("title", project_id)
                if not project_id or project_id in {p["project_id"] for p in _list_projects()}:
                    raise ValueError("project_id is required and must be unique")
                projects = _list_projects()
                projects.append({"project_id": project_id, "title": title})
                _save_projects(projects)
                _activate_project(project_id)
                self._send(201, {"ok": True, "project_id": project_id, "title": title})
                return
            if path == "/api/projects/switch":
                project_id = body["project_id"]
                if project_id not in {p["project_id"] for p in _list_projects()}:
                    raise ValueError("unknown project")
                _activate_project(project_id)
                self._send(200, {"ok": True, "project_id": STATE.project_id})
                return
            if path == "/api/localization/line":
                track_id = body.get("track_id", "loc-" + str(int(time.time() * 1000)))
                language = body.get("language", "fr")
                with _STATE_LOCK:
                    track = _LOCALIZATION_TRACKS.setdefault(
                        (STATE.project_id, track_id),
                        LocalizationTrack(scene_id=body.get("scene_id", "")),
                    )
                    line = LOCALIZATION.add_line(
                        track, body["line_id"], body["speaker_id"], language,
                        body["text"], body.get("voice_id", ""), body.get("subtitle", ""),
                    )
                    STATE.memory.remember("localization_line_added", {
                        "track_id": track_id, "scene_id": track.scene_id,
                        "line": asdict(line),
                    })
                    _persist_state(STATE)
                self._send(200, {"ok": True, "track_id": track_id,
                                 "line": asdict(line),
                                 "languages": LOCALIZATION.languages(track),
                                 "subtitles": LOCALIZATION.export_subtitles(track)})
                return

            if path == "/api/audio/voice":
                request = VoiceRequest(
                    request_id=body["request_id"],
                    project_id=body.get("project_id", STATE.project_id),
                    scene_id=body.get("scene_id", ""),
                    speaker_id=body["speaker_id"],
                    language=body.get("language", "fr"),
                    text=body["text"],
                    voice_id=body.get("voice_id", ""),
                    options=body.get("options", {}),
                )
                asset = AUDIO.generate(request, body.get("context", {}))
                with _STATE_LOCK:
                    STATE.memory.remember("voice_generation_requested", {
                        "request_id": request.request_id, "scene_id": request.scene_id,
                        "speaker_id": request.speaker_id, "language": request.language,
                        "provider": asset.get("provider"), "real_audio": asset.get("real_audio", False),
                    })
                    _persist_state(STATE)
                self._send(200, {"ok": True, "asset": asset,
                                 "real_audio": asset.get("real_audio", False)})
                return

            if path == "/api/media-sync":
                manifest_id = body.get("manifest_id", "sync-" + str(int(time.time() * 1000)))
                raw_cues = body.get("cues", [])
                cues = [SyncCue(
                    line_id=x["line_id"], start_ms=int(x["start_ms"]), end_ms=int(x["end_ms"]),
                    speaker_id=x["speaker_id"], language=x["language"], text=x["text"],
                    voice_request_id=x.get("voice_request_id", ""),
                ) for x in raw_cues]
                manifest = MediaSyncEngine().build_manifest(cues)
                with _STATE_LOCK:
                    STATE.memory.add_sync_manifest(manifest_id, manifest)
                    _persist_state(STATE)
                self._send(200, {"ok": True, "manifest_id": manifest_id, "manifest": manifest})
                return

            if path == "/api/subtitles/settings":
                enabled = body.get("enabled")
                if not isinstance(enabled, bool):
                    raise ValueError("enabled must be boolean")
                with _STATE_LOCK:
                    STATE.subtitles_enabled = enabled
                    STATE.memory.remember("subtitle_setting_changed", {"enabled": enabled})
                    _persist_state(STATE)
                self._send(200, {"ok": True, "subtitles_enabled": enabled})
                return

            if path == "/api/subtitles/generate":
                if not STATE.subtitles_enabled:
                    self._send(409, {"error": "subtitles are disabled; enable them explicitly first"})
                    return
                track_id = body.get("track_id", "sub-" + str(int(time.time() * 1000)))
                dialogue = body.get("dialogue", [])
                language = body.get("language", "fr")
                engine = SubtitleEngine()
                track = engine.build_track(
                    track_id=track_id,
                    project_id=STATE.project_id,
                    scene_id=body.get("scene_id"),
                    language=language,
                    dialogue=dialogue,
                    source=body.get("source", "dialogue"),
                    enabled=True,
                )
                with _STATE_LOCK:
                    STATE.memory.remember("subtitle_track_created", track.to_dict())
                    _persist_state(STATE)
                self._send(200, {"ok": True, "track": track.to_dict(), "srt": track.to_srt(), "vtt": track.to_vtt()})
                return

            if path == "/api/persistence/status":
                self._send(200, {"ok": True, "persistent": True, "exists": STATE_FILE.exists(),
                                 "characters": len(STATE.characters), "worlds": len(STATE.worlds),
                                 "scenes": len(STATE.scenes), "generations": len(STATE.memory.generations)})
                return
            if path == "/api/universe":
                mode = UniverseMode(body.get("mode", "original"))
                global UNIVERSE
                UNIVERSE = UniverseProduction(body.get("production_id", STATE.project_id), body.get("title", "WETU Production"), mode)
                if mode is UniverseMode.FAN_FILM:
                    for item in body.get("character_references", []):
                        UNIVERSE.add_ip_character(item["character_id"], item["display_name"], item["source_work"], item.get("notes", ""))
                elif body.get("original_universe_id"):
                    UNIVERSE.attach_original_universe(body["original_universe_id"])
                issues = UNIVERSE.validate()
                _save_runtime(STATE.project_id)
                self._send(200 if not issues else 400, {"ok": not issues, "issues": issues, "universe": _jsonable(UNIVERSE)}); return
            if path == "/api/entities":
                kind = body.get("kind")
                entities = list(CATALOG.entities.values())
                if kind:
                    from .entity_dna import EntityKind
                    entities = CATALOG.by_kind(EntityKind(kind))
                self._send(200, {"entities": [_jsonable(e) for e in entities]}); return
            if path == "/api/scriptural-production":
                production=build_scriptural_production(body["story_id"], FidelityMode(body.get("fidelity","historical_cinematic")))
                self._send(200, production); return
            if path == "/api/emotion-atmosphere":
                scene = EMOTION_ATMOSPHERE.build(scene_id=body["scene_id"], mood=body.get("mood","natural"), beats=body.get("emotional_beats",body.get("beats",[])), atmosphere=body.get("atmosphere",{}), sensory_focus=body.get("sensory_focus",[]), camera_guidance=body.get("camera_guidance",[]), continuity_notes=body.get("continuity_notes",[]), source_vs_interpretation=body.get("source_vs_interpretation","artistic_direction"))
                issues = EMOTION_ATMOSPHERE.validate(scene)
                self._send(200, {"ok": not issues, "issues": issues, "scene": EMOTION_ATMOSPHERE.to_dict(scene), "continuity_snapshot": EMOTION_ATMOSPHERE.continuity_snapshot(scene)}); return
            if path == "/api/providers":
                self._send(200, {"providers":[_jsonable(x) for x in CREATIVE_ORCHESTRATOR.selector.profiles()]}); return
            if path == "/api/produce":
                from .models.production import CharacterDNA, SceneMemory, WorldDNA
                chars=[CharacterDNA(**x) for x in body.get("characters",[])]
                world=WorldDNA(**body["world"])
                scenes=[SceneMemory(**x) for x in body.get("scenes",[])]
                result=CREATIVE_ORCHESTRATOR.produce(project_id=body["project_id"], brief=body["brief"], characters=chars, world=world, scenes=scenes, provider=body.get("provider","wetu-local"), kind=body.get("kind","image"), production_memory=body.get("production_memory",{}), default_mood=body.get("default_mood","natural"), true_story=body.get("true_story"), references=body.get("references",[]), options=body.get("options",{}))
                self._send(200, {"ok":True,"production":_jsonable(result)}); return
            if path == "/api/media-generate":
                request = MediaRequest(request_id=body["request_id"], project_id=body.get("project_id",STATE.project_id), scene_id=body.get("scene_id"), kind=body["kind"], prompt=body["prompt"], provider=body.get("provider","wetu-local"), references=body.get("references",[]), options=body.get("options",{}))
                asset = MEDIA.generate(request, body.get("context", {}))
                self._send(200, {"ok":True,"asset":_jsonable(asset),"real_media":asset.metadata.get("real_media",False)}); return
            if path == "/api/creative-plan":
                from .models.production import CharacterDNA, SceneMemory, WorldDNA
                characters=[CharacterDNA(**x) for x in body.get("characters",[])]
                world=WorldDNA(**body["world"])
                scenes=[SceneMemory(**x) for x in body.get("scenes",[])]
                plan=CREATIVE_ORCHESTRATOR.plan(project_id=body["project_id"],brief=body["brief"],characters=characters,world=world,scenes=scenes,production_memory=body.get("production_memory",{}),default_mood=body.get("default_mood","natural"))
                self._send(200, {"ok":True,"plan":plan}); return
            if path == "/api/production-realism":
                scene_id=body["scene_id"]; scene=STATE.scenes.get(scene_id)
                if scene is None: raise ValueError(f"unknown scene: {scene_id}")
                characters=[STATE.characters[cid] for cid in scene.character_ids if cid in STATE.characters]
                world=STATE.worlds.get(scene.world_id) if scene.world_id else None
                context=PRODUCTION_REALISM.build(scene_id=scene_id,scene=scene,characters=characters,world=world,production_context=CORE.build_context(scene_id),mood=body.get("mood","natural"),emotional_beats=body.get("emotional_beats",body.get("beats",[])),atmosphere=body.get("atmosphere",{}),sensory_focus=body.get("sensory_focus",[]),camera_guidance=body.get("camera_guidance",[]),true_story=body.get("true_story"))
                issues=PRODUCTION_REALISM.validate(context)
                self._send(200, {"ok":not issues,"issues":issues,"context":context}); return
            if path == "/api/true-story-realism":
                scene=TRUE_STORY_REALISM.build(scene_id=body["scene_id"],event=body["event"],mode=TrueStoryMode(body.get("mode","documentary_realism")),facts=body.get("facts",[]),emotional_context=body.get("emotional_context",{}),environmental_context=body.get("environmental_context",{}),dialogue=body.get("dialogue",[]),internal_thoughts=body.get("internal_thoughts",[]),victim_survivor_handling=body.get("victim_survivor_handling",{}),cinematic_direction=body.get("cinematic_direction",{}))
                issues=TRUE_STORY_REALISM.validate(scene)
                self._send(200, {"ok":not issues,"issues":issues,"scene":TRUE_STORY_REALISM.to_dict(scene)}); return
            if path == "/api/mature/access":
                request=MatureRequest(MatureAccess(body.get("access","unverified")),bool(body.get("all_characters_adult",False)),bool(body.get("consent_confirmed",False)),bool(body.get("real_person",False)),bool(body.get("explicit",False)),bool(body.get("ambiguous_age",False)))
                decision=MATURE_POLICY.evaluate(request); self._send(200, decision_json(decision)); return
            if path == "/api/scriptural-catalog":
                if body.get("story_id"): self._send(200, story_manifest(body["story_id"]))
                else: self._send(200, catalog_summary())
                return
            if path == "/api/scriptural-universe":
                global SCRIPTURAL
                source=ScripturalSource(body["source_id"],body["source_title"],SourceClass(body["source_class"]),body.get("tradition",""),body.get("source_notes",""))
                SCRIPTURAL=ScripturalUniverse(body["universe_id"],body["title"],source,FidelityMode(body.get("fidelity","source_faithful")),body.get("era",""),body.get("region",""),body.get("languages",[]),body.get("provenance",[]),body.get("canon_status",""),body.get("details",{}))
                issues=SCRIPTURAL.validate()
                _save_runtime(STATE.project_id)
                self._send(200 if not issues else 400, {"ok":not issues,"issues":issues,"universe":_jsonable(SCRIPTURAL)}); return
            if path == "/api/scriptural-qa":
                if SCRIPTURAL is None: raise ValueError("Scriptural universe is not configured")
                report=SCRIPTURAL_QA.evaluate(universe=SCRIPTURAL,scene_context=body)
                self._send(200,_jsonable(report)); return
            if path == "/api/fan-film/start":
                global FAN_PIPELINE
                if UNIVERSE.mode is not UniverseMode.FAN_FILM:
                    self._send(400, {"error":"Select FAN_FILM mode first"}); return
                FAN_PIPELINE=FanFilmPipeline(UNIVERSE); FAN_PIPELINE.start(); _save_runtime(STATE.project_id)
                self._send(200, {"ok":True,"pipeline":_jsonable(FAN_PIPELINE)}); return
            if path == "/api/fan-film/scene":
                if FAN_PIPELINE is None: raise ValueError("Fan-film pipeline is not started")
                FAN_PIPELINE.add_scene(body["scene_id"],body.get("title",body["scene_id"]),int(body["duration_ms"]),body.get("character_ids",[])); _save_runtime(STATE.project_id)
                self._send(201, {"ok":True,"pipeline":_jsonable(FAN_PIPELINE)}); return
            if path == "/api/fan-film/animation":
                if FAN_PIPELINE is None: raise ValueError("Fan-film pipeline is not started")
                FAN_PIPELINE.add_animation_request(body); _save_runtime(STATE.project_id); self._send(201, {"ok":True,"pipeline":_jsonable(FAN_PIPELINE)}); return
            if path == "/api/fan-film/audio":
                if FAN_PIPELINE is None: raise ValueError("Fan-film pipeline is not started")
                FAN_PIPELINE.add_audio_request(body); _save_runtime(STATE.project_id); self._send(201, {"ok":True,"pipeline":_jsonable(FAN_PIPELINE)}); return
            if path == "/api/fan-film/timeline":
                if FAN_PIPELINE is None: raise ValueError("Fan-film pipeline is not started")
                FAN_PIPELINE.add_timeline_item(body); _save_runtime(STATE.project_id); self._send(201, {"ok":True,"pipeline":_jsonable(FAN_PIPELINE)}); return
            if path == "/api/fan-film/qa":
                if FAN_PIPELINE is None: raise ValueError("Fan-film pipeline is not started")
                FAN_PIPELINE.add_qa(body); _save_runtime(STATE.project_id); self._send(201, {"ok":True,"pipeline":_jsonable(FAN_PIPELINE)}); return
            if path == "/api/fan-film/export":
                if FAN_PIPELINE is None: raise ValueError("Fan-film pipeline is not started")
                self._send(200,FAN_PIPELINE.export_manifest()); return
            if path == "/api/animation":
                style=AnimationStyle(**body["style"])
                request=AnimationRequest(body["request_id"],body.get("project_id",STATE.project_id),body["scene_id"],style,body["prompt"],body.get("references",[]),body.get("options",{}))
                self._send(200,ANIMATION.build_request(request)); return
            if path == "/api/characters":
                payload = dict(body)
                payload.pop("project_id", None)
                with _STATE_LOCK:
                    CORE.add_character(CharacterDNA(**payload)); _persist_state(STATE)
                self._send(201,{"ok":True}); return
            if path == "/api/worlds":
                payload = dict(body)
                payload.pop("project_id", None)
                with _STATE_LOCK:
                    CORE.add_world(WorldDNA(**payload)); _persist_state(STATE)
                self._send(201,{"ok":True}); return
            if path == "/api/scenes":
                with _STATE_LOCK:
                    CORE.add_scene(SceneMemory(**body)); _persist_state(STATE)
                self._send(201,{"ok":True}); return
            if path == "/api/generate":
                with _STATE_LOCK:
                    result=CORE.generate(**body); _persist_state(STATE)
                self._send(200,_jsonable(result)); return
            self._send(404, {"error":"not found"})
        except (ValueError,TypeError,KeyError,json.JSONDecodeError) as exc:
            self._send(400, {"error":str(exc)})
        except Exception as exc:
            # Keep the HTTP connection alive on unexpected application errors so
            # integration tests and clients receive a diagnosable response.
            print(f"WETU Creator POST error on {path}: {exc!r}", flush=True)
            self._send(500, {"error": "internal server error", "detail": str(exc)})

def serve(host="127.0.0.1", port=8787):
    print(f"WETU Creator: http://{host}:{port}")
    ThreadingHTTPServer((host,port),Handler).serve_forever()

if __name__ == "__main__":
    serve()
