from dataclasses import dataclass, field

@dataclass
class AudioLine:
    speaker_id: str
    text: str
    language: str
    voice_id: str = ""
    start_ms: int = 0
    end_ms: int = 0

@dataclass
class AudioTrack:
    track_id: str
    lines: list[AudioLine] = field(default_factory=list)
    music_refs: list[str] = field(default_factory=list)
    sfx_refs: list[str] = field(default_factory=list)

class AudioEngine:
    SUPPORTED_LANGUAGES = {"fr", "en", "es", "pt", "ar", "sw", "ln", "lua"}
    def create_track(self, track_id: str) -> AudioTrack:
        if not track_id.strip(): raise ValueError("track_id is required")
        return AudioTrack(track_id)
    def add_line(self, track: AudioTrack, speaker_id: str, text: str, language: str, voice_id="", start_ms=0, end_ms=0) -> AudioLine:
        if not speaker_id.strip() or not text.strip(): raise ValueError("speaker_id and text are required")
        if language not in self.SUPPORTED_LANGUAGES: raise ValueError("unsupported language")
        if start_ms < 0 or end_ms < start_ms: raise ValueError("invalid timing")
        line=AudioLine(speaker_id,text,language,voice_id,start_ms,end_ms); track.lines.append(line); return line
    def add_music(self, track: AudioTrack, ref: str) -> None:
        if ref.strip() and ref not in track.music_refs: track.music_refs.append(ref)
    def add_sfx(self, track: AudioTrack, ref: str) -> None:
        if ref.strip() and ref not in track.sfx_refs: track.sfx_refs.append(ref)
