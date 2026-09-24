"""Provider-neutral audio/voice request layer."""
from __future__ import annotations
import json, os
from dataclasses import dataclass, field
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from .security_controls import validate_media_uri

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

class HttpAudioProvider:
    name="wetu-http-audio"
    capabilities={"speech"}
    def __init__(self, endpoint: str, api_key: str="", timeout: float=120.0):
        if not endpoint.startswith("https://"):
            raise ValueError("audio provider endpoint must use HTTPS")
        self.endpoint,self.api_key,self.timeout=endpoint,api_key,timeout
    @classmethod
    def from_environment(cls):
        endpoint=os.getenv("WETU_AUDIO_ENDPOINT","").strip()
        return cls(endpoint,os.getenv("WETU_AUDIO_API_KEY","").strip(),
                   float(os.getenv("WETU_AUDIO_TIMEOUT","120"))) if endpoint else None
    def generate(self, request: VoiceRequest, context: dict[str,Any]) -> dict[str,Any]:
        payload={"request_id":request.request_id,"project_id":request.project_id,"scene_id":request.scene_id,
                 "speaker_id":request.speaker_id,"language":request.language,"text":request.text,
                 "voice_id":request.voice_id,"options":request.options,"contract":"wetu-audio-v1"}
        headers={"Content-Type":"application/json","X-WETU-Provider-Contract":"audio-v1"}
        if self.api_key: headers["Authorization"]="Bearer "+self.api_key
        req=Request(self.endpoint,data=json.dumps(payload).encode(),headers=headers,method="POST")
        try:
            with urlopen(req,timeout=self.timeout) as response:
                data=json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise RuntimeError(f"audio provider HTTP {exc.code}") from exc
        except URLError as exc:
            raise RuntimeError(f"audio provider unavailable: {exc.reason}") from exc
        except (TimeoutError,json.JSONDecodeError) as exc:
            raise RuntimeError("audio provider returned an invalid response") from exc
        if not isinstance(data,dict) or not data.get("uri"):
            raise ValueError("audio provider response must contain uri")
        uri=validate_media_uri(str(data["uri"]), require_https=True)
        return {"request_id":request.request_id,"provider":self.name,"kind":"audio","status":"READY",
                "uri":uri,"real_audio":True,"metadata":data.get("metadata",{})}

class AudioRegistry:
    def __init__(self):
        self.providers={AudioProvider.name:AudioProvider()}
        real=HttpAudioProvider.from_environment()
        if real is not None: self.providers[real.name]=real
    def register(self, provider): self.providers[provider.name]=provider
    def generate(self, request, context=None):
        provider_name=request.options.get("provider")
        p=self.providers.get(provider_name) if provider_name else self.providers.get("wetu-http-audio", self.providers[AudioProvider.name])
        if p is None: p=self.providers[AudioProvider.name]
        return p.generate(request, context or {})
