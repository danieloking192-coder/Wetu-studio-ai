# WETU Provider Strategy

WETU stays provider-neutral and uses a bounded fallback chain. OpenArt and Runway remain optional adapters; no credits are spent merely by having adapters installed.

## fal.ai
fal is a viable external provider to evaluate because it exposes a large model catalogue and a builder-grant program. Its current terms say usage is credit-metered and promotional/free credits expire after 90 days. The current Builder Grant advertises a 25 USD starter pack for eligible gen-media builders and larger packs for higher usage; applications are through approved partners. WETU therefore does not assume that a free daily API balance exists.

## Contract
A real provider must accept the WETU media request contract, return uri or asset_url, declare supported media kinds, expose failures clearly, and never receive secrets from the client UI.

FalMediaProvider is endpoint-configured. This avoids baking an unverified model-specific request schema into WETU.

## Free-access rule
Before a provider is connected to production, WETU must verify the actual account's remaining credits and capabilities. No provider connection is requested solely from a marketing claim.

## Fallback
MediaOrchestrator tries the requested provider first, then compatible configured providers, with a bounded attempt count. Local WETU generation remains a deterministic development fallback only; it is not represented as real AI media.
