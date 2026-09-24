"""Small, dependency-free security controls for WETU request and file boundaries."""
from __future__ import annotations

import ipaddress
import os
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

SAFE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
ALLOWED_MEDIA_SCHEMES = {"https", "http", "memory"}
BLOCKED_HOSTNAMES = {"localhost", "localhost.localdomain", "ip6-localhost", "ip6-loopback", "0.0.0.0", "[::]"}

def validate_project_id(project_id: str) -> str:
    if not isinstance(project_id, str) or not SAFE_ID_RE.fullmatch(project_id):
        raise ValueError("invalid project_id")
    return project_id

def validate_content_length(value: str | None, maximum: int) -> int:
    if value is None:
        raise ValueError("Content-Length required")
    try:
        size = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("invalid Content-Length") from exc
    if size < 0 or size > maximum:
        raise ValueError("request body too large")
    return size

def safe_project_path(root: Path, project_id: str, suffix: str = ".json") -> Path:
    project_id = validate_project_id(project_id)
    base = root.resolve()
    candidate = (base / f"{project_id}{suffix}").resolve()
    if candidate.parent != base:
        raise ValueError("unsafe project path")
    return candidate

def _allowed_media_hosts() -> set[str]:
    raw = os.getenv("WETU_MEDIA_ALLOWED_HOSTS", "")
    return {item.strip().lower().rstrip(".") for item in raw.split(",") if item.strip()}

def validate_media_uri(uri: str, *, require_https: bool = False) -> str:
    if not isinstance(uri, str) or not uri.strip():
        raise ValueError("media URI required")
    parsed = urlparse(uri.strip())
    if parsed.scheme not in ALLOWED_MEDIA_SCHEMES:
        raise ValueError("unsupported media URI scheme")
    if parsed.scheme == "memory":
        if parsed.netloc:
            raise ValueError("memory media URI must not contain a network host")
        return uri
    if require_https and parsed.scheme != "https":
        raise ValueError("HTTPS media URI required")
    hostname = (parsed.hostname or "").lower().rstrip(".")
    if not hostname:
        raise ValueError("invalid HTTP media URI")
    if hostname in BLOCKED_HOSTNAMES:
        raise ValueError("local media destination is blocked")
    try:
        ip = ipaddress.ip_address(hostname)
    except ValueError:
        ip = None
    if ip is not None and (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast or ip.is_unspecified):
        raise ValueError("private or local media destination is blocked")
    allowed = _allowed_media_hosts()
    if allowed and hostname not in allowed and not any(hostname.endswith("." + host) for host in allowed):
        raise ValueError("media host is not allowlisted")
    return uri

@dataclass
class BoundedRateLimiter:
    window_seconds: int = 60
    max_requests: int = 120
    max_clients: int = 4096
    _buckets: dict[str, list[float]] = field(default_factory=dict)

    def allow(self, client: str, now: float | None = None) -> bool:
        now = time.monotonic() if now is None else now
        cutoff = now - self.window_seconds
        bucket = self._buckets.setdefault(client, [])
        bucket[:] = [stamp for stamp in bucket if stamp > cutoff]
        if len(bucket) >= self.max_requests:
            return False
        bucket.append(now)
        if len(self._buckets) > self.max_clients:
            oldest = min(self._buckets, key=lambda key: self._buckets[key][-1] if self._buckets[key] else 0)
            self._buckets.pop(oldest, None)
        return True
