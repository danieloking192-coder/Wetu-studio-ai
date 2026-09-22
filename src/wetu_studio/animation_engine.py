"""Animation production layer for WETU Studio AI."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass(frozen=True)
class AnimationStyle:
    style_id: str
    medium: str
    visual_language: str
    camera_language: str = ""
    motion_language: str = ""
    lighting_language: str = ""
    notes: dict[str, Any] = field(default_factory=dict)

@dataclass
class AnimationRequest:
    request_id: str
    project_id: str
    scene_id: str
    style: AnimationStyle
    prompt: str
    references: list[str] = field(default_factory=list)
    options: dict[str, Any] = field(default_factory=dict)

class AnimationEngine:
    SUPPORTED_MEDIA = {"2d", "3d", "anime", "toon", "stop_motion", "hybrid"}
    def validate_style(self, style: AnimationStyle) -> None:
        if style.medium not in self.SUPPORTED_MEDIA:
            raise ValueError("unsupported animation medium")
        if not style.style_id.strip() or not style.visual_language.strip():
            raise ValueError("style_id and visual_language are required")

    def build_request(self, request: AnimationRequest) -> dict[str, Any]:
        self.validate_style(request.style)
        if not request.prompt.strip():
            raise ValueError("prompt is required")
        return {
            "request_id": request.request_id,
            "project_id": request.project_id,
            "scene_id": request.scene_id,
            "media": "animation",
            "style": {
                "id": request.style.style_id,
                "medium": request.style.medium,
                "visual_language": request.style.visual_language,
                "camera_language": request.style.camera_language,
                "motion_language": request.style.motion_language,
                "lighting_language": request.style.lighting_language,
                "notes": dict(request.style.notes),
            },
            "prompt": request.prompt,
            "references": list(request.references),
            "options": dict(request.options),
        }
