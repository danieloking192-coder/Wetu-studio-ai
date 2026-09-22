"""Buildable production plan from a WETU scriptural catalog entry."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from .scriptural_catalog import NarrativeEntry, get_story
from .scriptural_universe import FidelityMode, ScripturalSource, ScripturalUniverse, ScripturalRealismQA

@dataclass
class ScripturalProduction:
    story: NarrativeEntry
    universe: ScripturalUniverse
    scenes: list[dict[str, Any]] = field(default_factory=list)
    qa: dict[str, Any] | None = None

    def build(self) -> dict[str, Any]:
        self.scenes = [
            {"scene_id": f"{self.story.story_id}-setup", "role": "setup",
             "characters": list(self.story.characters), "places": list(self.story.places),
             "source_references": list(self.story.references)},
            {"scene_id": f"{self.story.story_id}-main", "role": "main_event",
             "characters": list(self.story.characters), "places": list(self.story.places),
             "source_references": list(self.story.references)},
            {"scene_id": f"{self.story.story_id}-resolution", "role": "resolution",
             "characters": list(self.story.characters), "places": list(self.story.places),
             "source_references": list(self.story.references)},
        ]
        report=ScripturalRealismQA().evaluate(
            universe=self.universe,
            scene_context={"source_passage": ", ".join(self.story.references)}
        )
        self.qa={"passed": report.passed, "checks": report.checks, "issues": report.issues}
        return {
            "story": self.story.story_id,
            "title": self.story.title,
            "source": self.story.source_id,
            "source_class": self.story.source_class.value,
            "fidelity": self.universe.fidelity.value,
            "era": self.story.era,
            "characters": list(self.story.characters),
            "places": list(self.story.places),
            "themes": list(self.story.themes),
            "scenes": self.scenes,
            "qa": self.qa,
            "render_status": "provider_required",
        }

def build_scriptural_production(story_id: str, fidelity: FidelityMode = FidelityMode.HISTORICAL_CINEMATIC) -> dict[str, Any]:
    story=get_story(story_id)
    source=ScripturalSource(story.source_id, story.title, story.source_class)
    universe=ScripturalUniverse(
        f"scriptural-{story.story_id}", story.title, source, fidelity,
        era=story.era, region="derived-from-source", provenance=list(story.references),
        canon_status=story.source_class.value,
        details={"characters":list(story.characters),"places":list(story.places)}
    )
    return ScripturalProduction(story, universe).build()
