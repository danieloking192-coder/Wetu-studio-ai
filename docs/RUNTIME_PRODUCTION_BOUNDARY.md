# WETU Runtime Production Boundary

This block adds persistent media-job state, provider health metrics and bounded runtime counters.

- Jobs are persisted atomically to a local JSON store and survive process restart.
- The store is bounded to prevent unbounded disk growth.
- Provider failures are counted without storing provider secrets.
- Runtime counters are in-memory and intentionally lightweight.
- This is not a distributed queue: horizontal workers and a shared database remain future deployment work.
- Real provider generation still requires configured credentials and provider capability; WETU never invents provider credits or availability.
