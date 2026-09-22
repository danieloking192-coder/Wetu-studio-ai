"""Synchronization contracts for dialogue, voice assets and subtitles."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class SyncCue:
    line_id: str
    start_ms: int
    end_ms: int
    speaker_id: str
    language: str
    text: str
    voice_request_id: str = ""

class MediaSyncEngine:
    def validate(self, cues: list[SyncCue]) -> None:
        previous_end = -1
        seen = set()
        for cue in cues:
            if cue.line_id in seen:
                raise ValueError("line_id must be unique")
            seen.add(cue.line_id)
            if cue.start_ms < 0 or cue.end_ms <= cue.start_ms:
                raise ValueError("invalid cue timing")
            if cue.start_ms < previous_end:
                raise ValueError("cues must not overlap")
            if not cue.speaker_id.strip() or not cue.language.strip() or not cue.text.strip():
                raise ValueError("speaker_id, language and text are required")
            previous_end = cue.end_ms

    def build_manifest(self, cues: list[SyncCue]) -> list[dict[str, object]]:
        self.validate(cues)
        return [{"line_id": c.line_id, "start_ms": c.start_ms, "end_ms": c.end_ms,
                 "speaker_id": c.speaker_id, "language": c.language, "text": c.text,
                 "voice_request_id": c.voice_request_id} for c in cues]
