"""Deterministic post-production contracts for WETU Studio."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any

@dataclass(frozen=True)
class TimelineItem:
    item_id: str
    kind: str
    asset_id: str
    start_ms: int
    end_ms: int
    track: str = "video"
    language: str | None = None

@dataclass(frozen=True)
class Caption:
    caption_id: str
    start_ms: int
    end_ms: int
    text: str
    language: str

@dataclass(frozen=True)
class AudioMix:
    track_id: str
    gain_db: float = 0.0
    pan: float = 0.0
    duck_under_dialogue: bool = False

class PostProductionEngine:
    def validate_timeline(self, items: list[TimelineItem]) -> list[str]:
        issues = []
        for item in items:
            if item.end_ms <= item.start_ms: issues.append(f"{item.item_id}: end must be greater than start")
            if item.start_ms < 0: issues.append(f"{item.item_id}: start must be non-negative")
            if not item.asset_id: issues.append(f"{item.item_id}: asset_id is required")
        ordered = sorted(items, key=lambda x: (x.track, x.start_ms, x.end_ms, x.item_id))
        previous = {}
        for item in ordered:
            prev = previous.get(item.track)
            if prev and item.start_ms < prev.end_ms: issues.append(f"{item.item_id}: overlaps {prev.item_id} on track {item.track}")
            previous[item.track] = item
        return issues

    def validate_captions(self, captions: list[Caption]) -> list[str]:
        issues = []
        for c in captions:
            if c.end_ms <= c.start_ms: issues.append(f"{c.caption_id}: invalid time range")
            if not c.text.strip(): issues.append(f"{c.caption_id}: empty text")
            if not c.language.strip(): issues.append(f"{c.caption_id}: language required")
        return issues

    def validate_audio_mix(self, mix: list[AudioMix]) -> list[str]:
        return [f"{m.track_id}: pan must be between -1 and 1" for m in mix if not -1 <= m.pan <= 1]

    def continuity_report(self, items: list[TimelineItem], expected_asset_ids: set[str]) -> dict[str, Any]:
        present = {x.asset_id for x in items}
        missing = sorted(expected_asset_ids - present)
        return {"passed": not missing, "missing_asset_ids": missing, "asset_count": len(present)}

    def export_manifest(self, *, project_id: str, items: list[TimelineItem], captions: list[Caption],
                        audio_mix: list[AudioMix], delivery_profiles: list[str]) -> dict[str, Any]:
        issues = self.validate_timeline(items) + self.validate_captions(captions) + self.validate_audio_mix(audio_mix)
        return {"project_id": project_id, "ready": not issues, "issues": issues,
                "timeline": [asdict(x) for x in items], "captions": [asdict(x) for x in captions],
                "audio_mix": [asdict(x) for x in audio_mix], "delivery_profiles": list(delivery_profiles),
                "contract_version": "wetu-postproduction-v1"}
