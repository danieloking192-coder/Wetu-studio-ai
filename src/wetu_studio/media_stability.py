"""Deterministic media quality gates for smooth, corruption-resistant output."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class StabilityReport:
    passed: bool
    issues: tuple[str,...]
    checks: tuple[str,...]

class MediaStabilityEngine:
    REQUIRED_VIDEO_FIELDS=("width","height","duration_seconds")
    def validate(self,output:dict[str,Any],target:dict[str,Any]|None=None)->StabilityReport:
        issues=[]; checks=["metadata","duration","dimensions","fps","bitrate","corruption"]
        if not isinstance(output,dict): return StabilityReport(False,("invalid_output",),tuple(checks))
        for key in self.REQUIRED_VIDEO_FIELDS:
            if key not in output: issues.append("missing_"+key)
        if "duration_seconds" in output:
            try:
                if float(output["duration_seconds"])<=0: issues.append("non_positive_duration")
            except (TypeError,ValueError): issues.append("invalid_duration")
        if "fps" in output:
            try:
                if not 12<=float(output["fps"])<=120: issues.append("fps_out_of_safe_range")
            except (TypeError,ValueError): issues.append("invalid_fps")
        if "width" in output and "height" in output:
            try:
                if int(output["width"])<256 or int(output["height"])<144: issues.append("resolution_too_low")
            except (TypeError,ValueError): issues.append("invalid_dimensions")
        if output.get("corrupt") is True or output.get("decode_ok") is False: issues.append("decode_failure")
        if output.get("av_sync_ms") is not None:
            try:
                if abs(float(output["av_sync_ms"]))>250: issues.append("av_sync_out_of_tolerance")
            except (TypeError,ValueError): issues.append("invalid_av_sync")
        if target:
            for k in ("width","height"):
                if k in output and k in target and int(output[k])>int(target[k]): issues.append(k+"_exceeds_delivery_target")
            if "fps" in output and "fps" in target and float(output["fps"])>float(target["fps"])+0.1: issues.append("fps_exceeds_delivery_target")
        return StabilityReport(not issues,tuple(sorted(set(issues))),tuple(checks))
