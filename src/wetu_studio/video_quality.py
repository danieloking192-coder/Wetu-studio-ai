"""Video quality and smoothness contracts for WETU Studio AI.

The engine defines production targets and validates provider output metadata. It never
claims a provider rendered a resolution or frame rate that was not actually reported.
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class VideoQualityProfile:
    name: str
    width: int
    height: int
    fps: int
    min_bitrate_kbps: int


PROFILES = {
    "smooth": VideoQualityProfile("smooth", 1280, 720, 30, 5000),
    "high_quality": VideoQualityProfile("high_quality", 1920, 1080, 30, 8000),
    "ultra_hd": VideoQualityProfile("ultra_hd", 3840, 2160, 30, 20000),
}


class VideoQualityEngine:
    """Validates video targets and measured provider output."""

    def profile(self, name: str = "high_quality") -> VideoQualityProfile:
        try:
            return PROFILES[name]
        except KeyError as exc:
            raise ValueError(f"unknown video quality profile: {name}") from exc

    def target(self, options: dict | None = None) -> dict[str, object]:
        options = options or {}
        profile = self.profile(str(options.get("quality_profile", "high_quality")))
        fps = int(options.get("fps", profile.fps))
        if fps not in (24, 25, 30, 50, 60):
            raise ValueError("fps must be one of 24, 25, 30, 50 or 60")
        return {"profile": profile.name, "width": profile.width, "height": profile.height,
                "fps": fps, "min_bitrate_kbps": profile.min_bitrate_kbps,
                "smooth_motion": True, "stable_frame_timing": True}

    def validate_output(self, output: dict, target: dict) -> list[str]:
        issues: list[str] = []
        if not isinstance(output, dict):
            return ["output_metadata_missing"]
        for key in ("width", "height", "fps"):
            if key not in output:
                issues.append(f"output_{key}_missing")
        if issues:
            return issues
        if int(output["width"]) < int(target["width"]):
            issues.append("output_resolution_below_target")
        if int(output["height"]) < int(target["height"]):
            issues.append("output_resolution_below_target")
        if float(output["fps"]) != float(target["fps"]):
            issues.append("output_fps_mismatch")
        if output.get("frame_timing_stable") is False:
            issues.append("unstable_frame_timing")
        if output.get("corrupt") is True:
            issues.append("corrupt_media")
        return sorted(set(issues))
