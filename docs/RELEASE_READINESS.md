# WETU Release Readiness

## Current state

WETU's integrated application spine is implemented and continuously tested:

- Creator workspace and project persistence
- Character DNA, World DNA and Scene Memory
- provider-neutral media orchestration with fallback
- mobile-first transcoding and adaptive delivery
- post-production timeline, captions and export quality gates
- usage limits and economic accounting
- protected admin accounting
- Apple StoreKit entitlement boundary
- persistent bounded runtime jobs and provider health telemetry
- PWA shell and production API security controls

## What the automated gate proves

The release-readiness test verifies that the major product modules and required production contracts are present together. The full WETU Integration QA remains the authoritative integration check.

## What is still external

A production launch still requires real deployment infrastructure, real AI-provider credentials/credits, live Apple signed-transaction verification, and final mobile-store packaging/review. These are external integrations, not silently simulated by WETU.

## Principle

No green test is treated as proof of real AI generation when no real provider is configured. WETU reports simulated/local media separately from real provider media.
