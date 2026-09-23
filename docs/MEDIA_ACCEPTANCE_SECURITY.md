# WETU Media Acceptance & Security Gate

The gate sits between an external media provider and WETU delivery.

Flow:
1. Provider returns an HTTPS media URL.
2. WETU applies an explicit provider-host allowlist and rejects non-public DNS destinations.
3. The file is downloaded with strict size and timeout limits.
4. Antivirus/signature scanning runs on the downloaded file.
5. ffprobe validates the actual container and streams.
6. FFmpeg performs a full video decode with strict error detection.
7. WETU runs the stability gate for duration, resolution and FPS.
8. Only accepted media proceeds to transcoding/delivery.

The URL policy follows OWASP guidance to allowlist trusted destinations and avoid accepting arbitrary complete URLs. FFprobe can inspect containers and individual streams, and FFmpeg supports strict decoding error detection.

Security boundary:
- Provider credentials never enter the browser.
- Provider output is untrusted input.
- Failed security, probe, decode or stability checks are rejected.
- This does not promise zero malware or zero playback bugs; it provides deterministic barriers and observable rejection.

Deployment requirements:
- FFmpeg/ffprobe installed.
- ClamAV/clamd configured when WETU_REQUIRE_ANTIVIRUS=1.
- WETU_PROVIDER_ALLOWED_HOSTS should contain only actual provider output hosts.
- Persistent media storage should be external to ephemeral containers in production.
