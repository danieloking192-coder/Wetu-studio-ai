# WETU Studio AI — Adaptive Streaming Contract

## Goal
Deliver the smallest suitable video representation over mobile data/Wi-Fi while
keeping the original master untouched.

## Renditions
- **480p Saver** — default for unknown/weak/offline conditions.
- **720p Mobile** — default for normal conditions.
- **1080p Standard** — selected for good conditions.

The policy is intentionally conservative: an unknown network falls back to
480p rather than spending data aggressively.

## HLS / DASH
The contract prepares provider-neutral:
- HLS master playlist + three variant playlists.
- DASH manifest + three variant representations.

This is a packaging contract only. It does **not** claim that a CDN, packager,
or production player has already been deployed.

## Selection
An explicit user/profile choice may override network policy. The master remains
immutable and is retained separately from delivery renditions.

## Next production integration
1. Connect the contract to the actual packager.
2. Generate HLS/DASH segments from validated renditions.
3. Publish manifests through the media storage/CDN layer.
4. Let the player switch variants using measured bandwidth/buffer state.
5. Re-run integrity and data-usage tests end-to-end.
