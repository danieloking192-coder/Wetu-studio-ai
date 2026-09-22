"""Production timeline orchestration for WETU."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass
class EditItem:
    item_id: str
    asset_id: str
    kind: str
    start_ms: int
    duration_ms: int
    layer: int = 0
    scene_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class ProductionTimeline:
    timeline_id: str
    fps: int = 24
    items: list[EditItem] = field(default_factory=list)

    def add(self, item: EditItem) -> EditItem:
        if not item.item_id.strip() or not item.asset_id.strip():
            raise ValueError("item_id and asset_id are required")
        if item.kind not in {"VIDEO","AUDIO","MUSIC","SFX","SUBTITLE"}:
            raise ValueError("unsupported timeline kind")
        if item.start_ms < 0 or item.duration_ms <= 0:
            raise ValueError("invalid timing")
        if any(x.item_id == item.item_id for x in self.items):
            raise ValueError("item_id must be unique")
        self.items.append(item)
        self.items.sort(key=lambda x: (x.start_ms, x.layer, x.item_id))
        return item

    def validate(self) -> dict[str, Any]:
        issues=[]
        for i,a in enumerate(self.items):
            for b in self.items[i+1:]:
                if a.layer == b.layer and a.start_ms < b.start_ms+b.duration_ms and b.start_ms < a.start_ms+a.duration_ms:
                    issues.append({"type":"overlap","items":[a.item_id,b.item_id],"layer":a.layer})
        return {"passed": not issues, "issues": issues, "item_count": len(self.items)}

    def duration_ms(self) -> int:
        return max((x.start_ms+x.duration_ms for x in self.items), default=0)
