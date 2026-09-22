from dataclasses import dataclass, field

@dataclass
class TimelineItem:
    item_id: str
    kind: str
    source_ref: str
    start_ms: int
    duration_ms: int
    layer: int = 0

@dataclass
class EditTimeline:
    timeline_id: str
    items: list[TimelineItem] = field(default_factory=list)

class EditEngine:
    ALLOWED_KINDS = {"VIDEO", "AUDIO", "MUSIC", "SFX", "SUBTITLE"}
    def create(self, timeline_id: str) -> EditTimeline:
        if not timeline_id.strip(): raise ValueError("timeline_id is required")
        return EditTimeline(timeline_id)
    def add_item(self, timeline: EditTimeline, item_id: str, kind: str, source_ref: str, start_ms: int, duration_ms: int, layer=0) -> TimelineItem:
        if not item_id.strip() or not source_ref.strip(): raise ValueError("item_id and source_ref are required")
        if kind not in self.ALLOWED_KINDS: raise ValueError("unsupported timeline kind")
        if start_ms < 0 or duration_ms <= 0: raise ValueError("invalid timeline timing")
        if any(x.item_id == item_id for x in timeline.items): raise ValueError("item_id must be unique")
        item=TimelineItem(item_id,kind,source_ref,start_ms,duration_ms,layer); timeline.items.append(item); return item
    def overlaps(self, timeline: EditTimeline, a: TimelineItem, b: TimelineItem) -> bool:
        if a.layer != b.layer: return False
        return a.start_ms < b.start_ms+b.duration_ms and b.start_ms < a.start_ms+a.duration_ms
