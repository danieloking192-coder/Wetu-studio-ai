"""High-level creative orchestrator for WETU Studio AI.

Turns a creator brief into a deterministic production plan while preserving
persistent identity, world context, scene memory, emotion, realism and QA.
Rendering remains provider-neutral.
"""
from __future__ import annotations
from dataclasses import asdict
from typing import Any

from .models.production import CharacterDNA, SceneMemory, WorldDNA
from .production_realism import ProductionRealismOrchestrator


class WetuCreativeOrchestrator:
    def __init__(self, realism: ProductionRealismOrchestrator | None = None):
        self.realism = realism or ProductionRealismOrchestrator()

    def plan(
        self,
        *,
        project_id: str,
        brief: str,
        characters: list[CharacterDNA],
        world: WorldDNA,
        scenes: list[SceneMemory],
        production_memory: dict[str, Any] | None = None,
        default_mood: str = "natural",
    ) -> dict[str, Any]:
        if not project_id.strip():
            raise ValueError("project_id is required")
        if not brief.strip():
            raise ValueError("brief is required")
        if not characters:
            raise ValueError("at least one character is required")
        if not scenes:
            raise ValueError("at least one scene is required")

        planned = []
        for scene in scenes:
            context = self.realism.build(
                scene_id=scene.scene_id,
                scene=scene,
                characters=[
                    c for c in characters if c.character_id in scene.character_ids
                ] or characters,
                world=world,
                production_context=production_memory or {},
                mood=default_mood,
                atmosphere={
                    "lighting": {"source": "scene-defined"},
                    "environment_sounds": ["context-dependent ambient sound"],
                },
                sensory_focus=["character behavior", "environment", "materials"],
                camera_guidance=["physically coherent camera movement"],
            )
            issues = self.realism.validate(context)
            planned.append({
                "scene_id": scene.scene_id,
                "sequence": scene.sequence,
                "status": "ready" if not issues else "needs_review",
                "issues": issues,
                "context": context,
            })

        return {
            "project_id": project_id,
            "brief": brief,
            "world": asdict(world),
            "characters": [asdict(c) for c in characters],
            "scenes": planned,
            "rendering": {
                "provider_neutral": True,
                "requires_real_provider": True,
                "do_not_reset_production_memory": True,
            },
        }
