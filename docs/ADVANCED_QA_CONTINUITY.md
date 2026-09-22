# WETU Advanced QA & Continuity Guard

Before export, WETU checks six production invariants:

1. character identity
2. world context
3. scene context
4. asset traceability
5. reference traceability
6. timeline integrity

The Continuity Guard also compares scene context and reports explicit changes in character IDs or world ID.

QA is deterministic and explainable. A failed check blocks a production from being marked ready for export. It does not claim to judge subjective cinematic quality; provider-specific visual/audio inspection can be added through QA adapters.