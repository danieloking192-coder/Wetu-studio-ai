"""Traceable visual references with continuity-aware retrieval."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

def utc_now(): return datetime.now(timezone.utc).isoformat()

@dataclass
class ReferenceRecord:
    reference_id: str
    project_id: str
    kind: str
    uri: str
    label: str = ""
    entity_id: str | None = None
    continuity_key: str | None = None
    source_scene_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)

class ReferenceStore:
    ALLOWED={"image","video","audio","document"}
    def __init__(self): self.items={}

    def add(self, record):
        if record.kind not in self.ALLOWED: raise ValueError("unsupported reference kind")
        if record.reference_id in self.items: raise ValueError("reference_id must be unique")
        if not record.uri.strip(): raise ValueError("uri is required")
        self.items[record.reference_id]=record
        return record

    def remember_asset(self, asset_record, entity_id=None, continuity_key=None, label=""):
        return self.add(ReferenceRecord(
            reference_id=f"ref:{asset_record.asset_id}",
            project_id=asset_record.project_id, kind=asset_record.kind,
            uri=asset_record.uri, label=label, entity_id=entity_id,
            continuity_key=continuity_key, source_scene_id=asset_record.scene_id,
            metadata=dict(asset_record.metadata)))

    def get(self, reference_id): return self.items.get(reference_id)

    def for_scene(self, project_id, scene_id=None, entity_ids=None, continuity_keys=None):
        entities=set(entity_ids or []); keys=set(continuity_keys or [])
        return [r for r in self.items.values() if r.project_id == project_id and (
            (scene_id and r.source_scene_id == scene_id) or
            (r.entity_id and r.entity_id in entities) or
            (r.continuity_key and r.continuity_key in keys))]

    def uris_for_scene(self, project_id, **kwargs):
        return [r.uri for r in self.for_scene(project_id, **kwargs)]
