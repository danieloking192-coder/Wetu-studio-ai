"""Bandwidth-aware video delivery contracts for WETU Studio AI."""
from __future__ import annotations

from dataclasses import dataclass

from .adaptive_streaming import AdaptiveStreamingEngine


@dataclass(frozen=True)
class DeliveryProfile:
    name: str
    width: int
    height: int
    fps: int
    video_bitrate_kbps: int
    audio_bitrate_kbps: int


PROFILES = {
    "mobile_saver": DeliveryProfile("mobile_saver", 854, 480, 24, 900, 64),
    "mobile": DeliveryProfile("mobile", 1280, 720, 30, 1800, 96),
    "standard": DeliveryProfile("standard", 1920, 1080, 30, 3500, 128),
    "high_quality": DeliveryProfile("high_quality", 1920, 1080, 30, 6000, 160),
}


class VideoDeliveryEngine:
    """Builds bandwidth-aware targets and estimates viewing size."""

    def __init__(self, adaptive_streaming: AdaptiveStreamingEngine | None = None):
        self.adaptive_streaming = adaptive_streaming or AdaptiveStreamingEngine()

    def profile(self, name: str = "mobile") -> DeliveryProfile:
        try:
            return PROFILES[name]
        except KeyError as exc:
            raise ValueError(f"unknown delivery profile: {name}") from exc

    def target(self, options: dict | None = None) -> dict[str, object]:
        options = options or {}
        network = str(options.get("network", "normal")).lower()
        preferred = options.get("delivery_profile")
        adaptive = bool(options.get("adaptive", True))
        if adaptive and not preferred:
            selected = self.adaptive_streaming.select(network=network)["profile"]
        else:
            selected = str(preferred or "mobile")
        profile = self.profile(selected)
        return {
            "profile": profile.name,
            "width": profile.width,
            "height": profile.height,
            "fps": profile.fps,
            "video_bitrate_kbps": profile.video_bitrate_kbps,
            "audio_bitrate_kbps": profile.audio_bitrate_kbps,
            "adaptive_delivery": adaptive,
            "network": network,
            "master_kept_separately": True,
        }

    def estimate_size_mb(self, duration_seconds: float, target: dict) -> float:
        if duration_seconds < 0:
            raise ValueError("duration_seconds must be non-negative")
        bitrate = int(target["video_bitrate_kbps"]) + int(target["audio_bitrate_kbps"])
        return round(duration_seconds * bitrate / 8 / 1024, 2)

    def validate_delivery_output(self, output: dict, target: dict) -> list[str]:
        if not isinstance(output, dict):
            return ["delivery_metadata_missing"]
        issues = []
        if "width" in output and int(output["width"]) > int(target["width"]):
            issues.append("delivery_width_exceeds_target")
        if "height" in output and int(output["height"]) > int(target["height"]):
            issues.append("delivery_height_exceeds_target")
        if "video_bitrate_kbps" in output and int(output["video_bitrate_kbps"]) > int(target["video_bitrate_kbps"]) * 1.15:
            issues.append("delivery_bitrate_exceeds_target")
        if output.get("corrupt") is True:
            issues.append("corrupt_media")
        return sorted(set(issues))
