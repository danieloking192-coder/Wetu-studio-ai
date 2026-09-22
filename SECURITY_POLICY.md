# WETU STUDIO AI — Security Policy

## Mandatory controls
- Secrets only through secure environment/secret management.
- Never commit API keys, tokens or private credentials.
- Authentication and authorization are separate controls.
- Least-privilege access for users, services and providers.
- Isolate projects and their assets.
- Validate uploaded files and generated exports.
- Record sensitive actions in an auditable log.
- Preserve provenance and rights/licensing metadata.
- Require consent/rights checks for protected or third-party material.
- External providers are isolated behind adapters and cannot compromise the core pipeline.
- Provider failure must degrade safely without exposing secrets or corrupting project state.

## Release rule
Security-sensitive features require tests and review evidence before production release.
