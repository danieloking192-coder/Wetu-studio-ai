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
        self.registry=registry
    def profiles(self):
        return [ProviderProfile(
            name=name,
            capabilities=set(p.capabilities),
            configured=True,
            endpoint_configured=hasattr(p, "endpoint"),
            notes=["provider registered"] if name != "wetu-local" else ["manifest-only; no real media"],
        ) for name,p in self.registry.providers.items()]
    def require(self, name: str, kind: str):
        p=self.registry.providers.get(name)
        if p is None: raise ValueError(f"unknown provider: {name}")
        if kind not in p.capabilities: raise ValueError(f"provider {name} does not support {kind}")
        return p
