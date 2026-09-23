"""Usage metering and plan limits for WETU Studio."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import RLock
from typing import Any

@dataclass(frozen=True)
class Plan:
    name: str
    monthly_units: int
    daily_generation_limit: int
    included_video_seconds: int
    features: tuple[str, ...]

PLANS = {
    "FREE": Plan("FREE", 30, 5, 3, ("image", "audio", "480p_delivery")),
    "CREATOR": Plan("CREATOR", 500, 40, 60, ("image", "audio", "video", "720p_delivery", "captions")),
    "PRO": Plan("PRO", 2500, 200, 300, ("image", "audio", "video", "1080p_delivery", "captions", "continuity")),
}
UNIT_COSTS = {"image": 1, "audio": 2, "video": 10, "upscale": 4, "edit": 3}

@dataclass
class UsageLedger:
    plan: str = "FREE"
    month_units: int = 0
    day_generations: int = 0
    day_key: str = ""
    events: list[dict[str, Any]] = field(default_factory=list)
    _lock: RLock = field(default_factory=RLock, repr=False, compare=False)

    def _today(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def _roll_day(self) -> None:
        today = self._today()
        if self.day_key != today:
            self.day_key, self.day_generations = today, 0

    def estimate_units(self, kind: str, options: dict[str, Any] | None = None) -> int:
        options = options or {}
        base = UNIT_COSTS.get(kind, 1)
        if kind == "video":
            seconds = max(1, int(float(options.get("duration_seconds", 1))))
            base *= seconds
        return base

    def reserve(self, kind: str, options: dict[str, Any] | None = None) -> int:
        with self._lock:
            self._roll_day()
            plan = PLANS.get(self.plan, PLANS["FREE"])
            units = self.estimate_units(kind, options)
            if self.day_generations >= plan.daily_generation_limit:
                raise PermissionError("daily generation limit reached")
            if self.month_units + units > plan.monthly_units:
                raise PermissionError("monthly usage limit reached")
            if kind == "video":
                seconds = max(1, int(float((options or {}).get("duration_seconds", 1))))
                if seconds > plan.included_video_seconds:
                    raise PermissionError("video duration exceeds plan limit")
            self.month_units += units
            self.day_generations += 1
            self.events.append({"at": datetime.now(timezone.utc).isoformat(), "kind": kind, "units": units, "status": "reserved"})
            return units

    def refund(self, units: int, kind: str) -> None:
        with self._lock:
            self.month_units = max(0, self.month_units - max(0, int(units)))
            self.day_generations = max(0, self.day_generations - 1)
            self.events.append({"at": datetime.now(timezone.utc).isoformat(), "kind": kind, "units": int(units), "status": "refunded"})

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            self._roll_day()
            plan = PLANS.get(self.plan, PLANS["FREE"])
            return {"plan": plan.name, "month_units_used": self.month_units, "month_units_limit": plan.monthly_units,
                    "day_generations_used": self.day_generations, "day_generations_limit": plan.daily_generation_limit,
                    "included_video_seconds": plan.included_video_seconds, "features": list(plan.features)}
