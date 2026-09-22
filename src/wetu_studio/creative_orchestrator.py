"""High-level creative-to-media production orchestrator for WETU Studio AI."""
from __future__ import annotations
from dataclasses import asdict
from typing import Any
from .models.production import CharacterDNA, SceneMemory, WorldDNA
from .production_realism import ProductionRealismOrchestrator
from .media_engine import MediaRegistry, MediaRequest
from .provider_registry import ProviderSelector
from .asset_store import AssetStore
from .reference_store import ReferenceStore
from .reference_store import ReferenceStore

class WetuCreativeOrchestrator:
    def __init__(self, realism=None, media=None, assets=None, references=None):
        self.realism = realism or ProductionRealismOrchestrator()
        self.media = media
        self.selector = ProviderSelector(media) if media else None
        self.assets = assets or AssetStore()
        self.references = references or ReferenceStore()

    def plan(self, *, project_id, brief, characters, world, scenes,
              production_memory=None, default_mood="natural", true_story=None):
        if not project_id.strip(): raise ValueError("project_id is required")
        if not brief.strip(): raise ValueError("brief is required")
        if not characters: raise ValueError("at least one character is required")
        if not scenes: raise ValueError("at least one scene is required")
        planned=[]
        for scene in scenes:
            context=self.realism.build(
                scene_id=scene.scene_id, scene=scene,
                characters=[c for c in characters if c.character_id in scene.character_ids] or characters,
                world=world, production_context=production_memory or {},
                mood=default_mood,
                atmosphere={"lighting":{"source":"scene-defined"},
                            "environment_sounds":["context-dependent ambient sound"]},
                sensory_focus=["character behavior","environment","materials"],
                camera_guidance=["physically coherent camera movement"],
                true_story=true_story.get(scene.scene_id) if true_story else None)
            issues=self.realism.validate(context)
            planned.append({"scene_id":scene.scene_id,"sequence":scene.sequence,
                            "status":"ready" if not issues else "needs_review",
                            "issues":issues,"context":context})
        return {"project_id":project_id,"brief":brief,"world":asdict(world),
                "characters":[asdict(c) for c in characters],"scenes":planned,
                "rendering":{"provider_neutral":True,"requires_real_provider":True,
                             "do_not_reset_production_memory":True}}

    def produce(self, *, project_id, brief, characters, world, scenes,
                provider, kind="image", production_memory=None,
                default_mood="natural", true_story=None, references=None,
                options=None):
        if self.media is None:
            raise ValueError("media registry is required for production")
        self.selector.require(provider, kind)
        plan=self.plan(project_id=project_id, brief=brief, characters=characters,
                       world=world, scenes=scenes, production_memory=production_memory,
                       default_mood=default_mood, true_story=true_story)
        assets=[]
        for item in plan["scenes"]:
            if item["status"] != "ready":
                assets.append({"scene_id":item["scene_id"],"status":"blocked",
                                "issues":item["issues"]})
                continue
            rid=f"{project_id}:{item['scene_id']}:{kind}"
            prompt=f"{brief}\nScene {item['sequence']}: {item['scene_id']}"
            auto_refs=self.references.uris_for_scene(project_id, scene_id=item["scene_id"])
            req=MediaRequest(rid, project_id, item["scene_id"], kind, prompt,
                              provider, list(dict.fromkeys((references or []) + auto_refs)), options or {})
            asset=self.media.generate(req, item["context"])
            record=self.assets.remember(asset)
            self.references.remember_asset(record, continuity_key=f"scene:{item['scene_id']}")
            assets.append({"scene_id":item["scene_id"],"status":"generated",
                           "asset":asdict(asset),"asset_record":asdict(record)})
        return {"project_id":project_id,"brief":brief,"plan":plan,"assets":assets,
                "provider_profiles":[asdict(p) for p in self.selector.profiles()],
                "pipeline":{"planned":True,"qa_before_generation":True,
                            "memory_preserved":True,"visual_references_persisted":True}}

    def render_scene(self, *, project_id, scene, context, provider,
                     kind="image", prompt="", references=None, options=None):
        if self.media is None: raise ValueError("media registry is required for production")
        req=MediaRequest(f"{project_id}:{scene.scene_id}:{kind}", project_id,
                         scene.scene_id, kind, prompt or scene.scene_id, provider,
                         references or [], options or {})
        return self.media.generate(req, context)
