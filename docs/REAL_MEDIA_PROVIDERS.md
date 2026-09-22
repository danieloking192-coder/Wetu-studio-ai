# WETU Real Media Providers

WETU now has a generic HTTP adapter for real generation services.

## Configuration

Set environment variables outside Git:
- WETU_MEDIA_ENDPOINT — endpoint
- WETU_MEDIA_NAME — provider name (optional)
- WETU_MEDIA_API_KEY — secret (optional; never commit it)
- WETU_MEDIA_TIMEOUT — request timeout in seconds

The adapter sends a provider-neutral JSON contract containing request ID, project/scene IDs, media kind, prompt, references, options and production context.

A real provider must return a JSON object. WETU reads model and uri (or asset_url) and preserves the provider response in asset metadata.

wetu-local remains available for deterministic development and explicitly returns real_media=false.

Vendor-specific authentication and payload conversion belong in dedicated adapters or a secure gateway; WETU does not hard-code vendor secrets or pretend that a local manifest is real media.
