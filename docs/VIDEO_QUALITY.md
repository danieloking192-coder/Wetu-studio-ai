# WETU Video Quality & Smoothness

WETU treats video smoothness and quality as production contracts, not cosmetic settings.

## Profiles

- **smooth**: 1280×720 at 30 FPS, for lightweight previews.
- **high_quality**: 1920×1080 at 30 FPS, the default production target.
- **ultra_hd**: 3840×2160 at 30 FPS, with optional 50/60 FPS when the provider supports it.

The quality engine validates requested targets and checks provider-reported output metadata. It does **not** falsely claim that a provider rendered HD/4K: an output is only considered compliant when its reported resolution, FPS, and frame-timing metadata meet the target.

Smoothness checks include stable frame timing, consistent FPS, and corruption detection. Future real providers must expose measurable output metadata so WETU can reject or retry non-compliant renders.
