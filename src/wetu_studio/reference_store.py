"""Traceable reference registry for WETU production assets."""
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
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)

class ReferenceStore:
    ALLOWED = {"image", "video", "audio", "document"}
    def __init__(self): self.items = {}
    def add(self, record: ReferenceRecord):
        if record.kind not in self.ALLOWED: raise ValueError("unsupported reference kind")
        if record.reference_id in self.items: raise ValueError("reference_id must be unique")
        if not record.uri.strip(): raise ValueError("uri is required")
        self.items[record.reference_id] = record
        return record
    def get(self, reference_id): return self.items.get(reference_id)