# Production Realism Orchestrator

WETU now has one provider-neutral integration boundary that combines:

- persistent Character DNA;
- persistent World DNA;
- Scene Memory and Production Memory;
- Emotion & Atmosphere;
- True Story provenance and dignity rules;
- continuity and disclosure contracts.

The orchestrator does **not** render media. It produces a structured scene context for an image/video/audio provider and validates the context before rendering.

## Endpoint

The creator server exposes `POST /api/production-realism`.

The response contains the fused context, continuity snapshot, and validation issues. A renderer should be called only when `ok=true`.

## Principle

> WETU ne mémorise pas seulement le prompt. WETU mémorise la production.

This is the integration layer that turns that principle into a single scene contract.
