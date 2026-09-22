# WETU Creator Runtime

The Creator prototype is now connected to a dependency-free Python HTTP runtime.

## Start

From the repository root:

    python run_creator.py

Then open:

    http://127.0.0.1:8787/

## API

- GET /api/state — current production state
- POST /api/characters — create/update Character DNA
- POST /api/worlds — create/update World DNA
- POST /api/scenes — create Scene Memory
- POST /api/generate — execute a provider-neutral generation

The included demo provider is deliberately local and deterministic. It proves the orchestration contract without pretending to be a real media-generation provider.

## Production path

A real image/video/audio provider can be added behind ProviderAdapter without changing Character DNA, World DNA, Scene Memory, Production Memory, QA, or the Creator UI.

The next integration boundary is therefore provider credentials + adapter implementation, not a rewrite of the Creator architecture.
