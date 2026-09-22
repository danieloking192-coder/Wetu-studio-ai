"""Bandwidth-aware video delivery contracts for WETU Studio AI."""
from __future__ import annotations
from dataclasses import dataclass

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

    def profile(self, name: str = "mobile") -> DeliveryProfile:
        try:
            return PROFILES[name]
        except KeyError as exc:
            raise ValueError(f"unknown delivery profile: {name}") from exc

    def target(self, options: dict | None = None) -> dict[str, object]:
        options = options or {}
        profile = self.profile(str(options.get("delivery_profile", "mobile")))
        return {"profile": profile.name, "width": profile.width, "height": profile.height,
                "fps": profile.fps, "video_bitrate_kbps": profile.video_bitrate_kbps,
                "audio_bitrate_kbps": profile.audio_bitrate_kbps,
                "adaptive_delivery": True, "master_kept_separately": True}

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
