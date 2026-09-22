# WETU Media Pipeline

WETU now has a provider-neutral media layer between Creator Core and external generation services.

Flow:
Project -> Character DNA / World DNA -> Scene Memory -> Context Assembly -> MediaRequest -> Provider Registry -> MediaAsset -> Realism QA -> Production Memory -> Timeline -> Export.

The core recognizes image, video, and audio. Providers advertise capabilities and implement one stable generate boundary. Provider-specific API payloads stay inside adapters, never inside Character DNA, World DNA, Scene Memory, or the UI.

Every asset gets a stable ID, provider/model metadata, media type, reference traceability and QA status. Timeline validation is deterministic.

The included wetu-local provider produces a manifest URI only. It is a development/test provider, not a real media generator.

Real providers must be implemented as separate adapters and configured with credentials outside source control. This architecture does not pretend an external provider is live when no adapter/credentials exist.