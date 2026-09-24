import pytest
from unittest.mock import patch

from wetu_studio.media_security import MediaSecurityScanner
from wetu_studio.media_stability import MediaStabilityEngine


def test_image_signature_and_hash(tmp_path):
    p = tmp_path / "x.jpg"
    p.write_bytes(b"\xff\xd8\xff" + b"x" * 20)
    r = MediaSecurityScanner(require_antivirus=False).scan(p, "image/jpeg")
    assert r.clean and len(r.sha256) == 64


def test_bad_signature_is_blocked(tmp_path):
    p = tmp_path / "x.jpg"
    p.write_bytes(b"not-jpeg")
    with pytest.raises(ValueError, match="signature"):
        MediaSecurityScanner(require_antivirus=False).scan(p, "image/jpeg")


def test_malware_required_blocks_without_scanner(tmp_path):
    p = tmp_path / "x.jpg"
    p.write_bytes(b"\xff\xd8\xff" + b"x" * 20)
    with patch("wetu_studio.media_security.shutil.which", return_value=None):
        with pytest.raises(RuntimeError, match="antivirus scanner unavailable"):
            MediaSecurityScanner(require_antivirus=True).scan(p, "image/jpeg")


def test_video_stability_passes():
    r = MediaStabilityEngine().validate({"width": 1280, "height": 720, "duration_seconds": 5, "fps": 30, "decode_ok": True, "av_sync_ms": 20})
    assert r.passed


def test_video_stability_rejects_corruption():
    r = MediaStabilityEngine().validate({"width": 1280, "height": 720, "duration_seconds": 5, "fps": 30, "corrupt": True})
    assert not r.passed and "decode_failure" in r.issues
