# WETU Studio AI — Security Baseline

## Security objective

WETU treats production memory, creative assets, references, provider credentials and project state as protected application data. Security controls are layered; no single control is treated as sufficient.

## Controls implemented

- Local-first binding: the development server binds to 127.0.0.1 by default.
- Optional bearer authentication: set WETU_AUTH_TOKEN to require Authorization: Bearer on API routes.
- Request-size limit: JSON POST bodies are capped by WETU_MAX_BODY_BYTES (2 MiB by default).
- Rate limiting: per-client in-memory request throttling is enabled by default (120 requests / 60 seconds).
- Path traversal defense: project identifiers are restricted to a bounded safe grammar and are never used as arbitrary paths.
- Atomic persistence: state is written to a temporary file and replaced atomically.
- File permissions: persisted state/index files are restricted to owner read/write where supported.
- Security headers: API/UI responses set MIME sniffing, framing, referrer, caching, permissions and CSP protections.
- No credential storage in source: external provider credentials are obtained from environment configuration.
- Provider isolation: provider adapters remain behind WETU interfaces; local deterministic manifests are explicitly distinguished from real media.
- Continuity/QA gates: generation is designed to pass through identity, world, scene-memory and realism checks instead of silently claiming validation.
- Persistent project isolation: each project has its own state file and project index.
- Client-side output escaping: dynamic dashboard values are escaped before being inserted into the DOM.

## Deployment responsibilities

For public deployment, add TLS termination, a production-grade identity provider, durable distributed rate limiting, secret management, audit-log retention, database access controls, backups, dependency scanning, SAST/DAST, network isolation and centralized monitoring.

WETU does not claim that a prototype HTTP server is production-internet hardened merely because these baseline controls exist.

## Security regression coverage

Security tests cover response headers, bounded payloads, project-ID traversal rejection and state-file permissions. Every security change must keep the integration suite green before release.
