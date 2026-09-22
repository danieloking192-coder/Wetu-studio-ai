"""End-to-end orchestration for a WETU fan-film short.

This creates a production plan and traceable pipeline state. Rendering remains
provider-dependent; the orchestrator never pretends a manifest is a rendered
video.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass
class FanFilmPipeline:
    production: Any
    stages: list[str] = field(default_factory=list)
    scenes: list[dict[str, Any]] = field(default_factory=list)
    animation_requests: list[dict[str, Any]] = field(default_factory=list)
    audio_requests: list[dict[str, Any]] = field(default_factory=list)
    timeline_items: list[dict[str, Any]] = field(default_factory=list)
    qa_reports: list[dict[str, Any]] = field(default_factory=list)

    def start(self) -> None:
        if self.production.mode.value != "fan_film":
            raise ValueError("FanFilmPipeline requires FAN_FILM mode.")
        self._stage("project")

    def add_scene(self, scene_id: str, title: str, duration_ms: int, character_ids: list[str]) -> dict:
        if not scene_id or duration_ms <= 0:
            raise ValueError("scene_id and positive duration_ms are required")
        scene = {"scene_id": scene_id, "title": title, "duration_ms": duration_ms,
                 "character_ids": list(character_ids)}
        self.scenes.append(scene)
        self._stage("scene")
        return scene

    def add_animation_request(self, request: dict) -> None:
        self.animation_requests.append(request)
        self._stage("animation")

    def add_audio_request(self, request: dict) -> None:
        self.audio_requests.append(request)
        self._stage("audio")

    def add_timeline_item(self, item: dict) -> None:
        self.timeline_items.append(item)
        self._stage("timeline")

    def add_qa(self, report: dict) -> None:
        self.qa_reports.append(report)
        self._stage("qa")

    def export_manifest(self) -> dict:
        if not self.scenes:
            raise ValueError("At least one scene is required before export")
        self._stage("export")
        return {
            "pipeline_version": "1.0",
            "production_id": self.production.production_id,
            "mode": self.production.mode.value,
            "source_references": [r.__dict__ for r in self.production.character_references],
            "stages": list(dict.fromkeys(self.stages)),
            "scenes": self.scenes,
            "animation_requests": self.animation_requests,
            "audio_requests": self.audio_requests,
            "timeline": self.timeline_items,
            "qa": self.qa_reports,
            "render_status": "provider_required",
        }

    def _stage(self, name: str) -> None:
        if name not in self.stages:
            self.stages.append(name)
