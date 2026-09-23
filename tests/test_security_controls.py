from pathlib import Path

import pytest

from wetu_studio.security_controls import (
    BoundedRateLimiter,
    safe_project_path,
    validate_content_length,
    validate_media_uri,
    validate_project_id,
)

def test_project_id_and_path_boundaries(tmp_path: Path):
    assert validate_project_id("project_01") == "project_01"
    assert safe_project_path(tmp_path, "project_01") == (tmp_path / "project_01.json").resolve()
    for value in ("../escape", "a/b", "a\\b", "-bad", "a" * 65):
        with pytest.raises(ValueError):
            validate_project_id(value)

def test_content_length_rejects_malformed_and_oversized():
    assert validate_content_length("64", 64) == 64
    with pytest.raises(ValueError):
        validate_content_length("not-a-number", 64)
    with pytest.raises(ValueError):
        validate_content_length("65", 64)
    with pytest.raises(ValueError):
        validate_content_length(None, 64)

def test_media_uri_scheme_is_restricted():
    assert validate_media_uri("https://cdn.example/video.mp4").startswith("https://")
    assert validate_media_uri("memory://wetu/demo/video").startswith("memory://")
    for uri in ("file:///etc/passwd", "ftp://example/video.mp4", ""):
        with pytest.raises(ValueError):
            validate_media_uri(uri)

def test_rate_limiter_is_bounded_and_windowed():
    limiter = BoundedRateLimiter(window_seconds=10, max_requests=2, max_clients=2)
    assert limiter.allow("a", now=100.0)
    assert limiter.allow("a", now=101.0)
    assert not limiter.allow("a", now=102.0)
    assert limiter.allow("a", now=111.0)
    limiter.allow("b", now=112.0)
    limiter.allow("c", now=113.0)
    assert len(limiter._buckets) <= 2
