import json
from pathlib import Path


def test_adaptive_package_data_usage():
    root = Path("media/test/adaptive")
    manifest = json.loads((root / "package_manifest.json").read_text())
    assert manifest["variants"] == ["mobile_saver", "mobile", "standard"]
    assert manifest["deployment_active"] is False
    sizes = {}
    for name in manifest["variants"]:
        playlist = root / "hls" / name / "index.m3u8"
        assert playlist.stat().st_size > 0
        segments = sorted((root / "hls" / name).glob("seg_*.ts"))
        assert segments
        sizes[name] = sum(p.stat().st_size for p in segments)
        assert all(p.stat().st_size > 0 for p in segments)
    assert sizes["mobile_saver"] < sizes["mobile"] < sizes["standard"]
