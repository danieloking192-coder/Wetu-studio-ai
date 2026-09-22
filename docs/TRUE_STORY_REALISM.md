# True Story Realism

WETU's true-story layer is designed for tragic and historical real events where emotional realism must not be confused with sensationalism.

## Modes

- **DOCUMENTARY_REALISM**: verified evidence has priority. Unknown details remain unknown.
- **DRAMATIZED_RECONSTRUCTION**: documented events remain traceable while reconstructed or dramatized details are explicitly disclosed.

## Evidence classes

Every factual element can be marked as:

- `VERIFIED_FACT`
- `RECONSTRUCTION`
- `DRAMATIZATION`
- `UNKNOWN`

A verified fact requires provenance. Invented dialogue or internal thoughts cannot be silently presented as documented fact.

## Dignity and realism

The engine keeps victim/survivor dignity explicit, rejects dehumanizing direction, and flags sensationalism in documentary mode. Emotional and atmospheric direction can be supplied separately by the Emotion & Atmosphere Engine.

The renderer is responsible for actual media generation; this layer provides structured, auditable production intent.
