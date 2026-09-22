# WETU STUDIO AI — Character Creation Studio

Status: CORE PRODUCT DESIGN

## Character Creator

WETU must provide a dedicated Character Creator before production workflows. A user can build an original realistic character from a structured visual identity profile and keep that identity stable across scenes.

## Visual controls

The profile supports face, skin, hair, eyes, body, age and distinctive signature features. The system stores a deterministic visual signature so downstream generation adapters can reuse the same identity references.

## Wardrobe Studio

Wardrobe is selectable rather than mandatory. A character can have zero or many outfits, choose a current outfit, change clothing between scenes, and preserve continuity metadata for each choice.

Examples include everyday clothing, formal wear, sportswear, uniforms, costumes and custom fictional designs.

## Realism and recognizability

The goal is a believable human appearance and persistent recognizability of the intended character. Generation quality depends on the selected generation provider/model; WETU's role is to preserve identity specifications and references rather than promise pixel-perfect results.

## Real-person likeness

Identifiable real-person likeness remains governed by IDENTITY_LIKENESS_POLICY.md and requires appropriate authorization before production use.

## UX direction

The application should expose a dedicated entry point such as **Create Character**, followed by:
1. Identity
2. Face & body
3. Hair & eyes
4. Signature features
5. Wardrobe
6. Preview/reference
7. Save Character

The same saved character can then be reused by Script, Storyboard, Generation and Continuity modules.
