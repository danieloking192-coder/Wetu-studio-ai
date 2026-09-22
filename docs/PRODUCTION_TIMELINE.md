# WETU Production Timeline

The production timeline turns generated MediaAssets into an ordered audiovisual production.

Flow:

Project → Scene Memory → Media Assets → Timeline → Validation → QA → Export.

## Supported layers

- VIDEO
- AUDIO
- MUSIC
- SFX
- SUBTITLE

Each item retains its asset ID, scene ID, timing, layer and metadata. The timeline validates overlapping items on the same layer and computes total production duration.

This is an orchestration layer: it does not pretend to be a full nonlinear video renderer. Rendering/export adapters remain provider/tool specific.