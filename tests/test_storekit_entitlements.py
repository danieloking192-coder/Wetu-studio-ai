from wetu_studio.economic_core import EconomicLedger
from wetu_studio.storekit_entitlements import StoreKitEntitlementService, PurchaseValidationError

def test_unverified_purchase_cannot_grant():
    ledger = EconomicLedger()
    service = StoreKitEntitlementService(ledger)
    try:
        service.validate_and_grant({"product_id":"wetu_100","transaction_id":"tx-1","verified":False})
    except PurchaseValidationError:
        pass
    else:
        raise AssertionError("unverified purchase granted")
    assert ledger.snapshot()["user"]["purchased_units"] == 0

def test_verified_purchase_is_idempotent():
    ledger = EconomicLedger()
    service = StoreKitEntitlementService(ledger)
    tx={"product_id":"wetu_100","transaction_id":"tx-1","verified":True}
    assert service.validate_and_grant(tx)["units_granted"] == 100
    assert service.validate_and_grant(tx)["duplicate"] is True
    assert ledger.snapshot()["user"]["purchased_units"] == 100
