# WETU StoreKit Entitlements

## Commercial boundary

The server is authoritative for purchased WETU credits. A client must never be able to grant itself credits by posting an arbitrary amount.

The StoreKit flow is:

1. iOS obtains the App Store transaction.
2. WETU sends the signed transaction/JWS to the server.
3. A future StoreKit server adapter verifies Apple's signed transaction data.
4. Only after verification does the server call the entitlement service.
5. The transaction ID is idempotent: replaying the same transaction cannot grant credits twice.
6. Purchased credits remain non-expiring in the entitlement ledger.

This repository now contains the server-side boundary and idempotency contract. It does **not** claim that Apple transaction verification is live until the iOS StoreKit adapter and Apple's signed-transaction verification are deployed.
