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
                                           "scriptural": _jsonable(SCRIPTURAL),
                                           "mature": {"mode": "MATURE_18_PLUS", "policy_version": "1.0"},
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
                scene = EMOTION_ATMOSPHERE.build(
                    scene_id=body["scene_id"],
                    mood=body.get("mood", "natural"),
                    beats=body.get("emotional_beats", body.get("beats", [])),
                    atmosphere=body.get("atmosphere", {}),
                    sensory_focus=body.get("sensory_focus", []),
                    camera_guidance=body.get("camera_guidance", []),
                    continuity_notes=body.get("continuity_notes", []),
                    source_vs_interpretation=body.get("source_vs_interpretation", "artistic_direction"),
                )
                issues = EMOTION_ATMOSPHERE.validate(scene)
                self._send(200, {"ok": not issues, "issues": issues, "scene": EMOTION_ATMOSPHERE.to_dict(scene), "continuity_snapshot": EMOTION_ATMOSPHERE.continuity_snapshot(scene)})
                return
            if path == "/api/providers":
                self._send(200, {"providers":[_jsonable(x) for x in CREATIVE_ORCHESTRATOR.selector.profiles()]})
                return
            if path == "/api/produce":
                from .models.production import CharacterDNA, SceneMemory, WorldDNA
                chars=[CharacterDNA(**x) for x in body.get("characters",[])]
                world=WorldDNA(**body["world"])
                scenes=[SceneMemory(**x) for x in body.get("scenes",[])]
                result=CREATIVE_ORCHESTRATOR.produce(
                    project_id=body["project_id"], brief=body["brief"],
                    characters=chars, world=world, scenes=scenes,
                    provider=body.get("provider","wetu-local"),
                    kind=body.get("kind","image"),
                    production_memory=body.get("production_memory",{}),
                    default_mood=body.get("default_mood","natural"),
                    true_story=body.get("true_story"),
                    references=body.get("references",[]),
                    options=body.get("options",{}),
                )
                self._send(200, {"ok":True,"production":_jsonable(result)})
                return
            if path == "/api/media-generate":
                request = MediaRequest(
                    request_id=body["request_id"],
                    project_id=body.get("project_id", STATE.project_id),
                    scene_id=body.get("scene_id"),
                    kind=body["kind"],
                    prompt=body["prompt"],
                    provider=body.get("provider", "wetu-local"),
                    references=body.get("references", []),
                    options=body.get("options", {}),
                )
                asset = MEDIA.generate(request, body.get("context", {}))
                self._send(200, {"ok": True, "asset": _jsonable(asset),
                                 "real_media": asset.metadata.get("real_media", False)})
                return
            if path == "/api/creative-plan":
                from .models.production import CharacterDNA, SceneMemory, WorldDNA
                characters = [CharacterDNA(**x) for x in body.get("characters", [])]
                world = WorldDNA(**body["world"])
                scenes = [SceneMemory(**x) for x in body.get("scenes", [])]
                plan = CREATIVE_ORCHESTRATOR.plan(
                    project_id=body["project_id"],
                    brief=body["brief"],
                    characters=characters,
                    world=world,
                    scenes=scenes,
                    production_memory=body.get("production_memory", {}),
                    default_mood=body.get("default_mood", "natural"),
                )
                self._send(200, {"ok": True, "plan": plan})
                return
            if path == "/api/production-realism":
                scene_id = body["scene_id"]
                scene = STATE.scenes.get(scene_id)
                if scene is None:
                    raise ValueError(f"unknown scene: {scene_id}")
                characters = [
                    STATE.characters[cid]
                    for cid in scene.character_ids
                    if cid in STATE.characters
                ]
                world = STATE.worlds.get(scene.world_id) if scene.world_id else None
                context = PRODUCTION_REALISM.build(
                    scene_id=scene_id,
                    scene=scene,
                    characters=characters,
                    world=world,
                    production_context=CORE.build_context(scene_id),
                    mood=body.get("mood", "natural"),
                    emotional_beats=body.get("emotional_beats", body.get("beats", [])),
                    atmosphere=body.get("atmosphere", {}),
                    sensory_focus=body.get("sensory_focus", []),
                    camera_guidance=body.get("camera_guidance", []),
                    true_story=body.get("true_story"),
                )
                issues = PRODUCTION_REALISM.validate(context)
                self._send(200, {"ok": not issues, "issues": issues, "context": context})
                return
            if path == "/api/true-story-realism":
                scene = TRUE_STORY_REALISM.build(
                    scene_id=body["scene_id"],
                    event=body["event"],
                    mode=TrueStoryMode(body.get("mode", "documentary_realism")),
                    facts=body.get("facts", []),
                    emotional_context=body.get("emotional_context", {}),
                    environmental_context=body.get("environmental_context", {}),
                    dialogue=body.get("dialogue", []),
                    internal_thoughts=body.get("internal_thoughts", []),
                    victim_survivor_handling=body.get("victim_survivor_handling", {}),
                    cinematic_direction=body.get("cinematic_direction", {}),
                )
                issues = TRUE_STORY_REALISM.validate(scene)
                self._send(200, {"ok": not issues, "issues": issues, "scene": TRUE_STORY_REALISM.to_dict(scene)})
                return
            if path == "/api/mature/access":
                request=MatureRequest(MatureAccess(body.get("access","unverified")), bool(body.get("all_characters_adult",False)), bool(body.get("consent_confirmed",False)), bool(body.get("real_person",False)), bool(body.get("explicit",False)), bool(body.get("ambiguous_age",False)))
                decision=MATURE_POLICY.evaluate(request)
                self._send(200, decision_json(decision)); return
            if path == "/api/scriptural-catalog":
                if body.get("story_id"):
                    self._send(200, story_manifest(body["story_id"]))
                else:
                    self._send(200, catalog_summary())
                return
            if path == "/api/scriptural-universe":
                global SCRIPTURAL
                source=ScripturalSource(body["source_id"], body["source_title"], SourceClass(body["source_class"]), body.get("tradition",""), body.get("source_notes",""))
                SCRIPTURAL=ScripturalUniverse(body["universe_id"], body["title"], source, FidelityMode(body.get("fidelity","source_faithful")), body.get("era",""), body.get("region",""), body.get("languages",[]), body.get("provenance",[]), body.get("canon_status",""), body.get("details",{}))
                issues=SCRIPTURAL.validate()
                self._send(200 if not issues else 400, {"ok": not issues, "issues": issues, "universe": _jsonable(SCRIPTURAL)}); return
            if path == "/api/scriptural-qa":
                if SCRIPTURAL is None: raise ValueError("Scriptural universe is not configured")
                report=SCRIPTURAL_QA.evaluate(universe=SCRIPTURAL, scene_context=body)
                self._send(200, _jsonable(report)); return
            if path == "/api/fan-film/start":
                global FAN_PIPELINE
                if UNIVERSE.mode is not UniverseMode.FAN_FILM:
                    self._send(400, {"error": "Select FAN_FILM mode first"}); return
                FAN_PIPELINE = FanFilmPipeline(UNIVERSE); FAN_PIPELINE.start()
                self._send(200, {"ok": True, "pipeline": _jsonable(FAN_PIPELINE)}); return
            if path == "/api/fan-film/scene":
                if FAN_PIPELINE is None: raise ValueError("Fan-film pipeline is not started")
                FAN_PIPELINE.add_scene(body["scene_id"], body.get("title", body["scene_id"]), int(body["duration_ms"]), body.get("character_ids", []))
                self._send(201, {"ok": True, "pipeline": _jsonable(FAN_PIPELINE)}); return
            if path == "/api/fan-film/animation":
                if FAN_PIPELINE is None: raise ValueError("Fan-film pipeline is not started")
                FAN_PIPELINE.add_animation_request(body)
                self._send(201, {"ok": True, "pipeline": _jsonable(FAN_PIPELINE)}); return
            if path == "/api/fan-film/audio":
                if FAN_PIPELINE is None: raise ValueError("Fan-film pipeline is not started")
                FAN_PIPELINE.add_audio_request(body)
                self._send(201, {"ok": True, "pipeline": _jsonable(FAN_PIPELINE)}); return
            if path == "/api/fan-film/timeline":
                if FAN_PIPELINE is None: raise ValueError("Fan-film pipeline is not started")
                FAN_PIPELINE.add_timeline_item(body)
                self._send(201, {"ok": True, "pipeline": _jsonable(FAN_PIPELINE)}); return
            if path == "/api/fan-film/qa":
                if FAN_PIPELINE is None: raise ValueError("Fan-film pipeline is not started")
                FAN_PIPELINE.add_qa(body)
                self._send(201, {"ok": True, "pipeline": _jsonable(FAN_PIPELINE)}); return
            if path == "/api/fan-film/export":
                if FAN_PIPELINE is None: raise ValueError("Fan-film pipeline is not started")
                self._send(200, FAN_PIPELINE.export_manifest()); return
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
