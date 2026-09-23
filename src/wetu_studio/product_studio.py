"""Product studio templates for WETU: advertising, film and series."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any

@dataclass(frozen=True)
class StudioTemplate:
    studio_id: str
    name: str
    default_duration_seconds: int
    required_stages: tuple[str, ...]
    delivery_profiles: tuple[str, ...]

TEMPLATES = {
    "advertising": StudioTemplate("advertising", "Advertising Studio", 30, ("brief","script","storyboard","generation","postproduction","export"), ("mobile_saver","mobile","standard")),
    "film": StudioTemplate("film", "Film Studio", 300, ("concept","script","characters","world","storyboard","generation","continuity","postproduction","export"), ("mobile","standard")),
    "series": StudioTemplate("series", "Series Studio", 180, ("bible","episode","characters","world","storyboard","generation","continuity","postproduction","export"), ("mobile","standard")),
}

class ProductStudio:
    def templates(self) -> list[dict[str, Any]]:
        return [asdict(x) for x in TEMPLATES.values()]

    def plan(self, studio_id: str, title: str, brief: str) -> dict[str, Any]:
        template = TEMPLATES.get(studio_id)
        if template is None:
            raise ValueError(f"unknown studio: {studio_id}")
        return {"studio": asdict(template), "project": {"title": title, "brief": brief}, "ready_for": list(template.required_stages)}
