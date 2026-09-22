# WETU STUDIO AI — Storyboard & Continuity Policy

Status: CORE PRODUCT DESIGN

## Storyboard
The storyboard is the bridge between script and generation. Each shot records scene, framing/type, description, characters, location and wardrobe selections.

## Character persistence
Every shot may reference saved character IDs rather than redefining appearance. This preserves a stable identity source for generation adapters.

## Wardrobe continuity
Wardrobe is attached to the character per shot. A deliberate outfit change is explicit; an accidental change is a continuity issue.

## Visual continuity
The Continuity Engine compares deterministic visual signatures between snapshots. A mismatch is surfaced rather than silently rewritten.

## Quality principle
WETU should prefer traceability and explicit correction over silently changing a character to hide a generation inconsistency.

## Realism target
Storyboard and continuity metadata must preserve the inputs needed to pursue cinematic photorealism, but do not guarantee the capabilities of any external generation provider.
