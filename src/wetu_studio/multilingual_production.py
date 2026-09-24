"""WETU language-neutral script adaptation and translation contract."""
from __future__ import annotations
import json, os
from dataclasses import dataclass, asdict
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

SUPPORTED_OUTPUT_LANGUAGES={"fr":"Français","en":"English","ln":"Lingala","sw":"Swahili","tsh":"Tshiluba","kg":"Kikongo"}

@dataclass
class MultilingualProductionRequest:
    project_id: str; scene_id: str | None; source_language: str; target_language: str; script: str
    preserve_meaning: bool=True; preserve_tone: bool=True; lip_sync: bool=True
    def validate(self)->list[str]:
        issues=[]
        if self.target_language not in SUPPORTED_OUTPUT_LANGUAGES: issues.append("unsupported target language")
        if not self.script.strip(): issues.append("script is empty")
        if len(self.script)>50000: issues.append("script exceeds 50,000 characters")
        return issues
    def to_dict(self)->dict[str,Any]: return asdict(self)

def build_language_pipeline(req: MultilingualProductionRequest)->dict[str,Any]:
    issues=req.validate()
    return {"ok":not issues,"issues":issues,"source_language":req.source_language,"target_language":req.target_language,
            "stages":["script_ingest","meaning_preserving_translation","dialogue_adaptation","target_language_voice","lip_sync","subtitle_policy","final_quality_gate"],
            "options":{"preserve_meaning":req.preserve_meaning,"preserve_tone":req.preserve_tone,"lip_sync":req.lip_sync},
            "provider_boundary":"Configure a server-side translation/TTS provider; WETU never exposes provider keys in the client."}

class HttpTranslationProvider:
    """Server-side translation adapter. No fake translation is returned when unconfigured."""
    def __init__(self, endpoint: str, api_key: str="", timeout: float=60.0):
        if not endpoint.startswith("https://"):
            raise ValueError("translation provider endpoint must use HTTPS")
        self.endpoint, self.api_key, self.timeout = endpoint, api_key, timeout

    @classmethod
    def from_environment(cls):
        endpoint=os.getenv("WETU_TRANSLATION_ENDPOINT","").strip()
        return cls(endpoint, os.getenv("WETU_TRANSLATION_API_KEY","").strip(),
                   float(os.getenv("WETU_TRANSLATION_TIMEOUT","60"))) if endpoint else None

    def translate(self, *, source_language: str, target_language: str, script: str,
                  preserve_meaning: bool=True, preserve_tone: bool=True) -> dict[str,Any]:
        payload={"source_language":source_language,"target_language":target_language,"script":script,
                 "preserve_meaning":preserve_meaning,"preserve_tone":preserve_tone,
                 "contract":"wetu-translation-v1"}
        headers={"Content-Type":"application/json","X-WETU-Provider-Contract":"translation-v1"}
        if self.api_key: headers["Authorization"]="Bearer "+self.api_key
        req=Request(self.endpoint,data=json.dumps(payload).encode(),headers=headers,method="POST")
        try:
            with urlopen(req,timeout=self.timeout) as response:
                data=json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise RuntimeError(f"translation provider HTTP {exc.code}") from exc
        except URLError as exc:
            raise RuntimeError(f"translation provider unavailable: {exc.reason}") from exc
        except (TimeoutError, json.JSONDecodeError) as exc:
            raise RuntimeError("translation provider returned an invalid response") from exc
        if not isinstance(data,dict) or not isinstance(data.get("text"),str) or not data["text"].strip():
            raise ValueError("translation provider response must contain non-empty text")
        return {"ok":True,"real_translation":True,"provider":"wetu-http-translation",
                "source_language":source_language,"target_language":target_language,
                "text":data["text"],"provider_metadata":data.get("metadata",{})}
