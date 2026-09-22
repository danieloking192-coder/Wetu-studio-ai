"""Provider-neutral editorial timeline and deterministic validation."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass
class TimelineClip:
    clip_id: str
    asset_id: str
    track: str
    start: float
    duration: float
    scene_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class Timeline:
    project_id: str
    fps: float = 24.0
    clips: list[TimelineClip] = field(default_factory=list)

    def add(self, clip: TimelineClip) -> None:
        if clip.duration <= 0 or clip.start < 0:
            raise ValueError("clip start must be >= 0 and duration must be > 0")
        self.clips.append(clip)

    def validate(self) -> dict[str, Any]:
        issues: list[str] = []
        grouped: dict[str, list[TimelineClip]] = {}
        for clip in self.clips:
            grouped.setdefault(clip.track, []).append(clip)
        for track, clips in grouped.items():
            ordered = sorted(clips, key=lambda c: c.start)
            for a, b in zip(ordered, ordered[1:]):
                if a.start + a.duration > b.start:
                    issues.append(f"overlap:{track}:{a.clip_id}:{b.clip_id}")
        return {"passed": not issues, "issues": issues, "clip_count": len(self.clips)}