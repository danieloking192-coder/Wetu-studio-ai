# WETU Container Deployment Boundary

WETU can now be packaged as a reproducible Python 3.11 container with FFmpeg.

## Runtime contract

- HTTP listener: `0.0.0.0:8787` by default
- `WETU_HOST` and `WETU_PORT` override the bind address
- `/api/runtime/health` is the container health target
- the process runs as a non-root user
- `.wetu` is intentionally excluded from the image and should be mounted as persistent storage
- provider credentials remain environment/server configuration; they are never baked into the image

## Production boundary

The container is deployment-ready, but this does not by itself deploy WETU to a public cloud or activate a real AI provider.

A real deployment still needs:
1. a container registry or deployment platform;
2. persistent storage for project/runtime state;
3. TLS/HTTPS and a domain;
4. server-side provider credentials and verified provider credits;
5. Apple signed-transaction verification before live IAP entitlement granting.

The container contract deliberately stops at a reproducible runtime boundary instead of pretending those external services are already active.
