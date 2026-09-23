# WETU Security & Media Quality Defense

WETU uses defense in depth rather than a single antivirus check.

## Upload barriers
1. Authorized request boundary and body-size limits.
2. MIME/type allowlist.
3. Filename normalization and generated storage names.
4. Maximum file size.
5. SHA-256 identity.
6. Magic-byte signature validation to detect MIME spoofing.
7. Antivirus hook using ClamAV (clamscan/clamdscan) when available.
8. Optional fail-closed mode with WETU_REQUIRE_ANTIVIRUS=1.
9. Private storage outside the public web surface.
10. Only validated media enters the AI/provider pipeline.

## Video smoothness gates
A provider URL alone does not make video production-ready. WETU checks metadata, duration, dimensions, frame rate, corruption/decode status and A/V sync when available. Existing delivery profiles then constrain bitrate and resolution.

Defective media should be rejected/retried rather than shown to the user.

## Supply chain
GitHub artifact attestations can establish build provenance, while dependency review helps detect risky dependency changes. Attestations are provenance evidence, not a guarantee that an artifact is safe.

## Honest limitation
No system can promise zero malware or zero playback bugs. WETU therefore uses multiple independent barriers and rejects assets that fail validation.
