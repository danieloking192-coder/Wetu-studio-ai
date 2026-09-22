# WETU STUDIO AI — Reference Engine Policy

Status: CORE PRODUCT FOUNDATION

The Reference Engine converts a saved character identity into a deterministic reference record that downstream image/video providers can consume.

## Requirements
- A character must have a non-empty visual identity.
- The reference preserves the character ID, visual signature and selected wardrobe.
- Every reference receives a SHA-256 content hash.
- Provider-specific generation adapters consume the reference; the core engine does not depend on one provider.
- References are versionable and auditable through metadata.
- A mismatch between a saved reference and the current character identity must be detected, not silently rewritten.

## Photorealism
The reference layer preserves the information required to pursue high-end photorealistic generation. Actual visual fidelity remains dependent on the connected generation provider/model.

## Identity safety
Real-person likeness continues to follow IDENTITY_LIKENESS_POLICY.md. The Reference Engine does not create or infer authorization.
