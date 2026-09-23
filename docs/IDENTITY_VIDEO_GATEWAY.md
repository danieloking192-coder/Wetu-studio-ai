# WETU Identity Video Gateway

WETU now has a concrete real-provider path for photo-to-realistic-video without requiring the WETU server to expose a user's portrait publicly.

Flow:
1. Phone uploads the portrait to WETU over the authenticated API.
2. WETU stores the identity privately and requires consent for a real person.
3. WETU server uploads the portrait directly to fal.ai temporary storage.
4. WETU sends the temporary fal URL, prompt, duration and resolution to the configured image-to-video model.
5. fal returns the generated video URL.
6. WETU returns that provider asset to its normal media pipeline.

The browser never receives FAL_KEY.

## Configuration
Install: pip install "wetu-studio-ai[fal]"

Server environment:
- FAL_KEY: fal API key, server-side only.
- FAL_VIDEO_MODEL: exact fal model/endpoint selected by deployment.
- FAL_VIDEO_ARGUMENTS_JSON: optional JSON object template; {image_url}, {prompt}, {duration}, {resolution} are replaced server-side.
- FAL_VIDEO_TIMEOUT: optional, default 300 seconds.

The default arguments are image_url, prompt, duration and resolution. Models differ, so WETU deliberately keeps the model-specific schema configurable.

## Privacy
The identity image is uploaded with a 1h lifecycle. WETU does not expose its local identity file as the provider input. The provider result URL remains provider-hosted until a future authenticated media-ingest layer copies it into WETU storage.

## Honest runtime boundary
CI uses a fake fal client and consumes no real credits. Without FAL_KEY or FAL_VIDEO_MODEL, WETU does not claim real AI rendering. Real rendering requires an actual fal account, model access and available credits.


## Provider output acceptance

When WETU_ACCEPT_PROVIDER_MEDIA is enabled (the production default when the fal gateway is created from environment), provider video is not trusted merely because the provider returned a URL. WETU validates HTTPS and provider host policy, rejects non-public DNS destinations, downloads with bounded size/time, scans the file, probes it with ffprobe, runs a full FFmpeg decode, and applies the media stability gate before accepting the asset.

Configure WETU_PROVIDER_ALLOWED_HOSTS with the exact provider output hostnames used by the deployment. Do not paste arbitrary user-supplied hosts into this setting.
