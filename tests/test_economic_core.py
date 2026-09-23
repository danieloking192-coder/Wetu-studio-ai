import unittest
from unittest.mock import patch
from wetu_studio.economic_core import EconomicLedger, AccountType

class EconomicCoreTests(unittest.TestCase):
    def test_user_uses_promotional_before_purchased(self):
        ledger = EconomicLedger(promotional_units=3, purchased_units=10)
        r = ledger.reserve(AccountType.USER, "image", {}, 0.02)
        ledger.commit(r)
        self.assertEqual(ledger.promotional_units, 2)
        self.assertEqual(ledger.purchased_units, 10)

    def test_purchased_units_are_non_expiring(self):
        ledger = EconomicLedger(promotional_units=0, purchased_units=5)
        r = ledger.reserve(AccountType.USER, "image", {}, 0.02)
        ledger.commit(r)
        self.assertEqual(ledger.purchased_units, 4)
        self.assertFalse(ledger.snapshot()["user"]["purchased_units_expire"])

    def test_admin_does_not_decrement_user_credits_but_logs_provider_cost(self):
        ledger = EconomicLedger(promotional_units=30, purchased_units=10)
        r = ledger.reserve(AccountType.ADMIN, "image", {}, 0.02)
        ledger.commit(r)
        self.assertEqual(ledger.promotional_units, 30)
        self.assertEqual(ledger.purchased_units, 10)
        self.assertEqual(ledger.admin_provider_cost, 0.02)

    def test_failed_generation_refunds_user_credits(self):
        ledger = EconomicLedger(promotional_units=3)
        r = ledger.reserve(AccountType.USER, "image", {}, 0.02)
        ledger.refund(r)
        self.assertEqual(ledger.promotional_units, 3)

    def test_cost_guard_blocks_expensive_provider(self):
        ledger = EconomicLedger()
        with patch.dict("os.environ", {"WETU_MAX_PROVIDER_COST": "0.10"}):
            with self.assertRaises(PermissionError):
                ledger.reserve(AccountType.USER, "video", {"duration_seconds": 3}, 0.15)

    def test_admin_role_requires_server_key(self):
        ledger = EconomicLedger()
        with self.assertRaises(PermissionError):
            ledger.resolve_account("ADMIN", {"X-WETU-ADMIN-KEY": "wrong"})

if __name__ == "__main__":
    unittest.main()
