"""Adaptive HLS/DASH packaging contracts for WETU Studio AI.

This layer describes packaging and selection policy; it does not claim that a
CDN, packager, or player has been deployed.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class StreamingVariant:
    profile: str
    width: int
    height: int
    video_bitrate_kbps: int
    audio_bitrate_kbps: int

VARIANTS = (
    StreamingVariant("mobile_saver", 854, 480, 900, 64),
    StreamingVariant("mobile", 1280, 720, 1800, 96),
    StreamingVariant("standard", 1920, 1080, 3500, 128),
)

NETWORK_POLICY = {
    "offline_or_unknown": "mobile_saver",
    "very_low": "mobile_saver",
    "low": "mobile_saver",
    "normal": "mobile",
    "good": "standard",
}

class AdaptiveStreamingEngine:
    """Selects a rendition and builds provider-neutral HLS/DASH manifests."""

    def variants(self) -> list[dict[str, Any]]:
        return [v.__dict__.copy() for v in VARIANTS]

    def select(self, network: str = "normal", preferred: str | None = None) -> dict[str, Any]:
        if preferred:
            valid = {v.profile for v in VARIANTS}
            if preferred not in valid:
                raise ValueError(f"unknown streaming profile: {preferred}")
            selected = preferred
        else:
            selected = NETWORK_POLICY.get(str(network).lower(), "mobile_saver")
        return {"profile": selected, "reason": "explicit" if preferred else "network_policy"}

    def manifests(self, base_uri: str) -> dict[str, dict[str, Any]]:
        if not base_uri or not base_uri.rstrip("/"):
            raise ValueError("base_uri is required")
        base = base_uri.rstrip("/")
        return {
            "hls": {
                "type": "HLS",
                "master_playlist": f"{base}/hls/master.m3u8",
                "variants": [f"{base}/hls/{v.profile}/index.m3u8" for v in VARIANTS],
            },
            "dash": {
                "type": "DASH",
                "manifest": f"{base}/dash/manifest.mpd",
                "variants": [f"{base}/dash/{v.profile}/index.m4s" for v in VARIANTS],
            },
        }

    def contract(self, base_uri: str = "https://media.invalid/assets/demo") -> dict[str, Any]:
        return {
            "adaptive": True,
            "master_immutable": True,
            "protocols": ["HLS", "DASH"],
            "variants": self.variants(),
            "selection": NETWORK_POLICY.copy(),
            "manifests": self.manifests(base_uri),
            "deployment_active": False,
        }
