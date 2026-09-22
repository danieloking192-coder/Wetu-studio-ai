from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json

@dataclass(frozen=True)
class GenerationRequest:
    generation_id: str
    project_id: str
    shot_id: str
    prompt: str
    reference_ids: tuple[str, ...] = ()
    provider: str = ""
    model: str = ""
    created_at: str = ""

@dataclass(frozen=True)
class GenerationArtifact:
    generation_id: str
    content_hash: str
    status: str
    metadata: dict[str, str] = field(default_factory=dict)

class GenerationEngine:
    """Provider-neutral orchestration records; actual media generation is adapter-owned."""
    def create_request(self, generation_id: str, project_id: str, shot_id: str, prompt: str, reference_ids=(), provider="", model="") -> GenerationRequest:
        if not generation_id.strip() or not project_id.strip() or not shot_id.strip():
            raise ValueError("generation_id, project_id and shot_id are required")
        if not prompt.strip():
            raise ValueError("prompt is required")
        return GenerationRequest(generation_id, project_id, shot_id, prompt, tuple(reference_ids), provider, model, datetime.now(timezone.utc).isoformat())

    def fingerprint_request(self, request: GenerationRequest) -> str:
        payload = {"generation_id": request.generation_id, "project_id": request.project_id, "shot_id": request.shot_id, "prompt": request.prompt, "reference_ids": request.reference_ids, "provider": request.provider, "model": request.model}
        return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    def register_artifact(self, request: GenerationRequest, content: bytes, status="READY", metadata=None) -> GenerationArtifact:
        if status not in {"READY", "FAILED", "REJECTED", "PENDING"}: raise ValueError("invalid artifact status")
        return GenerationArtifact(request.generation_id, hashlib.sha256(content).hexdigest(), status, dict(metadata or {}))
