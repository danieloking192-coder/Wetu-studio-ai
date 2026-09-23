"""Provider configuration and asset reference contracts for WETU."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass
class ProviderProfile:
    name: str
    capabilities: set[str]
    configured: bool
    endpoint_configured: bool = False
    notes: list[str] = field(default_factory=list)

@dataclass
class AssetReference:
    reference_id: str
    uri: str
    kind: str = "unknown"
    role: str = "reference"
    metadata: dict[str, Any] = field(default_factory=dict)

class ProviderSelector:
    def __init__(self, registry):
        self.registry = registry

    def profiles(self):
        return [ProviderProfile(
            name=name,
            capabilities=set(p.capabilities),
            configured=True,
            endpoint_configured=hasattr(p, "endpoint"),
            notes=["provider registered"] if name != "wetu-local" else ["manifest-only; no real media"],
        ) for name, p in self.registry.providers.items()]

    def require(self, name: str, kind: str):
        p = self.registry.providers.get(name)
        if p is None:
            raise ValueError(f"unknown provider: {name}")
        if kind not in p.capabilities:
            raise ValueError(f"provider {name} does not support {kind}")
        return p


@dataclass(frozen=True)
class ProviderRequest:
    request_id: str
    kind: str
    options: dict[str, Any] = field(default_factory=dict)
    references: list[AssetReference] = field(default_factory=list)

class ProviderGateway:
    """Provider-neutral gateway with capability checks and explicit fallback policy."""
    def __init__(self, registry):
        self.registry = registry
        self.selector = ProviderSelector(registry)

    def profiles(self):
        return self.selector.profiles()

    def require(self, name: str, kind: str):
        return self.selector.require(name, kind)

    def available(self, kind: str) -> list[ProviderProfile]:
        return [p for p in self.profiles() if kind in p.capabilities]

    def select(self, kind: str, preferred: str = ""):
        if preferred:
            return self.require(preferred, kind)
        candidates = self.available(kind)
        if not candidates:
            raise ValueError(f"no provider supports {kind}")
        # Prefer a configured non-local provider; local remains an explicit fallback.
        for profile in candidates:
            if profile.name != "wetu-local" and profile.endpoint_configured:
                return self.registry.providers[profile.name]
        return self.registry.providers[candidates[0].name]

    def prepare(self, request: ProviderRequest):
        provider = self.select(request.kind, str(request.options.get("provider", "")))
        return provider, {
            "request_id": request.request_id,
            "kind": request.kind,
            "provider": provider.name,
            "references": [r.reference_id for r in request.references],
            "options": dict(request.options),
            "real_provider": provider.name != "wetu-local",
        }
