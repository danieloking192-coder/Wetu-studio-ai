# WETU Studio AI — Generation, Audio, Editing & QA Policy

Status: CORE PRODUCT FOUNDATION / PROVIDER-NEUTRAL.

## Generation
Generation requests are immutable records linking project, shot, prompt, references, provider/model metadata and creation time. Media artifacts receive SHA-256 content hashes. Provider adapters own actual generation; WETU does not claim a provider-independent generation capability until connected and tested.

## Audio
Dialogue keeps speaker identity, source language, optional voice ID and timing. Initial languages: French, English, Spanish, Portuguese, Arabic, Swahili and Lingala. Music and SFX remain separate references so editing can mix them without replacing dialogue.

## Editing
A timeline contains typed media items with millisecond timing and layers. IDs are unique. Overlap is evaluated within the same layer; different layers may intentionally overlap.

## Quality gate
QA checks include identity continuity and timing at minimum. BLOCKER failures prevent a project from being considered ready. Future checks cover visual realism, hands/face anomalies, wardrobe/location continuity, audio sync, subtitle consistency, rights/provenance and export integrity.

## Testing rule
Pure Python foundations must have executable unit tests. External video/audio providers require integration tests only after credentials and provider adapters are available. No successful external generation is claimed from architecture alone.
