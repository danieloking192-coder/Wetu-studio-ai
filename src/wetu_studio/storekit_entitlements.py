"""Server-side entitlement boundary for Apple StoreKit purchases.

This module intentionally does not trust client-supplied purchase success.
A verified transaction is required before purchased WETU units are granted.
The verifier is provider-neutral so the iOS StoreKit adapter can be added later.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
import threading
from typing import Any

@dataclass(frozen=True)
class ProductEntitlement:
    product_id: str
    units: int
    kind: str = "consumable"

PRODUCTS = {
    "wetu_100": ProductEntitlement("wetu_100", 100),
    "wetu_600": ProductEntitlement("wetu_600", 600),
    "wetu_3000": ProductEntitlement("wetu_3000", 3000),
}

class PurchaseValidationError(ValueError):
    pass

class StoreKitEntitlementService:
    def __init__(self, economic_ledger):
        self.economic_ledger = economic_ledger
        self._seen_transactions: set[str] = set()
        self._lock = threading.RLock()

    def catalog(self) -> list[dict[str, Any]]:
        return [{"product_id": x.product_id, "units": x.units, "kind": x.kind, "expires": False}
                for x in PRODUCTS.values()]

    def validate_and_grant(self, transaction: dict[str, Any]) -> dict[str, Any]:
        product_id = transaction.get("product_id")
        transaction_id = transaction.get("transaction_id")
        verified = transaction.get("verified") is True
        if product_id not in PRODUCTS:
            raise PurchaseValidationError("unknown product")
        if not isinstance(transaction_id, str) or not transaction_id or len(transaction_id) > 256:
            raise PurchaseValidationError("invalid transaction_id")
        if not verified:
            raise PurchaseValidationError("transaction is not server-verified")
        with self._lock:
            if transaction_id in self._seen_transactions:
                return {"ok": True, "duplicate": True, "product_id": product_id, "transaction_id": transaction_id}
            entitlement = PRODUCTS[product_id]
            self.economic_ledger.grant_purchased(entitlement.units, source="apple_iap_verified")
            self._seen_transactions.add(transaction_id)
            return {"ok": True, "duplicate": False, "product_id": product_id,
                    "transaction_id": transaction_id, "units_granted": entitlement.units,
                    "granted_at": datetime.now(timezone.utc).isoformat()}
