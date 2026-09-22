"""Provider-neutral media orchestration for WETU Studio AI."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Protocol

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

@dataclass
class MediaAsset:
    asset_id: str
    project_id: str
    scene_id: str | None
    kind: str
    provider: str
    model: str
    uri: str
    status: str = "created"
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)

@dataclass
class MediaRequest:
    request_id: str
    project_id: str
    scene_id: str | None
    kind: str
    prompt: str
    provider: str
    references: list[str] = field(default_factory=list)
    options: dict[str, Any] = field(default_factory=dict)

class MediaProvider(Protocol):
    name: str
    capabilities: set[str]
    def generate(self, request: MediaRequest, context: dict[str, Any]) -> dict[str, Any]: ...

class LocalMediaProvider:
    """Deterministic development provider; never claims to create real media."""
    name = "wetu-local"
    capabilities = {"image", "video", "audio"}

    def generate(self, request: MediaRequest, context: dict[str, Any]) -> dict[str, Any]:
        return {"model": "wetu-local-manifest-v1",
                "uri": f"memory://wetu/{request.project_id}/{request.request_id}/{request.kind}",
                "kind": request.kind, "real_media": False,
                "context_items": len(context.get("recent_generations", []))}

class MediaRegistry:
    def __init__(self, providers: dict[str, MediaProvider] | None = None):
        self.providers = providers or {"wetu-local": LocalMediaProvider()}

    def register(self, provider: MediaProvider) -> None:
        self.providers[provider.name] = provider

    def generate(self, request: MediaRequest, context: dict[str, Any]) -> MediaAsset:
        provider = self.providers.get(request.provider)
        if provider is None:
            raise ValueError(f"unknown media provider: {request.provider}")
        if request.kind not in provider.capabilities:
            raise ValueError(f"provider {request.provider} does not support {request.kind}")
        result = provider.generate(request, context)
        return MediaAsset(request.request_id, request.project_id, request.scene_id,
                          request.kind, request.provider, str(result.get("model","unknown")),
                          str(result.get("uri","")), "ready",
                          {"request": request.options, "provider_result": result,
                           "references": list(request.references)})