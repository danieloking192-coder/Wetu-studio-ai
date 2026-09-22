"""Unified scene orchestration for WETU production realism."""
from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List

from .emotion_atmosphere import EmotionAtmosphereEngine
from .true_story_realism import TrueStoryRealismEngine, TrueStoryMode


class ProductionRealismOrchestrator:
    """Single integration boundary between narrative intent and rendering."""

    def __init__(self, *, emotion=None, true_story=None) -> None:
        self.emotion = emotion or EmotionAtmosphereEngine()
        self.true_story = true_story or TrueStoryRealismEngine()

    def build(
        self, *, scene_id: str, scene: Any, characters: List[Any],
        world: Any | None, production_context: Dict[str, Any],
        mood: str = "natural", emotional_beats: List[Dict[str, Any]] | None = None,
        atmosphere: Dict[str, Any] | None = None, sensory_focus: List[str] | None = None,
        camera_guidance: List[str] | None = None, true_story: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        emotion_scene = self.emotion.build(
            scene_id=scene_id, mood=mood, beats=emotional_beats or [],
            atmosphere=atmosphere or {}, sensory_focus=sensory_focus or [],
            camera_guidance=camera_guidance or [],
            continuity_notes=list(getattr(scene, "continuity_notes", []) or []),
        )

        ts = None
        if true_story:
            ts = self.true_story.build(
                scene_id=scene_id, event=str(true_story.get("event", "")),
                mode=TrueStoryMode(true_story.get("mode", "documentary_realism")),
                facts=true_story.get("facts", []),
                emotional_context=true_story.get("emotional_context", {}),
                environmental_context=true_story.get("environmental_context", {}),
                dialogue=true_story.get("dialogue", []),
                internal_thoughts=true_story.get("internal_thoughts", []),
                victim_survivor_handling=true_story.get("victim_survivor_handling", {}),
                cinematic_direction=true_story.get("cinematic_direction", {}),
            )

        context = {
            "scene": asdict(scene),
            "characters": [asdict(c) for c in characters],
            "world": asdict(world) if world is not None else None,
            "production_memory": production_context,
            "continuity": {
                **{c.character_id: [f"character:{c.character_id}"] for c in characters},
                **({f"world:{world.world_id}": [f"world:{world.world_id}"]} if world is not None else {}),
            },
            "emotion_atmosphere": self.emotion.to_dict(emotion_scene),
            "emotion_continuity": self.emotion.continuity_snapshot(emotion_scene),
            "true_story": self.true_story.to_dict(ts) if ts else None,
            "contract": {
                "character_identity": "preserve_character_dna",
                "world_identity": "preserve_world_dna",
                "scene_continuity": "preserve_scene_memory",
                "emotion": "preserve_cause_behavior_and_continuity",
                "true_story": "preserve_provenance_and_disclosure",
                "rendering": "provider_neutral",
            },
        }
        return context

    def validate(self, context: Dict[str, Any]) -> List[str]:
        issues=[]
        scene=context.get("scene", {})
        if not scene.get("scene_id") or not scene.get("project_id"):
            issues.append("scene_identity_missing")
        if not context.get("characters"):
            issues.append("character_dna_missing")

        emotion_raw=context.get("emotion_atmosphere")
        if emotion_raw:
            emotion_scene=self.emotion.build(
                scene_id=emotion_raw["scene_id"], mood=emotion_raw["mood"],
                beats=emotion_raw.get("emotional_beats", []),
                atmosphere=emotion_raw.get("atmosphere", {}),
                sensory_focus=emotion_raw.get("sensory_focus", []),
                camera_guidance=emotion_raw.get("camera_guidance", []),
                continuity_notes=emotion_raw.get("continuity_notes", []),
                source_vs_interpretation=emotion_raw.get("source_vs_interpretation","artistic_direction"))
            issues.extend(f"emotion:{x}" for x in self.emotion.validate(emotion_scene))

        ts_raw=context.get("true_story")
        if ts_raw:
            rebuilt=self.true_story.build(
                scene_id=ts_raw["scene_id"], event=ts_raw["event"],
                mode=TrueStoryMode(ts_raw["mode"]),
                facts=ts_raw.get("factual_context", []),
                emotional_context=ts_raw.get("emotional_context", {}),
                environmental_context=ts_raw.get("environmental_context", {}),
                dialogue=ts_raw.get("dialogue", []),
                internal_thoughts=ts_raw.get("internal_thoughts", []),
                victim_survivor_handling=ts_raw.get("victim_survivor_handling", {}),
                cinematic_direction=ts_raw.get("cinematic_direction", {}))
            issues.extend(f"true_story:{x}" for x in self.true_story.validate(rebuilt))

        if context.get("world") is None:
            issues.append("world_dna_missing")
        if not context.get("continuity"):
            issues.append("continuity_contract_missing")
        return issues
