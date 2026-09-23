from pathlib import Path


def test_container_deployment_contract():
    root = Path(__file__).resolve().parents[1]
    dockerfile = (root / "Dockerfile").read_text(encoding="utf-8")
    docs = (root / "docs" / "DEPLOYMENT_CONTAINER.md").read_text(encoding="utf-8")

    assert "python:3.11-slim" in dockerfile
    assert "ffmpeg" in dockerfile
    assert "USER wetu" in dockerfile
    assert "0.0.0.0" in dockerfile
    assert "/api/runtime/health" in dockerfile
    assert "WETU_PORT" in dockerfile
    assert "reproducible Python 3.11 container" in docs
