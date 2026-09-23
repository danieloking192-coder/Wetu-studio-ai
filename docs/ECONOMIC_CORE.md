# WETU Economic Core

WETU separates user entitlements, administrator accounting, and real external provider cost.

## Rules

- New users receive a monthly promotional allowance in the economic ledger.
- Purchased credits are a separate balance and are modeled as non-expiring.
- Admin generations do not decrement customer balances, but real provider cost is still logged.
- Admin access requires the server-side WETU_ADMIN_KEY; a client cannot grant itself admin mode.
- WETU_MAX_PROVIDER_COST is a hard cost guard.
- Provider credentials and provider balances are never exposed to clients.
- WETU credits are internal units, not provider credits.

## Apple boundary

When StoreKit is integrated, Apple IAP transactions should be validated server-side before grant_purchased() is called. Purchased IAP credits are modeled as non-expiring to respect Apple's current App Review rule for credits acquired through IAP.

The economic core is therefore ready for the later StoreKit/server transaction layer without pretending that an unvalidated purchase is complete.

## CI verification
Final integration verification is required before merge.
