"""WETU economic core: separates user entitlements from real provider cost.

WETU credits are an internal accounting unit. They are deliberately not treated
as provider credits and never expose provider credentials. Apple-purchased
entitlements are tracked separately and have no expiration in this model.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import os
import threading
import uuid
from typing import Any

class AccountType(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"

@dataclass(frozen=True)
class ProviderRate:
    provider: str
    image: float = 0.02
    audio: float = 0.01
    video_per_second: float = 0.05
    edit: float = 0.03

DEFAULT_RATES = {
    "default": ProviderRate("default"),
    "wetu-local": ProviderRate("wetu-local", 0.0, 0.0, 0.0, 0.0),
}

@dataclass
class EconomicReservation:
    reservation_id: str
    account_type: AccountType
    kind: str
    units: int
    provider_cost: float
    credit_source: str = "none"
    status: str = "reserved"

@dataclass
class EconomicLedger:
    promotional_units: int = 30
    purchased_units: int = 0
    admin_internal_units: int = 0
    month_key: str = ""
    provider_cost_total: float = 0.0
    admin_provider_cost: float = 0.0
    user_provider_cost: float = 0.0
    events: list[dict[str, Any]] = field(default_factory=list)
    _reservations: dict[str, EconomicReservation] = field(default_factory=dict, repr=False)
    _lock: threading.RLock = field(default_factory=threading.RLock, repr=False)

    def __post_init__(self):
        with self._lock:
            self._roll_month()

    def _month(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m")

    def _roll_month(self) -> None:
        month = self._month()
        if self.month_key != month:
            self.month_key = month
            self.promotional_units = 30

    def resolve_account(self, requested: str | None, headers: Any | None = None) -> AccountType:
        requested = str(requested or "USER").upper()
        if requested != AccountType.ADMIN.value:
            return AccountType.USER
        configured = os.environ.get("WETU_ADMIN_KEY", "")
        supplied = ""
        if headers is not None:
            supplied = headers.get("X-WETU-ADMIN-KEY", "")
        if configured and supplied == configured:
            return AccountType.ADMIN
        raise PermissionError("admin role requires server-side WETU_ADMIN_KEY")

    def _rate(self, provider: str | None) -> ProviderRate:
        provider = provider or "default"
        return DEFAULT_RATES.get(provider, ProviderRate(provider))

    def estimate_provider_cost(self, kind: str, options: dict[str, Any] | None = None, provider: str | None = None) -> float:
        options = options or {}
        rate = self._rate(provider)
        if kind == "video":
            seconds = max(1, float(options.get("duration_seconds", 1)))
            return round(rate.video_per_second * seconds, 6)
        if kind == "audio":
            return rate.audio
        if kind in {"edit", "upscale"}:
            return rate.edit
        return rate.image

    def _units(self, kind: str, options: dict[str, Any] | None = None) -> int:
        base = {"image": 1, "audio": 2, "video": 10, "edit": 3, "upscale": 4}.get(kind, 1)
        if kind == "video":
            base *= max(1, int(float((options or {}).get("duration_seconds", 1))))
        return base

    def reserve(self, account_type: AccountType, kind: str, options: dict[str, Any] | None, provider_cost: float) -> EconomicReservation:
        with self._lock:
            self._roll_month()
            max_cost = float(os.environ.get("WETU_MAX_PROVIDER_COST", "2.00"))
            if provider_cost > max_cost:
                raise PermissionError(f"provider cost guard exceeded: {provider_cost:.2f} > {max_cost:.2f}")
            units = self._units(kind, options)
            credit_source = "admin"
            if account_type is AccountType.USER:
                if self.promotional_units >= units:
                    self.promotional_units -= units
                    credit_source = "promotional"
                elif self.promotional_units + self.purchased_units >= units:
                    remaining = units - self.promotional_units
                    self.promotional_units = 0
                    self.purchased_units -= remaining
                    credit_source = "mixed" if remaining < units else "purchased"
                else:
                    raise PermissionError("insufficient WETU credits")
            reservation = EconomicReservation(uuid.uuid4().hex, account_type, kind, units, provider_cost, credit_source)
            self._reservations[reservation.reservation_id] = reservation
            self.events.append(self._event(reservation, "reserved"))
            return reservation

    def commit(self, reservation: EconomicReservation) -> None:
        with self._lock:
            current = self._reservations.pop(reservation.reservation_id, None)
            if current is None or current.status != "reserved":
                return
            current.status = "committed"
            self.provider_cost_total += current.provider_cost
            if current.account_type is AccountType.ADMIN:
                self.admin_internal_units += current.units
                self.admin_provider_cost += current.provider_cost
            else:
                self.user_provider_cost += current.provider_cost
            self.events.append(self._event(current, "committed"))

    def refund(self, reservation: EconomicReservation) -> None:
        with self._lock:
            current = self._reservations.pop(reservation.reservation_id, None)
            if current is None or current.status != "reserved":
                return
            current.status = "refunded"
            if current.account_type is AccountType.USER:
                if current.credit_source == "promotional":
                    self.promotional_units += current.units
                elif current.credit_source == "purchased":
                    self.purchased_units += current.units
                elif current.credit_source == "mixed":
                    # Mixed reservations are conservatively returned to purchased balance
                    # because the promotional portion may have crossed a month boundary.
                    self.purchased_units += current.units
            self.events.append(self._event(current, "refunded"))

    def grant_purchased(self, units: int, source: str = "apple_iap") -> None:
        if units <= 0:
            raise ValueError("units must be positive")
        with self._lock:
            self.purchased_units += int(units)
            self.events.append({"at": datetime.now(timezone.utc).isoformat(),
                                "type": "purchased_grant", "units": int(units),
                                "source": source, "expires": None})

    def _event(self, reservation: EconomicReservation, status: str) -> dict[str, Any]:
        return {"at": datetime.now(timezone.utc).isoformat(), "type": "generation",
                "reservation_id": reservation.reservation_id, "account_type": reservation.account_type.value,
                "kind": reservation.kind, "units": reservation.units, "credit_source": reservation.credit_source,
                "provider_cost": reservation.provider_cost, "status": status}

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            self._roll_month()
            return {"user": {"promotional_units": self.promotional_units,
                             "purchased_units": self.purchased_units,
                             "purchased_units_expire": False},
                    "admin": {"credit_decrement": False,
                              "internal_units_logged": self.admin_internal_units,
                              "provider_cost_logged": round(self.admin_provider_cost, 6)},
                    "provider_cost_total": round(self.provider_cost_total, 6),
                    "month": self.month_key,
                    "cost_guard_max": float(os.environ.get("WETU_MAX_PROVIDER_COST", "2.00"))}

    def admin_snapshot(self) -> dict[str, Any]:
        data = self.snapshot()
        data["events"] = list(self.events[-100:])
        data["pending_reservations"] = len(self._reservations)
        return data
