"""Creator Application Core orchestration boundary for WETU Studio AI."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Protocol
from .models.production import CharacterDNA, GenerationRecord, ProductionMemory, SceneMemory, WorldDNA

class ProviderAdapter(Protocol):
    name: str
    def generate(self, *, kind: str, prompt: str, context: dict[str, Any]) -> dict[str, Any]: ...

class QAEngine(Protocol):
    def evaluate(self, *, kind: str, context: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]: ...

class ContinuityGuard(Protocol):
    def check(self, *, scene: SceneMemory, context: dict[str, Any]) -> dict[str, Any]: ...

@dataclass
class CreatorState:
    project_id: str
    characters: dict[str, CharacterDNA] = field(default_factory=dict)
    worlds: dict[str, WorldDNA] = field(default_factory=dict)
    scenes: dict[str, SceneMemory] = field(default_factory=dict)
    memory: ProductionMemory = field(default_factory=ProductionMemory)

class CreatorApplicationCore:
    """Single application-facing API for the WETU creator workflow."""

    def __init__(self, state: CreatorState, *, providers=None, qa=None, continuity=None):
        self.state = state
        self.providers = providers or {}
        self.qa = qa
        self.continuity = continuity

    def add_character(self, character: CharacterDNA) -> None:
        self._same_project()
        self.state.characters[character.character_id] = character
        self.state.memory.remember("character_updated", {"character_id": character.character_id})

    def add_world(self, world: WorldDNA) -> None:
        self._same_project()
        self.state.worlds[world.world_id] = world
        self.state.memory.remember("world_updated", {"world_id": world.world_id})

    def add_scene(self, scene: SceneMemory) -> None:
        self._same_project()
        if scene.project_id != self.state.project_id:
            raise ValueError("scene belongs to another project")
        if scene.scene_id in self.state.scenes:
            raise ValueError(f"scene already exists: {scene.scene_id}")
        self.state.scenes[scene.scene_id] = scene
        self.state.memory.remember("scene_created", {"scene_id": scene.scene_id})

    def build_context(self, scene_id: str) -> dict[str, Any]:
        scene = self._scene(scene_id)
        context = self.state.memory.context_for(scene)
        context["characters"] = [
            self.state.characters[cid] for cid in scene.character_ids
            if cid in self.state.characters
        ]
        if scene.world_id and scene.world_id in self.state.worlds:
            context["world"] = self.state.worlds[scene.world_id]
        context["scene_state"] = scene.state
        return context

    def generate(self, *, scene_id: str, provider: str, kind: str,
                 prompt: str, generation_id: str) -> dict[str, Any]:
        context = self.build_context(scene_id)
        scene = self._scene(scene_id)

        if self.continuity:
            preflight = self.continuity.check(scene=scene, context=context)
            if not preflight.get("passed", False):
                return {"status": "blocked", "stage": "continuity_preflight", "qa": preflight}

        adapter = self.providers.get(provider)
        if adapter is None:
            raise ValueError(f"unknown provider: {provider}")

        result = adapter.generate(kind=kind, prompt=prompt, context=context)
        qa_result = (
            self.qa.evaluate(kind=kind, context=context, result=result)
            if self.qa else {"passed": True, "checks": []}
        )

        record = GenerationRecord(
            generation_id=generation_id,
            project_id=self.state.project_id,
            scene_id=scene_id,
            provider=provider,
            model=str(result.get("model", "unknown")),
            kind=kind,
            prompt=prompt,
            status="qa_passed" if qa_result.get("passed") else "qa_failed",
            metadata={"provider_result": result, "qa": qa_result},
        )
        self.state.memory.add_generation(record)
        return {"status": record.status, "generation": record, "qa": qa_result}

    def _scene(self, scene_id: str) -> SceneMemory:
        try:
            return self.state.scenes[scene_id]
        except KeyError as exc:
            raise ValueError(f"unknown scene: {scene_id}") from exc

    def _same_project(self) -> None:
        if not self.state.project_id.strip():
            raise ValueError("project_id is required")
