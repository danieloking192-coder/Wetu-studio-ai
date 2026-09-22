"""Deterministic subtitle track generation and SRT/VTT serialization for WETU.

The engine never invents dialogue: cues must come from supplied transcript/dialogue.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


def _ms(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("timestamp must be numeric milliseconds")
    value = int(value)
    if value < 0:
        raise ValueError("timestamp must be non-negative")
    return value


def _timestamp(ms: int, separator: str) -> str:
    ms = _ms(ms)
    hours, remainder = divmod(ms, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    seconds, millis = divmod(remainder, 1_000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}{separator}{millis:03d}"


@dataclass(frozen=True)
class SubtitleCue:
    start_ms: int
    end_ms: int
    text: str
    speaker: str | None = None
    cue_id: str | None = None

    def __post_init__(self) -> None:
        start = _ms(self.start_ms)
        end = _ms(self.end_ms)
        if end <= start:
            raise ValueError("cue end_ms must be greater than start_ms")
        if not isinstance(self.text, str) or not self.text.strip():
            raise ValueError("cue text is required")
        if len(self.text) > 2000:
            raise ValueError("cue text exceeds allowed length")
        if self.speaker is not None and not isinstance(self.speaker, str):
            raise ValueError("speaker must be a string or null")


@dataclass
class SubtitleTrack:
    track_id: str
    project_id: str
    scene_id: str | None
    language: str
    source: str = "dialogue"
    cues: list[SubtitleCue] = field(default_factory=list)
    enabled: bool = True

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not isinstance(self.track_id, str) or not self.track_id.strip():
            issues.append("track_id is required")
        if not isinstance(self.project_id, str) or not self.project_id.strip():
            issues.append("project_id is required")
        if not isinstance(self.language, str) or not self.language.strip():
            issues.append("language is required")
        previous_end = -1
        for cue in self.cues:
            try:
                cue.__post_init__()
            except ValueError as exc:
                issues.append(str(exc))
                continue
            if cue.start_ms < previous_end:
                issues.append("cues must be ordered and non-overlapping")
            previous_end = cue.end_ms
        return issues

    def to_dict(self) -> dict[str, Any]:
        return {
            "track_id": self.track_id,
            "project_id": self.project_id,
            "scene_id": self.scene_id,
            "language": self.language,
            "source": self.source,
            "enabled": self.enabled,
            "cues": [
                {"start_ms": c.start_ms, "end_ms": c.end_ms, "text": c.text,
                 "speaker": c.speaker, "cue_id": c.cue_id}
                for c in self.cues
            ],
        }

    def to_srt(self) -> str:
        issues = self.validate()
        if issues:
            raise ValueError("; ".join(issues))
        blocks = []
        for index, cue in enumerate(self.cues, 1):
            text = f"{cue.speaker}: {cue.text}" if cue.speaker else cue.text
            blocks.append(f"{index}\n{_timestamp(cue.start_ms, ',')} --> {_timestamp(cue.end_ms, ',')}\n{text}")
        return "\n\n".join(blocks) + ("\n" if blocks else "")

    def to_vtt(self) -> str:
        issues = self.validate()
        if issues:
            raise ValueError("; ".join(issues))
        blocks = ["WEBVTT", ""]
        for cue in self.cues:
            text = f"{cue.speaker}: {cue.text}" if cue.speaker else cue.text
            if cue.cue_id:
                blocks.append(cue.cue_id)
            blocks.extend([f"{_timestamp(cue.start_ms, '.')} --> {_timestamp(cue.end_ms, '.')}", text, ""])
        return "\n".join(blocks)


class SubtitleEngine:
    """Build tracks only from explicitly supplied, time-coded dialogue."""

    def build_track(
        self, *, track_id: str, project_id: str, scene_id: str | None,
        language: str, dialogue: list[dict[str, Any]],
        source: str = "dialogue", enabled: bool = True,
    ) -> SubtitleTrack:
        if not enabled:
            raise ValueError("subtitle generation is disabled")
        if not isinstance(dialogue, list):
            raise ValueError("dialogue must be a list")
        cues = [
            SubtitleCue(
                start_ms=item["start_ms"], end_ms=item["end_ms"],
                text=item["text"], speaker=item.get("speaker"), cue_id=item.get("cue_id"),
            )
            for item in dialogue
        ]
        track = SubtitleTrack(track_id, project_id, scene_id, language, source, cues, enabled)
        issues = track.validate()
        if issues:
            raise ValueError("; ".join(issues))
        return track
