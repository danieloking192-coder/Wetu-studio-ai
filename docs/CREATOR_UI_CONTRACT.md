# WETU Creator UI

A provider-neutral, production-memory-driven Creator UI contract.

## Workspaces
Project | Characters | World / City | Script | Storyboard | Generate | Audio | Timeline | QA | Export

## State contract
Every workspace receives the same project context:
project_id, CharacterDNA, WorldDNA, SceneMemory, ProductionMemory.

## Interaction rules
- Never ask the creator to re-enter persistent identity or world information when it is already known.
- Changes create explicit versions/events.
- Generation results always retain provider/model provenance.
- Rejected variants remain accessible.
- Continuity and QA findings are visible before export.
- Export is explicit and never silently publishes.

## Application shell
The reference implementation below is dependency-free HTML/CSS/JS so the prototype can run immediately in a browser and can later be replaced by React without changing the domain contract.
