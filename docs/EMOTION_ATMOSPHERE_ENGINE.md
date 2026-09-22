# Emotion & Atmosphere Engine

WETU treats realism as more than appearance. This layer converts a scene's
emotional intent into structured, persistent direction for characters,
environment, sound and camera.

## Contract

A scene can carry:
- emotional beats with causes and intensity;
- bodily signals and micro-expressions;
- environmental sound, motion, weather and lighting;
- sensory focus and camera guidance;
- continuity snapshots for later scenes.

The engine is provider-neutral. It does not pretend to render media itself.
A real renderer must consume this context and preserve it during generation.
