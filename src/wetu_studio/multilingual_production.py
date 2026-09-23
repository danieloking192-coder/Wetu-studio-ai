"""WETU language-neutral script adaptation contract."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any
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
