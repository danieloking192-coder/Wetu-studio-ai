# WETU Creator Application Core

## Purpose

The Creator Application Core is the single application-facing orchestration boundary between the WETU creator interface, persistent production memory, existing WETU engines, QA/continuity gates and external media providers.

## Canonical workflow

Project → Character DNA / World DNA → Script → Scene Memory → Storyboard → Context Assembly → Generate → Audio → Timeline → QA / Continuity Guard → Export → Production Memory.

No downstream operation silently destroys upstream production state.

## Persistent objects

- CharacterDNA: identity, face, body, hair, eyes, wardrobe, traits and voice profile.
- WorldDNA: geography, architecture, environment, culture and landmarks.
- SceneMemory: participants, world, sequence, predecessor scenes, language and scene state.
- GenerationRecord: provider/model provenance, prompt, status and QA metadata.
- ProductionDecision: selected and rejected generations plus rationale.
- ProductionMemory: append-oriented history of generations, decisions, references and events.

## Provider-neutral boundary

Providers implement a small adapter contract: generate(kind, prompt, context) returns provider-neutral metadata. The Creator Core does not import vendor SDKs.

## QA and continuity

Continuity can block generation before provider execution. QA runs after provider execution and records its result with the generation. Future implementations can add specialized checks for identity, anatomy, hands, wardrobe, materials, lighting, camera, environment, motion, audio and subtitles.

## UI contract

The Creator UI should expose ten workspaces backed by the same project state:

1. Project
2. Characters
3. World / City
4. Script
5. Storyboard
6. Generate
7. Audio
8. Timeline
9. QA
10. Export

## Reliability and security

- Provider credentials never enter ProductionMemory.
- Project state is isolated by project ID.
- Generation IDs make jobs traceable and can support idempotency.
- Provider failures must not corrupt project state.
- Export and publishing remain deliberate human actions.
