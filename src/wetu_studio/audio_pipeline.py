"""Provider-neutral audio/voice request layer."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass(frozen=True)
class VoiceRequest:
    request_id: str
    project_id: str
    scene_id: str
    speaker_id: str
    language: str
    text: str
    voice_id: str = ""
    options: dict[str, Any] = field(default_factory=dict)

class AudioProvider:
    name="wetu-local-audio"
    capabilities={"speech","music","sfx"}
    def generate(self, request: VoiceRequest, context: dict[str,Any]) -> dict[str,Any]:
        return {"request_id":request.request_id,"provider":self.name,
                "kind":"audio","status":"READY",
                "uri":f"memory://wetu/audio/{request.request_id}","real_audio":False}

class AudioRegistry:
    def __init__(self):
        self.providers={AudioProvider.name:AudioProvider()}
    def register(self, provider): self.providers[provider.name]=provider
    def generate(self, request, context):
        p=self.providers.get(request.options.get("provider",AudioProvider.name), self.providers[AudioProvider.name])
        return p.generate(request,context)
