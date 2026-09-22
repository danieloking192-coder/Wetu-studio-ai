"""Multilingual production orchestration for WETU."""
from __future__ import annotations
from dataclasses import dataclass, field

@dataclass(frozen=True)
class LocalizedLine:
    line_id: str
    speaker_id: str
    language: str
    text: str
    voice_id: str = ""
    subtitle: str = ""

@dataclass
class LocalizationTrack:
    scene_id: str
    lines: list[LocalizedLine] = field(default_factory=list)

class LocalizationEngine:
    SUPPORTED_LANGUAGES = {"fr","en","es","pt","ar","sw","ln"}
    def add_line(self, track: LocalizationTrack, line_id: str, speaker_id: str,
                 language: str, text: str, voice_id="", subtitle="") -> LocalizedLine:
        if language not in self.SUPPORTED_LANGUAGES:
            raise ValueError("unsupported language")
        if not line_id.strip() or not speaker_id.strip() or not text.strip():
            raise ValueError("line_id, speaker_id and text are required")
        if any(x.line_id == line_id for x in track.lines):
            raise ValueError("line_id must be unique")
        line=LocalizedLine(line_id,speaker_id,language,text,voice_id,subtitle or text)
        track.lines.append(line)
        return line

    def languages(self, track: LocalizationTrack) -> list[str]:
        return sorted({x.language for x in track.lines})

    def export_subtitles(self, track: LocalizationTrack) -> list[dict[str,str]]:
        return [{"line_id":x.line_id,"speaker_id":x.speaker_id,"language":x.language,
                 "text":x.subtitle} for x in track.lines]
