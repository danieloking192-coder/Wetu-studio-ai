"""Exportable production bundle manifest for WETU."""
from __future__ import annotations
from dataclasses import asdict
from typing import Any
from .timeline_engine import Timeline

class ProductionBundle:
    VERSION = "1.0"
    def build(self, state, timeline: Timeline | None = None, assets=None, qa=None) -> dict[str, Any]:
        bundle = {
            "schema_version": self.VERSION,
            "project_id": state.project_id,
            "characters": [asdict(x) for x in state.characters.values()],
            "worlds": [asdict(x) for x in state.worlds.values()],
            "scenes": [asdict(x) for x in state.scenes.values()],
            "generations": [asdict(x) for x in state.memory.generations.values()],
            "decisions": [asdict(x) for x in state.memory.decisions.values()],
            "references": dict(state.memory.references),
            "events": list(state.memory.events),
            "assets": [asdict(x) for x in (assets or [])],
            "timeline": asdict(timeline) if timeline else None,
            "qa": qa or {"status": "not_run"},
        }
        return bundle