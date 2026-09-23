# WETU Photo to Realistic Video

WETU now defines a first-class Character Identity pipeline:
1. Import a JPG, PNG or WEBP photo from the phone file picker.
2. Validate the file, record SHA-256 and store it in the private runtime area.
3. Turn the photo into a persistent character identity reference.
4. Send an image-to-video request to a configured provider with realistic motion and identity-preservation controls.
5. Keep identity metadata and the generation request linked for continuity.

fal documents image-to-video endpoints that accept an image URL plus a motion prompt, including multiple current video models. The deployment must provide a publicly reachable media URL to the configured provider.

## Safety and privacy
Real-person images require explicit consent confirmation. Provider credentials remain server-side.

## Reality boundary
The WETU code provides the application contract and provider-neutral orchestration. Realistic rendering requires a configured image-to-video provider and public media storage in deployment. Local WETU assets must never be described as real AI rendering.
