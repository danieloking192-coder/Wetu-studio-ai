"""Provider-neutral media orchestration for WETU Studio AI."""
from __future__ import annotations
import json, os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Protocol
from urllib.request import Request, urlopen
from .video_quality import VideoQualityEngine
from .video_delivery import VideoDeliveryEngine

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
    name = "wetu-local"
    capabilities = {"image", "video", "audio"}
    def generate(self, request: MediaRequest, context: dict[str, Any]) -> dict[str, Any]:
        return {"model": "wetu-local-manifest-v1",
                "uri": f"memory://wetu/{request.project_id}/{request.request_id}/{request.kind}",
                "kind": request.kind, "real_media": False,
                "context_items": len(context.get("recent_generations", []))}

class HttpMediaProvider:
    """Generic real-provider adapter. Endpoint and secret come only from environment variables."""
    capabilities = {"image", "video", "audio"}
    def __init__(self, name: str, endpoint: str, api_key: str = "", timeout: float = 60.0):
        if not name.strip() or not endpoint.startswith(("https://","http://")):
            raise ValueError("provider name and valid HTTP(S) endpoint are required")
        self.name, self.endpoint, self.api_key, self.timeout = name, endpoint, api_key, timeout

    def generate(self, request: MediaRequest, context: dict[str, Any]) -> dict[str, Any]:
        payload = {"request_id": request.request_id, "project_id": request.project_id,
                   "scene_id": request.scene_id, "kind": request.kind, "prompt": request.prompt,
                   "references": request.references, "options": request.options, "context": context}
        headers = {"Content-Type": "application/json", "X-WETU-Provider-Contract": "1"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        req = Request(self.endpoint, data=json.dumps(payload).encode(), headers=headers, method="POST")
        with urlopen(req, timeout=self.timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
        if not isinstance(data, dict):
            raise ValueError("provider response must be a JSON object")
        return data

def provider_from_environment(prefix: str = "WETU_MEDIA") -> HttpMediaProvider | None:
    endpoint = os.getenv(f"{prefix}_ENDPOINT", "").strip()
    if not endpoint:
        return None
    return HttpMediaProvider(os.getenv(f"{prefix}_NAME", "wetu-http"), endpoint,
                             os.getenv(f"{prefix}_API_KEY", ""), float(os.getenv(f"{prefix}_TIMEOUT", "60")))

class MediaRegistry:
    def __init__(self, providers: dict[str, MediaProvider] | None = None):
        self.providers = providers or {"wetu-local": LocalMediaProvider()}
        self.video_quality = VideoQualityEngine()
        self.video_delivery = VideoDeliveryEngine()

    def register(self, provider: MediaProvider) -> None:
        self.providers[provider.name] = provider

    def generate(self, request: MediaRequest, context: dict[str, Any]) -> MediaAsset:
        provider = self.providers.get(request.provider)
        if provider is None:
            raise ValueError(f"unknown media provider: {request.provider}")
        if request.kind not in provider.capabilities:
            raise ValueError(f"provider {request.provider} does not support {request.kind}")
        quality_target = None
        delivery_target = None
        if request.kind == "video":
            quality_target = self.video_quality.target(request.options)
            delivery_target = self.video_delivery.target(request.options)
        result = provider.generate(request, context)
        metadata = {"request": request.options, "provider_result": result,
                    "references": list(request.references), "real_media": bool(result.get("real_media", True))}
        if quality_target is not None:
            metadata["video_quality_target"] = quality_target
            metadata["video_quality_compliant"] = not self.video_quality.validate_output(result, quality_target)
            metadata["video_delivery_target"] = delivery_target
            metadata["video_delivery_compliant"] = not self.video_delivery.validate_delivery_output(result, delivery_target)
            if "duration_seconds" in result:
                metadata["estimated_delivery_size_mb"] = self.video_delivery.estimate_size_mb(
                    float(result["duration_seconds"]), delivery_target
                )
        return MediaAsset(request.request_id, request.project_id, request.scene_id,
                          request.kind, request.provider, str(result.get("model","unknown")),
                          str(result.get("uri", result.get("asset_url",""))), "ready", metadata)
