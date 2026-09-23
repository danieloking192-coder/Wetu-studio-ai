"""WETU photo-to-character and realistic image-to-video contract."""
from __future__ import annotations
import base64, hashlib, json, re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

ALLOWED_IMAGE_TYPES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
MAX_IMAGE_BYTES = 10 * 1024 * 1024
SAFE_NAME = re.compile(r"[^a-zA-Z0-9._-]+")

@dataclass
class CharacterIdentity:
    character_id: str
    filename: str
    mime_type: str
    path: str
    sha256: str
    consent_confirmed: bool
    real_person: bool = True
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

class CharacterIdentityStore:
    def __init__(self, root: str | Path = ".wetu/character_identity"):
        self.root = Path(root); self.images = self.root / "images"; self.registry = self.root / "characters.json"
        self.images.mkdir(parents=True, exist_ok=True)
    def import_image(self, character_id: str, filename: str, mime_type: str, data_base64: str,
                     consent_confirmed: bool, real_person: bool = True) -> CharacterIdentity:
        if not character_id or len(character_id) > 128: raise ValueError("character_id is required")
        if mime_type not in ALLOWED_IMAGE_TYPES: raise ValueError("unsupported image type")
        if real_person and not consent_confirmed: raise PermissionError("consent_confirmed is required for a real-person image")
        try: raw = base64.b64decode(data_base64, validate=True)
        except Exception as exc: raise ValueError("invalid base64 image payload") from exc
        if not raw or len(raw) > MAX_IMAGE_BYTES: raise ValueError("image exceeds the 10 MB limit")
        safe = SAFE_NAME.sub("_", Path(filename or "character").name)[:120] or "character"
        digest = hashlib.sha256(raw).hexdigest(); stored = self.images / f"{digest}{ALLOWED_IMAGE_TYPES[mime_type]}"
        stored.write_bytes(raw)
        record = CharacterIdentity(character_id, safe, mime_type, str(stored), digest, bool(consent_confirmed), bool(real_person))
        records = self._load(); records[character_id] = record.to_dict()
        self.registry.parent.mkdir(parents=True, exist_ok=True); self.registry.write_text(json.dumps(records, indent=2), encoding="utf-8")
        return record
    def get(self, character_id: str) -> CharacterIdentity | None:
        item = self._load().get(character_id); return CharacterIdentity(**item) if item else None
    def _load(self) -> dict[str, Any]:
        return json.loads(self.registry.read_text(encoding="utf-8")) if self.registry.exists() else {}

def build_image_to_video_request(identity: CharacterIdentity, prompt: str, provider: str = "auto",
                                 duration: int = 5, resolution: str = "720p") -> dict[str, Any]:
    if not prompt or len(prompt) > 5000: raise ValueError("prompt is required and must be <= 5000 characters")
    if duration not in {2,3,4,5,6,7,8,9,10}: raise ValueError("duration must be between 2 and 10 seconds")
    if resolution not in {"480p","720p","1080p"}: raise ValueError("unsupported resolution")
    return {"request_id":"identity-video-"+identity.character_id,"kind":"video","provider":provider,"prompt":prompt,
            "references":[identity.path],"options":{"image_to_video":True,"identity_character_id":identity.character_id,
            "identity_sha256":identity.sha256,"duration":duration,"resolution":resolution,"realistic_motion":True,"preserve_identity":True}}
